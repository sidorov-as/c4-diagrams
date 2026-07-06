from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass, field

from c4.converters.python.renderers import d2, mermaid, plantuml
from c4.diagrams.core import (
    DEFAULT_PROPERTIES_HEADER,
    BaseDiagramElement,
    Boundary,
    Diagram,
    DiagramElementProperties,
    Element,
    Relationship,
)
from c4.enums import RendererEnum
from c4.renderers import D2RenderOptions, MermaidRenderOptions, RenderOptions
from c4.renderers.base import IndentedStringBuilder
from c4.renderers.plantuml.options import PlantUMLRenderOptions

_DEFAULT_PROPERTIES_HEADER: tuple[str, str] = DEFAULT_PROPERTIES_HEADER
_C4_MACROS_MODULE_PREFIX = "c4.contrib.c4_macros"
_C4_MACROS_MODULE_PACKAGE = "c4.contrib.c4_macros"
_PLANTUML_CONTRIB_MODULE_PREFIX = "c4.contrib.plantuml"
_MERMAID_CONTRIB_MODULE_PREFIX = "c4.contrib.mermaid"
_PLANTUML_CONTRIB_PACKAGE = "c4.contrib.plantuml"
_MERMAID_CONTRIB_PACKAGE = "c4.contrib.mermaid"
_RENDERERS_PACKAGE = "c4.renderers"


@dataclass
class ImportPlan:
    """Grouped import names required by generated Python code."""

    c4_names: set[str] = field(default_factory=set)
    contrib_names: dict[str, set[str]] = field(default_factory=dict)
    renderer_names: set[str] = field(default_factory=set)

    def add_c4(self, name: str) -> None:
        self.c4_names.add(name)

    def add_contrib(self, package: str, name: str) -> None:
        self.contrib_names.setdefault(package, set()).add(name)


class PythonCodegen:
    """
    Generate Python DSL code that recreates an existing Diagram.

    The generated output is intended to be:

    - Readable: stable ordering, minimal noise, consistent spacing.
    - Executable: contains imports required to run the DSL.
    - Semantically equivalent: recreates the same structure
        (elements, boundaries, relationships, layouts, and
        macro-like ordered statements).

    Rendering rules / invariants:

    - Scope children are rendered directly from `ordered_elements`, matching
      the declaration stream used by runtime renderers.

    The codegen relies on `__repr__` implementations of DSL
    objects being valid DSL.
    """

    def __init__(self, backend: RendererEnum | None = None) -> None:
        self._backend = backend
        self._builder = IndentedStringBuilder()

    def _iter_ordered_items(
        self,
        scope: Diagram | Boundary,
    ) -> Iterator[BaseDiagramElement]:
        """Yield a scope's ordered items, recursively entering boundaries."""
        for item in scope.ordered_elements:
            yield item

            if isinstance(item, Boundary):
                yield from self._iter_ordered_items(item)

    def _build_import_plan(self, diagram: Diagram) -> ImportPlan:
        """Collect every import required by generated Python code."""
        import_plan = ImportPlan(c4_names={type(diagram).__name__})

        for item in self._iter_ordered_items(diagram):
            self._add_item_import(import_plan, item)

        render_options = diagram.render_options
        if render_options:
            if render_options.d2:
                import_plan.renderer_names.add("D2RenderOptionsBuilder")

                if render_options.d2.legend:
                    import_plan.renderer_names.add("D2Legend")
                    import_plan.renderer_names.add("D2LegendElement")
                    import_plan.renderer_names.add("D2LegendRel")

            if render_options.plantuml:
                import_plan.renderer_names.add("PlantUMLRenderOptionsBuilder")

            if render_options.mermaid:
                import_plan.renderer_names.add("MermaidRenderOptionsBuilder")

        return import_plan

    def _add_item_import(
        self,
        import_plan: ImportPlan,
        item: BaseDiagramElement,
    ) -> None:
        class_name = type(item).__name__
        package = self._contrib_import_package(item)
        if package:
            import_plan.add_contrib(package, class_name)
        else:
            import_plan.add_c4(class_name)

    def _contrib_import_package(
        self,
        item: BaseDiagramElement,
    ) -> str | None:
        module = type(item).__module__
        if module.startswith(_C4_MACROS_MODULE_PREFIX):
            if self._backend is RendererEnum.MERMAID:
                return _MERMAID_CONTRIB_PACKAGE
            elif self._backend is RendererEnum.PLANTUML:
                return _PLANTUML_CONTRIB_PACKAGE
            return _C4_MACROS_MODULE_PACKAGE
        if module.startswith(_PLANTUML_CONTRIB_MODULE_PREFIX):
            return _PLANTUML_CONTRIB_PACKAGE
        if module.startswith(_MERMAID_CONTRIB_MODULE_PREFIX):
            return _MERMAID_CONTRIB_PACKAGE

        return None

    def _render_ordered_statement(
        self,
        element: BaseDiagramElement,
    ) -> None:
        """
        Render an ordered item that is not a plain element, boundary, or
        relationship.
        """
        self._builder.add(f"{element!r}")

    @contextmanager
    def _render_boundary_def(self, boundary: Boundary) -> Iterator[None]:
        """
        Render the `with Boundary(...):` line and (optionally) its
        property table.

        If boundary has properties, we emit `with <repr> as <alias>:` so
        we can configure those properties on the alias inside the block.
        """
        alias = boundary.alias
        diagram = boundary.diagram

        has_properties = bool(boundary.properties)

        need_variable = (
            diagram.is_element_referenced_by_alias(alias) or has_properties
        )

        if need_variable:
            self._builder.add(f"with {boundary!r} as {alias}:")
        else:
            self._builder.add(f"with {boundary!r}:")

        if has_properties:
            with self._builder.indent():
                self._render_properties(alias, boundary.properties)

        with self._builder.indent():
            yield

    def _render_boundary(self, boundary: Boundary) -> None:
        """
        Render a boundary block, including its contents in canonical order.
        """
        with self._render_boundary_def(boundary):
            rendered = self._render_scope_items(boundary)

            if not rendered:
                self._render_pass()

    @contextmanager
    def _render_diagram_def(self, diagram: Diagram) -> Iterator[None]:
        """
        Render the outer `with Diagram(...):` block.
        """
        self._builder.add(f"with {diagram!r} as diagram:")

        with self._builder.indent():
            yield

    def _render_element(self, element: Element) -> None:
        """
        Render a single element assignment and its optional property table.
        """
        alias = element.alias

        self._builder.add(f"{alias} = {element!r}")

        if element.properties:
            self._render_properties(alias, element.properties)

    def _render_imports(self, diagram: Diagram) -> None:
        """
        Render a single `from c4 import (...)` block containing all
        required classes.

        The import list is alphabetically sorted to keep output stable
        across runs.
        """
        import_plan = self._build_import_plan(diagram)

        self._builder.add("from c4 import (")

        for class_name in sorted(import_plan.c4_names):
            self._builder.add(f"    {class_name},")

        self._builder.add(")")

        for package, package_class_names in sorted(
            import_plan.contrib_names.items()
        ):
            self._builder.add(f"from {package} import (")

            for class_name in sorted(package_class_names):
                self._builder.add(f"    {class_name},")

            self._builder.add(")")

        if import_plan.renderer_names:
            self._builder.add(f"from {_RENDERERS_PACKAGE} import (")
            for class_name in sorted(import_plan.renderer_names):
                self._builder.add(f"    {class_name},")

            self._builder.add(")")

        self._builder.add_blank_line(check_duplicates=False)
        self._builder.add_blank_line(check_duplicates=False)

    def _render_plantuml_render_options(
        self,
        render_options: PlantUMLRenderOptions,
    ) -> None:
        """
        Render PlantUML render options builder code after
        the diagram definition.

        This uses `PlantUMLRenderOptionsCodegen` to turn
        a `PlantUMLRenderOptions` into Python DSL that
        recreates the same config.
        """
        render_options_codegen = plantuml.PlantUMLRenderOptionsCodegen()

        self._builder.add(render_options_codegen.generate(render_options))

    def _render_mermaid_render_options(
        self,
        render_options: MermaidRenderOptions,
    ) -> None:
        """
        Render Mermaid render options builder code after
        the diagram definition.

        This uses `MermaidRenderOptionsCodegen` to turn
        a `MermaidRenderOptions` into Python DSL that
        recreates the same config.
        """
        render_options_codegen = mermaid.MermaidRenderOptionsCodegen()

        self._builder.add(render_options_codegen.generate(render_options))

    def _render_d2_render_options(
        self,
        render_options: D2RenderOptions,
    ) -> None:
        """Render D2 render options builder code after the diagram."""
        render_options_codegen = d2.D2RenderOptionsCodegen()

        self._builder.add(render_options_codegen.generate(render_options))

    def _set_diagram_render_options(
        self,
        render_options: RenderOptions,
    ) -> None:
        options_to_render = []

        self._builder.add_blank_line(check_duplicates=True)
        self._builder.add_blank_line(check_duplicates=False)

        if render_options.d2:
            self._render_d2_render_options(render_options.d2)
            options_to_render.append(f"d2={d2.RENDER_OPTIONS_VARIABLE_NAME}")

        if render_options.plantuml:
            self._render_plantuml_render_options(render_options.plantuml)
            options_to_render.append(
                f"plantuml={plantuml.RENDER_OPTIONS_VARIABLE_NAME}"
            )

        if render_options.mermaid:
            self._render_mermaid_render_options(render_options.mermaid)
            options_to_render.append(
                f"mermaid={mermaid.RENDER_OPTIONS_VARIABLE_NAME}"
            )

        if options_to_render:
            self._builder.add_blank_line(check_duplicates=True)
            attrs = [f"    {option}," for option in options_to_render]
            signature = "\n".join(attrs)
            self._builder.add(f"diagram.set_render_options(\n{signature}\n)")

    def _render_properties(
        self,
        alias: str,
        properties: DiagramElementProperties,
    ) -> None:
        """
        Render element/boundary property tables.

        Output minimization rules:

        - If there are no property rows, header is shown, and the
          header equals the library default, nothing is emitted.
        - If header should be hidden, emit `<alias>.without_property_header()`.
        - If header differs from default,
          emit `<alias>.set_property_header(...)`.
        - Each property row is emitted via `<alias>.add_property(...)`.

        A trailing blank line is added to visually separate the table
        from subsequent code.
        """
        has_rows = bool(properties.properties)
        header = tuple(properties.header)

        if not has_rows:
            return

        if not properties.show_header:
            self._builder.add(f"{alias}.without_property_header()")

        elif header != _DEFAULT_PROPERTIES_HEADER:
            header_sig = ", ".join([f"{item!r}" for item in properties.header])
            self._builder.add(f"{alias}.set_property_header({header_sig})")

        for row in properties.properties:
            row_sig = ", ".join([f"{item!r}" for item in row])
            self._builder.add(f"{alias}.add_property({row_sig})")

        self._builder.add_blank_line()

    def _render_relationship(self, relationship: Relationship) -> None:
        """
        Render a relationship in fluent DSL form: `a >> Rel(...) >> b`.
        """
        from_element, to_element = relationship.get_participants()  # type: ignore[var-annotated]
        diagram = relationship.diagram
        from_, to_ = from_element.alias, to_element.alias

        need_variable = bool(relationship.properties)

        if need_variable:
            rel_variable = diagram.generate_alias(label=f"rel_{from_}_{to_}")
            self._builder.add(
                f"{rel_variable} = {from_} >> {relationship!r} >> {to_}"
            )

            self._render_properties(rel_variable, relationship.properties)
        else:
            self._builder.add(f"{from_} >> {relationship!r} >> {to_}")

    def _render_pass(self) -> None:
        """
        Add `pass` statement.
        """
        self._builder.add("pass")

    def _render_scope_item(self, item: BaseDiagramElement) -> None:
        """Render one direct declaration item in a diagram or boundary scope."""
        if isinstance(item, Boundary):
            self._render_boundary(item)
        elif isinstance(item, Element):
            self._render_element(item)
        elif isinstance(item, Relationship):
            self._render_relationship(item)
        else:
            self._render_ordered_statement(item)

        if not isinstance(item, Relationship):
            self._builder.add_blank_line()

    def _render_scope_items(self, parent: Diagram | Boundary) -> bool:
        """Render direct children in definition order."""
        for item in parent.ordered_elements:
            self._render_scope_item(item)

        return bool(parent.ordered_elements)

    def generate(
        self,
        diagram: Diagram,
    ) -> str:
        """
        Generate Python DSL that recreates `diagram`.

        Args:
            diagram: The diagram instance to serialize into Python DSL.

        Returns:
            A Python source string that can be executed to reconstruct
            the diagram.
        """
        self._builder.reset()

        self._render_imports(diagram)

        with self._render_diagram_def(diagram):
            rendered = self._render_scope_items(diagram)

            if not rendered:
                self._render_pass()

        if diagram.render_options:
            self._set_diagram_render_options(diagram.render_options)

        return self._builder.get_result()


def diagram_to_python_code(
    diagram: Diagram, backend: RendererEnum | None = None
) -> str:
    """
    Convenience helper to generate Python DSL from a diagram.

    Args:
        diagram: The diagram instance to serialize.
        backend: Optional rendering backend type.

    Returns:
        Python code that recreates the given diagram.
    """
    renderer = PythonCodegen(backend)

    return renderer.generate(diagram)

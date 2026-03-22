from collections.abc import Iterator
from contextlib import contextmanager

from c4.converters.python.renderers import plantuml
from c4.diagrams.core import (
    DEFAULT_PROPERTIES_HEADER,
    BaseDiagramElement,
    Boundary,
    Diagram,
    DiagramElementProperties,
    Element,
    Relationship,
    increment,
    set_index,
)
from c4.renderers import RenderOptions
from c4.renderers.base import IndentedStringBuilder
from c4.renderers.plantuml.layout_options import LayoutConfig

_DEFAULT_PROPERTIES_HEADER: tuple[str, str] = DEFAULT_PROPERTIES_HEADER


class PythonCodegen:
    """
    Generate Python DSL code that recreates an existing Diagram.

    The generated output is intended to be:

    - Readable: stable ordering, minimal noise, consistent spacing.
    - Executable: contains imports required to run the DSL.
    - Semantically equivalent: recreates the same structure
        (elements, boundaries, relationships, layouts, and
        macro-like base elements).

    Rendering rules / invariants:

    - Elements are rendered before relationships so aliases exist.
    - Relationships are rendered from `parent.relationships`
      (not from `base_elements`) to avoid duplication
      (except for DynamicDiagram edge-cases, see below).
    - `base_elements` are rendered for non-structural macro calls
      (e.g., index macros in Dynamic diagrams) and in rare cases may also
      contain relationships
      (some DynamicDiagram implementations store them there).

    The codegen relies on `__repr__` implementations of DSL
    objects being valid DSL.
    """

    def __init__(self) -> None:
        self._builder = IndentedStringBuilder()

    def _collect_class_names(self, parent: Diagram | Boundary) -> set[str]:
        """
        Collect all DSL class names that must be imported to recreate `parent`.

        This walks the full subtree:
        - the parent object itself (Diagram or Boundary)
        - nested elements
        - nested boundaries (recursively)
        - relationships
        - layouts
        - base elements (macro-like nodes)

        Returns:
            A set of class names (strings) to import from `c4`.
        """
        class_names = {
            type(parent).__name__,
        }

        layouts = getattr(parent, "layouts", [])
        base_elements = getattr(parent, "base_elements", [])

        for element in parent.elements:
            class_names.add(type(element).__name__)

        for nested_boundary in parent.boundaries:
            class_names.update(self._collect_class_names(nested_boundary))

        for relationship in parent.relationships:
            class_names.add(type(relationship).__name__)

        for layout in layouts:
            class_names.add(type(layout).__name__)

        for base_element in base_elements:
            class_names.add(type(base_element).__name__)

        return class_names

    def _render_base_element(
        self,
        element: BaseDiagramElement,
    ) -> None:
        """
        Render a single non-structural "base element".

        Base elements usually represent macro-like calls
        (e.g. index manipulation), but some diagram types may store
        relationships here as well.
        """
        if isinstance(element, Relationship):  # Edge case for DynamicDiagram
            return self._render_relationship(element)
        elif isinstance(element, (increment, set_index)):
            return self._builder.add(f"{element!r}")

        raise TypeError(f"Unsupported element {element!r}")

    def _render_base_elements(self, parent: Diagram) -> bool:
        """
        Render all `base_elements` for the given parent, preserving
        their order.
        """
        for base_element in parent.base_elements:
            self._render_base_element(base_element)

        return bool(parent.base_elements)

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

        need_variable = (
            diagram.is_element_referenced_by_alias(alias)
            or boundary.properties.properties
        )

        if need_variable:
            self._builder.add(f"with {boundary!r} as {alias}:")
        else:
            self._builder.add(f"with {boundary!r}:")

        if boundary.properties.properties:
            with self._builder.indent():
                self._render_properties(alias, boundary.properties)

        with self._builder.indent():
            yield

    def _render_boundary(self, boundary: Boundary) -> None:
        """
        Render a boundary block, including its contents in canonical order.
        """
        with self._render_boundary_def(boundary):
            has_elements = (
                self._render_elements(boundary),
                self._render_boundaries(boundary),
                self._render_relationships(boundary),
            )

            if not any(has_elements):
                self._render_pass()

    def _render_boundaries(self, parent: Diagram | Boundary) -> bool:
        """
        Render all nested boundaries inside `parent`.
        """
        for boundary in parent.boundaries:
            self._render_boundary(boundary)
            self._builder.add_blank_line()

        if parent.boundaries:
            self._builder.add_blank_line(check_duplicates=True)

        return bool(parent.boundaries)

    @contextmanager
    def _render_diagram_def(self, diagram: Diagram) -> Iterator[None]:
        """
        Render the outer `with Diagram(...):` block.
        """
        need_variable = (
            diagram.render_options and not diagram.render_options.is_empty
        )

        if need_variable:
            self._builder.add(f"with {diagram!r} as diagram:")
        else:
            self._builder.add(f"with {diagram!r}:")

        with self._builder.indent():
            yield

    def _render_element(self, element: Element) -> None:
        """
        Render a single element assignment and its optional property table.
        """
        alias = element.alias

        self._builder.add(f"{alias} = {element!r}")

        if element.properties.properties:
            self._render_properties(alias, element.properties)

    def _render_elements(self, parent: Diagram | Boundary) -> bool:
        """
        Render all elements in `parent` in their original order.

        Elements are emitted before relationships so aliases are defined.
        """
        for element in parent.elements:
            self._render_element(element)

        return bool(parent.elements)

    def _render_imports(self, diagram: Diagram) -> None:
        """
        Render a single `from c4 import (...)` block containing all
        required classes.

        The import list is alphabetically sorted to keep output stable
        across runs.
        """
        class_names = self._collect_class_names(diagram)

        self._builder.add("from c4 import (")

        for class_name in sorted(class_names):
            self._builder.add(f"    {class_name},")

        self._builder.add(")")

        if diagram.render_options and not diagram.render_options.is_empty:
            self._builder.add("from c4.renderers import RenderOptions")

            if diagram.render_options.plantuml:  # pragma: no cover
                self._builder.add(
                    "from c4.renderers.plantuml import LayoutOptions"
                )

        self._builder.add_blank_line(check_duplicates=False)
        self._builder.add_blank_line(check_duplicates=False)

    def _render_layouts(self, diagram: Diagram) -> bool:
        """
        Render diagram layouts (if any) at the end of the diagram block.
        """
        for layout in diagram.layouts:
            self._builder.add(f"{layout!r}")

        return bool(diagram.layouts)

    def _render_plantuml_layout_options(
        self,
        layout_config: LayoutConfig,
    ) -> None:
        """
        Render PlantUML layout options builder code after
        the diagram definition.

        This uses `LayoutOptionsCodegen` to turn a `LayoutConfig` into
        Python DSL that recreates the same config.
        """
        layout_options_codegen = plantuml.LayoutOptionsCodegen()

        self._builder.add_blank_line(check_duplicates=False)
        self._builder.add_blank_line(check_duplicates=False)
        self._builder.add(layout_options_codegen.generate(layout_config))

    def _set_diagram_render_options(
        self,
        render_options: RenderOptions,
    ) -> None:
        options_to_render = []

        if render_options.plantuml:
            self._render_plantuml_layout_options(render_options.plantuml)
            options_to_render.append(
                f"plantuml={plantuml.LAYOUT_OPTIONS_VARIABLE_NAME}"
            )

        if options_to_render:
            self._builder.add_blank_line(check_duplicates=True)
            attrs = [f"    {option}," for option in options_to_render]
            signature = "\n".join(attrs)
            self._builder.add(
                f"render_options = RenderOptions(\n{signature}\n)"
            )

            self._builder.add_blank_line(check_duplicates=False)
            self._builder.add("diagram.render_options = render_options")

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
        from_element, to_element = relationship.get_participants()

        self._builder.add(
            f"{from_element.alias} >> {relationship!r} >> {to_element.alias}"
        )

    def _render_relationships(self, parent: Diagram | Boundary) -> bool:
        """
        Render relationships for `parent` in their original order.
        """
        for relationship in parent.relationships:
            self._render_relationship(relationship)

        return bool(parent.relationships)

    def _render_pass(self) -> None:
        """
        Add `pass` statement.
        """
        self._builder.add("pass")

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
            has_elements = (
                self._render_elements(diagram),
                self._render_boundaries(diagram),
                self._render_relationships(diagram),
                self._render_base_elements(diagram),
                self._render_layouts(diagram),
            )

            if not any(has_elements):
                self._render_pass()

        if diagram.render_options:
            self._set_diagram_render_options(diagram.render_options)

        return self._builder.get_result()


def diagram_to_python_code(diagram: Diagram) -> str:
    """
    Convenience helper to generate Python DSL from a diagram.

    Args:
        diagram: The diagram instance to serialize.

    Returns:
        Python code that recreates the given diagram.
    """
    renderer = PythonCodegen()

    return renderer.generate(diagram)

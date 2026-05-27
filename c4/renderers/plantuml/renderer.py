from __future__ import annotations

from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Generic,
    TypeAlias,
)

from typing_extensions import override

from c4 import (
    ComponentDiagram,
    ContainerDiagram,
    DeploymentDiagram,
    SystemContextDiagram,
    SystemLandscapeDiagram,
)
from c4.contrib.plantuml.components import Layout, increment, set_index
from c4.diagrams.core import (
    BaseDiagramElement,
    Boundary,
    Diagram,
    Element,
    Relationship,
    TDiagram,
)
from c4.diagrams.dynamic import DynamicDiagram
from c4.enums import RendererEnum
from c4.exceptions import PlantUMLBackendConfigurationError
from c4.renderers.base import (
    IGNORE_FOREIGN,
    BaseRenderer,
    ExtensionValidationModeType,
    IndentedStringBuilder,
)
from c4.renderers.plantuml.backends import BasePlantUMLBackend, DiagramFormat
from c4.renderers.plantuml.constants import (
    C4_COMPONENT_INCLUDE,
    C4_CONTAINER_INCLUDE,
    C4_CONTEXT_INCLUDE,
    C4_DEPLOYMENT_INCLUDE,
    C4_DYNAMIC_INCLUDE,
    RELATIVE_INCLUDE_COMMENT,
)
from c4.renderers.plantuml.macros import (
    DiagramLayoutPlantUMLMacro,
    ElementPlantUMLMacro,
    HidePersonSpritePlantUMLMacro,
    HideStereotypePlantUMLMacro,
    IncrementPlantUMLMacro,
    LayoutAsSketchPlantUMLMacro,
    LayoutPlantUMLMacro,
    LayoutWithLegendPlantUMLMacro,
    PlantUMLMacro,
    RelationshipPlantUMLMacro,
    SetIndexPlantUMLMacro,
    SetSketchStylePlantUMLMacro,
    ShowFloatingLegendPlantUMLMacro,
    ShowLegendPlantUMLMacro,
    ShowPersonOutlinePlantUMLMacro,
    ShowPersonSpritePlantUMLMacro,
    StylePlantUMLMacro,
    TagPlantUMLMacro,
    UpdateLegendTitlePlantUMLMacro,
    WithoutPropertyHeaderPlantUMLMacro,
)
from c4.renderers.plantuml.options import PlantUMLRenderOptions
from c4.renderers.plantuml.validation import validate_plantuml_diagram


class PlantUMLRenderOptionsRenderer:
    def __init__(
        self,
        includes: list[str],
        render_options: PlantUMLRenderOptions | None = None,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            includes: A list of PlantUML `!include` directives
                to be injected at the beginning of the diagram.
            render_options: Render options that controls
                diagram rendering behavior, such as direction,
                spacing, and group alignment.
        """
        self._includes = includes
        self._render_options = render_options or PlantUMLRenderOptions()

    def _render_tags(self) -> str:
        builder = IndentedStringBuilder()

        for tag in self._render_options.tags:
            macro = TagPlantUMLMacro.get_macro_by_tag(tag)  # type: ignore[var-annotated]
            builder.add(macro.render())

        return builder.get_result()

    def _render_styles(self) -> str:
        builder = IndentedStringBuilder()

        for style in self._render_options.styles:
            macro = StylePlantUMLMacro.get_macro_by_style(style)  # type: ignore[var-annotated]
            builder.add(macro.render())

        return builder.get_result()

    def _render_layout(self) -> str:
        builder = IndentedStringBuilder()
        macro: PlantUMLMacro[Any]

        if self._render_options.layout:
            macro = DiagramLayoutPlantUMLMacro(self._render_options.layout)
            builder.add(macro.render())

        if self._render_options.layout_with_legend:
            macro = LayoutWithLegendPlantUMLMacro()
            builder.add(macro.render())

        if self._render_options.layout_as_sketch:
            macro = LayoutAsSketchPlantUMLMacro()
            builder.add(macro.render())

        if self._render_options.hide_person_sprite:
            macro = HidePersonSpritePlantUMLMacro()
            builder.add(macro.render())

        if self._render_options.show_person_sprite:
            macro = ShowPersonSpritePlantUMLMacro(
                self._render_options.show_person_sprite
            )
            builder.add(macro.render())

        if self._render_options.show_person_outline:
            macro = ShowPersonOutlinePlantUMLMacro()
            builder.add(macro.render())

        if self._render_options.legend_title:
            macro = UpdateLegendTitlePlantUMLMacro(
                self._render_options.legend_title
            )
            builder.add(macro.render())

        if self._render_options.hide_stereotype:
            macro = HideStereotypePlantUMLMacro()
            builder.add(macro.render())

        if self._render_options.without_property_header:
            macro = WithoutPropertyHeaderPlantUMLMacro()
            builder.add(macro.render())

        return builder.get_result()

    def _render_sketch_style(self) -> str:
        builder = IndentedStringBuilder()

        if self._render_options.set_sketch_style:
            macro = SetSketchStylePlantUMLMacro(
                self._render_options.set_sketch_style
            )
            builder.add(macro.render())

        return builder.get_result()

    def render_header(self, diagram: TDiagram) -> str:
        builder = IndentedStringBuilder()

        builder.add(*self._includes, blank_line_after=True)

        builder.add(self._render_tags(), blank_line_after=True)
        builder.add(self._render_styles(), blank_line_after=True)
        builder.add(self._render_layout(), blank_line_after=True)
        builder.add(self._render_sketch_style(), blank_line_after=True)

        if diagram.title:
            builder.add(f"title {diagram.title}", blank_line_after=True)

        return builder.get_result()

    def render_footer(self) -> str:
        builder = IndentedStringBuilder()
        macro: PlantUMLMacro[Any]

        if self._render_options.show_legend:
            macro = ShowLegendPlantUMLMacro(self._render_options.show_legend)
            builder.add(macro.render(), blank_line_after=True)

        if self._render_options.show_floating_legend:
            macro = ShowFloatingLegendPlantUMLMacro(
                self._render_options.show_floating_legend
            )
            builder.add(macro.render(), blank_line_after=True)

        return builder.get_result()


class BasePlantUMLRenderer(BaseRenderer[TDiagram], Generic[TDiagram]):
    """A base renderer for converting a Diagram object into PlantUML syntax."""

    renderer_type: RendererEnum = RendererEnum.PLANTUML
    default_includes: ClassVar[list[str]]

    def __init__(
        self,
        includes: list[str] | None = None,
        render_options: PlantUMLRenderOptions | None = None,
        backend: BasePlantUMLBackend | None = None,
        use_new_c4_style: bool = False,
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            includes: A list of PlantUML `!include` directives
                to be injected at the beginning of the diagram.
            render_options: Render options that controls
                diagram rendering behavior, such as direction,
                spacing, and group alignment.
            backend:
                Optional PlantUML backend responsible for converting
                generated PlantUML source into image bytes (e.g. PNG, SVG).
                If not provided, image rendering is not available.
            use_new_c4_style:
                If ``True``, activates the new C4-PlantUML style by injecting
                the following directive into the generated source:
                    !NEW_C4_STYLE=1
            extension_validation_mode:
                Policy for foreign backend extensions.
        """
        super().__init__(extension_validation_mode=extension_validation_mode)
        self._render_options = render_options or PlantUMLRenderOptions()

        _includes = list(getattr(self, "default_includes", []))
        _includes.extend(includes or [])
        _includes.extend(self._render_options.includes)

        self._render_options_renderer = PlantUMLRenderOptionsRenderer(
            includes=_includes,
            render_options=self._render_options,
        )
        self._without_property_header = (
            self._render_options.without_property_header
        )

        self._builder = IndentedStringBuilder()

        self._includes = includes or []
        self._plantuml_backend = backend
        self._use_new_c4_style = use_new_c4_style

    def _render_element(self, element: Element) -> list[str]:
        macro = ElementPlantUMLMacro.from_element(element)

        properties_macros = macro.render_properties(
            self._without_property_header
        )
        element_macro = macro.render()

        return [*properties_macros, element_macro]

    def _render_boundary(self, boundary: Boundary, depth: int = 0) -> str:
        builder = IndentedStringBuilder(level=depth)

        *properties, element_macro = self._render_element(boundary)
        builder.add(*properties, element_macro + " {")

        with builder.indent() as level:
            for item in self.iter_boundary_render_items(boundary):
                if isinstance(item, Boundary):
                    builder.add(
                        self._render_boundary(item, depth=level),
                        indent=False,
                    )
                elif isinstance(item, Element):
                    *properties, element_macro = self._render_element(item)
                    builder.add(*properties, element_macro)
                elif isinstance(item, Relationship):
                    *properties, relationship_macro = self._render_relationship(
                        item
                    )
                    builder.add(*properties, relationship_macro)
                elif statement := self._render_backend_statement(item):
                    builder.add(*statement)
                else:  # pragma: no cover
                    raise TypeError(f"Unsupported element {item!r}")

        builder.add("}")

        return builder.get_result()

    def _render_relationship(self, relationship: Relationship) -> list[str]:
        macro = RelationshipPlantUMLMacro(relationship)

        properties_macros = macro.render_properties(
            self._without_property_header
        )
        relationship_macro = macro.render()
        return [*properties_macros, relationship_macro]

    def _render_layout(self, layout: Layout) -> list[str]:
        macro = LayoutPlantUMLMacro(layout)

        properties_macros = macro.render_properties(
            self._without_property_header
        )
        layout_macro = macro.render()

        return [*properties_macros, layout_macro]

    def _render_backend_statement(
        self, item: BaseDiagramElement
    ) -> list[str] | None:
        """Render backend-owned ordered statements inside scoped blocks."""
        return None

    def _render_header(self, diagram: TDiagram) -> None:
        self._builder.add("@startuml")

        if self._use_new_c4_style:
            self._builder.add_blank_line()
            self._builder.add("!NEW_C4_STYLE=1", blank_line_after=True)

        layout_header = self._render_options_renderer.render_header(diagram)
        self._builder.add(layout_header, blank_line_after=True)

    def _render_footer(self) -> None:
        footer = self._render_options_renderer.render_footer()

        self._builder.add(footer, blank_line_after=True)

        self._builder.add("@enduml")

    def _render_item(self, item: BaseDiagramElement) -> None:
        if isinstance(item, Layout):
            return

        if isinstance(item, Boundary):
            self._builder.add(self._render_boundary(item))
        elif isinstance(item, Element):
            *properties, element_macro = self._render_element(item)
            self._builder.add(*properties, element_macro)
        elif isinstance(item, Relationship):
            *properties, relationship_macro = self._render_relationship(item)
            self._builder.add(*properties, relationship_macro)
        else:  # pragma: no cover
            raise TypeError(f"Unsupported element {item!r}")

        if not isinstance(item, Relationship):
            self._builder.add_blank_line()

    def _render_body(self, diagram: TDiagram) -> None:
        for item in self.iter_render_items(diagram):
            self._render_item(item)

    def _render_layouts(self, diagram: TDiagram) -> None:
        layouts = [
            item
            for item in self.iter_render_items(diagram)
            if isinstance(item, Layout)
        ]

        for idx, layout in enumerate(layouts, start=1):
            *properties, layout_macro = self._render_layout(layout)
            self._builder.add(
                *properties,
                layout_macro,
                blank_line_after=idx == len(layouts),
            )

    @override
    def validate(self, diagram: TDiagram) -> None:
        """Validate PlantUML-specific rendering constraints."""
        validate_plantuml_diagram(
            diagram,
            renderer_name=self.__class__.__name__,
            extension_validation_mode=self._extension_validation_mode,
        )

    @override
    def render(self, diagram: TDiagram) -> str:
        """
        Render the given Diagram into PlantUML format.

        Args:
            diagram: The diagram to render.

        Returns:
            A PlantUML-formatted string representing the diagram.
        """
        self.validate(diagram)
        self._builder.reset()

        self._render_header(diagram)
        self._render_body(diagram)
        self._render_layouts(diagram)
        self._render_footer()

        return self._builder.get_result()

    def render_bytes(
        self,
        diagram: TDiagram,
        *,
        format: DiagramFormat,
    ) -> bytes:
        """
        Render a Diagram and return the result as raw bytes.

        This method first converts the Diagram into PlantUML source text
        and then delegates the actual rendering to the
        configured PlantUML backend.

        Args:
            diagram: The diagram instance to render.
            format: Output format of the rendered diagram.

        Returns:
            The rendered diagram content as raw bytes.

        Raises:
            PlantUMLBackendConfigurationError: If no PlantUML backend is
                configured for this renderer.
            PlantUMLError: If the underlying PlantUML backend fails to
                render the diagram.
        """
        if not self._plantuml_backend:
            raise PlantUMLBackendConfigurationError()

        diagram_source = self.render(diagram)

        return self._plantuml_backend.to_bytes(
            diagram=diagram_source,
            format=format,
        )

    def render_file(
        self,
        diagram: TDiagram,
        output_path: str | Path,
        *,
        format: DiagramFormat,
        overwrite: bool = True,
    ) -> Path:
        """
        Render a Diagram and write the result to a file.

        This method first converts the Diagram into PlantUML source text
        and then delegates file generation to the
        configured PlantUML backend.

        Args:
            diagram: The diagram instance to render.
            output_path: Path where the rendered diagram should be written.
            format: Output format of the rendered diagram.
            overwrite: Whether to overwrite the output file if it already
                exists.

        Returns:
            Path to the written output file.

        Raises:
            PlantUMLBackendConfigurationError: If no PlantUML backend is
                configured for this renderer.
            FileExistsError: If the output file exists and ``overwrite`` is
                set to ``False``.
            PlantUMLError: If the underlying PlantUML backend fails to
                render or write the diagram.
        """
        if not self._plantuml_backend:
            raise PlantUMLBackendConfigurationError()

        diagram_source = self.render(diagram)

        return self._plantuml_backend.to_file(
            diagram=diagram_source,
            output_path=output_path,
            format=format,
            overwrite=overwrite,
        )


_DiagramType: TypeAlias = type[Diagram]
_Renderer: TypeAlias = type[BasePlantUMLRenderer[Any]]


class PlantUMLSystemContextDiagramRenderer(
    BasePlantUMLRenderer[SystemContextDiagram]
):
    """
    Renderer for converting a SystemContextDiagram object into PlantUML syntax.
    """

    default_includes: ClassVar[list[str]] = [
        RELATIVE_INCLUDE_COMMENT,
        C4_CONTEXT_INCLUDE,
    ]


class PlantUMLSystemLandscapeDiagramRenderer(
    BasePlantUMLRenderer[SystemLandscapeDiagram]
):
    """
    Renderer for converting a SystemLandscapeDiagram object into
    PlantUML syntax.
    """

    default_includes: ClassVar[list[str]] = [
        RELATIVE_INCLUDE_COMMENT,
        C4_CONTEXT_INCLUDE,
    ]


class PlantUMLContainerDiagramRenderer(BasePlantUMLRenderer[ContainerDiagram]):
    """
    Renderer for converting a ContainerDiagram object into PlantUML syntax.
    """

    default_includes: ClassVar[list[str]] = [
        RELATIVE_INCLUDE_COMMENT,
        C4_CONTAINER_INCLUDE,
    ]


class PlantUMLComponentDiagramRenderer(BasePlantUMLRenderer[ComponentDiagram]):
    """
    Renderer for converting a ComponentDiagram object into PlantUML syntax.
    """

    default_includes: ClassVar[list[str]] = [
        RELATIVE_INCLUDE_COMMENT,
        C4_COMPONENT_INCLUDE,
    ]


class PlantUMLDynamicDiagramRenderer(BasePlantUMLRenderer[DynamicDiagram]):
    """
    Renderer for converting a DynamicDiagram object into PlantUML syntax.
    """

    default_includes: ClassVar[list[str]] = [
        RELATIVE_INCLUDE_COMMENT,
        C4_DYNAMIC_INCLUDE,
    ]

    @override
    def _render_backend_statement(
        self, item: BaseDiagramElement
    ) -> list[str] | None:
        macro: PlantUMLMacro[Any]

        if isinstance(item, increment):
            macro = IncrementPlantUMLMacro(item)
        elif isinstance(item, set_index):
            macro = SetIndexPlantUMLMacro(item)
        else:
            return None

        properties = macro.render_properties(self._without_property_header)
        element_macro = macro.render()

        return [*properties, element_macro]

    @override
    def _render_item(self, item: BaseDiagramElement) -> None:
        if isinstance(item, Relationship):
            *properties, relationship_macro = self._render_relationship(item)
            self._builder.add(*properties, relationship_macro)
            if properties:
                self._builder.add_blank_line()
        elif statement := self._render_backend_statement(item):
            self._builder.add(*statement)
        else:
            return super()._render_item(item)

        return None


class PlantUMLDeploymentDiagramRenderer(
    BasePlantUMLRenderer[DeploymentDiagram]
):
    """
    Renderer for converting a DeploymentDiagram object into PlantUML syntax.
    """

    default_includes: ClassVar[list[str]] = [
        RELATIVE_INCLUDE_COMMENT,
        C4_DEPLOYMENT_INCLUDE,
    ]


DIAGRAM_TYPE_TO_RENDERER_MAP: dict[_DiagramType, _Renderer] = {
    SystemContextDiagram: PlantUMLSystemContextDiagramRenderer,
    SystemLandscapeDiagram: PlantUMLSystemLandscapeDiagramRenderer,
    ContainerDiagram: PlantUMLContainerDiagramRenderer,
    ComponentDiagram: PlantUMLComponentDiagramRenderer,
    DynamicDiagram: PlantUMLDynamicDiagramRenderer,
    DeploymentDiagram: PlantUMLDeploymentDiagramRenderer,
}


class PlantUMLRenderer(BaseRenderer[Diagram]):
    """
    Renderer for converting a Diagram object into PlantUML syntax.
    """

    renderer_type: RendererEnum = RendererEnum.PLANTUML

    def __init__(
        self,
        includes: list[str] | None = None,
        render_options: PlantUMLRenderOptions | None = None,
        backend: BasePlantUMLBackend | None = None,
        use_new_c4_style: bool = False,
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ):
        """
        Initialize the renderer.

        Args:
            includes: A list of PlantUML `!include` directives
                to be injected at the beginning of the diagram.
            render_options: Render options that controls
                diagram rendering behavior, such as direction,
                spacing, and group alignment.
            backend:
                Optional PlantUML backend responsible for converting
                generated PlantUML source into image bytes (e.g. PNG, SVG).
                If not provided, image rendering is not available.

            use_new_c4_style:
                If ``True``, activates the new C4-PlantUML style by injecting
                the following directive into the generated source:
                    `!NEW_C4_STYLE=1`
            extension_validation_mode:
                Policy for foreign backend extensions.

            *args: Additional positional arguments passed to the base renderer.
            **kwargs: Additional keyword arguments passed to the base renderer.
        """
        super().__init__(
            extension_validation_mode=extension_validation_mode,
        )
        self._includes = includes or []
        self._render_options = render_options
        self._plantuml_backend = backend
        self._use_new_c4_style = use_new_c4_style

    def get_renderer(self, diagram: Diagram) -> BasePlantUMLRenderer[Diagram]:
        diagram_type = type(diagram)

        renderer_class = DIAGRAM_TYPE_TO_RENDERER_MAP.get(diagram_type)
        if not renderer_class:
            raise NotImplementedError(
                f"Unsupported PlantUML diagram type: {diagram_type}"
            )

        render_options = self._render_options
        if diagram.render_options and diagram.render_options.plantuml:
            render_options = diagram.render_options.plantuml

        return renderer_class(
            includes=self._includes,
            render_options=render_options,
            backend=self._plantuml_backend,
            use_new_c4_style=self._use_new_c4_style,
            extension_validation_mode=self._extension_validation_mode,
        )

    @override
    def render(self, diagram: Diagram) -> str:
        """
        Render the given Diagram into PlantUML format.

        Args:
            diagram: The diagram to render.

        Returns:
            A PlantUML-formatted string representing the diagram.
        """
        renderer = self.get_renderer(diagram)
        return renderer.render(diagram)

    def render_bytes(
        self,
        diagram: Diagram,
        *,
        format: DiagramFormat,
    ) -> bytes:
        """
        Render a Diagram and return the result as raw bytes.

        This method first converts the Diagram into PlantUML source text
        and then delegates the actual rendering to the
        configured PlantUML backend.

        Args:
            diagram: The diagram instance to render.
            format: Output format of the rendered diagram.

        Returns:
            The rendered diagram content as raw bytes.

        Raises:
            PlantUMLBackendConfigurationError: If no PlantUML backend is
                configured for this renderer.
            PlantUMLError: If the underlying PlantUML backend fails to
                render the diagram.
        """
        renderer = self.get_renderer(diagram)
        return renderer.render_bytes(
            diagram,
            format=format,
        )

    def render_file(
        self,
        diagram: Diagram,
        output_path: str | Path,
        *,
        format: DiagramFormat,
        overwrite: bool = True,
    ) -> Path:
        """
        Render a Diagram and write the result to a file.

        This method first converts the Diagram into PlantUML source text
        and then delegates file generation to the
        configured PlantUML backend.

        Args:
            diagram: The diagram instance to render.
            output_path: Path where the rendered diagram should be written.
            format: Output format of the rendered diagram.
            overwrite: Whether to overwrite the output file if it already
                exists.

        Returns:
            Path to the written output file.

        Raises:
            PlantUMLBackendConfigurationError: If no PlantUML backend is
                configured for this renderer.
            FileExistsError: If the output file exists and ``overwrite`` is
                set to ``False``.
            PlantUMLError: If the underlying PlantUML backend fails to
                render or write the diagram.
        """
        renderer = self.get_renderer(diagram)
        return renderer.render_file(
            diagram,
            output_path=output_path,
            format=format,
            overwrite=overwrite,
        )


__all__ = ("PlantUMLRenderer",)

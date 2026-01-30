from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING,
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
from c4.diagrams.core import (
    BaseDiagramElement,
    Boundary,
    Diagram,
    Element,
    Layout,
    Relationship,
    _TDiagram,
    increment,
    set_index,
)
from c4.diagrams.dynamic import DynamicDiagram
from c4.exceptions import PlantUMLBackendConfigurationError
from c4.renderers.base import BaseRenderer, IndentedStringBuilder
from c4.renderers.plantuml.backends import BasePlantUMLBackend, DiagramFormat
from c4.renderers.plantuml.constants import (
    C4_COMPONENT_INCLUDE,
    C4_CONTAINER_INCLUDE,
    C4_CONTEXT_INCLUDE,
    C4_DEPLOYMENT_INCLUDE,
    C4_DYNAMIC_INCLUDE,
    RELATIVE_INCLUDE_COMMENT,
)
from c4.renderers.plantuml.layout_options import LayoutConfig
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
    ShowElementDescriptionsPlantUMLMacro,
    ShowFloatingLegendPlantUMLMacro,
    ShowFootBoxesPlantUMLMacro,
    ShowIndexPlantUMLMacro,
    ShowLegendPlantUMLMacro,
    ShowPersonOutlinePlantUMLMacro,
    ShowPersonSpritePlantUMLMacro,
    StylePlantUMLMacro,
    TagPlantUMLMacro,
    UpdateLegendTitlePlantUMLMacro,
    WithoutPropertyHeaderPlantUMLMacro,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.renderers.plantuml.layout_options import LayoutOptions


class LayoutOptionsRenderer:
    def __init__(
        self,
        includes: list[str],
        layout_config: LayoutConfig | None = None,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            includes: A list of PlantUML `!include` directives
                to be injected at the beginning of the diagram.
            layout_config: Layout configuration that controls
                diagram rendering behavior, such as direction,
                spacing, and group alignment.
        """
        self._includes = includes
        self._config = layout_config or LayoutConfig()

    def _render_tags(self) -> str:
        builder = IndentedStringBuilder()

        for tag in self._config.tags:
            macro = TagPlantUMLMacro.get_macro_by_tag(tag)  # type: ignore[var-annotated]
            builder.add(macro.render())

        return builder.get_result()

    def _render_styles(self) -> str:
        builder = IndentedStringBuilder()

        for style in self._config.styles:
            macro = StylePlantUMLMacro.get_macro_by_style(style)  # type: ignore[var-annotated]
            builder.add(macro.render())

        return builder.get_result()

    def _render_layout(self) -> str:  # noqa: C901
        builder = IndentedStringBuilder()
        macro: PlantUMLMacro[Any]

        if self._config.layout:
            macro = DiagramLayoutPlantUMLMacro(self._config.layout)
            builder.add(macro.render())

        if self._config.layout_with_legend:
            macro = LayoutWithLegendPlantUMLMacro()
            builder.add(macro.render())

        if self._config.layout_as_sketch:
            macro = LayoutAsSketchPlantUMLMacro()
            builder.add(macro.render())

        if self._config.hide_person_sprite:
            macro = HidePersonSpritePlantUMLMacro()
            builder.add(macro.render())

        if self._config.show_person_sprite:
            macro = ShowPersonSpritePlantUMLMacro(
                self._config.show_person_sprite
            )
            builder.add(macro.render())

        if self._config.show_person_outline:
            macro = ShowPersonOutlinePlantUMLMacro()
            builder.add(macro.render())

        if self._config.show_element_descriptions:
            macro = ShowElementDescriptionsPlantUMLMacro()
            builder.add(macro.render())

        if self._config.show_foot_boxes:
            macro = ShowFootBoxesPlantUMLMacro()
            builder.add(macro.render())

        if self._config.show_index:
            macro = ShowIndexPlantUMLMacro()
            builder.add(macro.render())

        if self._config.legend_title:
            macro = UpdateLegendTitlePlantUMLMacro(self._config.legend_title)
            builder.add(macro.render())

        if self._config.hide_stereotype:
            macro = HideStereotypePlantUMLMacro()
            builder.add(macro.render())

        if self._config.without_property_header:
            macro = WithoutPropertyHeaderPlantUMLMacro()
            builder.add(macro.render())

        return builder.get_result()

    def _render_sketch_style(self) -> str:
        builder = IndentedStringBuilder()

        if self._config.set_sketch_style:
            macro = SetSketchStylePlantUMLMacro(self._config.set_sketch_style)
            builder.add(macro.render())

        return builder.get_result()

    def render_header(self, diagram: _TDiagram) -> str:
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

        if self._config.show_legend:
            macro = ShowLegendPlantUMLMacro(self._config.show_legend)
            builder.add(macro.render(), blank_line_after=True)

        if self._config.show_floating_legend:
            macro = ShowFloatingLegendPlantUMLMacro(
                self._config.show_floating_legend
            )
            builder.add(macro.render(), blank_line_after=True)

        return builder.get_result()


class BasePlantUMLRenderer(BaseRenderer[_TDiagram], Generic[_TDiagram]):
    """A base renderer for converting a Diagram object into PlantUML syntax."""

    default_includes: ClassVar[list[str]]

    def __init__(
        self,
        includes: list[str] | None = None,
        layout_config: LayoutConfig | None = None,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            includes: A list of PlantUML `!include` directives
                to be injected at the beginning of the diagram.
            layout_config: Layout configuration that controls
                diagram rendering behavior, such as direction,
                spacing, and group alignment.
        """
        self._config = layout_config or LayoutConfig()

        self._layout_options_renderer = LayoutOptionsRenderer(
            includes=includes or getattr(self, "default_includes", []),
            layout_config=self._config,
        )
        self._without_property_header = self._config.without_property_header

        self._builder = IndentedStringBuilder()

    def render_base_element(self, element: BaseDiagramElement) -> list[str]:
        raise NotImplementedError

    def render_element(self, element: Element) -> list[str]:
        macro = ElementPlantUMLMacro.from_element(element)

        properties_macros = macro.render_properties(
            self._without_property_header
        )
        element_macro = macro.render()

        return [*properties_macros, element_macro]

    def render_boundary(self, boundary: Boundary, depth: int = 0) -> str:
        builder = IndentedStringBuilder(level=depth)

        *properties, element_macro = self.render_element(boundary)
        builder.add(*properties, element_macro + " {")

        with builder.indent() as level:
            for idx, nested_element in enumerate(boundary.elements, start=1):
                *properties, element_macro = self.render_element(nested_element)
                builder.add(
                    *properties,
                    element_macro,
                    blank_line_after=idx < len(boundary.elements),
                )

            if boundary.elements and boundary.boundaries:
                builder.add_blank_line()

            for idx, nested_boundary in enumerate(boundary.boundaries, start=1):
                builder.add(
                    self.render_boundary(nested_boundary, depth=level),
                    indent=False,
                    blank_line_after=idx < len(boundary.boundaries),
                )

            if boundary.relationships:
                builder.add_blank_line()

            for idx, relationship in enumerate(boundary.relationships, start=1):  # noqa: B007
                *properties, relationship_macro = self.render_relationship(
                    relationship
                )
                builder.add(
                    *properties,
                    relationship_macro,
                )

        builder.add("}")

        return builder.get_result()

    def render_relationship(self, relationship: Relationship) -> list[str]:
        macro = RelationshipPlantUMLMacro(relationship)

        properties_macros = macro.render_properties(
            self._without_property_header
        )
        relationship_macro = macro.render()
        return [*properties_macros, relationship_macro]

    def render_layout(self, layout: Layout) -> list[str]:
        macro = LayoutPlantUMLMacro(layout)

        properties_macros = macro.render_properties(
            self._without_property_header
        )
        layout_macro = macro.render()

        return [*properties_macros, layout_macro]

    def _render_header(self, diagram: _TDiagram) -> None:
        self._builder.add("@startuml")

        layout_header = self._layout_options_renderer.render_header(diagram)
        self._builder.add(layout_header, blank_line_after=True)

    def _render_footer(self) -> None:
        layout_footer = self._layout_options_renderer.render_footer()

        self._builder.add(layout_footer, blank_line_after=True)

        self._builder.add("@enduml")

    def _render_elements(self, diagram: _TDiagram) -> None:
        for element in diagram.elements:
            *properties, element_macro = self.render_element(element)
            self._builder.add(*properties, element_macro, blank_line_after=True)

    def _render_base_elements(self, diagram: _TDiagram) -> None:
        for idx, element in enumerate(diagram.base_elements, start=1):
            *properties, element_macro = self.render_base_element(element)
            self._builder.add(
                *properties,
                element_macro,
                blank_line_after=idx == len(diagram.base_elements),
            )

    def _render_boundaries(self, diagram: _TDiagram) -> None:
        for boundary in diagram.boundaries:
            self._builder.add(
                self.render_boundary(boundary), blank_line_after=True
            )

    def _render_relationships(self, diagram: _TDiagram) -> None:
        for idx, relationship in enumerate(diagram.relationships, start=1):
            *properties, relationship_macro = self.render_relationship(
                relationship
            )
            self._builder.add(
                *properties,
                relationship_macro,
                blank_line_after=idx == len(diagram.relationships),
            )

    def _render_layouts(self, diagram: _TDiagram) -> None:
        for idx, layout in enumerate(diagram.layouts, start=1):
            *properties, layout_macro = self.render_layout(layout)
            self._builder.add(
                *properties,
                layout_macro,
                blank_line_after=idx == len(diagram.layouts),
            )

    @override
    def render(self, diagram: _TDiagram) -> str:
        """
        Render the given Diagram into PlantUML format.

        Args:
            diagram: The diagram to render.

        Returns:
            A PlantUML-formatted string representing the diagram.
        """
        self._builder.reset()

        self._render_header(diagram)
        self._render_elements(diagram)
        self._render_boundaries(diagram)
        self._render_relationships(diagram)
        self._render_base_elements(diagram)
        self._render_layouts(diagram)
        self._render_footer()

        return self._builder.get_result()


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
    def render_base_element(
        self,
        element: BaseDiagramElement,
    ) -> list[str]:
        macro: PlantUMLMacro[Any]

        if isinstance(element, Relationship):
            macro = RelationshipPlantUMLMacro(element)
        elif isinstance(element, increment):
            macro = IncrementPlantUMLMacro(element)
        elif isinstance(element, set_index):
            macro = SetIndexPlantUMLMacro(element)
        else:
            raise TypeError(
                f"Unsupported element {element!r} for DynamicDiagram."
            )

        properties_macros = macro.render_properties(
            self._without_property_header
        )
        element_macro = macro.render()

        return [*properties_macros, element_macro]


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

    def __init__(
        self,
        includes: list[str] | None = None,
        layout_options: LayoutOptions | None = None,
        backend: BasePlantUMLBackend | None = None,
        *args: Any,
        **kwargs: Any,
    ):
        """
        Initialize the renderer.

        Args:
            includes: A list of PlantUML `!include` directives
                to be injected at the beginning of the diagram.
            layout_options: Layout configuration that controls
                diagram rendering behavior, such as direction,
                spacing, and group alignment.
            *args: Additional positional arguments passed to the base renderer.
            **kwargs: Additional keyword arguments passed to the base renderer.
        """
        super().__init__(*args, **kwargs)
        self._includes = includes or []
        self._layout_config = None
        self._plantuml_backend = backend

        if layout_options:
            self._layout_config = layout_options.build()

    @override
    def render(self, diagram: Diagram) -> str:
        """
        Render the given Diagram into PlantUML format.

        Args:
            diagram: The diagram to render.

        Returns:
            A PlantUML-formatted string representing the diagram.
        """
        diagram_type = type(diagram)

        renderer_class = DIAGRAM_TYPE_TO_RENDERER_MAP.get(diagram_type)
        if not renderer_class:
            raise NotImplementedError(
                f"Unsupported PlantUML diagram type: {diagram_type}"
            )

        renderer = renderer_class(
            includes=self._includes,
            layout_config=self._layout_config,
        )
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
        if not self._plantuml_backend:
            raise PlantUMLBackendConfigurationError()

        diagram_source = self.render(diagram)

        return self._plantuml_backend.to_bytes(
            diagram=diagram_source,
            format=format,
        )

    def render_file(
        self,
        diagram: Diagram,
        output_path: Path,
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


__all__ = (
    "LayoutOptions",
    "PlantUMLRenderer",
)

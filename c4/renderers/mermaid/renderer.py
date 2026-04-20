from __future__ import annotations

from pathlib import Path
from typing import Any, Generic

from typing_extensions import override

from c4 import (
    ComponentDiagram,
    ContainerDiagram,
    DeploymentDiagram,
    DiagramFormat,
    DynamicDiagram,
    SystemContextDiagram,
    SystemLandscapeDiagram,
)
from c4.diagrams.core import (
    Boundary,
    Diagram,
    Element,
    Layout,
    Relationship,
    _TDiagram,
    increment,
    set_index,
)
from c4.exceptions import MermaidBackendConfigurationError
from c4.renderers.base import BaseRenderer, IndentedStringBuilder
from c4.renderers.macros import BaseMacro
from c4.renderers.mermaid.backends import BaseMermaidBackend
from c4.renderers.mermaid.macros import (
    ElementMermaidMacro,
    RelationshipMermaidMacro,
    UpdateElementStyleMermaidMacro,
    UpdateLayoutConfigMermaidMacro,
    UpdateRelStyleMermaidMacro,
)
from c4.renderers.mermaid.options import (
    ElementStyle,
    MermaidRenderOptions,
    RelStyle,
)

DIAGRAM_TYPE_TO_MERMAID_DEFINITION_MAP: dict[type[Diagram], str] = {
    SystemContextDiagram: "C4Context",
    SystemLandscapeDiagram: "C4Context",
    ContainerDiagram: "C4Container",
    ComponentDiagram: "C4Component",
    DynamicDiagram: "C4Dynamic",
    DeploymentDiagram: "C4Deployment",
}


class MermaidRenderOptionsRenderer:
    def __init__(
        self,
        render_options: MermaidRenderOptions | None = None,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            render_options: Render options that controls
                diagram rendering behavior, such as direction,
                spacing, and group alignment.
        """
        self._render_options = render_options or MermaidRenderOptions()

    def render_footer(self) -> str:
        builder = IndentedStringBuilder()
        macro: BaseMacro[Any]

        for style in self._render_options.styles:
            if isinstance(style, RelStyle):
                macro = UpdateRelStyleMermaidMacro(style)
            elif isinstance(style, ElementStyle):
                macro = UpdateElementStyleMermaidMacro(style)
            else:
                raise TypeError(
                    f"No macro registered for style type {type(style).__name__}"
                ) from None

            builder.add(macro.render())

        if self._render_options.update_layout_config:
            macro = UpdateLayoutConfigMermaidMacro(
                self._render_options.update_layout_config
            )
            builder.add(macro.render(), blank_line_after=True)

        return builder.get_result()


class MermaidRenderer(BaseRenderer[_TDiagram], Generic[_TDiagram]):
    """A renderer for converting a Diagram object into Mermaid syntax."""

    def __init__(
        self,
        render_options: MermaidRenderOptions | None = None,
        backend: BaseMermaidBackend | None = None,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            render_options: Render options that controls
                diagram rendering behavior, such as direction,
                spacing, and group alignment.
        """
        self._render_options = render_options or MermaidRenderOptions()

        self._builder = IndentedStringBuilder()
        self._mermaid_backend = backend

    def _render_base_elements(self, diagram: _TDiagram) -> None:
        for idx, element in enumerate(diagram.base_elements, start=1):
            if isinstance(element, Relationship):
                macro = RelationshipMermaidMacro(element)
            elif isinstance(element, (increment, set_index)):
                # Not supported: https://mermaid.js.org/syntax/c4.html
                continue
            else:  # pragma: no cover
                raise TypeError(f"Unsupported element {element!r}.")

            self._builder.add(
                macro.render(),
                blank_line_after=idx == len(diagram.base_elements),
            )

    def _render_header(self, diagram: _TDiagram) -> None:
        diagram_type = type(diagram)

        diagram_def = DIAGRAM_TYPE_TO_MERMAID_DEFINITION_MAP[diagram_type]

        self._builder.add(diagram_def)

        if diagram.title:
            self._builder.add(f"title {diagram.title}")

        self._builder.add_blank_line()

    def _render_element(self, element: Element) -> str:
        macro = ElementMermaidMacro.from_element(element)

        return macro.render()

    def _render_boundary(self, boundary: Boundary, depth: int = 0) -> str:
        builder = IndentedStringBuilder(level=depth)

        element_macro = self._render_element(boundary)
        builder.add(element_macro + " {")

        with builder.indent() as level:
            for element in boundary.ordered_elements:
                if isinstance(element, Boundary):
                    builder.add(
                        self._render_boundary(element, depth=level),
                        indent=False,
                    )
                elif isinstance(element, Element):
                    builder.add(self._render_element(element))
                elif isinstance(element, Relationship):
                    builder.add(self._render_relationship(element))
                else:  # pragma: no cover
                    raise TypeError(f"Unsupported element {element!r}")

                self._builder.add_blank_line()

        builder.add("}")

        return builder.get_result()

    def _render_relationship(self, relationship: Relationship) -> str:
        macro = RelationshipMermaidMacro(relationship)

        return macro.render()

    def _render_elements(self, diagram: _TDiagram) -> None:
        for element in diagram.ordered_elements:
            if element in diagram.base_elements:
                # base elements are rendered separately
                continue

            if isinstance(element, Boundary):
                self._builder.add(self._render_boundary(element))
            elif isinstance(element, Element):
                self._builder.add(self._render_element(element))
            elif isinstance(element, Relationship):
                self._builder.add(self._render_relationship(element))
            elif isinstance(element, Layout):
                # Layouts are not supported: https://mermaid.js.org/syntax/c4.html
                continue
            else:  # pragma: no cover
                raise TypeError(f"Unsupported element {element!r}")

            self._builder.add_blank_line()

    def _render_footer(self, render_options: MermaidRenderOptions) -> None:
        render_options_renderer = MermaidRenderOptionsRenderer(
            render_options=render_options,
        )

        footer = render_options_renderer.render_footer()

        self._builder.add(footer, blank_line_after=True)

    @override
    def render(self, diagram: _TDiagram) -> str:
        """
        Render the given Diagram into Mermaid format.

        Args:
            diagram: The diagram to render.

        Returns:
            A Mermaid-formatted string representing the diagram.
        """
        render_options = self._render_options
        if diagram.render_options and diagram.render_options.mermaid:
            render_options = diagram.render_options.mermaid

        self._builder.reset()

        self._render_header(diagram)
        self._render_elements(diagram)
        self._render_base_elements(diagram)
        self._render_footer(render_options)

        return self._builder.get_result()

    def render_bytes(
        self,
        diagram: _TDiagram,
        *,
        format: DiagramFormat,
    ) -> bytes:
        """
        Render a Diagram and return the result as raw bytes.

        This method first converts the Diagram into Mermaid source text
        and then delegates the actual rendering to the
        configured Mermaid backend.

        Args:
            diagram: The diagram instance to render.
            format: Output format of the rendered diagram.

        Returns:
            The rendered diagram content as raw bytes.

        Raises:
            MermaidBackendConfigurationError: If no Mermaid backend is
                configured for this renderer.
            MermaidError: If the underlying Mermaid backend fails to
                render the diagram.
        """
        if not self._mermaid_backend:
            raise MermaidBackendConfigurationError()

        diagram_source = self.render(diagram)

        return self._mermaid_backend.to_bytes(
            diagram=diagram_source,
            format=format,
        )

    def render_file(
        self,
        diagram: _TDiagram,
        output_path: str | Path,
        *,
        format: DiagramFormat,
        overwrite: bool = True,
    ) -> Path:
        """
        Render a Diagram and write the result to a file.

        This method first converts the Diagram into Mermaid source text
        and then delegates file generation to the
        configured Mermaid backend.

        Args:
            diagram: The diagram instance to render.
            output_path: Path where the rendered diagram should be written.
            format: Output format of the rendered diagram.
            overwrite: Whether to overwrite the output file if it already
                exists.

        Returns:
            Path to the written output file.

        Raises:
            MermaidBackendConfigurationError: If no Mermaid backend is
                configured for this renderer.
            FileExistsError: If the output file exists and ``overwrite`` is
                set to ``False``.
            MermaidError: If the underlying Mermaid backend fails to
                render or write the diagram.
        """
        if not self._mermaid_backend:
            raise MermaidBackendConfigurationError()

        diagram_source = self.render(diagram)

        return self._mermaid_backend.to_file(
            diagram=diagram_source,
            output_path=output_path,
            format=format,
            overwrite=overwrite,
        )

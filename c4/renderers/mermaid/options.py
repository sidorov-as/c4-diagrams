from __future__ import annotations

from dataclasses import dataclass, field
from typing import cast

from typing_extensions import Self

from c4.diagrams.core import Element


@dataclass
class BaseStyle:
    """
    Base class for Mermaid style update macros.

    Represents a style directive that modifies the visual appearance
    of diagram elements or relationships.
    """


@dataclass
class ElementStyle(BaseStyle):
    """
    Defines style overrides for a specific diagram element.

    Attributes:
        element: Alias of the element to style.
        bg_color: Background color of the element.
        font_color: Text color of the element label.
        border_color: Border color of the element.
    """

    element: str
    bg_color: str | None = None
    font_color: str | None = None
    border_color: str | None = None


@dataclass
class RelStyle(BaseStyle):
    """
    Defines style overrides for a relationship (edge).

    Attributes:
        from_element: Alias of the source element.
        to_element: Alias of the target element.
        text_color: Color of the relationship label text.
        line_color: Color of the connecting line.
        offset_x: Optional horizontal offset for the label position.
        offset_y: Optional vertical offset for the label position.
    """

    from_element: str
    to_element: str
    text_color: str | None = None
    line_color: str | None = None
    offset_x: int | None = None
    offset_y: int | None = None


@dataclass
class UpdateLayoutConfig:
    """
    Configuration for updating default layout behavior in Mermaid C4 diagrams.

    Mirrors the Mermaid `UpdateLayoutConfig` directive.

    Attributes:
        c4_shape_in_row: Maximum number of non-boundary elements
            (e.g. systems, containers, components) per row.
            Default in Mermaid: 4.
        c4_boundary_in_row: Maximum number of boundaries per row.
            Default in Mermaid: 2.
    """

    c4_shape_in_row: int | None = None
    c4_boundary_in_row: int | None = None


@dataclass
class MermaidRenderOptions:
    """
    Final render options for rendering a Mermaid C4 diagram.

    This includes style overrides and layout configuration that will be
    translated into Mermaid directives/macros during rendering.

    Attributes:
        styles: Collection of style overrides applied to elements
            and relationships.
        update_layout_config: Optional layout configuration override.
            If not provided, Mermaid defaults are used.
    """

    styles: list[BaseStyle] = field(default_factory=list)
    update_layout_config: UpdateLayoutConfig | None = None


class MermaidRenderOptionsBuilder:
    """
    Builder for constructing MermaidRenderOptions.

    Provides a fluent API for incrementally defining styles and layout
    configuration.
    """

    def __init__(self) -> None:
        """Initialize an empty render options."""
        self._styles: list[BaseStyle] = []
        self._layout_config: UpdateLayoutConfig | None = None

    def update_element_style(
        self,
        element: str | Element,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
    ) -> Self:
        """
        Adds an UpdateElementStyle() macro configuration.

        Args:
            element: Element or alias of the element to style.
            bg_color: Background color of the element.
            font_color: Text color of the element label.
            border_color: Border color of the element.

        Returns:
            The updated render options.
        """
        element_name = element
        if isinstance(element, Element):
            element_name = element.alias

        self._styles.append(
            ElementStyle(
                element=cast(str, element_name),
                bg_color=bg_color,
                font_color=font_color,
                border_color=border_color,
            )
        )
        return self

    def update_rel_style(
        self,
        from_element: str | Element,
        to_element: str | Element,
        text_color: str | None = None,
        line_color: str | None = None,
        offset_x: int | None = None,
        offset_y: int | None = None,
    ) -> Self:
        """
        Adds an UpdateRelStyle() macro configuration.

        Args:
            from_element: Element or alias of the source element.
            to_element: Element or alias of the target element.
            text_color: Color of the relationship label text.
            line_color: Color of the connecting line.
            offset_x: Optional horizontal offset for the label position.
            offset_y: Optional vertical offset for the label position.

        Returns:
            The updated render options.
        """
        from_element_name = from_element
        if isinstance(from_element, Element):
            from_element_name = from_element.alias

        to_element_name = to_element
        if isinstance(to_element, Element):
            to_element_name = to_element.alias

        self._styles.append(
            RelStyle(
                from_element=cast(str, from_element_name),
                to_element=cast(str, to_element_name),
                text_color=text_color,
                line_color=line_color,
                offset_x=offset_x,
                offset_y=offset_y,
            )
        )
        return self

    def update_layout_config(
        self,
        c4_shape_in_row: int | None = None,
        c4_boundary_in_row: int | None = None,
    ) -> Self:
        """
        Override default Mermaid layout configuration.

        Args:
            c4_shape_in_row: Maximum number of non-boundary elements
                (e.g. systems, containers, components) per row.
                Default in Mermaid: 4.
            c4_boundary_in_row: Maximum number of boundaries per row.
                Default in Mermaid: 2.

        Returns:
            The updated render options.
        """
        self._layout_config = UpdateLayoutConfig(
            c4_shape_in_row=c4_shape_in_row,
            c4_boundary_in_row=c4_boundary_in_row,
        )
        return self

    def build(self) -> MermaidRenderOptions:
        """
        Build and return the final MermaidRenderOptions instance.
        """
        return MermaidRenderOptions(
            styles=self._styles,
            update_layout_config=self._layout_config,
        )

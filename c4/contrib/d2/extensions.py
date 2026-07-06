from __future__ import annotations

from typing import Literal, TypedDict

D2Direction = Literal["up", "down", "left", "right"]
D2StyleValue = str | int | float | bool | None


class StyleExtensions(TypedDict, total=False):
    """
    D2 style attributes.

    D2 style keys are hyphenated and map directly to `style.<key>` fields.
    See https://d2lang.com/tour/style/ for the upstream D2 style reference.

    Args:
        opacity: Rendered as `style.opacity`.
        stroke: Rendered as `style.stroke`.
        fill: Rendered as `style.fill`.
        fill_pattern: Rendered as `style.fill-pattern`.
        stroke_width: Rendered as `style.stroke-width`.
        stroke_dash: Rendered as `style.stroke-dash`.
        border_radius: Rendered as `style.border-radius`.
        shadow: Rendered as `style.shadow`.
        three_d: Rendered as `style.3d`.
        multiple: Rendered as `style.multiple`.
        double_border: Rendered as `style.double-border`.
        font: Rendered as `style.font`.
        font_size: Rendered as `style.font-size`.
        font_color: Rendered as `style.font-color`.
        animated: Rendered as `style.animated`.
        bold: Rendered as `style.bold`.
        italic: Rendered as `style.italic`.
        underline: Rendered as `style.underline`.
        text_transform: Rendered as `style.text-transform`.
    """

    opacity: float | None
    stroke: str | None
    fill: str | None
    fill_pattern: str | None
    stroke_width: int | None
    stroke_dash: int | None
    border_radius: int | None
    shadow: bool | None
    three_d: bool | None
    multiple: bool | None
    double_border: bool | None
    font: str | None
    font_size: int | None
    font_color: str | None
    animated: bool | None
    bold: bool | None
    italic: bool | None
    underline: bool | None
    text_transform: str | None


class ElementExtensions(TypedDict, total=False):
    """
    D2-specific extension data for nodes and containers.

    See https://d2lang.com/tour/shapes/ for shapes,
    https://d2lang.com/tour/style/ for style attributes, and
    https://d2lang.com/tour/classes/ for classes.

    Args:
        shape: Rendered as `shape`.
        style: Rendered as nested `style.*` attributes.
        icon: Rendered as `icon`.
        near: Rendered as `near`.
        tooltip: Rendered as `tooltip`.
        link: Rendered as `link`.
        classes: Rendered as `class`.
        direction: Rendered as `direction`.
    """

    shape: str | None
    style: StyleExtensions | dict[str, D2StyleValue] | None
    icon: str | None
    near: str | None
    tooltip: str | None
    link: str | None
    classes: list[str] | None
    direction: D2Direction | None


class BoundaryExtensions(ElementExtensions, total=False):
    """
    D2-specific extension data for boundary containers.

    Inherits all node/container extension fields from `ElementExtensions`.
    Container-local `direction` is rendered as D2 `direction`.
    See https://d2lang.com/tour/containers/ and
    https://d2lang.com/tour/layouts/ for related D2 behavior.
    """


class RelationshipExtensions(TypedDict, total=False):
    """
    D2-specific extension data for relationship edges.

    See https://d2lang.com/tour/connections/ for D2 connections,
    https://d2lang.com/tour/style/ for style attributes, and
    https://d2lang.com/tour/classes/ for classes.

    Args:
        style: Rendered as nested `style.*` attributes.
        icon: Rendered as `icon`.
        near: Rendered as `near`.
        tooltip: Rendered as `tooltip`.
        link: Rendered as `link`.
        classes: Rendered as `class`.
    """

    style: StyleExtensions | dict[str, D2StyleValue] | None
    icon: str | None
    near: str | None
    tooltip: str | None
    link: str | None
    classes: list[str] | None

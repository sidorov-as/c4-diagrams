from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from c4.contrib.likec4._identifiers import check_identifier

StyleValue = str | int | bool

ELEMENT_SHAPES = frozenset({
    "rectangle",
    "person",
    "browser",
    "mobile",
    "cylinder",
    "storage",
    "queue",
    "component",
    "bucket",
    "document",
})
BORDERS = frozenset({"solid", "dashed", "dotted", "none"})
SIZES = frozenset({"xs", "sm", "md", "lg", "xl"})
ICON_POSITIONS = frozenset({"left", "right", "top", "bottom"})
LINE_TYPES = frozenset({"solid", "dashed", "dotted"})
ARROW_TYPES = frozenset({
    "none",
    "normal",
    "onormal",
    "dot",
    "odot",
    "diamond",
    "odiamond",
    "crow",
    "open",
    "vee",
})
THEME_COLORS = frozenset({
    "amber",
    "blue",
    "gray",
    "green",
    "indigo",
    "muted",
    "primary",
    "red",
    "secondary",
    "sky",
    "slate",
})

_CHOICES: dict[str, frozenset[str]] = {
    "shape": ELEMENT_SHAPES,
    "border": BORDERS,
    "size": SIZES,
    "textSize": SIZES,
    "padding": SIZES,
    "iconSize": SIZES,
    "iconPosition": ICON_POSITIONS,
    "line": LINE_TYPES,
    "head": ARROW_TYPES,
    "tail": ARROW_TYPES,
}

_ELEMENT_KEYS = (
    "color",
    "shape",
    "icon",
    "iconColor",
    "iconSize",
    "iconPosition",
    "opacity",
    "border",
    "size",
    "textSize",
    "padding",
    "multiple",
)
_RELATIONSHIP_KEYS = ("color", "line", "head", "tail")

_SNAKE_TO_CAMEL = {
    "icon_color": "iconColor",
    "icon_size": "iconSize",
    "icon_position": "iconPosition",
    "text_size": "textSize",
}


def _opacity(value: Any) -> int:
    if isinstance(value, bool):
        raise TypeError("opacity must be an integer percentage, not a bool")

    if isinstance(value, str) and value.endswith("%"):
        value = value[:-1]

    try:
        percent = int(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"opacity must be an integer percentage; got {value!r}."
        ) from None

    if not 0 <= percent <= 100:
        raise ValueError(f"opacity must be between 0 and 100; got {value!r}.")

    return percent


def _normalize(
    properties: Mapping[str, Any], allowed: tuple[str, ...], what: str
) -> dict[str, StyleValue]:
    result: dict[str, StyleValue] = {}
    for raw_key, value in properties.items():
        key = _SNAKE_TO_CAMEL.get(raw_key, raw_key)
        if key not in allowed:
            raise ValueError(
                f"Unknown {what} style property {raw_key!r}; expected one of "
                f"{', '.join(allowed)}."
            )

        if key == "opacity":
            result[key] = _opacity(value)
        elif key == "multiple":
            if not isinstance(value, bool):
                raise TypeError("multiple must be a bool")
            result[key] = value
        elif key == "icon":
            if not isinstance(value, str) or not value:
                raise TypeError("icon must be a non-empty string")
            result[key] = value
        elif key in {"color", "iconColor"}:
            result[key] = check_identifier(value, f"{what} {key}")
        else:
            choices = _CHOICES[key]
            if value not in choices:
                raise ValueError(
                    f"Invalid {what} {key} {value!r}; expected one of "
                    f"{', '.join(sorted(choices))}."
                )
            result[key] = value

    # Stable declaration order regardless of keyword order.
    return {key: result[key] for key in allowed if key in result}


def parse_element_style(**properties: Any) -> dict[str, StyleValue]:
    """Validate element/deployment style properties; keys use camelCase."""
    return _normalize(properties, _ELEMENT_KEYS, "element")


def parse_relationship_style(**properties: Any) -> dict[str, StyleValue]:
    """Validate relationship style properties."""
    return _normalize(properties, _RELATIONSHIP_KEYS, "relationship")

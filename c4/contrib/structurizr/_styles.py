from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, cast

StructurizrStylePreset = Literal["classic", "new-c4-style"]

STYLE_PRESETS = ("classic", "new-c4-style")
STYLE_PRESET_CLI_VALUES = (*STYLE_PRESETS, "none")

_SHAPE = "shape"
_BACKGROUND = "background"
_COLOR = "color"
_STROKE = "stroke"
_STROKE_WIDTH = "strokeWidth"
_BORDER = "border"
_THICKNESS = "thickness"

_PERSON = "Person"
_WHITE = "#ffffff"

STYLE_PROPERTY_NAMES = {
    _SHAPE: _SHAPE,
    "width": "width",
    "height": "height",
    _BACKGROUND: _BACKGROUND,
    _COLOR: _COLOR,
    _STROKE: _STROKE,
    "stroke_width": _STROKE_WIDTH,
    _BORDER: _BORDER,
    "opacity": "opacity",
    "font_size": "fontSize",
    "metadata": "metadata",
    "description": "description",
    _THICKNESS: _THICKNESS,
    "routing": "routing",
    "position": "position",
}
STYLE_PROPERTY_ORDER = tuple(STYLE_PROPERTY_NAMES.values())

_POSITIVE_INT_FIELDS = {
    "width",
    "height",
    "stroke_width",
    "font_size",
    "thickness",
}
_NON_NEGATIVE_INT_FIELDS = {"opacity", "position"}

ELEMENT_SHAPES = {
    "box": "Box",
    "roundedbox": "RoundedBox",
    "circle": "Circle",
    "ellipse": "Ellipse",
    "hexagon": "Hexagon",
    "cylinder": "Cylinder",
    "pipe": "Pipe",
    "person": _PERSON,
    "robot": "Robot",
    "folder": "Folder",
    "webbrowser": "WebBrowser",
    "mobiledevicelandscape": "MobileDeviceLandscape",
    "mobiledeviceportrait": "MobileDevicePortrait",
}
BORDERS = {
    "solid": "Solid",
    "dashed": "Dashed",
    "dotted": "Dotted",
}


@dataclass(frozen=True)
class StructurizrStyleModel:
    """Private Structurizr style model.

    Attributes:
        tag: Element or relationship tag the style targets.
        properties: Normalized Structurizr style properties.
    """

    tag: str
    properties: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class StructurizrStylesModel:
    """Private Structurizr style configuration model.

    Attributes:
        elements: Element style declarations.
        relationships: Relationship style declarations.
    """

    elements: tuple[StructurizrStyleModel, ...] = ()
    relationships: tuple[StructurizrStyleModel, ...] = ()

    @property
    def is_empty(self) -> bool:
        return not self.elements and not self.relationships


CLASSIC_ELEMENT_STYLES = (
    StructurizrStyleModel(
        _PERSON,
        {
            _SHAPE: _PERSON,
            _BACKGROUND: "#08427b",
            _COLOR: _WHITE,
            "fontSize": 22,
        },
    ),
    StructurizrStyleModel(
        "Software System",
        {_BACKGROUND: "#1168bd", _COLOR: _WHITE},
    ),
    StructurizrStyleModel(
        "Container",
        {_BACKGROUND: "#438dd5", _COLOR: _WHITE},
    ),
    StructurizrStyleModel(
        "Component",
        {_BACKGROUND: "#85bbf0", _COLOR: "#000000"},
    ),
    StructurizrStyleModel("Database", {_SHAPE: "Cylinder"}),
    StructurizrStyleModel("Queue", {_SHAPE: "Pipe"}),
    StructurizrStyleModel(
        "External",
        {_BACKGROUND: "#999999", _COLOR: _WHITE},
    ),
    StructurizrStyleModel(
        "Boundary",
        {_STROKE: "#444444", _STROKE_WIDTH: 1, _BORDER: "Dashed"},
    ),
)

NEW_C4_STYLE_ELEMENT_STYLES = (
    StructurizrStyleModel(
        "Element",
        {
            _COLOR: "#0773af",
            _STROKE: "#0773af",
            _STROKE_WIDTH: 7,
            _SHAPE: "RoundedBox",
        },
    ),
    StructurizrStyleModel(_PERSON, {_SHAPE: _PERSON}),
    StructurizrStyleModel("Database", {_SHAPE: "Cylinder"}),
    StructurizrStyleModel("Queue", {_SHAPE: "Pipe"}),
    StructurizrStyleModel("Boundary", {_STROKE_WIDTH: 5}),
)
NEW_C4_STYLE_RELATIONSHIP_STYLES = (
    StructurizrStyleModel("Relationship", {_THICKNESS: 4}),
)

STYLE_PRESET_MODELS = {
    "classic": StructurizrStylesModel(elements=CLASSIC_ELEMENT_STYLES),
    "new-c4-style": StructurizrStylesModel(
        elements=NEW_C4_STYLE_ELEMENT_STYLES,
        relationships=NEW_C4_STYLE_RELATIONSHIP_STYLES,
    ),
}


def allowed_style_preset_values() -> str:
    """Return human-readable allowed style preset values."""
    return ", ".join(repr(value) for value in (*STYLE_PRESETS, None))


def validate_style_preset(
    style_preset: str | None,
) -> StructurizrStylePreset | None:
    """Validate a Structurizr style preset option."""
    if style_preset is None:
        return None

    if style_preset not in STYLE_PRESETS:
        raise ValueError(
            "Structurizr style_preset must be one of "
            f"{allowed_style_preset_values()}. Got {style_preset!r}."
        )

    return style_preset  # type: ignore[return-value]


def parse_style_metadata(value: Any) -> Mapping[str, Any]:
    """Validate and normalize element-level Structurizr style metadata."""
    from c4.contrib.structurizr.renderer.errors import StructurizrRenderingError

    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise StructurizrRenderingError(
            "Structurizr extension field 'style' must be a mapping. "
            f"Got {value!r}."
        )

    result: dict[str, Any] = {}
    for key, raw_value in value.items():
        if key not in STYLE_PROPERTY_NAMES:
            allowed = ", ".join(repr(_field) for _field in STYLE_PROPERTY_NAMES)
            raise StructurizrRenderingError(
                f"Unknown Structurizr style field {key!r}. Allowed: {allowed}."
            )

        result[STYLE_PROPERTY_NAMES[key]] = _normalize_style_value(
            key,
            raw_value,
        )

    return result


def _normalize_style_value(key: str, value: Any) -> Any:
    from c4.contrib.structurizr.renderer.errors import StructurizrRenderingError

    if key in _POSITIVE_INT_FIELDS:
        return _positive_int(key, value)
    if key in _NON_NEGATIVE_INT_FIELDS:
        return _non_negative_int(key, value)
    if key in {"metadata", "description"}:
        if not isinstance(value, bool):
            raise StructurizrRenderingError(
                f"Structurizr style field {key!r} must be a boolean. "
                f"Got {value!r}."
            )
        return value
    if key == "shape":
        return _enum_value(key, value, ELEMENT_SHAPES)
    if key == "border":
        return _enum_value(key, value, BORDERS)
    if isinstance(value, (bool, int, str)):
        return value

    raise StructurizrRenderingError(
        f"Structurizr style field {key!r} must be a string, integer, "
        f"or boolean. Got {value!r}."
    )


def _positive_int(key: str, value: Any) -> int:
    from c4.contrib.structurizr.renderer.errors import StructurizrRenderingError

    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise StructurizrRenderingError(
            f"Structurizr style field {key!r} must be a positive integer. "
            f"Got {value!r}."
        )

    return cast(int, value)


def _non_negative_int(key: str, value: Any) -> int:
    from c4.contrib.structurizr.renderer.errors import StructurizrRenderingError

    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise StructurizrRenderingError(
            f"Structurizr style field {key!r} must be a non-negative integer. "
            f"Got {value!r}."
        )

    return cast(int, value)


def _enum_value(
    key: str,
    value: Any,
    allowed_values: Mapping[str, str],
) -> str:
    from c4.contrib.structurizr.renderer.errors import StructurizrRenderingError

    if not isinstance(value, str):
        raise StructurizrRenderingError(
            f"Structurizr style field {key!r} must be a string enum name. "
            f"Got {value!r}."
        )

    normalized = allowed_values.get(value.replace("_", "").lower())
    if normalized is None:
        allowed = ", ".join(sorted(set(allowed_values.values())))
        raise StructurizrRenderingError(
            f"Structurizr style field {key!r} must be one of {allowed}. "
            f"Got {value!r}."
        )

    return normalized

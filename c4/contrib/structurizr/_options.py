from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from c4.contrib.structurizr._styles import (
    StructurizrStylePreset,
    validate_style_preset,
)

StructurizrRankDirection = Literal[
    "TopBottom",
    "BottomTop",
    "LeftRight",
    "RightLeft",
]

RANK_DIRECTIONS = (
    "TopBottom",
    "BottomTop",
    "LeftRight",
    "RightLeft",
)


def _validate_optional_positive_int(name: str, value: int | None) -> None:
    if value is None:
        return

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(
            f"Structurizr {name} must be None or a positive integer. "
            f"Got {value!r}."
        )

    if value <= 0:
        raise ValueError(
            f"Structurizr {name} must be None or a positive integer. "
            f"Got {value!r}."
        )


@dataclass(frozen=True)
class AutoLayout:
    """
    Structurizr automatic layout settings.

    Defaults to left-to-right ranking. ``implementation``, ``rank_separation``
    and ``node_separation`` are optional and omitted from the DSL when unset.

    Attributes:
        rank_direction: Direction in which the layout ranks elements.
        implementation: Optional Structurizr layout implementation name.
        rank_separation: Optional positive gap between ranks.
        node_separation: Optional positive gap between nodes.
    """

    rank_direction: StructurizrRankDirection = "LeftRight"
    implementation: str | None = None
    rank_separation: int | None = None
    node_separation: int | None = None

    def __post_init__(self) -> None:
        if self.rank_direction not in RANK_DIRECTIONS:
            directions = ", ".join(
                repr(direction) for direction in RANK_DIRECTIONS
            )
            raise ValueError(
                "Structurizr rank direction must be one of "
                f"{directions}. Got {self.rank_direction!r}."
            )

        _validate_optional_positive_int(
            "rank_separation",
            self.rank_separation,
        )
        _validate_optional_positive_int(
            "node_separation",
            self.node_separation,
        )


@dataclass(frozen=True)
class StructurizrRenderOptions:
    """
    Render options for the Structurizr renderer.

    Attributes:
        auto_layout: Automatic layout settings emitted in generated views.
            Set to `None` to omit the `autoLayout` directive.
        style_preset: Named style preset to emit, or `None` to omit generated
            preset styles while keeping semantic tags and explicit overrides.
    """

    auto_layout: AutoLayout | None = AutoLayout()
    style_preset: StructurizrStylePreset | None = "classic"

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "style_preset",
            validate_style_preset(self.style_preset),
        )

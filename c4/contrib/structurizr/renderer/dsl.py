from __future__ import annotations

from collections.abc import Iterable

from c4.contrib.structurizr.renderer.formatting import (
    StructurizrStringBuilder,
    quote_structurizr_string,
)
from c4.contrib.structurizr.renderer.options import AutoLayout
from c4.contrib.structurizr.renderer.styles import STYLE_PROPERTY_ORDER


def auto_layout_directive(auto_layout: AutoLayout) -> str:
    """Return a Structurizr DSL `autoLayout` directive."""
    parts = ["autoLayout", _dsl_rank_direction(auto_layout.rank_direction)]

    if auto_layout.implementation is not None:
        parts.append(auto_layout.implementation)

    if auto_layout.rank_separation is not None:
        parts.append(str(auto_layout.rank_separation))

    if auto_layout.node_separation is not None:
        parts.append(str(auto_layout.node_separation))

    return " ".join(parts)


def properties_block(
    builder: StructurizrStringBuilder,
    properties: dict[str, str],
) -> None:
    """Add a Structurizr DSL properties block when values are present."""
    if not properties:
        return

    with builder.block("properties"):
        for key in sorted(properties):
            value = properties[key]
            builder.add(
                f"{quote_structurizr_string(key)} "
                f"{quote_structurizr_string(value)}"
            )


def tags_directive(tags: Iterable[str]) -> str | None:
    """Return a Structurizr DSL tags directive for non-empty tags."""
    tag_values = tuple(tags)
    if not tag_values:
        return None

    return f"tags {quote_structurizr_string(','.join(tag_values))}"


def style_value(value: object) -> str:
    """Return a Structurizr DSL style property value."""
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str) and (
        value.startswith("#") or value.replace("_", "").isidentifier()
    ):
        return value

    return quote_structurizr_string(str(value))


def ordered_style_properties(properties: dict[str, object]) -> Iterable[str]:
    """Yield Structurizr style property names in deterministic order."""
    emitted = set()
    for key in STYLE_PROPERTY_ORDER:
        if key in properties:
            emitted.add(key)
            yield key

    for key in sorted(set(properties) - emitted):
        yield key


def _dsl_rank_direction(rank_direction: str) -> str:
    return {
        "TopBottom": "tb",
        "BottomTop": "bt",
        "LeftRight": "lr",
        "RightLeft": "rl",
    }[rank_direction]

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, TypeAlias

from c4.contrib.structurizr._metadata import (
    normalize_structurizr_tags,
)
from c4.contrib.structurizr._options import AutoLayout

if TYPE_CHECKING:
    # Referenced only inside the ViewSelectorInput string below; a real
    # import here would reintroduce the workspace <-> _views cycle.
    from c4.contrib.structurizr.workspace import (
        StructurizrElement,
    )

ViewSelectorInput: TypeAlias = (
    "str | StructurizrElement | ViewSelector | "
    "Iterable[str | StructurizrElement | ViewSelector]"
)


@dataclass(frozen=True)
class ViewSelector:
    """A selector expression used to include or exclude view elements.

    Attributes:
        selector: Structurizr DSL selector expression.
    """

    selector: str


class RawSelector(ViewSelector):
    """A view selector expressed directly in Structurizr DSL syntax."""


class ViewTag(ViewSelector):
    """Select view elements that carry a specific tag."""

    def __init__(self, tag: str) -> None:
        """Initialize a tag-based view selector.

        Args:
            tag: Tag that selected elements must carry.
        """
        object.__setattr__(self, "selector", f"element.tag=={dsl_literal(tag)}")


@dataclass(frozen=True)
class ViewMetadata:
    """Raw metadata shared by all view factories, normalized on demand."""

    key: str | None = None
    description: str | None = None
    include: ViewSelectorInput | None = None
    exclude: ViewSelectorInput | None = None
    tags: list[str] | tuple[str, ...] | None = None
    properties: Mapping[str, object] | None = None
    auto_layout: AutoLayout | None = None
    animation: ViewSelectorInput | None = None

    def as_kwargs(self) -> dict[str, Any]:
        """Return normalized keyword arguments for a view constructor."""
        return {
            "key": self.key,
            "description": self.description,
            "include": normalize_view_selectors(self.include),
            "exclude": normalize_view_selectors(self.exclude),
            "tags": normalize_structurizr_tags(self.tags),
            "properties": self.properties,
            "auto_layout": self.auto_layout,
            "animation": normalize_animation(self.animation),
        }


def is_view_selector_value(value: Any) -> bool:
    from c4.contrib.structurizr.workspace import StructurizrElement

    return isinstance(value, (str, ViewSelector, StructurizrElement))


def view_selector(value: Any) -> str:
    if isinstance(value, ViewSelector):
        return value.selector

    from c4.contrib.structurizr.workspace import StructurizrElement

    if isinstance(value, StructurizrElement):
        return value.alias
    if isinstance(value, str):
        return value

    raise TypeError(f"Unsupported Structurizr view selector: {value!r}")


def normalize_view_selectors(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()

    return (
        (view_selector(value),)
        if is_view_selector_value(value)
        else tuple(view_selector(item) for item in value)
    )


def normalize_animation(value: Any) -> tuple[tuple[str, ...], ...]:
    if value is None:
        return ()

    if is_view_selector_value(value):
        return ((view_selector(value),),)

    return tuple(
        (view_selector(step),)
        if is_view_selector_value(step)
        else tuple(view_selector(item) for item in step)
        for step in value
    )


def dsl_literal(value: str) -> str:
    if value.replace("_", "").isidentifier():
        return value

    return (
        '"'
        + value
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
        .replace('"', '\\"')
        + '"'
    )

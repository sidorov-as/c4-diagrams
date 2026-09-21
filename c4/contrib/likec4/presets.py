"""Reusable specification vocabularies for LikeC4 projects."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import TypeVar

from c4.contrib.likec4._styles import parse_element_style
from c4.contrib.likec4.workspace.specification import (
    ElementKind,
    RelationshipKind,
    Tag,
)

_T = TypeVar("_T", ElementKind, RelationshipKind, Tag)


def _merge(base: tuple[_T, ...], extra: Iterable[_T]) -> tuple[_T, ...]:
    """Replace same-named entries in place and append new names."""
    merged = {item.name: item for item in base}
    for item in extra:
        merged[item.name] = item
    return tuple(merged.values())


@dataclass(frozen=True)
class Preset:
    """
    A set of kinds and tags applied with ``Specification.use``.

    A preset is plain data: it changes nothing until it is applied.

    Attributes:
        elements: Element kinds to declare.
        relationships: Relationship kinds to declare.
        tags: Tags to declare.
    """

    elements: tuple[ElementKind, ...] = ()
    relationships: tuple[RelationshipKind, ...] = ()
    tags: tuple[Tag, ...] = ()

    def with_(
        self,
        *,
        elements: Iterable[ElementKind] = (),
        relationships: Iterable[RelationshipKind] = (),
        tags: Iterable[Tag] = (),
    ) -> Preset:
        """
        Return a copy with kinds and tags added or overridden.

        An entry replaces the entry of the same name and keeps its position;
        a new name is appended.

        Args:
            elements: Element kinds to add or override.
            relationships: Relationship kinds to add or override.
            tags: Tags to add or override.
        """
        return Preset(
            _merge(self.elements, elements),
            _merge(self.relationships, relationships),
            _merge(self.tags, tags),
        )


C4 = Preset(
    elements=(
        ElementKind(
            "person",
            title="Person",
            style=parse_element_style(shape="person", color="blue"),
        ),
        ElementKind(
            "system",
            title="Software System",
            style=parse_element_style(color="primary"),
        ),
        ElementKind(
            "container",
            title="Container",
            style=parse_element_style(color="secondary"),
        ),
        ElementKind(
            "component",
            title="Component",
            style=parse_element_style(shape="component", color="muted"),
        ),
        ElementKind(
            "database",
            title="Database",
            style=parse_element_style(shape="storage", color="secondary"),
        ),
        ElementKind(
            "external",
            title="External System",
            style=parse_element_style(color="gray", border="dashed"),
        ),
    ),
)
"""The C4 vocabulary: six element kinds from the LikeC4 cheat-sheet."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from c4.contrib.likec4._identifiers import check_identifier

AUTO_LAYOUT_DIRECTIONS = ("TopBottom", "LeftRight", "BottomTop", "RightLeft")


@dataclass(frozen=True)
class Wildcard:
    """The ``*`` predicate: the scope of a view or all top-level elements."""


@dataclass(frozen=True)
class Children:
    """The direct children of ``element`` (``element.*``)."""

    element: Any


@dataclass(frozen=True)
class Descendants:
    """All nested elements of ``element`` (``element.**``)."""

    element: Any


@dataclass(frozen=True)
class RawPredicate:
    """Predicate text emitted verbatim; the renderer cannot check it."""

    text: str

    def __post_init__(self) -> None:
        if not isinstance(self.text, str) or not self.text.strip():
            raise ValueError("RawPredicate text must be a non-empty string")


@dataclass(frozen=True)
class Where:
    """
    ``item where tag is #tag and kind is kind`` filter over another item.

    Attributes:
        item: Element, ``Wildcard``, ``Children`` or ``Descendants``.
        tag: Tag name written without ``#``.
        kind: Element kind name.
    """

    item: Any
    tag: str | None = None
    kind: str | None = None

    def __post_init__(self) -> None:
        if self.tag is None and self.kind is None:
            raise ValueError("Where needs a tag or a kind condition")

        if self.tag is not None:
            if self.tag.startswith("#"):
                raise ValueError(
                    f"Tag {self.tag!r} must be written without '#'."
                )
            check_identifier(self.tag, "Tag")

        if self.kind is not None:
            check_identifier(self.kind, "Kind")

        if isinstance(self.item, (Where, RawPredicate)):
            raise TypeError(
                f"Where cannot wrap {type(self.item).__name__}; write a "
                "RawPredicate instead."
            )


def _check_predicate_side(owner: str, side: Any) -> None:
    """Reject sides that are themselves filters or relationship predicates."""
    if isinstance(
        side, (Between, Incoming, Outgoing, InOut, Where, RawPredicate)
    ):
        raise TypeError(
            f"{owner} cannot connect {type(side).__name__}; write a "
            "RawPredicate instead."
        )


@dataclass(frozen=True)
class Between:
    """
    Relationship predicate ``source -> target``.

    Attributes:
        source: Source item.
        target: Target item.
        both: Use ``<->`` (either direction).
    """

    source: Any
    target: Any
    both: bool = False

    def __post_init__(self) -> None:
        for side in (self.source, self.target):
            _check_predicate_side("Between", side)


@dataclass(frozen=True)
class Incoming:
    """Relationship predicate ``-> item``: relationships that enter it."""

    item: Any

    def __post_init__(self) -> None:
        _check_predicate_side("Incoming", self.item)


@dataclass(frozen=True)
class Outgoing:
    """Relationship predicate ``item ->``: relationships that leave it."""

    item: Any

    def __post_init__(self) -> None:
        _check_predicate_side("Outgoing", self.item)


@dataclass(frozen=True)
class InOut:
    """Relationship predicate ``-> item ->``: both directions."""

    item: Any

    def __post_init__(self) -> None:
        _check_predicate_side("InOut", self.item)


RELATIONSHIP_PREDICATES = (Between, Incoming, Outgoing, InOut)


@dataclass(frozen=True)
class IncludeRule:
    """``include items [with { navigateTo key }]`` rule."""

    items: tuple[Any, ...]
    navigate_to: str | None = None


@dataclass(frozen=True)
class ExcludeRule:
    """``exclude items`` rule."""

    items: tuple[Any, ...]


@dataclass(frozen=True)
class StyleRule:
    """``style targets { ... }`` rule."""

    targets: tuple[Any, ...]
    properties: tuple[tuple[str, Any], ...]


@dataclass(frozen=True)
class AutoLayoutRule:
    """``autoLayout direction [rank_sep [node_sep]]`` rule."""

    direction: str
    rank_sep: int | None = None
    node_sep: int | None = None


def validate_auto_layout(
    direction: str, rank_sep: int | None, node_sep: int | None
) -> AutoLayoutRule:
    """Validate ``autoLayout`` arguments."""
    if direction not in AUTO_LAYOUT_DIRECTIONS:
        raise ValueError(
            f"Invalid autoLayout direction {direction!r}; expected one of "
            f"{', '.join(AUTO_LAYOUT_DIRECTIONS)}."
        )

    if node_sep is not None and rank_sep is None:
        raise ValueError("node_sep requires rank_sep")

    for name, value in (("rank_sep", rank_sep), ("node_sep", node_sep)):
        if value is not None and (
            isinstance(value, bool) or not isinstance(value, int) or value < 0
        ):
            raise ValueError(f"{name} must be a non-negative integer")

    return AutoLayoutRule(direction, rank_sep, node_sep)

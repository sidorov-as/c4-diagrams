from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from c4.contrib.likec4._identifiers import check_identifier

MAX_SUMMARY_LENGTH = 150

MetadataValue = str | tuple[str, ...]


@dataclass(frozen=True)
class Link:
    """
    A hyperlink attached to an element, relationship or view.

    Attributes:
        url: Link target; may be relative to the document.
        title: Optional link title.
    """

    url: str
    title: str | None = None


def dedupe_preserving_order(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


def normalize_likec4_tags(value: Any) -> tuple[str, ...]:
    """Validate tags and strip nothing: tags are written without ``#``."""
    if value is None:
        return ()

    if (
        isinstance(value, str)
        or not isinstance(value, (list, tuple))
        or not all(isinstance(tag, str) for tag in value)
    ):
        raise TypeError("LikeC4 tags must be a list[str] or None")

    for tag in value:
        if tag.startswith("#"):
            raise ValueError(
                f"Tag {tag!r} must be written without '#'; the renderer "
                "adds it."
            )

        check_identifier(tag, "Tag")

    return dedupe_preserving_order(value)


def normalize_metadata(value: Any) -> dict[str, MetadataValue]:
    """Validate metadata: identifier keys, string or list-of-string values."""
    if value is None:
        return {}

    if not isinstance(value, Mapping):
        raise TypeError("LikeC4 metadata must be a mapping or None")

    result: dict[str, MetadataValue] = {}
    for key, item in value.items():
        check_identifier(key, "Metadata key")
        if isinstance(item, str):
            result[key] = item
        elif isinstance(item, (list, tuple)) and all(
            isinstance(entry, str) for entry in item
        ):
            result[key] = tuple(item)
        else:
            raise TypeError(
                f"Metadata value for {key!r} must be a string or a list of "
                "strings"
            )

    return result


def normalize_links(value: Any) -> tuple[Link, ...]:
    """Accept ``Link`` objects, URL strings or ``(url, title)`` pairs."""
    if value is None:
        return ()

    if isinstance(value, (str, Link)) or not isinstance(value, (list, tuple)):
        raise TypeError("LikeC4 links must be a list or None")

    links: list[Link] = []
    for item in value:
        if isinstance(item, Link):
            links.append(item)
        elif isinstance(item, str):
            links.append(Link(item))
        elif (
            isinstance(item, (list, tuple))
            and len(item) == 2
            and all(isinstance(part, str) for part in item)
        ):
            links.append(Link(item[0], item[1]))
        else:
            raise TypeError(
                "A LikeC4 link must be a Link, a URL string or a "
                "(url, title) pair"
            )
    return tuple(links)


def validate_summary(summary: str | None) -> str | None:
    """Reject summaries longer than LikeC4 allows."""
    if summary is not None and len(summary) > MAX_SUMMARY_LENGTH:
        raise ValueError(
            f"summary must not exceed {MAX_SUMMARY_LENGTH} characters; got "
            f"{len(summary)}."
        )

    return summary

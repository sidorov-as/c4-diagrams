from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def normalize_structurizr_tags(value: Any) -> tuple[str, ...]:
    """Validate tags supplied through the native Structurizr DSL."""
    if value is None:
        return ()

    if (
        isinstance(value, str)
        or not isinstance(value, (list, tuple))
        or not all(isinstance(tag, str) for tag in value)
    ):
        raise TypeError("Structurizr tags must be a list[str] or None")

    return dedupe_preserving_order(value)


def dedupe_preserving_order(values: Iterable[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))

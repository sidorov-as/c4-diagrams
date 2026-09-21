from __future__ import annotations

import re

IDENTIFIER_RE = re.compile(r"[A-Za-z_](?:[A-Za-z0-9_-]*[A-Za-z0-9_])?")

# Words the LikeC4 grammar does not accept as an element identifier or inside a
# predicate (checked against LikeC4 1.60.0).
RESERVED_WORDS = frozenset({
    "and",
    "autoLayout",
    "border",
    "color",
    "description",
    "dynamic",
    "exclude",
    "extends",
    "global",
    "icon",
    "include",
    "instanceOf",
    "is",
    "it",
    "link",
    "metadata",
    "navigateTo",
    "not",
    "notes",
    "of",
    "opacity",
    "or",
    "rank",
    "shape",
    "size",
    "specification",
    "style",
    "summary",
    "tag",
    "technology",
    "this",
    "title",
    "variant",
    "view",
    "views",
    "where",
    "with",
})


def is_valid_identifier(value: str) -> bool:
    """Return whether ``value`` is a valid LikeC4 identifier."""
    return IDENTIFIER_RE.fullmatch(value) is not None


def check_identifier(value: str, what: str) -> str:
    """Return ``value`` or raise ``ValueError`` naming the ``what`` it names."""
    if not isinstance(value, str) or not is_valid_identifier(value):
        raise ValueError(
            f"{what} {value!r} must contain only letters, digits, hyphens and "
            "underscores, must not start with a digit and must not end with "
            "a hyphen."
        )

    return value

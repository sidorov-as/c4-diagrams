from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

from c4.contrib.likec4._identifiers import (
    RESERVED_WORDS,
    is_valid_identifier,
)

Namespace = Literal["model", "deployment"]

_INVALID_CHARS_RE = re.compile(r"[^A-Za-z0-9_-]+")
_REPEATED_SEPARATOR_RE = re.compile(r"[_-]{2,}")


@dataclass(frozen=True)
class LikeC4Identifier:
    """
    A registered LikeC4 identifier.

    Attributes:
        identifier: Identifier written in the DSL, unique among siblings.
        fqn: Dotted path of identifiers from the root.
    """

    identifier: str
    fqn: str


class LikeC4IdentifierRegistry:
    """
    Derive valid LikeC4 identifiers and track their fully qualified names.

    The model and the deployment have separate namespaces. Within one
    namespace identifiers are unique per parent; a collision gets the first
    free numeric suffix (``name_2``, ``name_3``) so output is deterministic.
    """

    _FALLBACK_IDENTIFIER = "element"
    _LEADING_PREFIX = "el_"
    _RESERVED_SUFFIX = "_id"

    def __init__(self) -> None:
        self._siblings: dict[tuple[str, str | None], set[str]] = {}

    @classmethod
    def sanitize(cls, name: str) -> str:
        """Return a valid LikeC4 identifier derived from ``name``."""
        if is_valid_identifier(name) and name not in RESERVED_WORDS:
            return name

        sanitized = _INVALID_CHARS_RE.sub("_", name.strip())
        sanitized = _REPEATED_SEPARATOR_RE.sub("_", sanitized)
        sanitized = sanitized.strip("_-")

        if not sanitized.strip("_"):
            sanitized = cls._FALLBACK_IDENTIFIER
        if not sanitized[0].isalpha():
            sanitized = f"{cls._LEADING_PREFIX}{sanitized}"
        if sanitized in RESERVED_WORDS:
            sanitized = f"{sanitized}{cls._RESERVED_SUFFIX}"

        return sanitized

    def register(
        self,
        name: str,
        *,
        parent_fqn: str | None = None,
        namespace: Namespace = "model",
    ) -> LikeC4Identifier:
        """
        Register ``name`` under ``parent_fqn`` and return its identifier.

        Args:
            name: Alias or display name to derive the identifier from.
            parent_fqn: FQN of the parent, ``None`` for a root.
            namespace: ``"model"`` or ``"deployment"``.
        """
        used = self._siblings.setdefault((namespace, parent_fqn), set())
        base = self.sanitize(name)

        identifier, counter = base, 2
        while identifier in used:
            identifier = f"{base}_{counter}"
            counter += 1

        used.add(identifier)

        fqn = identifier if parent_fqn is None else f"{parent_fqn}.{identifier}"
        return LikeC4Identifier(identifier, fqn)

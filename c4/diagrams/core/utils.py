from __future__ import annotations

import re
from collections import defaultdict
from contextvars import ContextVar
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from c4.diagrams.core.diagram import Boundary, Diagram
else:
    Diagram = Boundary = Any


__diagram: ContextVar[Diagram | None] = ContextVar("diagram")
__boundary: ContextVar[Boundary | None] = ContextVar("boundary")

_ALIAS_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")
_CAMEL_CASE_BOUNDARY_RE = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
_INVALID_ALIAS_CHAR_RE = re.compile(r"[^a-zA-Z0-9_]+")
_REPEATED_UNDERSCORE_RE = re.compile(r"_+")


def _has_non_ascii_letters(label: str) -> bool:
    return any(char.isalpha() and not char.isascii() for char in label)


def is_valid_alias(alias: str) -> bool:
    """Return whether an alias can be safely used by all renderers."""
    return bool(_ALIAS_RE.fullmatch(alias))


def get_diagram() -> Diagram | None:
    """
    Get the current diagram from thread-local context.

    Returns:
        The currently active diagram, or None if not set.
    """
    try:
        return __diagram.get()
    except LookupError:  # pragma: no cover
        return None


def current_diagram() -> Diagram:
    """
    Get the current diagram, or raise if no diagram is active.

    Returns:
        The current diagram.

    Raises:
        ValueError: If no diagram is set in context.
    """
    diagram = get_diagram()
    if not diagram:
        raise ValueError("Element must be created within a diagram context")

    return diagram


def set_diagram(diagram: Diagram | None) -> None:
    """
    Set the current diagram in thread-local context.
    """
    __diagram.set(diagram)


def get_boundary() -> Boundary | None:
    """
    Get the current boundary from thread-local context.

    Returns:
        The currently active boundary, or None if not set.
    """
    try:
        return __boundary.get()
    except LookupError:
        return None


def current_boundary() -> Boundary:
    """
    Get the current boundary, or raise if no boundary is active.

    Returns:
        The current boundary.

    Raises:
        ValueError: If no boundary is set in context.
    """
    boundary = get_boundary()
    if not boundary:
        raise ValueError("Element must be created within a boundary context")

    return boundary


def set_boundary(boundary: Boundary | None) -> None:
    """
    Set the current boundary in thread-local context.
    """
    __boundary.set(boundary)


class AliasGenerator:
    """
    Generate unique, deterministic aliases from display labels.

    Alias generation rules:

    1. If an explicit `alias` is provided:
       - It is returned as-is.
       - A `ValueError` is raised if it has already been used.
       - Alias format validation is performed by the diagram when the element
         is registered.

    2. If `alias` is not provided:
       - If the label contains non-ASCII letters, the fallback prefix is used.
       - Otherwise, the label is normalized:
         * lowercased
         * spaces replaced with "_"
         * hyphens replaced with "_"
         * unsupported characters replaced with "_"
         * repeated and edge underscores removed
       - If the normalized value is not a valid ASCII alias, a normalized
         fallback prefix is used instead.
       - If the base value has not been used yet, it is returned as-is.
       - Otherwise, a numeric suffix is appended:
           `<base>_<n>`
         where numbering starts from 1 for the first collision.

    Example:
        >>> gen = AliasGenerator()
        >>> gen.generate("My Service")
        'my_service'
        >>> gen.generate("My Service")
        'my_service_1'
        >>> gen.generate("My Service")
        'my_service_2'
        >>> gen.generate("Пользователь")
        'element'
        >>> gen.generate("Пользователь", fallback_prefix="SystemBoundary")
        'system_boundary'

    Notes:
        - Generated aliases are valid ASCII identifiers:
          `[A-Za-z_][A-Za-z0-9_]*`.
        - Uniqueness is enforced per generator instance.
        - Explicit aliases participate in uniqueness checks.
        - Counters are maintained per normalized base alias.
        - The constructor-level fallback prefix defaults to "element".
    """

    _DEFAULT_FALLBACK_PREFIX: str = "element"

    def __init__(
        self,
        fallback_prefix: str = _DEFAULT_FALLBACK_PREFIX,
    ) -> None:
        self._fallback_prefix = self._normalize_fallback_prefix(fallback_prefix)
        self._counters: dict[str, int] = defaultdict(int)
        self._used: set[str] = set()

    @staticmethod
    def _normalize(label: str) -> str:
        """Normalize a display label into an ASCII alias base."""
        normalized = label.lower().replace(" ", "_").replace("-", "_")
        normalized = _INVALID_ALIAS_CHAR_RE.sub("_", normalized)
        normalized = _REPEATED_UNDERSCORE_RE.sub("_", normalized).strip("_")
        return normalized

    @classmethod
    def _normalize_fallback_prefix(cls, fallback_prefix: str) -> str:
        """Normalize a fallback prefix or return the default fallback."""
        normalized = _CAMEL_CASE_BOUNDARY_RE.sub("_", fallback_prefix)
        normalized_prefix = cls._normalize(normalized)

        if not is_valid_alias(normalized_prefix):
            return cls._DEFAULT_FALLBACK_PREFIX

        return normalized_prefix

    def generate(
        self,
        label: str,
        alias: str | None = None,
        fallback_prefix: str | None = None,
    ) -> str:
        """
        Generate a unique alias.

        Args:
            label: Source label used to derive the alias when `alias` is None.
            alias: Optional explicit alias. If provided, it must be unique.
            fallback_prefix: Prefix to use when the label cannot produce a
                valid alias. If omitted, the generator's default fallback
                prefix is used.

        Returns:
            A unique alias string.

        Raises:
            ValueError: If alias already exists.
        """
        if alias:
            if alias in self._used:
                raise ValueError(f"Alias {alias!r} already exists.")
            self._used.add(alias)
            return alias

        if _has_non_ascii_letters(label):
            base = self._normalize_fallback_prefix(
                fallback_prefix or self._fallback_prefix
            )
        else:
            base = self._normalize(label)

        if not is_valid_alias(base):
            base = self._normalize_fallback_prefix(
                fallback_prefix or self._fallback_prefix
            )

        if not is_valid_alias(base):
            base = self._fallback_prefix

        if base not in self._used:
            self._used.add(base)
            self._counters[base] = 1
            return base

        counter = self._counters[base] or 1
        while True:
            candidate = f"{base}_{counter}"
            counter += 1
            if candidate not in self._used:
                self._used.add(candidate)
                self._counters[base] = counter
                return candidate

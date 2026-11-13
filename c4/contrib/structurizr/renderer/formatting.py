from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager


def escape_structurizr_string(value: str) -> str:
    """Escape text for use inside a Structurizr DSL string literal."""
    return (
        value
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
        .replace('"', '\\"')
    )


def quote_structurizr_string(value: str) -> str:
    """Return a quoted Structurizr DSL string literal."""
    return f'"{escape_structurizr_string(value)}"'


class StructurizrStringBuilder:
    """Structurizr-oriented helper for indentation and nested blocks."""

    def __init__(self, *, level: int = 0, indent: str = "  ") -> None:
        """Initialize an empty DSL string builder.

        Args:
            level: Initial indentation level.
            indent: Text used for one indentation level.
        """
        self._level = level
        self._indent = indent
        self._lines: list[str] = []

    def add(self, line: str = "") -> None:
        """Add one line at the current indentation level.

        Args:
            line: DSL source line to append.
        """
        if not line:
            self._lines.append("")
            return

        for part in line.splitlines():
            self._lines.append(f"{self._indent * self._level}{part}")

    @contextmanager
    def indent(self) -> Iterator[None]:
        """Increase indentation while inside the context."""
        self._level += 1
        try:
            yield
        finally:
            self._level -= 1

    @contextmanager
    def block(self, header: str) -> Iterator[None]:
        """Add a Structurizr DSL block with nested indented contents.

        Args:
            header: DSL text preceding the opening brace.
        """
        self.add(f"{header} {{")
        with self.indent():
            yield
        self.add("}")

    @property
    def lines(self) -> list[str]:
        """Return a copy of the accumulated lines."""
        return list(self._lines)

    def get_result(self) -> str:
        """Return all accumulated lines joined by newlines."""
        return "\n".join(self._lines)

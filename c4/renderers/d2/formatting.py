from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager


def escape_d2_string(value: str) -> str:
    """
    Escape text for use inside a quoted D2 string.

    D2 quoted strings use backslash escaping, so the backslash must be escaped
    before replacing control characters and double quotes.
    """
    return (
        value
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace("\r", "\\r")
        .replace("\t", "\\t")
        .replace('"', '\\"')
    )


def quote_d2_string(value: str) -> str:
    """Return a quoted D2 string literal."""
    return f'"{escape_d2_string(value)}"'


def d2_markdown_value(markdown: str) -> str:
    """Return a raw D2 markdown block value."""
    body = "\n".join(
        f"  {line}" if line else "" for line in markdown.splitlines()
    )
    return f"||md\n{body}\n||"


def is_d2_markdown_value(value: str) -> bool:
    """Return whether a D2 value is a raw markdown block."""
    return value.startswith("||md\n") and value.endswith("\n||")


def d2_label(
    label: str,
    technology: str | None = None,
    *,
    include_technology: bool = True,
) -> str:
    """
    Return a quoted D2 label, optionally adding technology on a second line.
    """
    if technology and include_technology:
        return quote_d2_string(f"{label}\n[{technology}]")

    return quote_d2_string(label)


class D2StringBuilder:
    """Small D2-oriented helper for indentation and nested blocks."""

    def __init__(self, *, level: int = 0, indent: str = "  ") -> None:
        self._level = level
        self._indent = indent
        self._lines: list[str] = []

    def add(self, line: str = "") -> None:
        """Add one line at the current indentation level."""
        if line:
            for part in line.splitlines():
                self._lines.append(f"{self._indent * self._level}{part}")
            return

        self._lines.append("")

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
        """Add a D2 block with nested indented contents."""
        self.add(f"{header}: {{")
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

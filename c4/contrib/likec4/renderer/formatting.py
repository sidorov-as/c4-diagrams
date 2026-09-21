from __future__ import annotations


def escape_likec4_string(value: str) -> str:
    """Escape backslashes and double quotes for a quoted LikeC4 string."""
    return value.replace("\\", "\\\\").replace('"', '\\"')


def quote_likec4_string(value: str) -> str:
    """Return ``value`` as a double-quoted LikeC4 string."""
    return f'"{escape_likec4_string(value)}"'


def escape_likec4_markdown(value: str) -> str:
    """
    Escape user Markdown so that ``[[`` never becomes an element link.

    ``[[`` becomes ``\\[\\[`` (Markdown escapes); the string-level escaping
    of ``quote_likec4_markdown`` then doubles the backslashes.
    """
    return value.replace("[[", "\\[\\[")


def quote_likec4_markdown(value: str) -> str:
    """Return ``value`` as a triple-quoted Markdown LikeC4 string."""
    escaped = escape_likec4_markdown(value)
    escaped = escaped.replace("\\", "\\\\").replace("'", "\\'")
    return f"'''{escaped}'''"

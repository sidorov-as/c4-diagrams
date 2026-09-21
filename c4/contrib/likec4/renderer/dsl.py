from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from c4.contrib.likec4._metadata import Link, MetadataValue
from c4.contrib.likec4.renderer.formatting import quote_likec4_string

INDENT = "  "


def indent(lines: Iterable[str]) -> list[str]:
    """Indent every line by one level."""
    return [f"{INDENT}{line}" if line else line for line in lines]


def block(
    header: str,
    body: Sequence[str],
    *,
    braces_if_empty: bool = False,
    collapse: bool = True,
) -> list[str]:
    """
    Wrap ``body`` in ``header { ... }``.

    A body of one single-line statement collapses to ``header { body }``;
    an empty body renders only the header unless ``braces_if_empty``.
    ``collapse=False`` keeps even a one-line body on separate lines.
    """
    if not body:
        return [f"{header} {{}}"] if braces_if_empty else [header]

    if collapse and len(body) == 1 and "\n" not in body[0]:
        return [f"{header} {{ {body[0]} }}"]

    return [f"{header} {{", *indent(body), "}"]


def tags_line(tags: Iterable[str]) -> list[str]:
    """Return the ``#a #b`` tag statement, if there are tags."""
    names = [f"#{tag}" for tag in tags]
    return [" ".join(names)] if names else []


def style_value(key: str, value: Any) -> str:
    """Format one style value."""
    if key == "opacity":
        return f"{value}%"

    if isinstance(value, bool):
        return "true" if value else "false"

    return str(value)


def style_block(style: Mapping[str, Any]) -> list[str]:
    """Return a ``style { ... }`` block for ``style``, if not empty."""
    body = [f"{key} {style_value(key, v)}" for key, v in style.items()]
    return block("style", body) if body else []


def _metadata_value(value: MetadataValue) -> str:
    if isinstance(value, str):
        return quote_likec4_string(value)

    return "[" + ", ".join(quote_likec4_string(v) for v in value) + "]"


def metadata_block(metadata: Mapping[str, MetadataValue]) -> list[str]:
    """Return a ``metadata { ... }`` block, if there is metadata."""
    body = [f"{key} {_metadata_value(v)}" for key, v in metadata.items()]
    return block("metadata", body) if body else []


def link_lines(links: Iterable[Link]) -> list[str]:
    """Return one ``link`` statement per link."""
    return [
        f"link {link.url}"
        + (f" {quote_likec4_string(link.title)}" if link.title else "")
        for link in links
    ]

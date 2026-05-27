from __future__ import annotations

from typing import TypedDict


class BoundaryExtensions(TypedDict, total=False):
    """
    Mermaid-specific extension data for boundary elements.

    Args:
        tags: Optional tags for styling or grouping.
        link: URL link associated with the boundary.
        type: Optional boundary type rendered as the third Mermaid boundary
            macro argument.
    """

    tags: list[str] | None
    link: str | None
    type: str | None

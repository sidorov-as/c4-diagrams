from __future__ import annotations

from typing import TYPE_CHECKING, Any

from c4.contrib.structurizr._styles import (
    StructurizrStyleModel,
    parse_style_metadata,
)
from c4.contrib.structurizr.workspace.elements import (
    StructurizrElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.structurizr.workspace.workspace import Workspace


class Styles:
    """Workspace-level element and relationship style declarations."""

    def __init__(self, workspace: Workspace) -> None:
        """
        Initialize style declarations for ``workspace``.

        Args:
            workspace: Workspace that owns the style declarations.
        """
        self._workspace = workspace

    def element(
        self, target: str | StructurizrElement, **properties: Any
    ) -> Styles:
        """
        Apply styles to an element instance or element tag.

        Args:
            target: Element instance or tag to style.
            **properties: Structurizr element style properties.
        """
        if isinstance(target, StructurizrElement):
            target.style(**properties)
        else:
            self._workspace._element_styles.append(
                StructurizrStyleModel(target, parse_style_metadata(properties))
            )

        return self

    def tag(self, tag: str, **properties: Any) -> Styles:
        """
        Apply styles to all elements with ``tag``.

        Args:
            tag: Element tag to style.
            **properties: Structurizr element style properties.
        """
        return self.element(tag, **properties)

    def relationship(
        self, tag: str = "Relationship", **properties: Any
    ) -> Styles:
        """
        Apply styles to relationships with ``tag``.

        Args:
            tag: Relationship tag to style.
            **properties: Structurizr relationship style properties.
        """
        self._workspace._relationship_styles.append(
            StructurizrStyleModel(tag, parse_style_metadata(properties))
        )
        return self

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol, TypeVar

from c4.diagrams.core import BaseDiagramElement, Boundary, Diagram, Element

_INVALID_D2_IDENTIFIER_CHAR_RE = re.compile(r"[^a-zA-Z0-9_]+")
_REPEATED_UNDERSCORE_RE = re.compile(r"_+")

TDiagram = TypeVar("TDiagram", bound=Diagram)
TDiagram_contra = TypeVar(
    "TDiagram_contra",
    bound=Diagram,
    contravariant=True,
)


class D2ItemSource(Protocol[TDiagram_contra]):
    """Traversal interface used by D2 rendering and validation."""

    def iter_render_items(
        self,
        diagram: TDiagram_contra,
    ) -> Iterator[BaseDiagramElement]: ...  # pragma: no cover

    def iter_boundary_render_items(
        self,
        boundary: Boundary,
    ) -> Iterator[BaseDiagramElement]: ...  # pragma: no cover


class D2IdentifierCollisionError(ValueError):
    """Raised when aliases collapse to the same D2 identifier."""


@dataclass(frozen=True)
class D2Identifier:
    """D2 identifier data for a C4 element alias."""

    alias: str
    identifier: str
    path: tuple[str, ...]

    @property
    def d2_path(self) -> str:
        """Return the fully qualified D2 path."""
        return ".".join(self.path)


class D2IdentifierPolicy:
    """Build stable, sanitized D2 identifiers from C4 aliases."""

    _FALLBACK_IDENTIFIER = "element"
    TITLE_IDENTIFIER = "__title"

    def __init__(self, *, strict: bool = False) -> None:
        self._strict = strict
        self._aliases_by_identifier: dict[str, str] = {
            self.TITLE_IDENTIFIER: "generated diagram title",
        }
        self._identifiers_by_alias: dict[str, D2Identifier] = {}

    @staticmethod
    def sanitize(alias: str) -> str:
        """Return an ASCII identifier that can be used in unquoted D2 syntax."""
        sanitized = _INVALID_D2_IDENTIFIER_CHAR_RE.sub("_", alias)
        sanitized = _REPEATED_UNDERSCORE_RE.sub("_", sanitized)

        if not sanitized:
            return D2IdentifierPolicy._FALLBACK_IDENTIFIER

        if sanitized[0].isdigit():
            sanitized = f"_{sanitized}"

        return sanitized

    def build(
        self,
        diagram: TDiagram,
        renderer: D2ItemSource[TDiagram],
    ) -> dict[str, D2Identifier]:
        """Return D2 identifiers keyed by original C4 alias."""
        for item in renderer.iter_render_items(diagram):
            self._collect_item(item, renderer, parent_path=())

        return dict(self._identifiers_by_alias)

    def _collect_item(
        self,
        item: BaseDiagramElement,
        renderer: D2ItemSource[TDiagram],
        *,
        parent_path: tuple[str, ...],
    ) -> None:
        if not isinstance(item, Element):
            return

        d2_identifier = self._register(item, parent_path=parent_path)

        if not isinstance(item, Boundary):
            return

        for child in renderer.iter_boundary_render_items(item):
            self._collect_item(
                child,
                renderer,
                parent_path=d2_identifier.path,
            )

    def _register(
        self,
        element: Element,
        *,
        parent_path: tuple[str, ...],
    ) -> D2Identifier:
        base_identifier = self.sanitize(element.alias)
        identifier = self._unique_identifier(element.alias, base_identifier)
        d2_identifier = D2Identifier(
            alias=element.alias,
            identifier=identifier,
            path=(*parent_path, identifier),
        )
        self._identifiers_by_alias[element.alias] = d2_identifier

        return d2_identifier

    def _unique_identifier(self, alias: str, base_identifier: str) -> str:
        existing_alias = self._aliases_by_identifier.get(base_identifier)
        if existing_alias is None:
            self._aliases_by_identifier[base_identifier] = alias
            return base_identifier

        if self._strict:
            raise D2IdentifierCollisionError(
                "D2 identifier collision after sanitizing aliases: "
                f"{existing_alias!r} and {alias!r} both map to "
                f"{base_identifier!r}."
            )

        counter = 1
        while True:
            candidate = f"{base_identifier}_{counter}"
            if candidate not in self._aliases_by_identifier:
                self._aliases_by_identifier[candidate] = alias
                return candidate

            counter += 1

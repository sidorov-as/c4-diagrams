from __future__ import annotations

import re
from dataclasses import dataclass

_INVALID_IDENTIFIER_CHAR_RE = re.compile(r"[^a-zA-Z0-9_]+")
_REPEATED_UNDERSCORE_RE = re.compile(r"_+")
_RELATIONSHIP_IDENTIFIER_RE = re.compile(r"rel[0-9]+")

_STRUCTURIZR_RESERVED_WORDS = frozenset({
    "animation",
    "autoLayout",
    "branding",
    "component",
    "configuration",
    "container",
    "deployment",
    "deploymentEnvironment",
    "deploymentGroup",
    "deploymentNode",
    "description",
    "dynamic",
    "enterprise",
    "exclude",
    "filtered",
    "group",
    "healthCheck",
    "include",
    "infrastructureNode",
    "model",
    "person",
    "properties",
    "relationship",
    "softwareSystem",
    "styles",
    "systemContext",
    "systemLandscape",
    "tags",
    "technology",
    "theme",
    "themes",
    "title",
    "url",
    "views",
    "workspace",
})

_STRUCTURIZR_RENDERER_RESERVED_WORDS = frozenset({
    "rel",
})


@dataclass(frozen=True)
class StructurizrIdentifier:
    """Structurizr identifier data for a c4 element alias.

    Attributes:
        alias: Original c4 element alias.
        identifier: Sanitized Structurizr identifier.
    """

    alias: str
    identifier: str


class StructurizrIdentifierRegistry:
    """Build stable Structurizr-safe identifiers from c4 aliases.

    Attributes:
        RELATIONSHIP_PREFIX: Prefix used for generated relationship IDs.
    """

    _FALLBACK_IDENTIFIER = "element"
    _LEADING_PREFIX = "el_"
    RELATIONSHIP_PREFIX = "rel"

    def __init__(self) -> None:
        self._aliases_by_identifier: dict[str, str] = {}
        self._identifiers_by_alias: dict[str, StructurizrIdentifier] = {}
        self._relationship_index = 0

    @staticmethod
    def sanitize(alias: str) -> str:
        """Return an identifier that can be used in Structurizr DSL.

        Args:
            alias: Source c4 element alias.
        """
        sanitized = _INVALID_IDENTIFIER_CHAR_RE.sub("_", alias.strip())
        sanitized = _REPEATED_UNDERSCORE_RE.sub("_", sanitized)

        if not sanitized.strip("_"):
            sanitized = StructurizrIdentifierRegistry._FALLBACK_IDENTIFIER

        if not sanitized[0].isalpha():
            sanitized = (
                f"{StructurizrIdentifierRegistry._LEADING_PREFIX}"
                f"{sanitized.lstrip('_')}"
            )

        if (
            sanitized in _STRUCTURIZR_RESERVED_WORDS
            or sanitized in _STRUCTURIZR_RENDERER_RESERVED_WORDS
            or _RELATIONSHIP_IDENTIFIER_RE.fullmatch(sanitized) is not None
        ):
            sanitized = f"{sanitized}_id"

        return sanitized

    def register_alias(self, alias: str) -> StructurizrIdentifier:
        """Register one alias and return its Structurizr identifier.

        Args:
            alias: Source c4 element alias.
        """
        base_identifier = self.sanitize(alias)
        identifier = self._unique_identifier(alias, base_identifier)
        structurizr_identifier = StructurizrIdentifier(
            alias=alias,
            identifier=identifier,
        )
        self._identifiers_by_alias[alias] = structurizr_identifier
        return structurizr_identifier

    def next_relationship_id(self) -> str:
        """Return a stable relationship identifier for declaration order."""
        self._relationship_index += 1
        return f"{self.RELATIONSHIP_PREFIX}{self._relationship_index}"

    @property
    def identifiers(self) -> dict[str, StructurizrIdentifier]:
        """Return registered identifiers without diagram traversal."""
        return dict(self._identifiers_by_alias)

    def _unique_identifier(self, alias: str, base_identifier: str) -> str:
        existing_alias = self._aliases_by_identifier.get(base_identifier)
        if existing_alias is None:
            self._aliases_by_identifier[base_identifier] = alias
            return base_identifier

        if existing_alias == alias:
            return base_identifier

        counter = 1
        while True:
            candidate = f"{base_identifier}_{counter}"
            if candidate not in self._aliases_by_identifier:
                self._aliases_by_identifier[candidate] = alias
                return candidate

            counter += 1

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from c4.contrib.likec4._identifiers import check_identifier
from c4.contrib.likec4._metadata import normalize_likec4_tags
from c4.contrib.likec4._styles import (
    StyleValue,
    parse_element_style,
    parse_relationship_style,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.likec4.presets import Preset
    from c4.contrib.likec4.workspace.project import Project

_COLOR_VALUE_RE = re.compile(
    r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})"
    r"|rgba?\(\s*\d{1,3}\s*,\s*\d{1,3}\s*,\s*\d{1,3}\s*(?:,\s*[\d.]+\s*)?\)"
)


@dataclass(frozen=True)
class ElementKind:
    """
    A declared element or deployment node kind.

    Attributes:
        name: Kind identifier.
        title: Default title for elements of the kind.
        technology: Default technology.
        description: Default description.
        notation: Legend title for the kind.
        tags: Tags applied to every element of the kind.
        style: Default style properties.
    """

    name: str
    title: str | None = None
    technology: str | None = None
    description: str | None = None
    notation: str | None = None
    tags: tuple[str, ...] = ()
    style: dict[str, StyleValue] = field(default_factory=dict)


@dataclass(frozen=True)
class RelationshipKind:
    """
    A declared relationship kind.

    Attributes:
        name: Kind identifier.
        technology: Default technology.
        description: Default description.
        style: Default style properties.
    """

    name: str
    technology: str | None = None
    description: str | None = None
    style: dict[str, StyleValue] = field(default_factory=dict)


@dataclass(frozen=True)
class Tag:
    """
    A declared tag; the name is written without ``#``.

    Attributes:
        name: Tag identifier.
        color: Optional theme or custom color name.
    """

    name: str
    color: str | None = None


@dataclass(frozen=True)
class CustomColor:
    """
    A custom named color.

    Attributes:
        name: Color identifier.
        value: Hex or ``rgb()``/``rgba()`` value.
    """

    name: str
    value: str


class Specification:
    """
    The vocabulary of a project: kinds, tags and custom colors.

    Declarations keep their order and a name may be declared only once per
    category.
    """

    def __init__(self, project: Project) -> None:
        """
        Initialize an empty specification.

        Args:
            project: Project that owns the specification.
        """
        self._project = project
        self.element_kinds: dict[str, ElementKind] = {}
        self.relationship_kinds: dict[str, RelationshipKind] = {}
        self.deployment_kinds: dict[str, ElementKind] = {}
        self.tags: dict[str, Tag] = {}
        self.colors: dict[str, CustomColor] = {}

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    @staticmethod
    def _declare(
        registry: dict[str, Any], name: str, item: Any, what: str
    ) -> None:
        if name in registry:
            raise ValueError(f"{what} {name!r} is already declared.")

        registry[name] = item

    def element(
        self,
        name: str,
        *,
        title: str | None = None,
        technology: str | None = None,
        description: str | None = None,
        notation: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        **style: Any,
    ) -> Self:
        """
        Declare an element kind.

        Args:
            name: Kind identifier.
            title: Default title.
            technology: Default technology.
            description: Default description.
            notation: Legend title.
            tags: Tags applied to every element of the kind.
            **style: Default element style properties.
        """
        self._declare(
            self.element_kinds,
            check_identifier(name, "Element kind"),
            ElementKind(
                name,
                title,
                technology,
                description,
                notation,
                normalize_likec4_tags(tags),
                parse_element_style(**style),
            ),
            "Element kind",
        )
        return self

    def deployment_node(
        self,
        name: str,
        *,
        title: str | None = None,
        technology: str | None = None,
        description: str | None = None,
        notation: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        **style: Any,
    ) -> Self:
        """
        Declare a deployment node kind.

        Args:
            name: Kind identifier.
            title: Default title.
            technology: Default technology.
            description: Default description.
            notation: Legend title.
            tags: Tags applied to every node of the kind.
            **style: Default style properties.
        """
        self._declare(
            self.deployment_kinds,
            check_identifier(name, "Deployment node kind"),
            ElementKind(
                name,
                title,
                technology,
                description,
                notation,
                normalize_likec4_tags(tags),
                parse_element_style(**style),
            ),
            "Deployment node kind",
        )
        return self

    def relationship(
        self,
        name: str,
        *,
        technology: str | None = None,
        description: str | None = None,
        **style: Any,
    ) -> Self:
        """
        Declare a relationship kind.

        Args:
            name: Kind identifier.
            technology: Default technology.
            description: Default description.
            **style: Default relationship style properties.
        """
        self._declare(
            self.relationship_kinds,
            check_identifier(name, "Relationship kind"),
            RelationshipKind(
                name, technology, description, parse_relationship_style(**style)
            ),
            "Relationship kind",
        )
        return self

    def tag(self, name: str, color: str | None = None) -> Self:
        """
        Declare a tag.

        Args:
            name: Tag identifier, written without ``#``.
            color: Optional theme or custom color name.
        """
        if name.startswith("#"):
            raise ValueError(
                f"Tag {name!r} must be declared without '#'; the renderer "
                "adds it."
            )
        if color is not None:
            check_identifier(color, "Tag color")
        self._declare(
            self.tags, check_identifier(name, "Tag"), Tag(name, color), "Tag"
        )
        return self

    def color(self, name: str, value: str) -> Self:
        """
        Declare a custom color.

        Args:
            name: Color identifier.
            value: Hex or ``rgb()``/``rgba()`` value.
        """
        if _COLOR_VALUE_RE.fullmatch(value) is None:
            raise ValueError(
                f"Color value {value!r} must be a hex or rgb()/rgba() value."
            )
        self._declare(
            self.colors,
            check_identifier(name, "Color"),
            CustomColor(name, value),
            "Color",
        )
        return self

    def use(self, preset: Preset) -> Self:
        """
        Declare every kind and tag of a preset, in the preset's order.

        Names go through the same duplicate check as manual declarations.

        Args:
            preset: Preset to apply, such as ``C4``.
        """
        for kind in preset.elements:
            self._declare(
                self.element_kinds,
                check_identifier(kind.name, "Element kind"),
                kind,
                "Element kind",
            )

        for rel_kind in preset.relationships:
            self._declare(
                self.relationship_kinds,
                check_identifier(rel_kind.name, "Relationship kind"),
                rel_kind,
                "Relationship kind",
            )

        for tag in preset.tags:
            self._declare(
                self.tags, check_identifier(tag.name, "Tag"), tag, "Tag"
            )

        return self

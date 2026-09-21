from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import TracebackType
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from c4.contrib.structurizr._metadata import (
    dedupe_preserving_order,
    normalize_structurizr_tags,
)
from c4.contrib.structurizr._styles import (
    parse_style_metadata,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.structurizr.workspace.model import Model


def _alias(name: str, explicit: str | None, used: set[str]) -> str:
    """Return a unique valid alias derived from a name or explicit value."""
    value = (
        explicit
        or "".join(
            char.lower() if char.isalnum() else "_" for char in name
        ).strip("_")
        or "element"
    )

    if not value.isidentifier():
        raise ValueError(f"Alias {value!r} must be a valid identifier.")

    base, suffix = value, 2
    while value in used:
        value, suffix = f"{base}_{suffix}", suffix + 1

    return value


@dataclass
class Relationship:
    """
    A directed relationship declared between two Structurizr elements.

    Attributes:
        source: Element that initiates the relationship.
        destination: Element that receives the relationship.
        description: Human-readable relationship label. ``None`` for an
            unlabeled relationship (``a >> b``), which renders without a
            description; set it later with ``a >> b | "label"``.
        technology: Optional technology used by the relationship.
        tags: Tags applied to the relationship.
        properties: Custom relationship properties.
        url: Optional hyperlink associated with the relationship.
        style: Relationship-local style properties.
    """

    source: StructurizrElement
    destination: StructurizrElement
    description: str | None = None
    technology: str | None = None
    tags: tuple[str, ...] = ()
    properties: dict[str, Any] | None = None
    url: str | None = None
    style: dict[str, Any] | None = None

    @property
    def label(self) -> str | None:
        return self.description

    def __or__(self, description: str) -> Relationship:
        """
        Set the description of an unlabeled relationship: ``a >> b | "text"``.

        Args:
            description: Human-readable relationship label.

        Raises:
            ValueError: If the relationship already has a description.
        """
        if not isinstance(description, str):
            return NotImplemented

        if self.description is not None:
            raise ValueError(
                f"Relationship already has the description {self.description!r}"
            )

        self.description = description

        return self


@dataclass(frozen=True)
class DynamicStep:
    """
    One ordered interaction in a dynamic view.

    Attributes:
        source: Element that initiates the interaction.
        destination: Element that receives the interaction.
        description: Human-readable interaction label; ``None`` when the step
            comes from an unlabeled relationship.
        technology: Optional technology used by the interaction.
        relationship: Optional model relationship represented by this step.
        tags: Tags applied to the step.
        url: Optional hyperlink associated with the step.
        properties: Custom step properties.
        style: Step-local style properties.
    """

    source: StructurizrElement
    destination: StructurizrElement
    description: str | None
    technology: str | None = None
    relationship: Relationship | None = None
    tags: tuple[str, ...] = ()
    url: str | None = None
    properties: Mapping[str, Any] | None = None
    style: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class _RelationshipExpression:
    """
    An immutable relationship expression produced by ``Rel(...)``.

    Binding it to an element with ``>>`` or ``<<`` returns a new
    ``_BoundRelationship`` and leaves the expression unchanged, so one
    ``Rel`` can be reused for any number of relationships.

    Attributes:
        description: Human-readable relationship label.
        technology: Optional technology used by the relationship.
        tags: Tags applied to the relationship.
        properties: Custom relationship properties.
        url: Optional hyperlink associated with the relationship.
        style: Relationship-local style properties.
    """

    description: str | None = None
    technology: str | None = None
    tags: tuple[str, ...] = ()
    properties: Mapping[str, Any] | None = None
    url: str | None = None
    style: Mapping[str, Any] | None = None

    def __rrshift__(
        self, other: StructurizrElement | list[StructurizrElement]
    ) -> _BoundRelationship:
        """Bind left-hand sources: ``a >> Rel()`` or ``[a, b] >> Rel()``."""
        return _BoundRelationship.bind(self, other, is_source=True)

    def __rlshift__(
        self, other: StructurizrElement | list[StructurizrElement]
    ) -> _BoundRelationship:
        """Bind left-hand targets: ``c << Rel()`` or ``[a, b] << Rel()``."""
        return _BoundRelationship.bind(self, other, is_source=False)


@dataclass(frozen=True)
class _BoundRelationship:
    """
    A relationship expression with one side already chosen.

    Attributes:
        expression: The expression that supplies the relationship metadata.
        fixed: Elements already on one side of the relationship.
        fixed_is_list: Whether that side was written as a list.
        fixed_is_source: Whether the fixed side is the source.
    """

    expression: _RelationshipExpression
    fixed: tuple[StructurizrElement, ...]
    fixed_is_list: bool
    fixed_is_source: bool

    @classmethod
    def bind(
        cls,
        expression: _RelationshipExpression,
        other: StructurizrElement | list[StructurizrElement],
        *,
        is_source: bool,
    ) -> _BoundRelationship:
        """Bind ``expression`` to a single element or a list of elements."""
        is_list = isinstance(other, list)

        return cls(
            expression=expression,
            fixed=tuple(other) if isinstance(other, list) else (other,),
            fixed_is_list=is_list,
            fixed_is_source=is_source,
        )

    def __rshift__(
        self, other: StructurizrElement | list[StructurizrElement]
    ) -> Relationship | list[Relationship]:
        """Complete ``source >> Rel() >> destination``."""
        if not self.fixed_is_source:
            return NotImplemented

        return self._complete(other)

    def __lshift__(
        self, other: StructurizrElement | list[StructurizrElement]
    ) -> Relationship | list[Relationship]:
        """Complete ``destination << Rel() << source``."""
        if self.fixed_is_source:
            return NotImplemented

        return self._complete(other)

    def _complete(
        self, other: StructurizrElement | list[StructurizrElement]
    ) -> Relationship | list[Relationship]:
        """Create one relationship per element on the open side."""
        other_is_list = isinstance(other, list)
        if self.fixed_is_list and other_is_list:
            raise ValueError(
                "Either source or destination must be a single element"
            )

        others = tuple(other) if isinstance(other, list) else (other,)
        pairs = [
            (fixed, item) if self.fixed_is_source else (item, fixed)
            for fixed in self.fixed
            for item in others
        ]
        result = [
            self._relationship(source, destination)
            for source, destination in pairs
        ]
        if self.fixed_is_list or other_is_list:
            return result

        return result[0]

    def _relationship(
        self, source: StructurizrElement, destination: StructurizrElement
    ) -> Relationship:
        """Create the relationship between two elements."""
        expression = self.expression

        return source._model._relationship(
            source=source,
            destination=destination,
            description=expression.description,
            technology=expression.technology,
            tags=expression.tags,
            properties=expression.properties,
            url=expression.url,
            style=expression.style,
        )


def Rel(
    description: str | None = None,
    *,
    technology: str | None = None,
    tags: list[str] | tuple[str, ...] | None = None,
    properties: Mapping[str, Any] | None = None,
    url: str | None = None,
    style: Mapping[str, Any] | None = None,
) -> _RelationshipExpression:
    """
    Start a relationship expression with optional metadata.

    Only ``description`` may be positional; pass ``technology`` and the other
    options by name. The expression is immutable and can be reused.

    Args:
        description: Relationship description to render.
        technology: Optional technology used by the relationship.
        tags: Tags applied to the relationship.
        properties: Custom relationship properties.
        url: Optional hyperlink associated with the relationship.
        style: Relationship-local style properties.
    """
    return _RelationshipExpression(
        description=description,
        technology=technology,
        tags=normalize_structurizr_tags(tags),
        properties=properties,
        url=url,
        style=style,
    )


class StructurizrElement:
    """
    Base class for elements declared in a Structurizr workspace model.

    Attributes:
        alias: Unique Structurizr identifier for the element.
        name: Display name of the element.
        description: Optional description of the element.
        technology: Optional implementation technology.
        tags: Tags applied to the element.
        properties: Custom element properties.
        url: Optional hyperlink associated with the element.
    """

    kind = "element"

    def __init__(
        self,
        model: Model,
        name: str,
        *,
        description: str | None = None,
        technology: str | None = None,
        alias: str | None = None,
        parent: StructurizrElement | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        url: str | None = None,
        style: Mapping[str, Any] | None = None,
    ) -> None:
        """
        Initialize a model element.

        Args:
            model: Model that owns the element.
            name: Display name of the element.
            description: Optional description of its responsibility.
            technology: Optional technology used to implement it.
            alias: Optional Structurizr identifier; one is derived when omitted.
            parent: Optional containing model element.
            tags: Tags applied to the element.
            properties: Custom element properties.
            url: Optional hyperlink associated with the element.
            style: Element-local style properties.
        """
        self._model = model
        self.name = name
        self.description = description
        self.technology = technology
        self.alias = _alias(name, alias, model._aliases)
        model._aliases.add(self.alias)
        self.parent = parent
        self.tags = normalize_structurizr_tags(tags)
        self.properties = dict(properties or {})
        self.url = url
        self.style_properties = dict(parse_style_metadata(style))

    def __enter__(self) -> Self:
        self._model._owner_stack.append(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._model._pop_owner(self)

    def tag(self, *tags: str) -> Self:
        """
        Add tags to this element and return it.

        Args:
            *tags: Tags to add, in declaration order.
        """
        self.tags = dedupe_preserving_order((
            *self.tags,
            *normalize_structurizr_tags(tags),
        ))
        return self

    def property(self, key: str, value: Any) -> Self:
        """
        Set a custom property on this element and return it.

        Args:
            key: Property name.
            value: Property value.
        """
        self.properties[key] = value
        return self

    def style(self, **properties: Any) -> Self:
        """
        Apply element style properties and return this element.

        Args:
            **properties: Structurizr element style properties.
        """
        self.style_properties.update(parse_style_metadata(properties))
        return self

    def uses(
        self,
        other: StructurizrElement,
        description: str | None,
        *,
        technology: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        url: str | None = None,
        style: Mapping[str, Any] | None = None,
    ) -> Relationship:
        """
        Declare that this element uses another element.

        Args:
            other: Destination element.
            description: Human-readable relationship label.
            technology: Optional technology used by the relationship.
            tags: Tags applied to the relationship.
            properties: Custom relationship properties.
            url: Optional hyperlink associated with the relationship.
            style: Relationship-local style properties.
        """
        return self._model._relationship(
            source=self,
            destination=other,
            description=description,
            technology=technology,
            tags=normalize_structurizr_tags(tags),
            properties=properties,
            url=url,
            style=style,
        )

    def used_by(
        self, other: StructurizrElement, description: str | None, **kwargs: Any
    ) -> Relationship:
        """
        Declare that another element uses this element.

        Args:
            other: Source element.
            description: Human-readable relationship label.
            **kwargs: Additional relationship metadata accepted by ``uses``.
        """
        return other.uses(self, description, **kwargs)

    def __rshift__(self, other: Any) -> Any:
        """Build a relationship through the concise ``>>`` DSL."""
        if isinstance(other, str):
            return _BoundRelationship.bind(
                _RelationshipExpression(other), self, is_source=True
            )

        if isinstance(other, _RelationshipExpression):
            return _BoundRelationship.bind(other, self, is_source=True)

        if isinstance(other, StructurizrElement):
            return self._model._relationship(
                source=self,
                destination=other,
                description=None,
                technology=None,
            )

        return NotImplemented

    def __lshift__(self, other: Any) -> Any:
        """Build a relationship through the concise ``<<`` DSL."""
        if isinstance(other, str):
            return _BoundRelationship.bind(
                _RelationshipExpression(other), self, is_source=False
            )

        if isinstance(other, _RelationshipExpression):
            return _BoundRelationship.bind(other, self, is_source=False)

        if isinstance(other, StructurizrElement):
            return other >> self

        return NotImplemented

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}(alias={self.alias!r}, name={self.name!r})"
        )


class Person(StructurizrElement):
    """A person who interacts with one or more software systems."""

    kind = "person"


class SoftwareSystem(StructurizrElement):
    """A software system in the workspace model."""

    kind = "softwareSystem"

    def Container(self, name: str, **kwargs: Any) -> Container:
        """Add a container owned by this software system."""
        return self._model.Container(name, owner=self, **kwargs)


class Container(StructurizrElement):
    """A deployable application or data store within a software system."""

    kind = "container"

    def Component(self, name: str, **kwargs: Any) -> Component:
        """Add a component owned by this container."""
        return self._model.Component(name, owner=self, **kwargs)


class Component(StructurizrElement):
    """A component within a software-system container."""

    kind = "component"


class DeploymentNode(StructurizrElement):
    """An infrastructure location on which software is deployed."""

    kind = "deploymentNode"

    def __init__(
        self,
        model: Model,
        name: str,
        *,
        environment: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a deployment node.

        Args:
            model: Model that owns the node.
            name: Display name of the node.
            environment: Optional deployment environment name.
            **kwargs: Element metadata accepted by ``StructurizrElement``.
        """
        super().__init__(model, name, **kwargs)
        self.environment = environment
        self.deployment_nodes: list[DeploymentNode] = []
        self.infrastructure_nodes: list[InfrastructureNode] = []
        self.software_system_instances: list[SoftwareSystemInstance] = []
        self.container_instances: list[ContainerInstance] = []

    def DeploymentNode(self, name: str, **kwargs: Any) -> DeploymentNode:
        """Add a deployment node nested inside this node."""
        return self._model.DeploymentNode(name, parent=self, **kwargs)

    def InfrastructureNode(
        self, name: str, **kwargs: Any
    ) -> InfrastructureNode:
        """Add an infrastructure node nested inside this node."""
        return self._model.InfrastructureNode(name, parent=self, **kwargs)

    def SoftwareSystemInstance(
        self, target: SoftwareSystem, **kwargs: Any
    ) -> SoftwareSystemInstance:
        """Add an instance of a software system to this node."""
        return self._model.SoftwareSystemInstance(target, parent=self, **kwargs)

    def ContainerInstance(
        self, target: Container, **kwargs: Any
    ) -> ContainerInstance:
        """Add an instance of a container to this node."""
        return self._model.ContainerInstance(target, parent=self, **kwargs)


class InfrastructureNode(DeploymentNode):
    """A deployment node representing supporting infrastructure."""

    kind = "infrastructureNode"


class _DeploymentInstance(StructurizrElement):
    """Base class for a model element deployed on a deployment node."""

    def __init__(
        self,
        model: Model,
        target: StructurizrElement,
        *,
        parent: DeploymentNode,
        alias: str | None = None,
        description: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        url: str | None = None,
        style: Mapping[str, Any] | None = None,
    ) -> None:
        resolved_description = (
            description if description is not None else target.description
        )

        super().__init__(
            model,
            target.name,
            description=resolved_description,
            technology=target.technology,
            alias=alias or f"{target.alias}_instance",
            parent=parent,
            tags=tags,
            properties=properties,
            url=url,
            style=style,
        )
        self.model_element = target
        self.parent_node = parent


class SoftwareSystemInstance(_DeploymentInstance):
    """A software system deployed on a deployment node."""

    kind = "softwareSystemInstance"


class ContainerInstance(_DeploymentInstance):
    """A container deployed on a deployment node."""

    kind = "containerInstance"

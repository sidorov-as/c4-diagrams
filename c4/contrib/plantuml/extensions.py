from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.plantuml.components import BaseIndex


class RelationshipExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for relationships.

    Args:
        sprite: Optional sprite to represent the relationship.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the relationship.
        index: Index associated with the relationship.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None
    index: str | BaseIndex | None


class ElementExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for diagram elements.

    Args:
        sprite: Optional sprite to represent the element.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the element.
        type: Optional custom type or stereotype label.
        base_shape: Optional shape override for rendering.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None
    type: str | None
    base_shape: str | None


class PersonExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for people.

    Args:
        sprite: Optional sprite to represent the person.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the person.
        type: Optional custom type or stereotype label.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None
    type: str | None


class SystemExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for software systems.

    Args:
        sprite: Optional sprite to represent the system.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the system.
        type: Optional custom type or stereotype label.
        base_shape: Optional shape override for rendering.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None
    type: str | None
    base_shape: str | None


class SystemStorageExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for database-like or queue-like systems.

    Args:
        sprite: Optional sprite to represent the system.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the system.
        type: Optional custom type or stereotype label.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None
    type: str | None


class BoundaryExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for boundary elements.

    Args:
        tags: Optional tags for styling or grouping.
        link: URL link associated with the boundary.
        type: Optional custom type or stereotype label.
    """

    tags: list[str] | None
    link: str | None
    type: str | None


class NodeExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for deployment nodes.

    Args:
        sprite: Optional sprite to represent the node.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the node.
        type: Optional custom type or stereotype label.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None
    type: str | None


class ContainerExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for containers.

    Args:
        sprite: Optional sprite to represent the container.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the container.
        base_shape: Optional shape override for rendering.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None
    base_shape: str | None


class ContainerStorageExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for database-like or queue-like containers.

    Args:
        sprite: Optional sprite to represent the container.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the container.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None


class ComponentExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for components.

    Args:
        sprite: Optional sprite to represent the component.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the component.
        base_shape: Optional shape override for rendering.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None
    base_shape: str | None


class ComponentStorageExtensions(TypedDict, total=False):
    """
    PlantUML-specific extension data for database-like or queue-like components.

    Args:
        sprite: Optional sprite to represent the component.
        tags: Optional tags for styling or grouping.
        link: URL link associated with the component.
    """

    sprite: str | None
    tags: list[str] | None
    link: str | None

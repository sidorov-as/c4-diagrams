from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from c4.contrib.structurizr.renderer.options import AutoLayout
from c4.contrib.structurizr.renderer.styles import (
    StructurizrStylesModel,
)


@dataclass
class StructurizrRelationshipModel:
    """Internal Structurizr relationship model.

    Attributes:
        id: Stable relationship identifier.
        source_id: Identifier of the source element.
        destination_id: Identifier of the destination element.
        description: Optional human-readable relationship label.
        technology: Optional technology used by the relationship.
        tags: Tags applied to the relationship.
        style: Relationship-local style properties.
        url: Optional relationship hyperlink.
        properties: Custom relationship properties.
    """

    id: str
    source_id: str
    destination_id: str
    description: str | None = None
    technology: str | None = None
    tags: tuple[str, ...] = ()
    style: Mapping[str, Any] = field(default_factory=dict)
    url: str | None = None
    properties: dict[str, str] = field(default_factory=dict)


@dataclass
class StructurizrElementModel:
    """Internal Structurizr element model.

    Attributes:
        id: Stable element identifier.
        name: Element display name.
        element_type: Structurizr element type.
        description: Optional element description.
        technology: Optional implementation technology.
        tags: Tags applied to the element.
        style: Element-local style properties.
        url: Optional element hyperlink.
        properties: Custom element properties.
        relationships: Relationships declared from the element.
        children: Nested model elements.
        software_system_instances: Deployed software-system instances.
        container_instances: Deployed container instances.
        infrastructure_nodes: Nested infrastructure nodes.
        instance_of_id: Identifier of the model element being instantiated.
        environment: Deployment environment name.
    """

    id: str
    name: str
    element_type: str
    description: str | None = None
    technology: str | None = None
    tags: tuple[str, ...] = ()
    style: Mapping[str, Any] = field(default_factory=dict)
    url: str | None = None
    properties: dict[str, str] = field(default_factory=dict)
    relationships: list[StructurizrRelationshipModel] = field(
        default_factory=list
    )
    children: list[StructurizrElementModel] = field(default_factory=list)
    software_system_instances: list[StructurizrElementModel] = field(
        default_factory=list
    )
    container_instances: list[StructurizrElementModel] = field(
        default_factory=list
    )
    infrastructure_nodes: list[StructurizrElementModel] = field(
        default_factory=list
    )
    instance_of_id: str | None = None
    environment: str | None = None


@dataclass
class StructurizrViewModel:
    """Internal Structurizr view model.

    Attributes:
        key: Stable Structurizr view key.
        type: Structurizr view type.
        title: Optional displayed title.
        description: Optional view description.
        tags: Tags applied to the view.
        scope_id: Optional identifier of the scoped element.
        environment: Optional deployment environment name.
        auto_layout: Optional automatic-layout configuration.
        include: Element selectors to include.
        exclude: Element selectors to exclude.
        animation: Ordered animation selector groups.
        relationships: Relationships rendered by the view.
        properties: Custom view properties.
    """

    key: str
    type: str
    title: str | None = None
    description: str | None = None
    tags: tuple[str, ...] = ()
    scope_id: str | None = None
    environment: str | None = None
    auto_layout: AutoLayout | None = None
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    animation: tuple[tuple[str, ...], ...] = ()
    relationships: list[StructurizrRelationshipModel] = field(
        default_factory=list
    )
    properties: dict[str, str] = field(default_factory=dict)


_DeploymentEnvironment = tuple[str, list[StructurizrElementModel]]


@dataclass
class StructurizrWorkspaceModel:
    """Internal Structurizr workspace model.

    Attributes:
        name: Workspace title.
        description: Optional workspace description.
        people: Root person elements.
        software_systems: Root software-system elements.
        deployment_nodes: Root deployment nodes.
        deployment_environments: Deployment environments and root nodes.
        relationships: Model-level relationships.
        views: Declared views.
        styles: Workspace style configuration.
        theme: Optional custom Structurizr theme URL or path.
        properties: Custom workspace properties.
    """

    name: str
    description: str | None = None
    people: list[StructurizrElementModel] = field(default_factory=list)
    software_systems: list[StructurizrElementModel] = field(
        default_factory=list
    )
    deployment_nodes: list[StructurizrElementModel] = field(
        default_factory=list
    )
    deployment_environments: list[_DeploymentEnvironment] = field(
        default_factory=list
    )

    relationships: list[StructurizrRelationshipModel] = field(
        default_factory=list
    )
    views: list[StructurizrViewModel] = field(default_factory=list)
    styles: StructurizrStylesModel = field(
        default_factory=StructurizrStylesModel
    )
    theme: str | None = None
    properties: dict[str, str] = field(default_factory=dict)


def iter_workspace_elements(
    workspace: StructurizrWorkspaceModel,
) -> Iterable[StructurizrElementModel]:
    """Yield every element in the workspace, flattening all element trees."""
    for person in workspace.people:
        yield from iter_element_tree(person)

    for system in workspace.software_systems:
        yield from iter_element_tree(system)

    for node in workspace.deployment_nodes:
        yield from iter_element_tree(node)


def iter_element_tree(
    element: StructurizrElementModel,
) -> Iterable[StructurizrElementModel]:
    """Yield an element and every element nested beneath it."""
    yield element
    for child in element.children:
        yield from iter_element_tree(child)

    for child in element.infrastructure_nodes:
        yield from iter_element_tree(child)

    for instance in element.software_system_instances:
        yield from iter_element_tree(instance)

    for instance in element.container_instances:
        yield from iter_element_tree(instance)

from __future__ import annotations

from typing import Any

from c4.contrib.structurizr.renderer.models import (
    StructurizrElementModel,
    StructurizrRelationshipModel,
    StructurizrViewModel,
)
from c4.contrib.structurizr.renderer.styles import (
    StructurizrStyleModel,
    StructurizrStylesModel,
)


def element_to_dict(element: StructurizrElementModel) -> dict[str, Any]:
    """Return the Structurizr JSON representation of an element, recursively."""
    result: dict[str, Any] = {
        "id": element.id,
        "name": element.name,
        "description": element.description,
        "technology": element.technology,
        "tags": ",".join(element.tags),
        "url": element.url,
        "properties": dict(element.properties),
        "relationships": [
            relationship_to_dict(relationship)
            for relationship in element.relationships
        ],
        "environment": element.environment,
    }

    if element.element_type == "softwareSystem":
        result["containers"] = [
            element_to_dict(child) for child in element.children
        ]
    elif element.element_type == "container":
        result["components"] = [
            element_to_dict(child) for child in element.children
        ]
    elif element.element_type == "deploymentNode":
        result["children"] = [
            element_to_dict(child) for child in element.children
        ]
        result["infrastructureNodes"] = [
            element_to_dict(child) for child in element.infrastructure_nodes
        ]
        result["softwareSystemInstances"] = [
            element_to_dict(instance)
            for instance in element.software_system_instances
        ]
        result["containerInstances"] = [
            element_to_dict(instance)
            for instance in element.container_instances
        ]
    elif element.element_type == "softwareSystemInstance":
        result["softwareSystemId"] = element.instance_of_id
    elif element.element_type == "containerInstance":
        result["containerId"] = element.instance_of_id

    return result


def relationship_to_dict(
    relationship: StructurizrRelationshipModel,
) -> dict[str, Any]:
    """Return the Structurizr JSON representation of a relationship."""
    return {
        "id": relationship.id,
        "sourceId": relationship.source_id,
        "destinationId": relationship.destination_id,
        "description": relationship.description,
        "technology": relationship.technology,
        "tags": list(relationship.tags),
        "url": relationship.url,
        "properties": dict(relationship.properties),
    }


def styles_to_dict(
    styles: StructurizrStylesModel,
) -> dict[str, Any] | None:
    """Return the Structurizr JSON styles block, or `None` if empty."""
    if styles.is_empty:
        return None

    return {
        "elements": [_style_to_dict(style) for style in styles.elements],
        "relationships": [
            _style_to_dict(style) for style in styles.relationships
        ],
    }


def _style_to_dict(style: StructurizrStyleModel) -> dict[str, Any]:
    """Return the Structurizr JSON representation of one style declaration."""
    return {
        "tag": style.tag,
        **dict(style.properties),
    }


_VIEW_COLLECTIONS_BY_TYPE = {
    "systemLandscape": "systemLandscapeViews",
    "systemContext": "systemContextViews",
    "container": "containerViews",
    "component": "componentViews",
    "dynamic": "dynamicViews",
    "deployment": "deploymentViews",
}


def views_to_dict(views: list[StructurizrViewModel]) -> dict[str, Any]:
    """Group views by type into the Structurizr JSON views collections."""
    result: dict[str, Any] = {
        collection_name: []
        for collection_name in _VIEW_COLLECTIONS_BY_TYPE.values()
    }

    for view in views:
        result[_VIEW_COLLECTIONS_BY_TYPE[view.type]].append(_view_to_dict(view))

    return result


def _view_to_dict(view: StructurizrViewModel) -> dict[str, Any]:
    """Return the Structurizr JSON representation of one view."""
    automatic_layout = None
    if view.auto_layout is not None:
        automatic_layout = {
            "implementation": view.auto_layout.implementation,
            "rankDirection": view.auto_layout.rank_direction,
            "rankSeparation": view.auto_layout.rank_separation,
            "nodeSeparation": view.auto_layout.node_separation,
        }

    result: dict[str, Any] = {
        "key": view.key,
        "title": view.title,
        "description": view.description,
        "tags": ",".join(view.tags),
        "automaticLayout": automatic_layout,
        "include": list(view.include),
        "exclude": list(view.exclude),
        "animation": [list(step) for step in view.animation],
        "elements": [],
        "relationships": [
            {
                **relationship_to_dict(relationship),
                "order": str(index),
            }
            for index, relationship in enumerate(view.relationships, start=1)
        ],
        "properties": dict(view.properties),
    }

    if view.type in {
        "systemContext",
        "container",
        "deployment",
    }:
        result["softwareSystemId"] = view.scope_id
    elif view.type == "component":
        result["containerId"] = view.scope_id
    elif view.type == "dynamic":
        result["elementId"] = view.scope_id

    if view.type == "deployment":
        result["environment"] = view.environment

    return result

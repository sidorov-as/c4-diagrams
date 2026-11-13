from __future__ import annotations

import re
from collections.abc import Callable, Iterable
from typing import Any

from c4.contrib.structurizr.renderer.errors import (
    relationship_missing_endpoint_error,
)
from c4.contrib.structurizr.renderer.identifiers import StructurizrIdentifier
from c4.contrib.structurizr.renderer.models import (
    StructurizrElementModel,
    StructurizrRelationshipModel,
    StructurizrViewModel,
    StructurizrWorkspaceModel,
    iter_workspace_elements,
)
from c4.contrib.structurizr.renderer.options import AutoLayout
from c4.contrib.structurizr.renderer.serialize import (
    element_to_dict,
    relationship_to_dict,
    styles_to_dict,
    views_to_dict,
)
from c4.contrib.structurizr.renderer.styles import (
    STYLE_PRESET_MODELS,
    StructurizrStyleModel,
    StructurizrStylePreset,
    StructurizrStylesModel,
)
from c4.contrib.structurizr.workspace import (
    ContainerInstance,
    DeploymentNode,
    DynamicStep,
    DynamicView,
    InfrastructureNode,
    Relationship,
    SoftwareSystemInstance,
    StructurizrElement,
    Workspace,
)

_VIEW_KEY_CHAR_RE = re.compile(r"[^a-zA-Z0-9_]+")
_REPEATED_UNDERSCORE_RE = re.compile(r"_+")

_SEMANTIC_TAGS_BY_KIND = {
    "person": ("Person",),
    "softwareSystem": ("Software System",),
    "container": ("Container",),
    "component": ("Component",),
    "deploymentNode": ("Boundary",),
    "infrastructureNode": ("Boundary",),
}


class StructurizrWorkspaceBuilder:
    """Builder for the private Structurizr workspace model."""

    def __init__(self, name: str = "Workspace") -> None:
        """Initialize a workspace-model builder.

        Args:
            name: Title for the workspace being built.
        """
        self._workspace = StructurizrWorkspaceModel(name=name)
        self._elements: dict[str, StructurizrElementModel] = {}

    @property
    def workspace(self) -> StructurizrWorkspaceModel:
        """Return the mutable workspace model being built."""
        return self._workspace

    def build(
        self,
        *,
        workspace: Workspace,
        identifiers: dict[str, StructurizrIdentifier],
        auto_layout: AutoLayout | None,
        style_preset: StructurizrStylePreset | None,
        next_relationship_id: Callable[[], str],
    ) -> StructurizrWorkspaceBuilder:
        """Populate this builder's workspace model from a DSL workspace."""
        self._workspace.description = workspace.description
        self._workspace.properties.update(workspace.properties)
        self._add_elements(workspace, identifiers)
        self._add_deployment_environments(workspace, identifiers)

        relationships = self._add_relationships(
            workspace, identifiers, next_relationship_id
        )

        self._add_views(
            workspace, identifiers, auto_layout, next_relationship_id
        )

        self._workspace.theme = workspace.theme
        _add_styles(
            self._workspace,
            style_preset=style_preset,
            element_styles=workspace.element_styles,
            relationship_styles=workspace.relationship_styles,
            relationships=relationships,
        )

        return self

    def _add_elements(
        self,
        workspace: Workspace,
        identifiers: dict[str, StructurizrIdentifier],
    ) -> None:
        """Add people, software systems, containers, and components."""
        elements = self._elements

        def add(
            element: StructurizrElement, element_type: str
        ) -> StructurizrElementModel:
            model = _element_model(element, identifiers, element_type)
            elements[element.alias] = model
            return model

        for person in workspace.model.people:
            self._workspace.people.append(add(person, "person"))

        for system in workspace.model.software_systems:
            self._workspace.software_systems.append(
                add(system, "softwareSystem")
            )

        for container in workspace.model.containers:
            parent = container.parent
            if parent is None or parent.alias not in elements:
                continue
            elements[parent.alias].children.append(add(container, "container"))

        for component in workspace.model.components:
            parent = component.parent
            if parent is None or parent.alias not in elements:
                continue
            elements[parent.alias].children.append(add(component, "component"))

    def _add_deployment_environments(
        self,
        workspace: Workspace,
        identifiers: dict[str, StructurizrIdentifier],
    ) -> None:
        """Add deployment environments and their root deployment nodes."""
        for environment in workspace.model.deployment_environments:
            if not environment.nodes:
                continue

            nodes: list[StructurizrElementModel] = []
            for node in environment.nodes:
                nodes.append(
                    _deployment_node_model(
                        node=node,
                        environment=environment.name,
                        identifiers=identifiers,
                        elements_by_alias=self._elements,
                    )
                )

            self._workspace.deployment_environments.append((
                environment.name,
                nodes,
            ))
            self._workspace.deployment_nodes.extend(nodes)

    def _add_relationships(
        self,
        workspace: Workspace,
        identifiers: dict[str, StructurizrIdentifier],
        next_relationship_id: Callable[[], str],
    ) -> list[StructurizrRelationshipModel]:
        """Add model-level relationships and attach them to their sources."""
        relationships = [
            _relationship_model(
                relationship,
                relationship_id=next_relationship_id(),
                identifiers=identifiers,
                elements_by_alias=self._elements,
            )
            for relationship in workspace.model.relationships
        ]

        self._workspace.relationships.extend(relationships)
        _attach_relationships_to_sources(relationships, self._elements)
        return relationships

    def _add_views(
        self,
        workspace: Workspace,
        identifiers: dict[str, StructurizrIdentifier],
        auto_layout: AutoLayout | None,
        next_relationship_id: Callable[[], str],
    ) -> None:
        """Add declared views, including dynamic-view relationship steps."""
        for view in workspace.views:
            scope = getattr(view, "scope_target", None)
            scope_id = (
                identifiers[scope.alias].identifier
                if scope is not None and scope.alias in identifiers
                else None
            )
            model = StructurizrViewModel(
                key=view.key or generated_view_key(view),
                type=view.type,
                title=view.title,
                description=view.description,
                tags=view.tags,
                scope_id=scope_id,
                environment=view.environment,
                auto_layout=view.auto_layout or auto_layout,
                include=view.include_selectors,
                exclude=view.exclude_selectors,
                animation=view.animation,
                properties=dict(view.properties),
            )

            if isinstance(view, DynamicView):
                model.relationships = _dynamic_step_models(
                    render_items=view.steps,
                    identifiers=identifiers,
                    elements_by_alias=self._elements,
                    next_relationship_id=next_relationship_id,
                )
            self._workspace.views.append(model)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation of the workspace model."""
        result: dict[str, Any] = {
            "name": self._workspace.name,
            "description": self._workspace.description,
            "model": {
                "people": [
                    element_to_dict(element)
                    for element in self._workspace.people
                ],
                "softwareSystems": [
                    element_to_dict(element)
                    for element in self._workspace.software_systems
                ],
                "deploymentNodes": [
                    element_to_dict(element)
                    for element in self._workspace.deployment_nodes
                ],
                "relationships": [
                    relationship_to_dict(relationship)
                    for relationship in self._workspace.relationships
                ],
            },
            "views": views_to_dict(self._workspace.views),
            "properties": dict(self._workspace.properties),
        }

        views = result["views"]
        configuration: dict[str, Any] = {}
        if self._workspace.theme is not None:
            configuration["themes"] = [{"url": self._workspace.theme}]

        styles = styles_to_dict(self._workspace.styles)
        if styles is not None:
            configuration["styles"] = styles

        views["configuration"] = configuration

        return result


def _add_styles(
    workspace: StructurizrWorkspaceModel,
    *,
    style_preset: StructurizrStylePreset | None,
    element_styles: Iterable[StructurizrStyleModel] = (),
    relationship_styles: Iterable[StructurizrStyleModel] = (),
    relationships: Iterable[StructurizrRelationshipModel] = (),
) -> None:
    """Combine preset, workspace-level, and per-tag override styles."""
    preset_styles = (
        STYLE_PRESET_MODELS[style_preset]
        if style_preset is not None
        else StructurizrStylesModel()
    )

    override_styles = [
        StructurizrStyleModel(tag, element.style)
        for element in iter_workspace_elements(workspace)
        for tag in element.tags
        if tag.startswith("c4diagrams_style_") and element.style
    ]

    relationship_override_styles = [
        StructurizrStyleModel(tag, relationship.style)
        for relationship in relationships
        for tag in relationship.tags
        if tag.startswith("c4diagrams_style_") and relationship.style
    ]

    workspace.styles = StructurizrStylesModel(
        elements=(
            *preset_styles.elements,
            *tuple(element_styles),
            *override_styles,
        ),
        relationships=(
            *preset_styles.relationships,
            *tuple(relationship_styles),
            *relationship_override_styles,
        ),
    )


def _deployment_node_model(
    *,
    node: DeploymentNode,
    environment: str,
    identifiers: dict[str, StructurizrIdentifier],
    elements_by_alias: dict[str, StructurizrElementModel],
) -> StructurizrElementModel:
    """Build a deployment node model, recursing into its nested topology."""
    node_environment = node.environment or environment
    element_type = (
        "infrastructureNode"
        if isinstance(node, InfrastructureNode)
        else "deploymentNode"
    )
    model = _element_model(node, identifiers, element_type)
    model.environment = node_environment

    for child_node in node.deployment_nodes:
        model.children.append(
            _deployment_node_model(
                node=child_node,
                environment=node_environment,
                identifiers=identifiers,
                elements_by_alias=elements_by_alias,
            )
        )
    for infrastructure_node in node.infrastructure_nodes:
        model.infrastructure_nodes.append(
            _deployment_node_model(
                node=infrastructure_node,
                environment=node_environment,
                identifiers=identifiers,
                elements_by_alias=elements_by_alias,
            )
        )
    for instance_element in node.software_system_instances:
        instance = _instance_model(
            instance_element,
            identifiers=identifiers,
            element_type="softwareSystemInstance",
            environment=node_environment,
        )
        model.software_system_instances.append(instance)
        elements_by_alias[instance_element.alias] = instance
    for container_instance_element in node.container_instances:
        instance = _instance_model(
            container_instance_element,
            identifiers=identifiers,
            element_type="containerInstance",
            environment=node_environment,
        )
        model.container_instances.append(instance)
        elements_by_alias[container_instance_element.alias] = instance

    return model


def _instance_model(
    element: SoftwareSystemInstance | ContainerInstance,
    *,
    identifiers: dict[str, StructurizrIdentifier],
    element_type: str,
    environment: str,
) -> StructurizrElementModel:
    """Build a deployment instance model referencing its target element."""
    target = getattr(element, "model_element", None)
    if target is None:
        raise ValueError("Deployment instance is missing its model target")

    return StructurizrElementModel(
        id=identifiers[element.alias].identifier,
        name=element.name,
        element_type=element_type,
        description=element.description,
        technology=element.technology,
        tags=_merge_tags(
            _semantic_tags(target),
            _merge_tags(target.tags, element.tags),
        ),
        style=element.style_properties,
        url=element.url,
        properties=dict(element.properties),
        instance_of_id=identifiers[target.alias].identifier,
        environment=getattr(element, "environment", None) or environment,
    )


def _dynamic_step_models(
    *,
    render_items: Iterable[DynamicStep],
    identifiers: dict[str, StructurizrIdentifier],
    elements_by_alias: dict[str, StructurizrElementModel],
    next_relationship_id: Callable[[], str],
) -> list[StructurizrRelationshipModel]:
    """Build relationship models for a dynamic view's ordered steps."""
    relationships: list[StructurizrRelationshipModel] = []

    for item in render_items:
        if (
            hasattr(item, "source")
            and hasattr(item, "destination")
            and not hasattr(item, "relationship")
        ):
            # Every DynamicStep declares a `relationship` field (even when
            # `None`), so `not hasattr(item, "relationship")` never holds for
            # DynamicStep input and this branch is currently unreachable.
            # Kept as-is (pure mechanical retyping, no behavior change);
            # worth a follow-up to simplify separately.
            relationships.append(
                _relationship_model(
                    item,  # type: ignore[arg-type]
                    relationship_id=next_relationship_id(),
                    identifiers=identifiers,
                    elements_by_alias=elements_by_alias,
                )
            )
            continue

        if not isinstance(item, DynamicStep):
            continue

        dynamic_step = item
        source = dynamic_step.source
        destination = dynamic_step.destination
        relationship = getattr(dynamic_step, "relationship", None)
        if relationship is not None:
            model = _relationship_model(
                relationship,
                relationship_id=next_relationship_id(),
                identifiers=identifiers,
                elements_by_alias=elements_by_alias,
            )
            model.description = dynamic_step.description
            model.technology = dynamic_step.technology
            model.tags = _merge_tags(("Relationship",), dynamic_step.tags)
            model.url = dynamic_step.url
            model.properties = dict(dynamic_step.properties or {})
            model.style = dict(dynamic_step.style or {})
            _apply_relationship_style_tag(model)
            relationships.append(model)
            continue

        _ensure_relationship_endpoint(
            source_alias=source.alias,
            destination_alias=destination.alias,
            endpoint_alias=source.alias,
            elements_by_alias=elements_by_alias,
            missing_side="source",
        )
        _ensure_relationship_endpoint(
            source_alias=source.alias,
            destination_alias=destination.alias,
            endpoint_alias=destination.alias,
            elements_by_alias=elements_by_alias,
            missing_side="destination",
        )
        model = StructurizrRelationshipModel(
            id=next_relationship_id(),
            source_id=identifiers[source.alias].identifier,
            destination_id=identifiers[destination.alias].identifier,
            description=dynamic_step.description,
            technology=dynamic_step.technology,
            tags=_merge_tags(("Relationship",), dynamic_step.tags),
            style=dict(dynamic_step.style or {}),
            url=dynamic_step.url,
            properties=dict(dynamic_step.properties or {}),
        )
        _apply_relationship_style_tag(model)
        relationships.append(model)

    return relationships


def generated_view_key(diagram: Any) -> str:
    """Return the deterministic default Structurizr view key for a view."""
    source = f"{diagram.type}_{diagram.title or 'Workspace'}"
    key = _VIEW_KEY_CHAR_RE.sub("_", source.strip())
    key = _REPEATED_UNDERSCORE_RE.sub("_", key).strip("_")
    return key or diagram.type


def _element_model(
    element: StructurizrElement,
    identifiers: dict[str, StructurizrIdentifier],
    element_type: str,
) -> StructurizrElementModel:
    """Build an element model, merging semantic and style-override tags."""
    semantic_tags = _semantic_tags(element)
    tags = _merge_tags(semantic_tags, element.tags)
    if element.style_properties:
        tags = _merge_tags(
            tags,
            (_style_override_tag(identifiers[element.alias].identifier, tags),),
        )
    return StructurizrElementModel(
        id=identifiers[element.alias].identifier,
        name=element.name,
        element_type=element_type,
        description=element.description,
        technology=element.technology,
        tags=tags,
        style=element.style_properties,
        url=element.url,
        properties=dict(element.properties),
    )


def _relationship_model(
    relationship: Relationship,
    *,
    relationship_id: str,
    identifiers: dict[str, StructurizrIdentifier],
    elements_by_alias: dict[str, StructurizrElementModel],
    relationship_ids_by_alias: dict[str, str] | None = None,
) -> StructurizrRelationshipModel:
    """Build a relationship model, validating both endpoints are known."""
    source, destination = relationship.source, relationship.destination

    _ensure_relationship_endpoint(
        source_alias=source.alias,
        destination_alias=destination.alias,
        endpoint_alias=source.alias,
        elements_by_alias=elements_by_alias,
        missing_side="source",
    )
    _ensure_relationship_endpoint(
        source_alias=source.alias,
        destination_alias=destination.alias,
        endpoint_alias=destination.alias,
        elements_by_alias=elements_by_alias,
        missing_side="destination",
    )

    relationship_ids_by_alias = relationship_ids_by_alias or {}
    model = StructurizrRelationshipModel(
        id=relationship_id,
        source_id=relationship_ids_by_alias.get(
            source.alias,
            identifiers[source.alias].identifier,
        ),
        destination_id=relationship_ids_by_alias.get(
            destination.alias,
            identifiers[destination.alias].identifier,
        ),
        description=relationship.description,
        technology=relationship.technology,
        tags=_merge_tags(("Relationship",), relationship.tags),
        style=relationship.style or {},
        url=relationship.url,
        properties=dict(relationship.properties or {}),
    )
    _apply_relationship_style_tag(model)
    return model


def _ensure_relationship_endpoint(
    *,
    source_alias: str,
    destination_alias: str,
    endpoint_alias: str,
    elements_by_alias: dict[str, StructurizrElementModel],
    missing_side: str,
) -> None:
    """Raise if a relationship endpoint was never emitted into the model."""
    if endpoint_alias in elements_by_alias:
        return

    raise relationship_missing_endpoint_error(
        source_alias=source_alias,
        destination_alias=destination_alias,
        missing_side=missing_side,
        missing_alias=endpoint_alias,
    )


def _semantic_tags(element: StructurizrElement) -> tuple[str, ...]:
    """Return the built-in Structurizr tags implied by an element's kind."""
    return _SEMANTIC_TAGS_BY_KIND.get(element.kind, ())


def _merge_tags(
    generated_tags: Iterable[str],
    user_tags: Iterable[str],
) -> tuple[str, ...]:
    """Combine two tag sequences, keeping first occurrence order, no dupes."""
    result: list[str] = []
    seen: set[str] = set()
    for tag in (*tuple(generated_tags), *tuple(user_tags)):
        if tag not in seen:
            result.append(tag)
            seen.add(tag)
    return tuple(result)


def _style_override_tag(identifier: str, existing_tags: tuple[str, ...]) -> str:
    """Return a unique tag name for a local element/relationship style."""
    base_tag = f"c4diagrams_style_{identifier}"
    if base_tag not in existing_tags:
        return base_tag

    counter = 2
    while True:
        candidate = f"{base_tag}_{counter}"
        if candidate not in existing_tags:
            return candidate
        counter += 1


def _apply_relationship_style_tag(
    relationship: StructurizrRelationshipModel,
) -> None:
    """Tag a relationship with its style-override tag, if it has a style."""
    if not relationship.style:
        return
    relationship.tags = _merge_tags(
        relationship.tags,
        (_style_override_tag(relationship.id, relationship.tags),),
    )


def _attach_relationships_to_sources(
    relationships: list[StructurizrRelationshipModel],
    elements_by_alias: dict[str, StructurizrElementModel],
) -> None:
    """Attach each relationship to its source element's model."""
    elements_by_id = {
        element.id: element for element in elements_by_alias.values()
    }
    for relationship in relationships:
        source = elements_by_id.get(relationship.source_id)
        if source is not None:
            source.relationships.append(relationship)

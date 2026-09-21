from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)

from c4.contrib.structurizr import Workspace
from c4.converters.json.mixins import JSONSchemaMixin


class _StructurizrSchema(JSONSchemaMixin, BaseModel):
    """Strict base class for the Structurizr workspace JSON contract."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class StructurizrSelectorSchema(_StructurizrSchema):
    """A named element selector, to be resolved by workspace conversion."""

    id: str


class StructurizrStyleSchema(_StructurizrSchema):
    """A style declaration for an element tag or relationship tag."""

    target: str
    properties: dict[str, Any] = Field(default_factory=dict)


class StructurizrStylesSchema(_StructurizrSchema):
    """Workspace style declarations."""

    elements: list[StructurizrStyleSchema] = Field(default_factory=list)
    relationships: list[StructurizrStyleSchema] = Field(default_factory=list)


class StructurizrElementSchema(_StructurizrSchema):
    """Metadata shared by model elements with stable JSON references."""

    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    description: str | None = None
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    style: dict[str, Any] | None = None


class StructurizrPersonSchema(StructurizrElementSchema):
    """A root person in the workspace model."""


class StructurizrComponentSchema(StructurizrElementSchema):
    """A component owned by its containing container."""

    technology: str | None = None


class StructurizrContainerSchema(StructurizrElementSchema):
    """A container owned by its containing software system."""

    technology: str | None = None
    components: list[StructurizrComponentSchema] = Field(default_factory=list)


class StructurizrSoftwareSystemSchema(StructurizrElementSchema):
    """A root software system and its explicitly owned containers."""

    containers: list[StructurizrContainerSchema] = Field(default_factory=list)


class _StructurizrInstanceSchema(_StructurizrSchema):
    """Metadata for a separately identified deployment instance."""

    id: str = Field(min_length=1)
    description: str | None = None
    tags: list[str] | None = None
    url: str | None = None
    properties: dict[str, Any] | None = None
    style: dict[str, Any] | None = None


class StructurizrSoftwareSystemInstanceSchema(_StructurizrInstanceSchema):
    """A software-system instance and the model element it represents."""

    software_system: str = Field(min_length=1)


class StructurizrContainerInstanceSchema(_StructurizrInstanceSchema):
    """A container instance and the model element it represents."""

    container: str = Field(min_length=1)


class StructurizrInfrastructureNodeSchema(StructurizrElementSchema):
    """Infrastructure nested below a deployment or infrastructure node."""

    technology: str | None = None
    deployment_nodes: list[StructurizrDeploymentNodeSchema] = Field(
        default_factory=list
    )
    infrastructure_nodes: list[StructurizrInfrastructureNodeSchema] = Field(
        default_factory=list
    )


class StructurizrDeploymentNodeSchema(StructurizrElementSchema):
    """A deployment node with explicitly nested nodes and instances."""

    technology: str | None = None
    deployment_nodes: list[StructurizrDeploymentNodeSchema] = Field(
        default_factory=list
    )
    infrastructure_nodes: list[StructurizrInfrastructureNodeSchema] = Field(
        default_factory=list
    )
    software_system_instances: list[StructurizrSoftwareSystemInstanceSchema] = (
        Field(default_factory=list)
    )
    container_instances: list[StructurizrContainerInstanceSchema] = Field(
        default_factory=list
    )


class StructurizrDeploymentEnvironmentSchema(_StructurizrSchema):
    """A named deployment environment containing its root deployment nodes."""

    name: str = Field(min_length=1)
    deployment_nodes: list[StructurizrDeploymentNodeSchema] = Field(
        default_factory=list
    )


class StructurizrDeploymentSchema(_StructurizrSchema):
    """Deployment environments and their explicitly owned node trees."""

    environments: list[StructurizrDeploymentEnvironmentSchema] = Field(
        default_factory=list
    )


class StructurizrRelationshipSchema(_StructurizrSchema):
    """A model-level relationship using c4-diagrams ``from``/``to`` spelling."""

    from_: str = Field(alias="from")
    to: str
    description: str | None = None
    technology: str | None = None
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    style: dict[str, Any] | None = None


class StructurizrModelSchema(_StructurizrSchema):
    """The workspace model inventory.

    Ownership is encoded structurally: containers belong to systems, components
    belong to containers, and deployment content belongs to environments/nodes.
    """

    people: list[StructurizrPersonSchema] = Field(default_factory=list)
    software_systems: list[StructurizrSoftwareSystemSchema] = Field(
        default_factory=list
    )
    relationships: list[StructurizrRelationshipSchema] = Field(
        default_factory=list
    )
    deployment: StructurizrDeploymentSchema | None = None


class StructurizrViewSchema(_StructurizrSchema):
    """Base shape for a declared Structurizr view."""

    type: str
    key: str | None = None
    title: str | None = None
    description: str | None = None
    include: list[str | StructurizrSelectorSchema] = Field(default_factory=list)
    exclude: list[str | StructurizrSelectorSchema] = Field(default_factory=list)
    animation: list[list[str | StructurizrSelectorSchema]] = Field(
        default_factory=list
    )
    tags: list[str] = Field(default_factory=list)
    properties: dict[str, Any] = Field(default_factory=dict)
    auto_layout: StructurizrAutoLayoutSchema | None = None


class StructurizrSystemLandscapeViewSchema(StructurizrViewSchema):
    type: Literal["system_landscape"]


class _ScopedViewSchema(StructurizrViewSchema):
    scope: str = Field(min_length=1)


class StructurizrSystemContextViewSchema(_ScopedViewSchema):
    type: Literal["system_context"]


class StructurizrContainerViewSchema(_ScopedViewSchema):
    type: Literal["container"]


class StructurizrComponentViewSchema(_ScopedViewSchema):
    type: Literal["component"]


class StructurizrDynamicStepSchema(_StructurizrSchema):
    """A view-local ordered interaction; it is not a model relationship."""

    from_: str = Field(alias="from", min_length=1)
    to: str = Field(min_length=1)
    description: str | None = Field(default=None, min_length=1)
    technology: str | None = None
    tags: list[str] = Field(default_factory=list)
    url: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    style: dict[str, Any] | None = None


class StructurizrDynamicViewSchema(StructurizrViewSchema):
    type: Literal["dynamic"]
    scope: str | None = None
    steps: list[StructurizrDynamicStepSchema] = Field(default_factory=list)


class StructurizrDeploymentViewSchema(StructurizrViewSchema):
    type: Literal["deployment"]
    scope: str | None = None
    environment: str = Field(min_length=1)


class StructurizrViewsSchema(_StructurizrSchema):
    """Declared Structurizr views in authoring order."""

    items: list[
        Annotated[
            StructurizrSystemLandscapeViewSchema
            | StructurizrSystemContextViewSchema
            | StructurizrContainerViewSchema
            | StructurizrComponentViewSchema
            | StructurizrDynamicViewSchema
            | StructurizrDeploymentViewSchema,
            Field(discriminator="type"),
        ]
    ] = Field(default_factory=list)


_DeploymentNodeSchema = (
    StructurizrDeploymentNodeSchema | StructurizrInfrastructureNodeSchema
)


def _deployment_nodes_with_paths(
    node: _DeploymentNodeSchema,
    path: str,
) -> list[tuple[_DeploymentNodeSchema, str]]:
    result = [(node, path)]
    for index, deployment_node in enumerate(node.deployment_nodes):
        result.extend(
            _deployment_nodes_with_paths(
                deployment_node,
                f"{path}->deployment_nodes[{index}]",
            )
        )

    for index, infrastructure_node in enumerate(node.infrastructure_nodes):
        result.extend(
            _deployment_nodes_with_paths(
                infrastructure_node,
                f"{path}->infrastructure_nodes[{index}]",
            )
        )

    return result


def _element_registry(model: StructurizrModelSchema) -> dict[str, str]:
    registry: dict[str, str] = {}

    def add(
        element: StructurizrElementSchema,
        element_kind: str,
        path: str,
    ) -> None:
        if element.id in registry:
            raise ValueError(
                f"{path}->id: Duplicate workspace element id: {element.id!r}"
            )
        registry[element.id] = element_kind

    for person_index, person in enumerate(model.people):
        add(person, "person", f"model->people[{person_index}]")

    for system_index, system in enumerate(model.software_systems):
        system_path = f"model->software_systems[{system_index}]"
        add(system, "software system", system_path)

        for container_index, container in enumerate(system.containers):
            container_path = f"{system_path}->containers[{container_index}]"
            add(container, "container", container_path)

            for component_index, component in enumerate(container.components):
                add(
                    component,
                    "component",
                    f"{container_path}->components[{component_index}]",
                )

    deployment = model.deployment or StructurizrDeploymentSchema()
    for environment_index, environment in enumerate(deployment.environments):
        for node_index, node in enumerate(environment.deployment_nodes):
            node_path = (
                "model->deployment->environments"
                f"[{environment_index}]->deployment_nodes[{node_index}]"
            )
            for descendant, descendant_path in _deployment_nodes_with_paths(
                node, node_path
            ):
                kind = (
                    "deployment node"
                    if isinstance(descendant, StructurizrDeploymentNodeSchema)
                    else "infrastructure node"
                )
                add(descendant, kind, descendant_path)

    return registry


def _reference(registry: dict[str, str], value: str, path: str) -> str:
    if value not in registry:
        raise ValueError(f"{path}: Unknown element id {value!r}")

    return registry[value]


def _validate_deployment(
    model: StructurizrModelSchema,
    registry: dict[str, str],
) -> set[str]:
    environments: set[str] = set()
    deployment = model.deployment or StructurizrDeploymentSchema()

    for environment_index, environment in enumerate(deployment.environments):
        environment_path = (
            f"model->deployment->environments[{environment_index}]"
        )
        if environment.name in environments:
            raise ValueError(
                f"{environment_path}->name: Duplicate deployment environment: "
                f"{environment.name!r}"
            )

        if environment.deployment_nodes:
            environments.add(environment.name)

        for node_index, node in enumerate(environment.deployment_nodes):
            node_path = f"{environment_path}->deployment_nodes[{node_index}]"
            for descendant, descendant_path in _deployment_nodes_with_paths(
                node, node_path
            ):
                if isinstance(descendant, StructurizrDeploymentNodeSchema):
                    _register_node_instances(
                        descendant, descendant_path, registry
                    )

    return environments


def _register_node_instances(
    node: StructurizrDeploymentNodeSchema,
    path: str,
    registry: dict[str, str],
) -> None:
    _register_instances(
        [
            (item.id, item.software_system)
            for item in node.software_system_instances
        ],
        registry,
        path=f"{path}->software_system_instances",
        target_kind="software system",
    )
    _register_instances(
        [(item.id, item.container) for item in node.container_instances],
        registry,
        path=f"{path}->container_instances",
        target_kind="container",
    )


def _register_instances(
    instances: list[tuple[str, str]],
    registry: dict[str, str],
    *,
    path: str,
    target_kind: str,
) -> None:
    """Check each (instance id, target id) pair and register the instance."""
    for index, (instance_id, target) in enumerate(instances):
        if registry.get(target) != target_kind:
            raise ValueError(
                f"{path}[{index}]->id: Unknown {target_kind} instance "
                f"reference {target!r}"
            )

        if instance_id in registry:
            raise ValueError(
                f"{path}[{index}]->id: Duplicate element id {instance_id!r}"
            )

        registry[instance_id] = f"{target_kind} instance"


def _validate_views(
    views: StructurizrViewsSchema,
    registry: dict[str, str],
    environments: set[str],
) -> None:
    for view_index, view in enumerate(views.items):
        view_path = f"views->items[{view_index}]"
        for field_name, selectors in (
            ("include", view.include),
            ("exclude", view.exclude),
        ):
            for selector_index, selector in enumerate(selectors):
                if isinstance(selector, StructurizrSelectorSchema):
                    _reference(
                        registry,
                        selector.id,
                        f"{view_path}->{field_name}[{selector_index}]->id",
                    )

        for step_index, animation_step in enumerate(view.animation):
            for selector_index, selector in enumerate(animation_step):
                if isinstance(selector, StructurizrSelectorSchema):
                    _reference(
                        registry,
                        selector.id,
                        f"{view_path}->animation[{step_index}]"
                        f"[{selector_index}]->id",
                    )

        _validate_view_scope(view, registry, environments, view_path)


def _validate_view_scope(
    view: StructurizrViewSchema,
    registry: dict[str, str],
    environments: set[str],
    path: str,
) -> None:
    if isinstance(
        view,
        StructurizrSystemContextViewSchema | StructurizrContainerViewSchema,
    ):
        if _reference(registry, view.scope, f"{path}->scope") != (
            "software system"
        ):
            raise ValueError(
                f"{path}->scope: {view.type} view scope must reference a "
                "software system"
            )
    elif isinstance(view, StructurizrComponentViewSchema):
        if (
            _reference(
                registry,
                view.scope,
                f"{path}->scope",
            )
            != "container"
        ):
            raise ValueError(
                f"{path}->scope: component view scope must reference a "
                "container"
            )
    elif isinstance(view, StructurizrDynamicViewSchema):
        _validate_dynamic_view(view, registry, path)
    elif isinstance(view, StructurizrDeploymentViewSchema):
        _validate_deployment_view(view, registry, environments, path)


def _validate_dynamic_view(
    view: StructurizrDynamicViewSchema,
    registry: dict[str, str],
    path: str,
) -> None:
    if view.scope is not None:
        _reference(registry, view.scope, f"{path}->scope")

    for step_index, step in enumerate(view.steps):
        step_path = f"{path}->steps[{step_index}]"
        _reference(registry, step.from_, f"{step_path}->from")
        _reference(registry, step.to, f"{step_path}->to")


def _validate_deployment_view(
    view: StructurizrDeploymentViewSchema,
    registry: dict[str, str],
    environments: set[str],
    path: str,
) -> None:
    if view.environment not in environments:
        raise ValueError(
            f"{path}->environment: Unknown deployment environment "
            f"{view.environment!r}"
        )

    if (
        view.scope is not None
        and _reference(registry, view.scope, f"{path}->scope")
        != "software system"
    ):
        raise ValueError(
            f"{path}->scope: deployment view scope must reference a "
            "software system"
        )


class StructurizrAutoLayoutSchema(_StructurizrSchema):
    """Structurizr automatic-layout settings."""

    rank_direction: Literal[
        "TopBottom", "BottomTop", "LeftRight", "RightLeft"
    ] = "LeftRight"
    implementation: str | None = None
    rank_separation: int | None = Field(None, gt=0)
    node_separation: int | None = Field(None, gt=0)


class StructurizrRenderOptionsSchema(_StructurizrSchema):
    """Reserved Structurizr renderer options for workspace JSON."""

    auto_layout: StructurizrAutoLayoutSchema | None = None
    style_preset: Literal["classic", "new-c4-style"] | None = None


class StructurizrWorkspaceSchema(_StructurizrSchema):
    """A c4-diagrams, backend-specific Structurizr workspace document."""

    backend: Literal["structurizr"] = Field(
        ...,
        description=(
            "Required discriminator for the Structurizr workspace JSON format."
        ),
    )
    name: str = Field(
        "Workspace",
        description=(
            "Workspace name; defaults to the renderer's Workspace fallback."
        ),
    )
    description: str | None = None
    properties: dict[str, Any] = Field(default_factory=dict)
    theme: str | None = None
    styles: StructurizrStylesSchema | None = None
    render_options: StructurizrRenderOptionsSchema | None = None
    model: StructurizrModelSchema
    views: StructurizrViewsSchema

    @model_validator(mode="after")
    def validate_workspace_references(self) -> StructurizrWorkspaceSchema:
        """Reject unresolved references before a workspace is constructed."""
        registry = _element_registry(self.model)
        environments = _validate_deployment(self.model, registry)

        for relationship_index, relationship in enumerate(
            self.model.relationships
        ):
            path = f"model->relationships[{relationship_index}]"
            _reference(registry, relationship.from_, f"{path}->from")
            _reference(registry, relationship.to, f"{path}->to")

        _validate_views(self.views, registry, environments)
        return self

    def to_workspace(self) -> Workspace:
        """Convert this complete workspace document into a Workspace."""
        from c4.contrib.structurizr.converters.json.converter import (
            JSONToStructurizrWorkspaceConverter,
        )

        return JSONToStructurizrWorkspaceConverter(self).convert()

from __future__ import annotations

from c4.contrib.structurizr.renderer.errors import (
    StructurizrRenderingError,
    parent_child_relationship_error,
)
from c4.contrib.structurizr.workspace import (
    ComponentView,
    ContainerView,
    DeploymentEnvironment,
    DeploymentView,
    DynamicView,
    Model,
    Relationship,
    SoftwareSystem,
    StructurizrElement,
    SystemContextView,
    Workspace,
)
from c4.contrib.structurizr.workspace import (
    Container as StructurizrContainer,
)
from c4.contrib.structurizr.workspace.views import _WorkspaceView


def validate_structurizr_workspace(
    workspace: Workspace,
    views: object = None,
) -> None:
    """Validate object-reference ownership and view scopes.

    Aliases are used only to identify the public objects in diagnostics; no
    renderer behaviour depends on alias ownership or view-scope metadata.
    """
    StructurizrWorkspaceValidator(workspace).validate()


class StructurizrWorkspaceValidator:
    """Validate object-reference ownership and view scopes for a workspace."""

    def __init__(self, workspace: Workspace) -> None:
        """Index a workspace's members and non-empty deployment environments."""
        if not isinstance(workspace, Workspace):
            raise StructurizrRenderingError(
                "Structurizr rendering accepts only "
                "c4.contrib.structurizr.Workspace instances."
            )

        self.workspace = workspace
        self.model: Model = workspace.model
        self.members: set[StructurizrElement] = {
            item
            for collection in (
                self.model.people,
                self.model.software_systems,
                self.model.containers,
                self.model.components,
                self.model.deployment_nodes,
                self.model.software_system_instances,
                self.model.container_instances,
            )
            for item in collection
        }

        self.environments: set[DeploymentEnvironment] = {
            environment
            for environment in self.model.deployment_environments
            if environment.nodes
        }

    def validate(self) -> None:
        """Run every workspace-model check, in the same order as before."""
        self._check_ownership()
        self._check_instance_ownership()
        self._check_relationships()
        self._check_environment_membership()
        self._check_views()

    def _check_ownership(self) -> None:
        """Validate that containers and components have the right parent."""
        for container in self.model.containers:
            if not isinstance(container.parent, SoftwareSystem):
                raise StructurizrRenderingError(
                    f'Container "{container.alias}" must reference a '
                    "software system parent."
                )

        for component in self.model.components:
            if not isinstance(component.parent, StructurizrContainer):
                raise StructurizrRenderingError(
                    f'Component "{component.alias}" must reference a '
                    "container parent."
                )

    def _check_instance_ownership(self) -> None:
        """Ensure every deployment instance still targets a local entity."""
        model = self.model
        for instances, targets, expected_type in (
            (
                model.software_system_instances,
                model.software_systems,
                SoftwareSystem,
            ),
            (model.container_instances, model.containers, StructurizrContainer),
        ):
            for instance in instances:
                target: StructurizrElement = instance.model_element
                is_expected_type = isinstance(target, expected_type)

                if (
                    not is_expected_type
                    or target._model is not model
                    or target not in targets
                    or instance.parent_node not in model.deployment_nodes
                ):
                    raise StructurizrRenderingError(
                        f'Deployment instance "{instance.alias}" must '
                        "reference a model element in this workspace."
                    )

    def _check_relationships(self) -> None:
        """Validate every relationship's endpoints and ancestry rules."""
        for relationship in self.model.relationships:
            self._check_relationship_endpoints(relationship)
            self._check_relationship_ancestry(relationship)

    def _check_relationship_endpoints(self, relationship: Relationship) -> None:
        """Ensure both relationship endpoints belong to this workspace."""
        source, destination = relationship.source, relationship.destination
        if source not in self.members or destination not in self.members:
            raise StructurizrRenderingError(
                "Cannot render relationship "
                f'"{source.alias} -> {destination.alias}": '
                "both endpoints must belong to this workspace."
            )

    def _check_relationship_ancestry(self, relationship: Relationship) -> None:
        """Reject relationships between a parent and its own descendant."""
        source, destination = relationship.source, relationship.destination
        if _is_ancestor(source, destination) or _is_ancestor(
            destination, source
        ):
            raise parent_child_relationship_error(
                source_alias=source.alias,
                destination_alias=destination.alias,
                relationship_text=f"{source.alias} -> {destination.alias}",
            )

    def _check_environment_membership(self) -> None:
        """Ensure every deployment node belongs to exactly one environment."""
        node_counts: dict[object, int] = {}
        for environment in self.environments:
            for node in environment.nodes:
                node_counts[node] = node_counts.get(node, 0) + 1

        for counted_node, count in node_counts.items():
            if count != 1:
                identifier = str(getattr(counted_node, "alias", counted_node))
                raise StructurizrRenderingError(
                    f'Deployment node "{identifier}" must belong to exactly '
                    "one environment."
                )

    def _check_views(self) -> None:
        """Validate every declared view's scope and environment reference."""
        for view in self.workspace.views:
            self._check_view(view)

    def _check_view(self, view: _WorkspaceView) -> None:
        """Validate one declared view's scope and environment reference."""
        scope = getattr(view, "scope_target", None)
        expected: tuple[type[object], ...] | None = None
        required = False

        if isinstance(view, (SystemContextView, ContainerView)):
            expected, required = (SoftwareSystem,), True
        elif isinstance(view, ComponentView):
            expected, required = (StructurizrContainer,), True
        elif isinstance(view, DynamicView):
            expected = (SoftwareSystem, StructurizrContainer)

        if required and scope is None:
            raise StructurizrRenderingError(
                f"{view.__class__.__name__} requires a scope reference."
            )

        if scope is not None and (
            scope not in self.members
            or (expected and not isinstance(scope, expected))
        ):
            raise StructurizrRenderingError(
                f"{view.__class__.__name__} has an invalid scope reference."
            )

        if isinstance(view, DeploymentView) and not any(
            item.name == view.environment for item in self.environments
        ):
            raise StructurizrRenderingError(
                "DeploymentView references an unknown deployment environment."
            )


def _is_ancestor(child: object, ancestor: object) -> bool:
    """Return whether `ancestor` is a parent, grandparent, ... of `child`."""
    current = getattr(child, "parent", None)
    while current is not None:
        if current is ancestor:
            return True
        current = getattr(current, "parent", None)

    return False

from __future__ import annotations

import pytest

from c4 import ContainerDiagram
from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import StructurizrRenderer
from c4.contrib.structurizr.renderer.errors import StructurizrRenderingError
from c4.contrib.structurizr.renderer.validation import (
    validate_structurizr_workspace,
)


def test_validation_rejects_non_workspace_targets():
    with pytest.raises(StructurizrRenderingError, match="accepts only"):
        validate_structurizr_workspace(ContainerDiagram("Containers"))


def test_model_rejects_cross_workspace_relationship_endpoints():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer", alias="customer")
    with Workspace("Other") as other:
        with other.model as model:
            payments = model.SoftwareSystem("Payments", alias="payments")
            with pytest.raises(
                ValueError,
                match="Relationship endpoints must belong to this workspace model",
            ):
                customer.uses(payments, "Uses")


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (
            lambda views: views.SystemContextView(None),
            "requires a scope reference",
        ),
        (lambda views: views.ContainerView(None), "requires a scope reference"),
    ],
)
def test_validation_requires_native_scopes_for_scoped_views(factory, message):
    workspace = Workspace("Payments")
    factory(workspace.views)

    with pytest.raises(StructurizrRenderingError, match=message):
        validate_structurizr_workspace(workspace)


def test_validation_rejects_invalid_scope_type():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer")
        workspace.views.ComponentView(customer)

    with pytest.raises(
        StructurizrRenderingError, match="invalid scope reference"
    ):
        validate_structurizr_workspace(workspace)


def test_deployment_view_does_not_create_or_accept_empty_environments():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments")
            model.DeploymentEnvironment("Production")
        workspace.views.DeploymentView(payments, environment="Production")

    assert workspace.model.deployment_environments[0].nodes == []
    with pytest.raises(
        StructurizrRenderingError, match="unknown deployment environment"
    ):
        validate_structurizr_workspace(workspace)


def test_empty_deployment_environments_are_not_rendered():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            model.DeploymentEnvironment("Empty")
            with model.DeploymentEnvironment("Production") as production:
                production.DeploymentNode("Server")

    rendered = StructurizrRenderer().render(workspace)

    assert 'deploymentEnvironment "Production"' in rendered
    assert 'deploymentEnvironment "Empty"' not in rendered


def test_validation_rejects_dangling_deployment_instance_target():
    with Workspace("Other") as other:
        with other.model as other_model:
            foreign_system = other_model.SoftwareSystem("Foreign")

    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments")
            with model.DeploymentEnvironment("Production") as production:
                with production.DeploymentNode("Server") as server:
                    instance = server.SoftwareSystemInstance(payments)
        instance.model_element = foreign_system

    with pytest.raises(
        StructurizrRenderingError,
        match="must reference a model element in this workspace",
    ):
        validate_structurizr_workspace(workspace)


def test_validation_allows_object_reference_scopes_and_deployment_trees():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments")
            api = payments.Container("API")
            worker = payments.Container("Worker")
            api.uses(worker, "Dispatches")
            with model.DeploymentEnvironment("Production") as production:
                with production.DeploymentNode("Kubernetes") as kubernetes:
                    kubernetes.ContainerInstance(api)
        workspace.views.ContainerView(payments)
        workspace.views.ComponentView(api)
        workspace.views.DynamicView(payments)
        workspace.views.DeploymentView(payments, environment="Production")

    validate_structurizr_workspace(workspace)

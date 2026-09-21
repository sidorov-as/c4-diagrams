from __future__ import annotations

from pathlib import Path

import pytest

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import StructurizrRenderer
from c4.contrib.structurizr.renderer.errors import StructurizrRenderingError
from c4.diagrams.core import Diagram


def _workspace_model(workspace: Workspace) -> dict[str, object]:
    return StructurizrRenderer()._build_workspace(workspace).to_dict()


def test_workspace_model_shape_is_derived_from_local_structurizr_schema():
    schema = (
        Path(__file__).parents[4] / "local" / "structurizr.yaml"
    ).read_text()

    for name in (
        "Workspace",
        "Model",
        "Person",
        "SoftwareSystem",
        "Container",
        "Component",
        "DeploymentNode",
        "Views",
    ):
        assert f"    {name}:" in schema


def test_renderer_rejects_diagram_target():
    with pytest.raises(
        StructurizrRenderingError,
        match=r"accepts only c4\.contrib\.structurizr\.Workspace",
    ):
        StructurizrRenderer().render(Diagram("Legacy diagram"))


def test_model_uses_native_collections_and_explicit_parent_references():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer", alias="customer")
            payments = model.SoftwareSystem("Payments", alias="payments")
            api = model.Container("API", alias="api", owner=payments)
            checkout = model.Component("Checkout", alias="checkout", owner=api)
            customer.uses(api, "Uses")
            checkout.uses(api, "Calls parent")

    assert workspace.model.people == [customer]
    assert workspace.model.software_systems == [payments]
    assert workspace.model.containers == [api]
    assert workspace.model.components == [checkout]
    assert api.parent is payments
    assert checkout.parent is api

    with pytest.raises(StructurizrRenderingError, match="checkout -> api"):
        StructurizrRenderer().render(workspace)


def test_model_serializes_native_declaration_order_and_relationship_references():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer", alias="customer")
            orders = model.SoftwareSystem("Orders", alias="orders")
            payments = model.SoftwareSystem("Payments", alias="payments")
            api = payments.Container("API", alias="api")
            database = payments.Container("Database", alias="database")
            customer.uses(api, "Uses")
            api.uses(database, "Reads")
            api.uses(orders, "Publishes")

    result = _workspace_model(workspace)["model"]
    assert [item["id"] for item in result["people"]] == ["customer"]
    assert [item["id"] for item in result["softwareSystems"]] == [
        "orders",
        "payments",
    ]
    assert [
        item["id"] for item in result["softwareSystems"][1]["containers"]
    ] == [
        "api",
        "database",
    ]
    assert [
        (item["sourceId"], item["destinationId"], item["description"])
        for item in result["relationships"]
    ] == [
        ("customer", "api", "Uses"),
        ("api", "database", "Reads"),
        ("api", "orders", "Publishes"),
    ]


def test_typed_views_serialize_object_reference_scopes():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments", alias="payments")
            api = payments.Container("API", alias="api")
            with model.DeploymentEnvironment("Production") as production:
                production.DeploymentNode("AWS", alias="aws")

        workspace.views.SystemLandscapeView(key="landscape")
        workspace.views.SystemContextView(payments, key="context")
        workspace.views.ContainerView(payments, key="containers")
        workspace.views.ComponentView(api, key="components")
        workspace.views.DynamicView(payments, key="flow")
        workspace.views.DeploymentView(
            payments,
            environment="Production",
            key="deployment",
        )

    views = _workspace_model(workspace)["views"]
    assert views["systemLandscapeViews"][0]["key"] == "landscape"
    assert views["systemContextViews"][0]["softwareSystemId"] == "payments"
    assert views["containerViews"][0]["softwareSystemId"] == "payments"
    assert views["componentViews"][0]["containerId"] == "api"
    assert views["dynamicViews"][0]["elementId"] == "payments"
    assert views["deploymentViews"][0]["softwareSystemId"] == "payments"
    assert views["deploymentViews"][0]["environment"] == "Production"


def test_deployment_environments_and_trees_preserve_declaration_order():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments", alias="payments")
            api = payments.Container("API", alias="api")
            with model.DeploymentEnvironment("Staging") as staging:
                staging.DeploymentNode("Edge", alias="edge")
            with model.DeploymentEnvironment("Production") as production:
                with production.DeploymentNode("AWS", alias="aws") as aws:
                    aws.InfrastructureNode("Ingress", alias="ingress")
                    aws.ContainerInstance(api)
                production.DeploymentNode("Backup", alias="backup")

    model = _workspace_model(workspace)["model"]
    assert [item["id"] for item in model["deploymentNodes"]] == [
        "edge",
        "aws",
        "backup",
    ]
    assert [
        item["id"]
        for item in model["deploymentNodes"][1]["infrastructureNodes"]
    ] == ["ingress"]
    assert [
        item["containerId"]
        for item in model["deploymentNodes"][1]["containerInstances"]
    ] == ["api"]


def test_invalid_native_references_report_public_objects():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments", alias="payments")
            model.Container("API", alias="api")

    with pytest.raises(
        StructurizrRenderingError,
        match='Container "api" must reference a software system parent',
    ):
        StructurizrRenderer().render(workspace)


def test_cross_workspace_relationship_is_rejected_by_native_model():
    with Workspace("Source") as source:
        with source.model as model:
            customer = model.Person("Customer", alias="customer")
    with Workspace("Target") as target:
        with target.model as model:
            payments = model.SoftwareSystem("Payments", alias="payments")
            with pytest.raises(
                ValueError,
                match="Relationship endpoints must belong to this workspace model",
            ):
                customer.uses(payments, "Uses")


def test_auto_layout_is_importable_from_contrib_package():
    from c4.contrib.structurizr import AutoLayout
    from c4.contrib.structurizr.renderer import AutoLayout as RendererAutoLayout

    assert AutoLayout is RendererAutoLayout

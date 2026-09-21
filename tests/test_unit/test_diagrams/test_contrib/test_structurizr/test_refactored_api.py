from __future__ import annotations

import pytest

from c4.contrib.structurizr import Rel, Workspace
from c4.contrib.structurizr.renderer import AutoLayout


def test_model_and_views_are_persistent_native_facades():
    with Workspace("Payments") as workspace:
        assert workspace.model is workspace.model
        assert workspace.views is workspace.views
        with workspace.model as model:
            customer = model.Person("Customer", tags=["External", "External"])
            payments = model.SoftwareSystem("Payments")
            api = model.Container("API", owner=payments)
            component = api.Component("Checkout")

    assert customer.tags == ("External",)
    assert api.parent is payments
    assert component.parent is api
    assert not hasattr(customer, "core")


def test_dynamic_relationships_are_view_local_without_context_switching():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer")
            payments = model.SoftwareSystem("Payments")
            flow = workspace.views.DynamicView(payments, key="flow")
            flow.step(customer, payments, "Calls", technology="HTTPS")
    assert workspace.model.relationships == []
    assert [(step.description, step.technology) for step in flow.steps] == [
        ("Calls", "HTTPS")
    ]


def test_views_store_object_reference_scopes_and_configuration():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments")
            api = payments.Container("API")

        with workspace.views.ContainerView(
            payments,
            key="containers",
            auto_layout=AutoLayout("TopBottom"),
        ) as view:
            view.include(api)
            view.exclude("element.tag==Legacy")

    assert view.scope_target is payments
    assert view.auto_layout == AutoLayout("TopBottom")
    assert view.include_selectors == ("api",)
    assert view.exclude_selectors == ("element.tag==Legacy",)


@pytest.mark.parametrize(
    ("factory", "scope_name", "extra"),
    [
        ("SystemLandscapeView", None, {}),
        ("SystemContextView", "system", {}),
        ("ContainerView", "system", {}),
        ("ComponentView", "container", {}),
        ("DynamicView", "system", {}),
        ("DeploymentView", "system", {"environment": "Production"}),
    ],
)
def test_every_view_factory_persists_typed_metadata(factory, scope_name, extra):
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            system = model.SoftwareSystem("Payments")
            container = system.Container("API")

        scope = {"system": system, "container": container}.get(scope_name)
        metadata = {
            "title": "Architecture",
            "key": "architecture",
            "description": "Architecture notes",
            "include": system,
            "exclude": "element.tag==Legacy",
            "tags": ["Documented"],
            "properties": {"owner": "platform"},
            "auto_layout": AutoLayout("TopBottom"),
            "animation": [system],
        }
        create = getattr(workspace.views, factory)
        if scope is None:
            view = create(**metadata, **extra)
        else:
            view = create(scope, **metadata, **extra)

    assert view.scope_target is scope
    assert view.title == "Architecture"
    assert view.key == "architecture"
    assert view.description == "Architecture notes"
    assert view.include_selectors == (system.alias,)
    assert view.exclude_selectors == ("element.tag==Legacy",)
    assert view.tags == ("Documented",)
    assert view.properties == {"owner": "platform"}
    assert view.auto_layout == AutoLayout("TopBottom")
    assert view.animation == ((system.alias,),)
    assert view.environment == extra.get("environment")


@pytest.mark.parametrize(
    ("factory", "scope_name", "extra"),
    [
        ("SystemContextView", "system", {}),
        ("ContainerView", "system", {}),
        ("ComponentView", "container", {}),
        ("DynamicView", "system", {}),
        ("DeploymentView", "system", {"environment": "Production"}),
    ],
)
def test_scoped_view_factories_reject_foreign_model_scopes(
    factory, scope_name, extra
):
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            system = model.SoftwareSystem("Payments")
            container = system.Container("API")

    with Workspace("Other") as other:
        foreign = other.model.SoftwareSystem("Other")
        if scope_name == "container":
            foreign = foreign.Container("API")

    create = getattr(workspace.views, factory)
    with pytest.raises(ValueError, match="must belong to this workspace model"):
        create(foreign, **extra)


def test_view_factories_reject_alias_scopes():
    with Workspace("Payments") as workspace:
        with pytest.raises(TypeError, match="model objects, not aliases"):
            workspace.views.SystemContextView("payments")  # type: ignore[arg-type]


def test_workspace_context_does_not_install_a_global_authoring_sink():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer")
            payments = model.SoftwareSystem("Payments")

    with pytest.raises(ValueError, match="must belong to this workspace model"):
        customer >> Rel("Leaked") >> Workspace("Other").model.Person("Other")


def test_relationship_expressions_create_complete_relationships():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer")
            payments = model.SoftwareSystem("Payments")
            direct = customer >> "Browses" >> payments
            described = customer >> Rel("Pays", technology="HTTPS") >> payments

    assert (direct.source, direct.destination, direct.description) == (
        customer,
        payments,
        "Browses",
    )
    assert (described.source, described.destination, described.technology) == (
        customer,
        payments,
        "HTTPS",
    )


def test_deployment_instances_have_independent_identity_metadata_and_relationships():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments", alias="payments")
            api = payments.Container("API", alias="api")
            with model.DeploymentEnvironment("Production") as environment:
                with environment.DeploymentNode(
                    "Server", alias="server"
                ) as server:
                    system_instance = server.SoftwareSystemInstance(
                        payments,
                        alias="payments_primary",
                        description="Primary payments deployment",
                    )
                    primary = server.ContainerInstance(
                        api,
                        alias="api_primary",
                        description="Primary API deployment",
                        tags=["Primary"],
                    )
                    replica = server.ContainerInstance(
                        api,
                        alias="api_replica",
                        properties={"zone": "b"},
                    )
                    primary.uses(replica, "Replicates")

    assert primary.model_element is api
    assert replica.model_element is api
    assert primary.alias != replica.alias
    assert system_instance.parent_node is server
    assert primary.tags == ("Primary",)
    assert replica.properties == {"zone": "b"}


def test_deployment_instances_reject_foreign_model_targets():
    with Workspace("Source") as source_workspace:
        with source_workspace.model as source_model:
            foreign_system = source_model.SoftwareSystem("Foreign")

    with Workspace("Target") as target_workspace:
        with target_workspace.model as target_model:
            with target_model.DeploymentEnvironment(
                "Production"
            ) as environment:
                with environment.DeploymentNode("Server") as server:
                    with pytest.raises(
                        ValueError,
                        match="must belong to this workspace model",
                    ):
                        server.SoftwareSystemInstance(foreign_system)


def test_deployment_instances_reject_non_native_model_elements():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments")
            api = payments.Container("API")
            with model.DeploymentEnvironment("Production") as environment:
                with environment.DeploymentNode("Server") as server:
                    with pytest.raises(
                        TypeError, match="SoftwareSystem target"
                    ):
                        server.SoftwareSystemInstance(object())  # type: ignore[arg-type]
                    with pytest.raises(TypeError, match="Container target"):
                        server.ContainerInstance(object())  # type: ignore[arg-type]


def test_dynamic_created_relationship_preserves_style_metadata():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer")
            payments = model.SoftwareSystem("Payments")

        view = workspace.views.DynamicView(payments)
        view.step(
            customer,
            payments,
            "Uses",
            create_relationship=True,
            style={"color": "#123456"},
        )

    relationship = workspace.model.relationships[0]
    assert relationship.style == {"color": "#123456"}

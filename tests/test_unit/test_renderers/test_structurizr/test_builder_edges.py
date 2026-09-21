from __future__ import annotations

from types import SimpleNamespace

import pytest

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer.builder import (
    StructurizrWorkspaceBuilder,
    _dynamic_step_models,
    _instance_model,
    _relationship_model,
    _style_override_tag,
)
from c4.contrib.structurizr.renderer.errors import (
    StructurizrRenderingError,
    relationship_missing_endpoint_error,
)
from c4.contrib.structurizr.renderer.identifiers import (
    StructurizrIdentifierRegistry,
)
from c4.contrib.structurizr.renderer.validation import (
    validate_structurizr_workspace,
)


def _build(workspace: Workspace) -> StructurizrWorkspaceBuilder:
    registry = StructurizrIdentifierRegistry()
    model = workspace.model
    for element in (
        *model.people,
        *model.software_systems,
        *model.containers,
        *model.components,
        *model.deployment_nodes,
        *model.software_system_instances,
        *model.container_instances,
    ):
        registry.register_alias(element.alias)
    return StructurizrWorkspaceBuilder(workspace.name).build(
        workspace=workspace,
        identifiers=registry.identifiers,
        auto_layout=None,
        style_preset=None,
        next_relationship_id=registry.next_relationship_id,
    )


def _registry(*aliases: str) -> StructurizrIdentifierRegistry:
    registry = StructurizrIdentifierRegistry()
    for alias in aliases:
        registry.register_alias(alias)
    return registry


def test_to_dict_includes_theme_and_system_instances():
    with Workspace("Shop", theme="https://example.com/theme.json") as workspace:
        with workspace.model as model:
            shop = model.SoftwareSystem("Shop")
            with model.DeploymentEnvironment("Live") as live:
                with live.DeploymentNode("Server") as server:
                    server.SoftwareSystemInstance(shop)

    result = _build(workspace).to_dict()

    assert result["views"]["configuration"]["themes"] == [
        {"url": "https://example.com/theme.json"}
    ]
    node = result["model"]["deploymentNodes"][0]
    assert node["softwareSystemInstances"][0]["softwareSystemId"]


def test_children_with_unknown_parent_are_skipped():
    with Workspace("Shop") as workspace:
        with workspace.model as model:
            shop = model.SoftwareSystem("Shop")
            api = shop.Container("API")
            api.Component("Auth")
        api.parent = None
        workspace.model.components[0].parent = None

    built = _build(workspace)

    assert built.workspace.software_systems[0].children == []


def test_instance_without_model_target_is_rejected():
    element = SimpleNamespace(alias="x", model_element=None)

    with pytest.raises(ValueError, match="missing its model target"):
        _instance_model(
            element,  # type: ignore[arg-type]
            identifiers=_registry("x").identifiers,
            element_type="softwareSystemInstance",
            environment="Live",
        )


def test_relationship_with_unknown_endpoint_is_rejected():
    with Workspace("Shop") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer", alias="customer")
            shop = model.SoftwareSystem("Shop", alias="shop")
            relationship = customer.uses(shop, "buys")

    with pytest.raises(StructurizrRenderingError, match="shop"):
        _relationship_model(
            relationship,
            relationship_id="rel-1",
            identifiers=_registry("customer", "shop").identifiers,
            elements_by_alias={},
        )


def test_missing_endpoint_error_names_both_ends():
    error = relationship_missing_endpoint_error(
        source_alias="a",
        destination_alias="b",
        missing_side="source",
        missing_alias="a",
    )

    assert 'relationship "a -> b"' in str(error)


def test_style_override_tag_is_made_unique():
    base = "c4diagrams_style_rel"

    assert _style_override_tag("rel", ()) == base
    assert _style_override_tag("rel", (base,)) == f"{base}_2"
    assert _style_override_tag("rel", (base, f"{base}_2")) == f"{base}_3"


def test_dynamic_steps_accept_bare_relationship_like_items():
    with Workspace("Shop") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer", alias="customer")
            shop = model.SoftwareSystem("Shop", alias="shop")
    registry = _registry("customer", "shop")
    built = _build(workspace)
    bare = SimpleNamespace(
        source=customer,
        destination=shop,
        description="buys",
        technology=None,
        tags=(),
        style=None,
        url=None,
        properties=None,
    )

    result = _dynamic_step_models(
        render_items=[bare, object()],  # type: ignore[list-item]
        identifiers=registry.identifiers,
        elements_by_alias=built._elements,
        next_relationship_id=registry.next_relationship_id,
    )

    assert [item.description for item in result] == ["buys"]


def test_validation_requires_software_system_parent_for_containers():
    with Workspace("Shop") as workspace:
        shop = workspace.model.SoftwareSystem("Shop")
        shop.Container("API")
    workspace.model.containers[0].parent = None

    with pytest.raises(StructurizrRenderingError, match="software system"):
        validate_structurizr_workspace(workspace)


def test_validation_rejects_relationship_to_unregistered_element():
    with Workspace("Shop") as workspace:
        customer = workspace.model.Person("Customer")
        shop = workspace.model.SoftwareSystem("Shop")
        customer.uses(shop, "buys")
    workspace.model.people.remove(customer)

    with pytest.raises(StructurizrRenderingError, match="both endpoints"):
        validate_structurizr_workspace(workspace)


def test_validation_rejects_node_in_two_environments():
    with Workspace("Shop") as workspace:
        with workspace.model as model:
            with model.DeploymentEnvironment("Live") as live:
                node = live.DeploymentNode("Server")
            with model.DeploymentEnvironment("Staging") as staging:
                staging.DeploymentNode("Other")
    staging.nodes.append(node)

    with pytest.raises(StructurizrRenderingError, match="exactly one"):
        validate_structurizr_workspace(workspace)


def test_validation_requires_container_parent_for_components():
    with Workspace("Shop") as workspace:
        shop = workspace.model.SoftwareSystem("Shop")
        shop.Container("API").Component("Auth")
    workspace.model.components[0].parent = None

    with pytest.raises(StructurizrRenderingError, match="container parent"):
        validate_structurizr_workspace(workspace)

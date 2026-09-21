from __future__ import annotations

import pytest

from c4 import DiagramFormat
from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import (
    StructurizrElementModel,
    StructurizrRelationshipModel,
    StructurizrRenderer,
    StructurizrRenderOptions,
    StructurizrStyleModel,
    StructurizrStylesModel,
    StructurizrViewModel,
    StructurizrWorkspaceBuilder,
)
from c4.contrib.structurizr.renderer.errors import (
    StructurizrBackendConfigurationError,
)


def test_render__builds_structurizr_workspace_from_workspace_dsl():
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer()

    with Workspace("Payments landscape") as workspace:
        with workspace.model as model:
            customer = model.Person(
                "Customer",
                description="Pays for an order.",
                alias="customer",
                tags=["External", "Person"],
                url="https://example.com/customer",
                properties={"team": "growth"},
            )
            payments = model.SoftwareSystem(
                "Payments",
                description="Collects money.",
                alias="payments",
            )
            customer.uses(
                payments,
                "Makes a payment",
                technology="HTTPS",
                tags=["Synchronous"],
                url="https://example.com/pay",
                properties={"sla": "99.9"},
            )

        workspace.views.SystemLandscapeView(key="landscape")
    result = renderer.render(workspace)

    assert 'workspace "Payments landscape"' in result
    assert 'systemLandscape "landscape"' in result
    assert "theme " not in result
    assert 'tags "Person,External"' in result
    assert 'tags "Software System"' in result
    assert 'tags "Relationship,Synchronous"' in result
    assert 'url "https://example.com/customer"' in result
    assert '"team" "growth"' in result
    assert 'element "Person" {' in result
    assert "shape Person" in result
    assert 'element "Boundary" {' in result


def test_build_workspace__uses_workspace_metadata_and_view_configuration():
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer()

    with Workspace("Payments", description="Workspace notes") as workspace:
        workspace.views.SystemLandscapeView(
            key="custom_landscape",
            description="Landscape notes",
            properties={"owner": "architecture"},
        )

    workspace_builder = renderer._build_workspace(workspace)
    workspace_model = workspace_builder.to_dict()

    styles = workspace_model["views"].pop("configuration")["styles"]
    assert [style["tag"] for style in styles["elements"]] == [
        "Person",
        "Software System",
        "Container",
        "Component",
        "Database",
        "Queue",
        "External",
        "Boundary",
    ]
    assert styles["relationships"] == []

    assert workspace_model == {
        "name": "Payments",
        "description": "Workspace notes",
        "model": {
            "people": [],
            "softwareSystems": [],
            "deploymentNodes": [],
            "relationships": [],
        },
        "views": {
            "systemLandscapeViews": [
                {
                    "key": "custom_landscape",
                    "title": None,
                    "description": "Landscape notes",
                    "tags": "",
                    "automaticLayout": {
                        "implementation": None,
                        "rankDirection": "LeftRight",
                        "rankSeparation": None,
                        "nodeSeparation": None,
                    },
                    "include": [],
                    "exclude": [],
                    "animation": [],
                    "elements": [],
                    "relationships": [],
                    "properties": {"owner": "architecture"},
                }
            ],
            "systemContextViews": [],
            "containerViews": [],
            "componentViews": [],
            "dynamicViews": [],
            "deploymentViews": [],
        },
        "properties": {},
    }


def test_render_bytes__without_backend_raises_configuration_error():
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer()

    with pytest.raises(
        StructurizrBackendConfigurationError,
        match="requires a configured backend",
    ):
        renderer.render_bytes(
            Workspace("Payments landscape"),
            format=DiagramFormat.SVG,
        )


def test_render_bytes__passes_rendered_workspace_to_backend(
    mocker,
):
    backend = mocker.Mock()
    backend.to_bytes.return_value = b"svg"
    render_options = StructurizrRenderOptions()
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer(
        render_options=render_options,
        backend=backend,
    )

    result = renderer.render_bytes(
        Workspace("Landscape"),
        format=DiagramFormat.SVG,
    )

    assert result == b"svg"
    backend.to_bytes.assert_called_once()
    assert 'workspace "Landscape"' in backend.to_bytes.call_args.args[0]
    assert backend.to_bytes.call_args.kwargs == {
        "format": DiagramFormat.SVG,
        "render_options": render_options,
    }


def test_render_file__without_backend_raises_configuration_error(tmp_path):
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer()

    with pytest.raises(
        StructurizrBackendConfigurationError,
        match="requires a configured backend",
    ):
        renderer.render_file(
            Workspace("Payments landscape"),
            tmp_path / "workspace.svg",
            format=DiagramFormat.SVG,
        )


def test_render_file__passes_rendered_workspace_to_backend(
    tmp_path,
    mocker,
):
    backend = mocker.Mock()
    output_path = tmp_path / "workspace.svg"
    backend.to_file.return_value = output_path
    render_options = StructurizrRenderOptions()
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer(
        render_options=render_options,
        backend=backend,
    )

    result = renderer.render_file(
        Workspace("Landscape"),
        output_path,
        format=DiagramFormat.SVG,
        overwrite=False,
    )

    assert result == output_path
    backend.to_file.assert_called_once()
    assert 'workspace "Landscape"' in backend.to_file.call_args.args[0]
    assert backend.to_file.call_args.args[1] == output_path
    assert backend.to_file.call_args.kwargs == {
        "format": DiagramFormat.SVG,
        "overwrite": False,
        "render_options": render_options,
    }


def test_dynamic_relationship__preserves_technology_without_description():
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer()
    relationship = StructurizrRelationshipModel(
        id="1",
        source_id="customer",
        destination_id="payments",
        technology="HTTPS",
    )

    result = renderer._dynamic_relationship(relationship)

    assert result == 'customer -> payments "" "HTTPS"'


def test_renderer_private_render_helpers_cover_minimal_and_metadata_branches():
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer()
    workspace_builder = StructurizrWorkspaceBuilder("Workspace")
    workspace_builder.workspace.people.append(
        StructurizrElementModel(
            id="customer",
            name="Customer",
            element_type="person",
        )
    )
    workspace_builder.workspace.software_systems.append(
        StructurizrElementModel(
            id="payments",
            name="Payments",
            element_type="softwareSystem",
            description="Collects money",
            technology="Python",
            properties={"team": "platform"},
            children=[
                StructurizrElementModel(
                    id="api",
                    name="API",
                    element_type="container",
                    software_system_instances=[
                        StructurizrElementModel(
                            id="payments_instance",
                            name="Payments Instance",
                            element_type="softwareSystemInstance",
                            instance_of_id="payments",
                        )
                    ],
                    container_instances=[
                        StructurizrElementModel(
                            id="api_instance",
                            name="API Instance",
                            element_type="containerInstance",
                            instance_of_id="api",
                            tags=("Runtime",),
                            url="https://example.com/api",
                            properties={"node": "app"},
                        )
                    ],
                )
            ],
        )
    )
    workspace_builder.workspace.relationships.append(
        StructurizrRelationshipModel(
            id="rel1",
            source_id="customer",
            destination_id="payments",
        )
    )
    workspace_builder.workspace.views.append(
        StructurizrViewModel(
            key="custom",
            type="CustomView",
            title="Custom",
            relationships=[
                StructurizrRelationshipModel(
                    id="rel2",
                    source_id="customer",
                    destination_id="payments",
                    technology="HTTPS",
                )
            ],
        )
    )
    workspace_builder.workspace.views.append(
        StructurizrViewModel(
            key="documented",
            type="CustomView",
            description="Documented view",
            relationships=[
                StructurizrRelationshipModel(
                    id="rel3",
                    source_id="customer",
                    destination_id="payments",
                    description="Uses",
                    technology="HTTPS",
                )
            ],
        )
    )
    workspace_builder.workspace.styles = StructurizrStylesModel(
        elements=(StructurizrStyleModel("Custom", {"zeta": "two words"}),)
    )

    result = renderer._render_workspace(workspace_builder)

    assert 'customer = person "Customer"' in result
    assert 'payments = softwareSystem "Payments" "Collects money"' in result
    assert "payments_instance = softwareSystemInstance payments" in result
    assert "api_instance = containerInstance api {" in result
    assert 'tags "Runtime"' in result
    assert "customer -> payments" in result
    assert 'customer -> payments "" "HTTPS"' in result
    assert 'customer -> payments "Uses" "HTTPS"' in result
    assert 'description "Documented view"' in result
    assert 'CustomView "custom"' in result
    assert 'element "Custom" {' in result
    assert 'zeta "two words"' in result


def test_theme_line_is_absent_by_default():
    with Workspace("Plain") as workspace:
        with workspace.model as model:
            model.Person("Customer")
        workspace.views.SystemLandscapeView(key="landscape")

    assert "theme" not in StructurizrRenderer().render(workspace)


def test_explicit_theme_is_emitted():
    with Workspace("Themed", theme="https://example.test/theme.json") as ws:
        with ws.model as model:
            model.Person("Customer")
        ws.views.SystemLandscapeView(key="landscape")

    result = StructurizrRenderer().render(ws)

    assert 'theme "https://example.test/theme.json"' in result


def test_default_theme_is_dropped_with_deprecation_warning():
    with pytest.warns(DeprecationWarning, match="theme"):
        workspace = Workspace("Legacy", theme="default")

    assert workspace.theme is None


def test_technology_without_description_keeps_the_technology_slot():
    with Workspace("Tech") as workspace:
        with workspace.model as model:
            shop = model.SoftwareSystem("Shop", technology="ignored")
            model.Person("Customer", technology="ignored")
            model.Container("API", technology="FastAPI", owner=shop)
        workspace.views.SystemLandscapeView(key="landscape")

    result = StructurizrRenderer().render(workspace)

    assert 'api = container "API" "" "FastAPI"' in result
    assert 'customer = person "Customer" {' in result
    assert 'shop = softwareSystem "Shop" {' in result

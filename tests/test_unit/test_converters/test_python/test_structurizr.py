from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.converters.json import workspace_from_dict
from c4.contrib.structurizr.converters.python import (
    WorkspacePythonCodegen,
    workspace_to_python_code,
)
from c4.contrib.structurizr.renderer import (
    AutoLayout,
    StructurizrRenderer,
    StructurizrRenderOptions,
)


def _execute(source: str) -> Workspace:
    compile(source, "<generated Structurizr DSL>", "exec")
    namespace: dict[str, Any] = {}
    exec(source, namespace)  # noqa: S102 - executing generated source is the test.
    return namespace["workspace"]


def test_workspace_to_python_code__minimal_workspace_round_trips() -> None:
    with Workspace("Minimal") as workspace:
        with workspace.model as model:
            user = model.Person("User", alias="user")
            system = model.SoftwareSystem("System", alias="system")
            user.uses(system, "Uses")
        workspace.views.SystemLandscapeView(include=[user, system])

    source = workspace_to_python_code(workspace)

    assert "workspace_from_dict" not in source
    assert StructurizrRenderer().render(
        workspace
    ) == StructurizrRenderer().render(_execute(source))

    assert WorkspacePythonCodegen().generate(workspace) == source


def test_workspace_to_python_code__complete_json_workspace_round_trips() -> (
    None
):
    document = {
        "backend": "structurizr",
        "name": "Complete",
        "description": "Workspace description",
        "properties": {"owner": "architecture"},
        "theme": "https://example.test/theme.json",
        "styles": {
            "elements": [{"target": "Custom", "properties": {"color": "#fff"}}],
            "relationships": [
                {"target": "Async", "properties": {"color": "#000"}}
            ],
        },
        "render_options": {
            "auto_layout": {"rank_direction": "TopBottom"},
            "style_preset": "classic",
        },
        "model": {
            "people": [{"id": "user", "name": "User", "tags": ["Custom"]}],
            "software_systems": [
                {
                    "id": "system",
                    "name": "System",
                    "containers": [
                        {
                            "id": "api",
                            "name": "API",
                            "technology": "Python",
                            "components": [
                                {"id": "handler", "name": "Handler"}
                            ],
                        }
                    ],
                }
            ],
            "relationships": [
                {
                    "from": "user",
                    "to": "handler",
                    "description": "Uses",
                    "tags": ["Async"],
                    "style": {"color": "#f00"},
                }
            ],
            "deployment": {
                "environments": [
                    {
                        "name": "Production",
                        "deployment_nodes": [
                            {
                                "id": "server",
                                "name": "Server",
                                "software_system_instances": [
                                    {
                                        "id": "system_instance",
                                        "software_system": "system",
                                    }
                                ],
                                "container_instances": [
                                    {"id": "api_instance", "container": "api"}
                                ],
                                "infrastructure_nodes": [
                                    {
                                        "id": "database",
                                        "name": "Database",
                                        "technology": "PostgreSQL",
                                    }
                                ],
                            }
                        ],
                    }
                ]
            },
        },
        "views": {
            "items": [
                {
                    "type": "system_landscape",
                    "key": "landscape",
                    "include": [{"id": "user"}],
                    "auto_layout": {"rank_direction": "LeftRight"},
                },
                {
                    "type": "dynamic",
                    "scope": "system",
                    "steps": [
                        {
                            "from": "user",
                            "to": "handler",
                            "description": "Request",
                            "style": {"color": "#00f"},
                        }
                    ],
                },
                {
                    "type": "deployment",
                    "scope": "system",
                    "environment": "Production",
                },
            ]
        },
    }
    workspace, _ = workspace_from_dict(document)

    source = workspace_to_python_code(workspace)

    assert "workspace_from_dict" not in source
    assert "workspace.set_property" in source
    assert "model.InfrastructureNode" in source
    assert "AutoLayout" in source
    assert StructurizrRenderer().render(
        workspace
    ) == StructurizrRenderer().render(_execute(source))


def test_workspace_to_python_code__retains_explicit_aliases() -> None:
    workspace = Workspace("Aliases")
    with workspace.model as model:
        model.Person("User", alias="user_alias")

    assert "alias='user_alias'" in workspace_to_python_code(workspace)


@pytest.mark.parametrize("rank_direction", ["LeftRight", "TopBottom"])
def test_workspace_to_python_code__renders_auto_layout(
    rank_direction: str,
) -> None:
    workspace = Workspace("Layout")
    workspace.views.SystemLandscapeView(
        auto_layout=AutoLayout(rank_direction=rank_direction)  # type: ignore[arg-type]
    )

    assert f"rank_direction='{rank_direction}'" in workspace_to_python_code(
        workspace
    )


def test_workspace_to_python_code__animation_steps_round_trip() -> None:
    with Workspace("Animation") as workspace:
        with workspace.model as model:
            user = model.Person("User", alias="user")
            system = model.SoftwareSystem("System", alias="system")
            web = model.Container("Web", alias="web", owner=system)
            api = model.Container("API", alias="api", owner=system)
            db = model.Container("DB", alias="db", owner=system)
            user.uses(web, "Uses")
            web.uses(api, "Calls")
            api.uses(db, "Reads")
        workspace.views.ContainerView(
            system, key="containers", animation=[[user, web, api], [db]]
        )

    source = workspace_to_python_code(workspace)

    assert "animation=[[user, web, api], [db]]" in source
    assert StructurizrRenderer().render(
        workspace
    ) == StructurizrRenderer().render(_execute(source))


def test_workspace_to_python_code__optional_fields_round_trip() -> None:
    with Workspace("Full") as workspace:
        with workspace.model as model:
            user = model.Person(
                "User",
                alias="user",
                description="A user",
                properties={"team": "a"},
                url="https://example.test/user",
                style={"background": "#ffffff"},
            )
            system = model.SoftwareSystem("System", alias="system")
            user.uses(
                system,
                "Uses",
                technology="HTTPS",
                tags=["Sync"],
                properties={"p": "1"},
                url="https://example.test/rel",
                style={"color": "#000000"},
            )
            with model.DeploymentEnvironment("Live") as live:
                live.DeploymentNode("Server")
        workspace.views.SystemLandscapeView(
            include=["*"], exclude=[user], animation=[["*"]]
        )
        workspace.views.DeploymentView(environment="Live")
        workspace.render_options = StructurizrRenderOptions(
            style_preset="classic"
        )
    workspace.views.SystemContextView(
        system,
        auto_layout=AutoLayout(
            implementation="graphviz", rank_separation=3, node_separation=4
        ),
    )

    source = workspace_to_python_code(workspace)

    assert "exclude=" in source
    assert "style_preset='classic'" in source
    assert "implementation='graphviz'" in source
    assert StructurizrRenderer().render(
        workspace
    ) == StructurizrRenderer().render(_execute(source))


def test_workspace_to_python_code__layout_only_render_options() -> None:
    workspace = Workspace("Layout")
    workspace.render_options = StructurizrRenderOptions(
        auto_layout=AutoLayout(), style_preset=None
    )

    source = workspace_to_python_code(workspace)

    assert "style_preset" not in source
    assert "auto_layout=AutoLayout(" in source


def test_workspace_to_python_code__rejects_unsupported_constructs() -> None:
    workspace = Workspace("Odd")
    workspace.views._items.append(  # type: ignore[arg-type]
        SimpleNamespace(
            key=None,
            title=None,
            description=None,
            tags=(),
            properties={},
            include_selectors=(),
            exclude_selectors=(),
            auto_layout=None,
            animation=(),
        )
    )
    with pytest.raises(TypeError, match="Unsupported Structurizr view"):
        workspace_to_python_code(workspace)

    codegen = WorkspacePythonCodegen()
    with pytest.raises(TypeError, match="Unsupported Structurizr model"):
        codegen._render_model_element(
            SimpleNamespace(
                alias="x",
                name="X",
                description=None,
                technology=None,
                tags=(),
                properties={},
                url=None,
                style_properties={},
            ),
            indent="",
        )


def test_workspace_python_variable_names_are_valid_and_unique() -> None:
    codegen = WorkspacePythonCodegen()

    assert codegen._variable("1st") == "element_1st"
    assert codegen._variable("class") == "class_"
    assert codegen._variable("a-b") == "a_b"
    assert codegen._variable("a b") == "a_b_2"
    assert codegen._variable("a-b") == "a_b"


def test_workspace_to_python_code__preset_only_render_options() -> None:
    workspace = Workspace("Preset")
    workspace.render_options = StructurizrRenderOptions(
        style_preset="classic", auto_layout=None
    )

    source = workspace_to_python_code(workspace)

    assert "StructurizrRenderOptions(style_preset='classic')" in source


def test_workspace_to_python_code__unlabeled_relationships_and_steps() -> None:
    with Workspace("Unlabeled") as workspace:
        with workspace.model as model:
            user = model.Person("User", alias="user")
            system = model.SoftwareSystem("System", alias="system")
            user >> system
        workspace.views.DynamicView(system, key="flow").step(user, system)

    source = workspace_to_python_code(workspace)

    assert "user >> system\n" in source
    assert ".step(user, system)" in source
    assert "Rel" not in source
    assert StructurizrRenderer().render(
        workspace
    ) == StructurizrRenderer().render(_execute(source))

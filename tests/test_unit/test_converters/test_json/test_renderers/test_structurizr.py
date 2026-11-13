from __future__ import annotations

from c4.contrib.structurizr.renderer import (
    StructurizrRenderer,
    StructurizrRenderOptions,
)
from c4.converters.json.converter import diagram_from_dict
from tests.conftest import AssertMatchSnapshot
from tests.test_unit.test_converters.test_json.test_diagrams.test_structurizr import (
    complete_workspace,
    minimal_workspace,
)


def test_render_minimal_structurizr_json_workspace_snapshot(
    assert_match_snapshot: AssertMatchSnapshot,
):
    workspace, _ = diagram_from_dict(minimal_workspace())

    renderer = StructurizrRenderer(StructurizrRenderOptions(style_preset=None))
    rendered = renderer.render(workspace)

    assert 'workspace "Workspace"' in rendered
    assert 'systemLandscape "landscape"' in rendered
    assert_match_snapshot(
        snapshot_name="structurizr/workspace.minimal.dsl",
        diagram_code=rendered,
    )
    person = renderer._last_workspace_builder.to_dict()["model"]["people"][0]
    assert {key: person[key] for key in ("id", "name", "tags")} == {
        "id": "customer",
        "name": "Customer",
        "tags": "Person",
    }


def test_render_complete_structurizr_json_workspace_snapshot(
    assert_match_snapshot: AssertMatchSnapshot,
):
    workspace, _ = diagram_from_dict(complete_workspace())

    assert_match_snapshot(
        snapshot_name="structurizr/workspace.complete.dsl",
        diagram_code=StructurizrRenderer(
            StructurizrRenderOptions(style_preset=None),
        ).render(workspace),
    )

from __future__ import annotations

import pytest

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import (
    AutoLayout,
    StructurizrRenderer,
    StructurizrRenderOptions,
)
from c4.contrib.structurizr.renderer.errors import StructurizrRenderingError
from c4.contrib.structurizr.renderer.styles import (
    allowed_style_preset_values,
    parse_style_metadata,
)


def test_render_default_classic_style_preset():
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            model.Person("Customer", alias="customer")
            model.SoftwareSystem("Payments", alias="payments")

    result = StructurizrRenderer().render(workspace)

    assert 'element "Person" {' in result
    assert "background #08427b" in result
    assert 'element "Software System" {' in result
    assert 'element "Boundary" {' in result
    assert 'relationship "Relationship"' not in result


def test_render_new_c4_style_preset():
    renderer = StructurizrRenderer(
        StructurizrRenderOptions(style_preset="new-c4-style")
    )
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            model.Person("Customer", alias="customer")
            model.SoftwareSystem("Payments", alias="payments")

    result = renderer.render(workspace)

    assert 'element "Element" {' in result
    assert "strokeWidth 7" in result
    assert "shape RoundedBox" in result
    assert 'relationship "Relationship" {' in result
    assert "thickness 4" in result


def test_render_style_preset_none_keeps_semantic_tags_without_styles():
    renderer = StructurizrRenderer(StructurizrRenderOptions(style_preset=None))
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            model.Person("Customer", alias="customer", tags=["External"])
            model.SoftwareSystem("Payments", alias="payments")

    result = renderer.render(workspace)

    assert 'tags "Person,External"' in result
    assert 'tags "Software System"' in result
    assert "styles {" not in result


def test_generated_tags_cover_database_queue_external_and_relationship():
    with Workspace("Containers") as workspace:
        with workspace.model as model:
            model.SoftwareSystem(
                "Identity", alias="identity", tags=["External"]
            )
            payments = model.SoftwareSystem("Payments", alias="payments")
            repository = payments.Container(
                "Repository", alias="repository", tags=["Database"]
            )
            outbox = payments.Container(
                "Outbox", alias="outbox", tags=["Queue"]
            )
            repository.uses(outbox, "Publishes to")

    result = StructurizrRenderer(
        StructurizrRenderOptions(style_preset=None)
    ).render(workspace)

    assert 'tags "Software System,External"' in result
    assert 'tags "Container,Database"' in result
    assert 'tags "Container,Queue"' in result
    assert 'tags "Relationship"' in result


def test_user_tags_merge_after_generated_tags_without_duplicates():
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            model.Person(
                "Customer",
                alias="customer",
                tags=["Person", "External", "Critical"],
            )

    result = StructurizrRenderer(
        StructurizrRenderOptions(style_preset=None)
    ).render(workspace)

    assert 'tags "Person,External,Critical"' in result


def test_element_style_override_emits_deterministic_override_tag_and_style():
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            model.SoftwareSystem(
                "Payments",
                alias="payments",
                style={
                    "background": "#123456",
                    "color": "#ffffff",
                    "shape": "cylinder",
                    "stroke_width": 3,
                },
            )

    result = StructurizrRenderer().render(workspace)

    assert 'tags "Software System,c4diagrams_style_payments"' in result
    assert result.index('element "Software System"') < result.index(
        'element "c4diagrams_style_payments"'
    )
    assert 'element "c4diagrams_style_payments" {' in result
    assert "shape Cylinder" in result
    assert "background #123456" in result
    assert "strokeWidth 3" in result


def test_style_preset_none_keeps_element_override_styles():
    renderer = StructurizrRenderer(StructurizrRenderOptions(style_preset=None))
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            model.SoftwareSystem(
                "Payments",
                alias="payments",
                style={"background": "#123456"},
            )

    result = renderer.render(workspace)

    assert 'element "Person"' not in result
    assert 'element "c4diagrams_style_payments" {' in result


def test_workspace_model_includes_style_configuration():
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            model.Person("Customer", alias="customer")

    workspace = StructurizrRenderer()._build_workspace(workspace).to_dict()

    styles = workspace["views"]["configuration"]["styles"]
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


def test_workspace_model_omits_style_configuration_when_disabled():
    renderer = StructurizrRenderer(StructurizrRenderOptions(style_preset=None))
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            model.Person("Customer", alias="customer")

    workspace = renderer._build_workspace(workspace).to_dict()

    assert workspace["views"]["configuration"] == {}


def test_relationship_border_style_renders_as_structurizr_line_style():
    renderer = StructurizrRenderer(StructurizrRenderOptions(style_preset=None))
    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer", alias="customer")
            payments = model.SoftwareSystem("Payments", alias="payments")
            customer.uses(payments, "Uses")

        workspace.styles.relationship(
            "Async",
            color="#00695c",
            thickness=2,
            border="dotted",
        ).relationship(
            "ExternalCall",
            color="#455a64",
            thickness=2,
            border="dashed",
        )

    result = renderer.render(workspace)

    assert 'relationship "Async" {' in result
    assert "style dotted" in result
    assert 'relationship "ExternalCall" {' in result
    assert "style dashed" in result
    assert "border Dotted" not in result
    assert "border Dashed" not in result


def test_unknown_style_preset_raises_allowed_values_error():
    with pytest.raises(ValueError, match=r"'classic'.*'new-c4-style'.*None"):
        StructurizrRenderOptions(style_preset="unknown")  # type: ignore[arg-type]


def test_invalid_style_metadata_raises_actionable_error():
    with pytest.raises(
        StructurizrRenderingError,
        match=r"stroke_width.*positive integer",
    ):
        with Workspace("Landscape") as workspace:
            with workspace.model as model:
                model.SoftwareSystem(
                    "Payments",
                    alias="payments",
                    style={"stroke_width": 0},
                )


def test_allowed_style_preset_values_includes_none():
    assert allowed_style_preset_values() == "'classic', 'new-c4-style', None"


def test_auto_layout_rejects_invalid_rank_direction():
    with pytest.raises(ValueError, match="rank direction"):
        AutoLayout(rank_direction="Diagonal")  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, -1, True, "12"])
def test_auto_layout_rejects_invalid_rank_separation(value: object):
    with pytest.raises((TypeError, ValueError), match="rank_separation"):
        AutoLayout(rank_separation=value)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [0, -1, True, "12"])
def test_auto_layout_rejects_invalid_node_separation(value: object):
    with pytest.raises((TypeError, ValueError), match="node_separation"):
        AutoLayout(node_separation=value)  # type: ignore[arg-type]


def test_parse_style_metadata__normalizes_supported_fields():
    assert parse_style_metadata({
        "shape": "web_browser",
        "border": "dotted",
        "width": 450,
        "height": 300,
        "stroke_width": 4,
        "font_size": 18,
        "opacity": 0,
        "metadata": True,
        "description": False,
        "background": "#fff",
        "color": "#000",
    }) == {
        "shape": "WebBrowser",
        "border": "Dotted",
        "width": 450,
        "height": 300,
        "strokeWidth": 4,
        "fontSize": 18,
        "opacity": 0,
        "metadata": True,
        "description": False,
        "background": "#fff",
        "color": "#000",
    }


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ([], "style.*mapping"),
        ({"unknown": "value"}, "Unknown Structurizr style field"),
        ({"width": True}, "width.*positive integer"),
        ({"opacity": -1}, "opacity.*non-negative integer"),
        ({"metadata": "yes"}, "metadata.*boolean"),
        ({"shape": 1}, "shape.*string enum name"),
        ({"shape": "triangle"}, "shape.*must be one of"),
        ({"border": "double"}, "border.*must be one of"),
        ({"background": object()}, "background.*string, integer"),
    ],
)
def test_parse_style_metadata__rejects_invalid_values(
    value: object,
    message: str,
):
    with pytest.raises(StructurizrRenderingError, match=message):
        parse_style_metadata(value)

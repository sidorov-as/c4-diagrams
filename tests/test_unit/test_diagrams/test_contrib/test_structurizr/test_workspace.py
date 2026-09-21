from __future__ import annotations

import textwrap

import pytest

import c4.cli.discover as discover
from c4 import Boundary, Person
from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import (
    StructurizrRenderer,
    StructurizrRenderOptions,
)
from c4.diagrams.core import Diagram
from c4.exceptions import (
    D2RenderingError,
    MermaidRenderingError,
    PlantUMLRenderingError,
)
from c4.renderers import D2Renderer, MermaidRenderer, PlantUMLRenderer


def test_workspace_is_a_standalone_render_target():
    workspace = Workspace("Payments", description="Payments architecture")

    assert not isinstance(workspace, Diagram)
    assert workspace.name == "Payments"
    assert workspace.description == "Payments architecture"
    assert not hasattr(workspace, "ordered_elements")
    assert not hasattr(workspace, "get_element_by_alias")


def test_workspace_can_be_resolved_and_auto_discovered_by_cli(make_tmp_py_file):
    make_tmp_py_file(
        "structurizr_workspace_module.py",
        textwrap.dedent(
            """
            from c4.contrib.structurizr import Workspace

            workspace = Workspace(name="Payments")
            """
        ),
    )

    assert isinstance(
        discover.resolve_diagram("structurizr_workspace_module:workspace"),
        Workspace,
    )
    assert isinstance(
        discover.resolve_diagram("structurizr_workspace_module"),
        Workspace,
    )


def test_workspace_render_and_save_keep_native_lifecycle_ergonomics(tmp_path):
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer", alias="customer")
            payments = model.SoftwareSystem("Payments", alias="payments")
            customer.uses(payments, "Uses")

    expected = StructurizrRenderer(
        StructurizrRenderOptions(style_preset=None)
    ).render(workspace)
    assert (
        workspace.render(
            StructurizrRenderer(StructurizrRenderOptions(style_preset=None))
        )
        == expected
    )

    output = workspace.save(
        tmp_path / "architecture.dsl",
        StructurizrRenderer(StructurizrRenderOptions(style_preset=None)),
    )
    assert output.read_text() == expected


@pytest.mark.parametrize(
    ("renderer", "error"),
    [
        (D2Renderer(), D2RenderingError),
        (MermaidRenderer(), MermaidRenderingError),
        (PlantUMLRenderer(), PlantUMLRenderingError),
    ],
)
def test_diagram_renderers_reject_workspace_targets(renderer, error):
    with pytest.raises(
        error,
        match=rf"{renderer.__class__.__name__} requires a c4\.diagrams\.core\.Diagram",
    ):
        renderer.render(Workspace("Payments"))


@pytest.mark.parametrize(
    "renderer",
    [D2Renderer(), MermaidRenderer(), PlantUMLRenderer()],
)
def test_workspace_lifecycle_rejects_incompatible_renderer(renderer):
    with pytest.raises(
        TypeError,
        match=r"Structurizr Workspace requires StructurizrRenderer",
    ):
        Workspace("Payments").render(renderer)


@pytest.mark.parametrize(
    "renderer",
    [D2Renderer(), MermaidRenderer(), PlantUMLRenderer()],
)
def test_diagram_renderers_retain_base_diagram_traversal(renderer):
    with Diagram("Inventory") as diagram:
        person = Person("Customer", alias="customer")
        with Boundary("Platform", alias="platform") as boundary:
            service = Person("Service", alias="service")

    assert list(renderer.iter_render_items(diagram)) == [person, boundary]
    assert list(renderer.iter_boundary_render_items(boundary)) == [service]


def test_workspace_renders_explicit_parent_references_without_boundaries_or_owner_aliases():
    with Workspace("Payments") as workspace:
        with workspace.model as model:
            payments = model.SoftwareSystem("Payments", alias="payments")
            api = model.Container("API", alias="api", owner=payments)
            checkout = model.Component("Checkout", alias="checkout", owner=api)
            database = model.Container(
                "Database", alias="database", owner=payments
            )
            checkout.uses(database, "Reads")

        workspace.views.ComponentView(api, key="components")

    rendered = StructurizrRenderer(
        StructurizrRenderOptions(style_preset=None)
    ).render(workspace)
    assert 'payments = softwareSystem "Payments"' in rendered
    assert 'api = container "API"' in rendered
    assert 'checkout = component "Checkout"' in rendered
    assert 'checkout -> database "Reads"' in rendered
    assert 'component api "components"' in rendered
    assert "owner_alias" not in rendered

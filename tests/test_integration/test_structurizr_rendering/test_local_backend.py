from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import (
    LocalStructurizrBackend,
    StructurizrRenderer,
    StructurizrRenderingError,
)
from c4.enums import PNG, SVG

pytestmark = [
    pytest.mark.structurizr,
    pytest.mark.skipif(
        shutil.which("structurizr") is None,
        reason="structurizr CLI is not installed",
    ),
]

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


@pytest.fixture
def workspace() -> Workspace:
    workspace = Workspace("Demo")
    with workspace.model as model:
        model.Person("Customer", alias="customer")
    workspace.views.SystemLandscapeView(key="landscape")
    return workspace


def test_renders_png_through_renderer(workspace: Workspace):
    renderer = StructurizrRenderer(
        backend=LocalStructurizrBackend(view_key="landscape")
    )

    data = renderer.render_bytes(workspace, format=PNG)

    assert data.startswith(PNG_SIGNATURE)


def test_single_view_needs_no_view_key(workspace: Workspace, tmp_path: Path):
    renderer = StructurizrRenderer(backend=LocalStructurizrBackend())

    output = renderer.render_file(
        workspace, tmp_path / "landscape.svg", format=SVG
    )

    assert b"<svg" in output.read_bytes()


def test_unknown_view_key_raises(workspace: Workspace):
    renderer = StructurizrRenderer(
        backend=LocalStructurizrBackend(view_key="missing")
    )

    with pytest.raises(StructurizrRenderingError, match="available views"):
        renderer.render_bytes(workspace, format=PNG)

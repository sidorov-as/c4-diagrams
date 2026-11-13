from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from c4.contrib.likec4 import Project, Wildcard
from c4.contrib.likec4.renderer import (
    LikeC4BackendConfigurationError,
    LikeC4LocalRenderingError,
    LikeC4Renderer,
    LocalLikeC4Backend,
)
from c4.enums import JPG, PNG

pytestmark = [
    pytest.mark.likec4,
    pytest.mark.skipif(
        shutil.which("likec4") is None, reason="likec4 is not installed"
    ),
]

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPG_SIGNATURE = b"\xff\xd8\xff"


@pytest.fixture
def renderer() -> LikeC4Renderer:
    return LikeC4Renderer(backend=LocalLikeC4Backend(), view_key="index")


@pytest.fixture
def project() -> Project:
    project = Project()
    project.specification.element("system")
    project.model.element("system", "Cloud", alias="cloud")
    project.views.element_view("index", title="Landscape").include(Wildcard())
    return project


def _skip_without_chromium(error: LikeC4BackendConfigurationError) -> None:
    pytest.skip(f"LikeC4 export is not available: {error}")


def test_png_export(renderer: LikeC4Renderer, project: Project):
    try:
        data = renderer.render_bytes(project, format=PNG)
    except LikeC4BackendConfigurationError as error:
        _skip_without_chromium(error)

    assert data.startswith(PNG_SIGNATURE)


def test_jpg_export_to_file(
    renderer: LikeC4Renderer, project: Project, tmp_path: Path
):
    try:
        path = renderer.render_file(project, tmp_path / "out.jpg", format=JPG)
    except LikeC4BackendConfigurationError as error:
        _skip_without_chromium(error)

    assert path.read_bytes().startswith(JPG_SIGNATURE)


def test_unknown_view_is_reported(project: Project):
    renderer = LikeC4Renderer(backend=LocalLikeC4Backend(), view_key="ghost")

    try:
        renderer.render_bytes(project, format=PNG)
    except LikeC4BackendConfigurationError as error:
        _skip_without_chromium(error)
    except LikeC4LocalRenderingError as error:
        assert "ghost" in str(error)
    else:
        pytest.fail("Expected LikeC4LocalRenderingError")

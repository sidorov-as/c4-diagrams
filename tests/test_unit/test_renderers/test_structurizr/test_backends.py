from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from c4 import DiagramFormat
from c4.contrib.structurizr.renderer.backends import (
    BaseStructurizrBackend,
)
from c4.contrib.structurizr.renderer.options import StructurizrRenderOptions


class DummyStructurizrBackend(BaseStructurizrBackend):
    def __init__(self, content: bytes = b"rendered") -> None:
        self.content = content
        self.calls: list[tuple[str, Any]] = []

    def validate(
        self,
        workspace: str,
        *,
        render_options: StructurizrRenderOptions | None = None,
    ) -> None:
        self.calls.append((workspace, render_options))

    def to_bytes(
        self,
        workspace: str,
        *,
        format: DiagramFormat | str,  # noqa: A002
        render_options: StructurizrRenderOptions | None = None,
    ) -> bytes:
        self.calls.append((workspace, format, render_options))
        return self.content


def test_base_structurizr_backend__to_file__empty_format_and_extension(
    tmp_path: Path,
):
    backend = DummyStructurizrBackend()

    with pytest.raises(
        ValueError,
        match="format is None and output_path has no extension",
    ):
        backend.to_file("workspace {}", tmp_path / "workspace", format=None)


def test_base_structurizr_backend__to_file__infers_format_from_extension(
    tmp_path: Path,
):
    backend = DummyStructurizrBackend(content=b"svg")

    output_path = backend.to_file(
        "workspace {}",
        tmp_path / "nested" / "workspace.svg",
        format=None,
    )

    assert output_path == tmp_path / "nested" / "workspace.svg"
    assert output_path.read_bytes() == b"svg"
    assert backend.calls == [("workspace {}", "svg", None)]


def test_base_structurizr_backend__to_file__respects_overwrite_false(
    tmp_path: Path,
):
    backend = DummyStructurizrBackend()
    output_path = tmp_path / "workspace.svg"
    output_path.write_bytes(b"existing")

    with pytest.raises(FileExistsError, match="Output file already exists"):
        backend.to_file(
            "workspace {}",
            output_path,
            format=DiagramFormat.SVG,
            overwrite=False,
        )

    assert output_path.read_bytes() == b"existing"
    assert backend.calls == []


def test_base_structurizr_backend__to_file__passes_render_options(
    tmp_path: Path,
):
    backend = DummyStructurizrBackend()
    render_options = StructurizrRenderOptions()

    backend.to_file(
        "workspace {}",
        tmp_path / "workspace.svg",
        format=DiagramFormat.SVG,
        render_options=render_options,
    )

    assert backend.calls == [
        ("workspace {}", DiagramFormat.SVG, render_options)
    ]

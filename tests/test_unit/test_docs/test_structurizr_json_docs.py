from __future__ import annotations

import json
from pathlib import Path
from runpy import run_path

from c4.contrib.structurizr.converters.json.schemas import (
    StructurizrWorkspaceSchema,
)
from c4.contrib.structurizr.renderer import StructurizrRenderer
from docs.scripts.generate_diagram_spec_docs import BACKEND_SCHEMAS, generate


def test_structurizr_workspace_spec_docs_are_generated(tmp_path: Path):
    backend = next(
        item for item in BACKEND_SCHEMAS if item.slug == "structurizr"
    )
    spec_path = tmp_path / "structurizr.workspace.json"
    markdown_path = tmp_path / "structurizr.workspace.md"

    generate(
        backend=backend,
        spec_path=spec_path,
        md_path=markdown_path,
        diagram_schema=StructurizrWorkspaceSchema,
    )

    schema = json.loads(spec_path.read_text(encoding="utf-8"))
    assert schema["properties"]["backend"]["const"] == "structurizr"
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "`Workspace` workspace spec" in markdown
    assert "Structurizr DSL" in markdown


def test_structurizr_json_examples_validate_and_render():
    examples_dir = (
        Path(__file__).parents[3] / "docs/assets/examples/json/structurizr"
    )
    renderer = StructurizrRenderer()

    for example_path in sorted(examples_dir.glob("*.json")):
        schema = StructurizrWorkspaceSchema.model_validate_json(
            example_path.read_text(encoding="utf-8")
        )
        assert renderer.render(schema.to_workspace()).startswith("workspace ")


def test_published_structurizr_example_artifacts_are_consistent():
    """Keep each published Workspace example in sync with its rendered DSL."""
    repo_root = Path(__file__).parents[3]
    examples_dir = repo_root / "docs/assets/examples"
    json_examples_dir = examples_dir / "json/structurizr"
    structurizr_examples_dir = examples_dir / "structurizr"
    renderer = StructurizrRenderer()
    example_names = ("workspace.advanced", "workspace.minimal")
    json_paths = tuple(sorted(json_examples_dir.glob("*.json")))
    python_paths = tuple(sorted(structurizr_examples_dir.glob("*.py")))

    assert tuple(path.stem for path in json_paths) == example_names
    assert tuple(path.stem for path in python_paths) == example_names

    for json_path in json_paths:
        expected_dsl = structurizr_examples_dir.joinpath(
            json_path.with_suffix(".dsl").name
        ).read_text(encoding="utf-8")
        workspace = StructurizrWorkspaceSchema.model_validate_json(
            json_path.read_text(encoding="utf-8")
        ).to_workspace()

        assert renderer.render(workspace) == expected_dsl

    for python_path in python_paths:
        expected_dsl = python_path.with_suffix(".dsl").read_text(
            encoding="utf-8"
        )
        workspace = run_path(str(python_path))["workspace"]

        assert renderer.render(workspace) == expected_dsl

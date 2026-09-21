from __future__ import annotations

import json
from pathlib import Path
from runpy import run_path

from c4.contrib.likec4.converters.json.schemas import LikeC4ProjectSchema
from c4.contrib.likec4.converters.python import project_to_python_code
from docs.scripts.generate_diagram_spec_docs import BACKEND_SCHEMAS, generate

REPO_ROOT = Path(__file__).parents[3]
EXAMPLES = REPO_ROOT / "docs/assets/examples"
EXAMPLE_NAMES = ("project.advanced", "project.minimal")


def test_likec4_project_spec_docs_are_generated(tmp_path: Path):
    backend = next(item for item in BACKEND_SCHEMAS if item.slug == "likec4")
    spec_path = tmp_path / "likec4.project.json"
    markdown_path = tmp_path / "likec4.project.md"

    generate(
        backend=backend,
        spec_path=spec_path,
        md_path=markdown_path,
        diagram_schema=LikeC4ProjectSchema,
    )

    schema = json.loads(spec_path.read_text(encoding="utf-8"))
    assert schema["properties"]["backend"]["const"] == "likec4"
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "`Project` project spec" in markdown
    assert "LikeC4 DSL" in markdown
    assert "project.advanced.json" in markdown


def test_published_spec_assets_are_up_to_date(tmp_path: Path):
    backend = next(item for item in BACKEND_SCHEMAS if item.slug == "likec4")
    spec_path = tmp_path / "likec4.project.json"
    markdown_path = tmp_path / "likec4.project.md"

    generate(
        backend=backend,
        spec_path=spec_path,
        md_path=markdown_path,
        diagram_schema=LikeC4ProjectSchema,
    )

    assert spec_path.read_text(encoding="utf-8") == (
        REPO_ROOT / "docs/assets/specs/likec4.project.json"
    ).read_text(encoding="utf-8")
    assert markdown_path.read_text(encoding="utf-8") == (
        REPO_ROOT / "docs/converters/json/specs/likec4.project.md"
    ).read_text(encoding="utf-8")


def test_published_likec4_example_artifacts_are_consistent():
    """Keep each published example in sync with its rendered DSL and code."""
    json_dir = EXAMPLES / "json/likec4"
    likec4_dir = EXAMPLES / "likec4"
    json_paths = tuple(sorted(json_dir.glob("*.json")))
    python_paths = tuple(sorted(likec4_dir.glob("*.py")))

    assert tuple(path.stem for path in json_paths) == EXAMPLE_NAMES
    assert tuple(path.stem for path in python_paths) == EXAMPLE_NAMES

    for json_path in json_paths:
        project = LikeC4ProjectSchema.model_validate_json(
            json_path.read_text(encoding="utf-8")
        ).to_project()
        expected_dsl = likec4_dir.joinpath(
            json_path.with_suffix(".c4").name
        ).read_text(encoding="utf-8")

        assert project.render() == expected_dsl
        assert project_to_python_code(project) == likec4_dir.joinpath(
            json_path.with_suffix(".py").name
        ).read_text(encoding="utf-8")

    for python_path in python_paths:
        project = run_path(str(python_path))["project"]

        assert project.render() == python_path.with_suffix(".c4").read_text(
            encoding="utf-8"
        )

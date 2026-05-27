import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import TypeAdapter

from c4.constants import MERMAID, PLANTUML
from c4.converters.json.converter import (
    CoreDiagramSchemaAdapter,
    MermaidDiagramSchemaAdapter,
    PlantUMLDiagramSchemaAdapter,
)
from tests.conftest import CLI, AssertMatchSnapshot
from tests.utils import ASSETS_DIR, ParametrizeArgs

JSON_EXAMPLES_DIR = ASSETS_DIR / "examples" / "json"


def __examples__json_asset_schema__parametrize() -> ParametrizeArgs:
    arg_names = (
        "json_diagram_file",
        "schema_adapter",
    )
    arg_values = []
    ids = []

    for backend_dir, schema_adapter in (
        ("core", CoreDiagramSchemaAdapter),
        (PLANTUML.value, PlantUMLDiagramSchemaAdapter),
        (MERMAID.value, MermaidDiagramSchemaAdapter),
    ):
        examples_dir = JSON_EXAMPLES_DIR / backend_dir

        for json_diagram_file in sorted(examples_dir.glob("*.json")):
            arg_values.append((json_diagram_file, schema_adapter))
            ids.append(f"{backend_dir}/{json_diagram_file.name}")

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__derived_artifacts__parametrize() -> ParametrizeArgs:
    arg_names = (
        "json_diagram_file",
        "expected_source_file",
        "expected_png_file",
    )
    arg_values = []
    ids = []

    for backend, source_suffix in (
        (PLANTUML.value, ".puml"),
        (MERMAID.value, ".mmd"),
    ):
        examples_dir = JSON_EXAMPLES_DIR / backend

        for json_diagram_file in sorted(examples_dir.glob("*.json")):
            arg_values.append((
                json_diagram_file,
                ASSETS_DIR
                / "examples"
                / backend
                / json_diagram_file.with_suffix(source_suffix).name,
                ASSETS_DIR
                / "examples"
                / backend
                / json_diagram_file.with_suffix(".png").name,
            ))
            ids.append(f"{backend}/{json_diagram_file.name}")

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__json_to_plantuml__parametrize() -> ParametrizeArgs:
    examples_dir = JSON_EXAMPLES_DIR / "plantuml"

    arg_names = (
        "json_diagram_file",
        "expected_puml_file",
    )
    arg_values = []
    ids = []

    for json_diagram_file in sorted(examples_dir.glob("*.json")):
        puml_file = (
            ASSETS_DIR
            / "examples"
            / "plantuml"
            / json_diagram_file.with_suffix(".puml").name
        )
        arg_values.append((json_diagram_file, puml_file))
        ids.append(json_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__json_to_mermaid__parametrize() -> ParametrizeArgs:
    examples_dir = JSON_EXAMPLES_DIR / "mermaid"

    arg_names = (
        "json_diagram_file",
        "expected_mmd_file",
    )
    arg_values = []
    ids = []

    for json_diagram_file in sorted(examples_dir.glob("*.json")):
        mmd_file = (
            ASSETS_DIR
            / "examples"
            / "mermaid"
            / json_diagram_file.with_suffix(".mmd").name
        )
        arg_values.append((json_diagram_file, mmd_file))
        ids.append(json_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__plantuml__json_to_py__parametrize() -> ParametrizeArgs:
    examples_dir = JSON_EXAMPLES_DIR / "plantuml"

    arg_names = (
        "json_diagram_file",
        "expected_py_file",
    )
    arg_values = []
    ids = []

    for json_diagram_file in sorted(examples_dir.glob("*.json")):
        py_file = (
            ASSETS_DIR
            / "examples"
            / "plantuml"
            / json_diagram_file.with_suffix(".py").name
        )
        arg_values.append((json_diagram_file, py_file))
        ids.append(json_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__plantuml__py_to_plantuml__parametrize() -> ParametrizeArgs:
    examples_dir = ASSETS_DIR / "examples" / "plantuml"

    arg_names = ("py_diagram_file",)
    arg_values = []
    ids = []

    for py_diagram_file in sorted(examples_dir.glob("*.py")):
        arg_values.append((py_diagram_file,))
        ids.append(py_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__mermaid__json_to_py__parametrize() -> ParametrizeArgs:
    examples_dir = JSON_EXAMPLES_DIR / "mermaid"

    arg_names = (
        "json_diagram_file",
        "expected_py_file",
    )
    arg_values = []
    ids = []

    for json_diagram_file in sorted(examples_dir.glob("*.json")):
        py_file = (
            ASSETS_DIR
            / "examples"
            / "mermaid"
            / json_diagram_file.with_suffix(".py").name
        )
        arg_values.append((json_diagram_file, py_file))
        ids.append(json_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__mermaid__py_to_mermaid__parametrize() -> ParametrizeArgs:
    examples_dir = ASSETS_DIR / "examples" / "mermaid"

    arg_names = ("py_diagram_file",)
    arg_values = []
    ids = []

    for py_diagram_file in sorted(examples_dir.glob("*.py")):
        arg_values.append((py_diagram_file,))
        ids.append(py_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


@pytest.mark.parametrize(**__examples__json_asset_schema__parametrize())
def test_backend_json_example_assets_validate_against_backend_schema(
    json_diagram_file: Path,
    schema_adapter: TypeAdapter,
):
    """
    Backend example assets are grouped by backend directory; mirror that
    path-level contract when validating against backend-specific schemas.
    """
    payload: dict[str, Any] = json.loads(
        json_diagram_file.read_text(encoding="utf-8")
    )

    schema = schema_adapter.validate_python(payload)

    assert schema.type == payload["type"]


@pytest.mark.parametrize(**__examples__derived_artifacts__parametrize())
def test_backend_json_example_assets_have_derived_artifacts(
    json_diagram_file: Path,
    expected_source_file: Path,
    expected_png_file: Path,
):
    assert json_diagram_file.exists()
    assert expected_source_file.exists()
    assert expected_source_file.read_text(encoding="utf-8").strip()
    assert expected_png_file.exists()
    assert expected_png_file.stat().st_size > 0


@pytest.mark.parametrize(**__examples__json_to_plantuml__parametrize())
def test_json_to_plantuml_examples(
    json_diagram_file: Path,
    expected_puml_file: Path,
    cli: CLI,
    tmp_path: Path,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"

    result = cli([
        "render",
        str(json_diagram_file),
        "--plantuml",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert diagram_output.exists()
    assert_match_snapshot(
        snapshot_file=expected_puml_file,
        diagram_code_file=diagram_output,
    )


@pytest.mark.parametrize(**__examples__json_to_mermaid__parametrize())
def test_json_to_mermaid_examples(
    json_diagram_file: Path,
    expected_mmd_file: Path,
    cli: CLI,
    tmp_path: Path,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.mmd"

    result = cli([
        "render",
        str(json_diagram_file),
        "--mermaid",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert diagram_output.exists()
    assert_match_snapshot(
        snapshot_file=expected_mmd_file,
        diagram_code_file=diagram_output,
    )


@pytest.mark.parametrize(**__examples__plantuml__json_to_py__parametrize())
def test__plantuml__json_to_python_examples(
    json_diagram_file: Path,
    expected_py_file: Path,
    cli: CLI,
    tmp_path: Path,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.py"

    result = cli([
        "convert",
        str(json_diagram_file),
        "--json-to-py",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0, result.stderr
    assert not result.stdout
    assert not result.stderr
    assert diagram_output.exists()
    assert_match_snapshot(
        snapshot_file=expected_py_file,
        diagram_code_file=diagram_output,
    )


@pytest.mark.parametrize(**__examples__plantuml__py_to_plantuml__parametrize())
def test_python_to_plantuml_examples(
    py_diagram_file: Path,
    cli: CLI,
    tmp_path: Path,
):
    diagram_output = tmp_path / "diagram.puml"

    result = cli([
        "render",
        str(py_diagram_file),
        "--plantuml",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0, result.stderr
    assert not result.stdout
    assert not result.stderr
    assert diagram_output.exists()
    assert diagram_output.read_text(encoding="utf-8").strip()


@pytest.mark.parametrize(**__examples__mermaid__json_to_py__parametrize())
def test__mermaid__json_to_python_examples(
    json_diagram_file: Path,
    expected_py_file: Path,
    cli: CLI,
    tmp_path: Path,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.py"

    result = cli([
        "convert",
        str(json_diagram_file),
        "--json-to-py",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0, result.stderr
    assert not result.stdout
    assert not result.stderr
    assert diagram_output.exists()
    assert_match_snapshot(
        snapshot_file=expected_py_file,
        diagram_code_file=diagram_output,
    )


@pytest.mark.parametrize(**__examples__mermaid__py_to_mermaid__parametrize())
def test_python_to_mermaid_examples(
    py_diagram_file: Path,
    cli: CLI,
    tmp_path: Path,
):
    diagram_output = tmp_path / "diagram.mmd"

    result = cli([
        "render",
        str(py_diagram_file),
        "--mermaid",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0, result.stderr
    assert not result.stdout
    assert not result.stderr
    assert diagram_output.exists()
    assert diagram_output.read_text(encoding="utf-8").strip()

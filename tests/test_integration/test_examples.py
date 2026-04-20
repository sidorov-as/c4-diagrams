from pathlib import Path

import pytest

from tests.conftest import CLI, AssertMatchSnapshot
from tests.utils import ASSETS_DIR, ParametrizeArgs


def __examples__json_to_plantuml__parametrize() -> ParametrizeArgs:
    examples_dir = ASSETS_DIR / "examples" / "plantuml"

    arg_names = (
        "json_diagram_file",
        "expected_puml_file",
    )
    arg_values = []
    ids = []

    for json_diagram_file in examples_dir.glob("*.json"):
        puml_file = json_diagram_file.with_suffix(".puml")
        arg_values.append((json_diagram_file, puml_file))
        ids.append(json_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__json_to_mermaid__parametrize() -> ParametrizeArgs:
    examples_dir = ASSETS_DIR / "examples" / "mermaid"

    arg_names = (
        "json_diagram_file",
        "expected_mmd_file",
    )
    arg_values = []
    ids = []

    for json_diagram_file in examples_dir.glob("*.json"):
        puml_file = json_diagram_file.with_suffix(".mmd")
        arg_values.append((json_diagram_file, puml_file))
        ids.append(json_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__plantuml__json_to_py__parametrize() -> ParametrizeArgs:
    examples_dir = ASSETS_DIR / "examples" / "plantuml"

    arg_names = (
        "json_diagram_file",
        "expected_py_file",
    )
    arg_values = []
    ids = []

    for json_diagram_file in examples_dir.glob("*.json"):
        py_file = json_diagram_file.with_suffix(".py")
        arg_values.append((json_diagram_file, py_file))
        ids.append(json_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


def __examples__mermaid__json_to_py__parametrize() -> ParametrizeArgs:
    examples_dir = ASSETS_DIR / "examples" / "mermaid"

    arg_names = (
        "json_diagram_file",
        "expected_py_file",
    )
    arg_values = []
    ids = []

    for json_diagram_file in examples_dir.glob("*.json"):
        py_file = json_diagram_file.with_suffix(".py")
        arg_values.append((json_diagram_file, py_file))
        ids.append(json_diagram_file.name)

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


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

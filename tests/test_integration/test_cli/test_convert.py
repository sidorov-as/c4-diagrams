import sys
import textwrap
from pathlib import Path

import pytest

from tests.test_integration.test_cli.conftest import CLI


def test_convert__json_to_py(
    tmp_path: Path,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    diagram_output = tmp_path / "diagram.py"
    json_diagram.write_text(
        """
        {"type": "SystemContextDiagram", "title": "Example"}
        """
    )
    expected_py_diagram = textwrap.dedent(
        """
        from c4 import (
            SystemContextDiagram,
        )


        with SystemContextDiagram(title='Example'):
            pass
        """
    ).strip()

    result = cli([
        "convert",
        str(json_diagram),
        "--json-to-py",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert diagram_output.exists()
    assert diagram_output.read_text(encoding="utf-8") == expected_py_diagram


def test_convert__json_to_py__to_stdout(
    tmp_path: Path,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    json_diagram.write_text(
        """
        {"type": "SystemContextDiagram", "title": "Example"}
        """
    )
    expected_py_diagram = textwrap.dedent(
        """
        from c4 import (
            SystemContextDiagram,
        )


        with SystemContextDiagram(title='Example'):
            pass
        """
    ).strip()

    result = cli([
        "convert",
        str(json_diagram),
        "--json-to-py",
    ])

    assert result.exit_code == 0
    assert not result.stderr
    assert result.stdout == expected_py_diagram


def test_convert__target_not_found(
    tmp_path: Path,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    diagram_output = tmp_path / "diagram.py"
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        f"c4: error: Diagram file not found: {json_diagram!s}.\n"
    )

    result = cli([
        "convert",
        str(json_diagram),
        "--json-to-py",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error
    assert not json_diagram.exists()
    assert not diagram_output.exists()


@pytest.mark.parametrize(
    ("args", "expected_message"),
    [
        (
            ["convert"],
            "the following arguments are required: target",
        ),
        (
            ["convert", "--json-to-py"],
            "the following arguments are required: target",
        ),
    ],
)
def test_convert__requires_target(
    args: list[str],
    expected_message: str,
    cli: CLI,
):
    result = cli(args)

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_message in result.stderr


def test_convert__rejects_from_and_from_json_together(
    tmp_path: Path,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    json_diagram.write_text(
        """
        {"type": "SystemContextDiagram", "title": "Example"}
        """,
        encoding="utf-8",
    )

    result = cli([
        "convert",
        str(json_diagram),
        "--from",
        "json",
        "--from-json",
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert "not allowed with argument --from" in result.stderr


def test_convert__rejects_to_and_to_py_together(
    tmp_path: Path,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    json_diagram.write_text(
        """
        {"type": "SystemContextDiagram", "title": "Example"}
        """,
        encoding="utf-8",
    )

    result = cli([
        "convert",
        str(json_diagram),
        "--to",
        "py",
        "--to-py",
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert "not allowed with argument --to" in result.stderr


@pytest.mark.parametrize(
    ("option", "value"),
    [
        ("--from", "py"),
        ("--to", "json"),
    ],
)
def test_convert__rejects_invalid_format_choice(
    tmp_path: Path,
    option: str,
    value: str,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    json_diagram.write_text(
        """
        {"type": "SystemContextDiagram", "title": "Example"}
        """,
        encoding="utf-8",
    )

    result = cli([
        "convert",
        str(json_diagram),
        option,
        value,
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert "invalid choice" in result.stderr


def test_convert__help_contains_supported_arguments(
    cli: CLI,
):
    result = cli(["convert", "--help"])

    assert result.exit_code == 0
    assert not result.stderr
    assert "--json-to-py" in result.stdout
    assert "--from" in result.stdout
    assert "--from-json" in result.stdout
    assert "--to" in result.stdout
    assert "--to-py" in result.stdout
    assert "--output" in result.stdout


@pytest.mark.skipif(
    sys.version_info <= (3, 14),
    reason="Different JSON parsing error",
)
def test_convert__invalid_json(
    tmp_path: Path,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    json_diagram.write_text(
        """
        {
            "type": "SystemContextDiagram",
            "title": "Example",
            "elements": [
                {
                    "type": "Person",
                    "title": "Person 1",
                    "alias": "person"
                },
            ]
        }
        """
    )
    diagram_output = tmp_path / "diagram.py"
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        "c4: error: "
        "Failed to parse JSON diagram: "
        "Illegal trailing comma before end of array: "
        "line 10 column 18 (char 265).\n"
    )

    result = cli([
        "convert",
        str(json_diagram),
        "--json-to-py",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error
    assert not diagram_output.exists()


def test_convert__invalid_json_schema(
    tmp_path: Path,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    json_diagram.write_text(
        """
        {
            "type": "SystemContextDiagram",
            "title": "Example",
            "elements": [
                {
                    "type": "Unknown",
                    "title": "Person 1",
                    "alias": "person"
                }
            ]
        }
        """
    )
    diagram_output = tmp_path / "diagram.py"
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        "c4: error: "
        "JSON diagram schema validation failed:\n"
        "root->SystemContextDiagram->elements[0]->PersonSchema->type: Input should be 'Person'\n"
        "root->SystemContextDiagram->elements[0]->PersonSchema->label: Field required\n"
    )

    result = cli([
        "convert",
        str(json_diagram),
        "--json-to-py",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr
    assert not diagram_output.exists()


def test_convert__duplicated_aliases(
    tmp_path: Path,
    cli: CLI,
):
    json_diagram = tmp_path / "diagram.json"
    json_diagram.write_text(
        """
        {
            "type": "SystemContextDiagram",
            "title": "Example",
            "elements": [
                {
                    "type": "Person",
                    "label": "Person 1",
                    "alias": "person"
                },
                {
                    "type": "Person",
                    "label": "Person 1",
                    "alias": "person"
                }
            ]
        }
        """
    )
    diagram_output = tmp_path / "diagram.py"
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        "c4: error: Duplicated alias 'person': "
        "Person(alias='person', label='Person 1').\n"
    )

    result = cli([
        "convert",
        str(json_diagram),
        "--json-to-py",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error
    assert not diagram_output.exists()

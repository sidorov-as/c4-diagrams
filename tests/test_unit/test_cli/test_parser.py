import argparse
import textwrap
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from c4.cli import main
from c4.cli.parser import (
    HelpFormatter,
    _env_default,
    _output_file_path,
    _plantuml_bin_type,
    _plantuml_jar_type,
)
from tests.conftest import MakeTmpPyFile


@pytest.mark.parametrize(
    ("text", "width", "expected"),
    [
        (
            "hello world\nfoo bar",
            5,
            ["hello", "world", "foo", "bar"],
        ),
        (
            "  hello   world  \n  foo  ",
            5,
            ["hello", "world", "foo"],
        ),
        (
            "hello\n\nworld",
            80,
            ["hello", "world"],
        ),
    ],
)
def test_help_formatter__split_lines_wraps_each_line_separately(
    text: str,
    width: int,
    expected: list[str],
):
    formatter = HelpFormatter(prog="prog")

    result = formatter._split_lines(text, width)

    assert result == expected


def test_plantuml_bin_type_returns_value_when_found(mocker: MockerFixture):
    mocker.patch("shutil.which", return_value="/usr/bin/plantuml")

    result = _plantuml_bin_type("plantuml")

    assert result == "plantuml"


def test_plantuml_bin_type_raises_when_not_found(mocker: MockerFixture):
    mocker.patch("shutil.which", return_value=None)
    expected_error = (
        "PlantUML binary 'plantuml' was not found in PATH or is not executable."
    )

    with pytest.raises(argparse.ArgumentTypeError, match=expected_error):
        _plantuml_bin_type("plantuml")


def test_plantuml_jar_type_returns_path_for_existing_file(tmp_path: Path):
    jar = tmp_path / "plantuml.jar"
    jar.write_bytes(b"stub")

    result = _plantuml_jar_type(str(jar))

    assert result == jar


def test_plantuml_jar_type_raises_when_path_does_not_exist(tmp_path: Path):
    jar = tmp_path / "missing.jar"
    expected_error = f"PlantUML jar file does not exist: {str(jar)!r}."

    with pytest.raises(argparse.ArgumentTypeError, match=expected_error):
        _plantuml_jar_type(str(jar))


def test_plantuml_jar_type_raises_when_path_is_not_a_file(tmp_path: Path):
    jar_dir = tmp_path / "plantuml.jar"
    jar_dir.mkdir()
    expected_error = f"PlantUML jar path is not a file: {str(jar_dir)!r}."

    with pytest.raises(argparse.ArgumentTypeError, match=expected_error):
        _plantuml_jar_type(str(jar_dir))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("out.txt", Path("out.txt")),
        ("nested/out.txt", Path("nested/out.txt")),
    ],
)
def test_output_file_path_returns_path_for_valid_file_path(
    tmp_path: Path,
    raw: str,
    expected: Path,
):
    if raw.startswith("nested/"):
        (tmp_path / "nested").mkdir()

    cwd = tmp_path
    raw_in_tmp = str(cwd / raw)

    result = _output_file_path(raw_in_tmp)

    assert result == (cwd / expected)


def test_output_file_path_raises_for_existing_directory(tmp_path: Path):
    out_dir = tmp_path / "out"
    out_dir.mkdir()

    with pytest.raises(
        argparse.ArgumentTypeError,
        match=r"expected a file path",
    ):
        _output_file_path(str(out_dir))


@pytest.mark.parametrize(
    "raw",
    [
        "missing/out.txt",
        "missing/nested/out.txt",
    ],
)
def test_output_file_path_missing_parent_directory(
    tmp_path: Path,
    raw: str,
):
    path = tmp_path / raw
    parent = str(path.parent)

    with pytest.raises(
        argparse.ArgumentTypeError,
        match=rf"Directory '{parent}' does not exist\.",
    ):
        _output_file_path(path)


def test_output_file_path_allows_existing_file(tmp_path: Path):
    out_file = tmp_path / "out.txt"
    out_file.write_text("x", encoding="utf-8")

    result = _output_file_path(str(out_file))

    assert result == out_file


def test_env_default_returns_first_env_value_when_set(mocker: MockerFixture):
    getenv = mocker.patch("os.getenv", return_value="http://example")

    result = _env_default(["A", "B"])

    assert result == "http://example"
    getenv.assert_called_once_with("A")


def test_env_default_returns_second_env_value_when_set(mocker: MockerFixture):
    getenv = mocker.patch("os.getenv", side_effect=[None, "http://example"])

    result = _env_default(["A", "B"])

    assert result == "http://example"
    getenv.assert_has_calls([mocker.call("A"), mocker.call("B")])


def test_env_default_returns_second_env_value_not_set(mocker: MockerFixture):
    getenv = mocker.patch("os.getenv", side_effect=[None, None])

    result = _env_default(["A", "B"])

    assert result is None
    getenv.assert_has_calls([mocker.call("A"), mocker.call("B")])


def test_env_default_casts_value_when_cast_provided(mocker: MockerFixture):
    getenv = mocker.patch("os.getenv", return_value="123")

    result = _env_default(["A"], cast=int)

    assert result == 123
    getenv.assert_called_once_with("A")


def test_env_default_raises_argument_type_error_when_cast_fails(
    mocker: MockerFixture,
):
    mocker.patch("os.getenv", return_value="nope")

    with pytest.raises(
        argparse.ArgumentTypeError,
        match=r"Invalid value for env var A: 'nope'",
    ):
        _env_default(["A"], cast=int)


def test_render_default_cli_args(
    mocker: MockerFixture,
    make_tmp_py_file: MakeTmpPyFile,
):
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )
    mocked_handle_render = mocker.patch(
        "c4.cli.parser.handle_render", return_value=0
    )

    main(["render", str(module_path)])

    mocked_handle_render.assert_called_once()
    args = mocked_handle_render.call_args.args[0]
    assert isinstance(args, argparse.Namespace)
    assert args.target == str(module_path)
    assert args.renderer == "plantuml"


def test_export_default_cli_args(
    mocker: MockerFixture,
    make_tmp_py_file: MakeTmpPyFile,
):
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )
    mocked_handle_render = mocker.patch(
        "c4.cli.parser.handle_export", return_value=0
    )

    main(["export", str(module_path)])

    mocked_handle_render.assert_called_once()
    args = mocked_handle_render.call_args.args[0]
    assert isinstance(args, argparse.Namespace)
    assert args.target == str(module_path)
    assert args.renderer == "plantuml"
    assert args.format == "png"
    assert args.timeout == 30.0
    assert args.plantuml_backend == "local"
    assert args.plantuml_bin == "plantuml"
    assert args.java_bin == "java"
    assert args.plantuml_server_url == "https://www.plantuml.com/plantuml"

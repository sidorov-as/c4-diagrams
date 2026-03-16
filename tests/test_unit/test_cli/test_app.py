from __future__ import annotations

import argparse
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from c4 import SVG
from c4.cli import entrypoint, main
from c4.cli.exceptions import CLIError
from c4.cli.options import ExportCLIOptions, RenderCLIOptions
from c4.diagrams.core import Diagram
from c4.renderers import PlantUMLRenderer


def test_main_render_success(
    tmp_path: Path,
    mocker: MockerFixture,
):
    diagram_output = tmp_path / "diagram.puml"
    mocked_renderer = mocker.create_autospec(spec=PlantUMLRenderer)
    mocked_diagram = mocker.create_autospec(spec=Diagram)
    mocked_resolve_diagram = mocker.patch(
        "c4.cli.commands.resolve_diagram",
        autospec=True,
        return_value=mocked_diagram,
    )
    mocked_build_renderer = mocker.patch(
        "c4.cli.commands.build_renderer",
        autospec=True,
        return_value=mocked_renderer,
    )
    mocked_renderer.render.return_value = "diagram source"

    result = main(["render", "module:diagram", "-o", str(diagram_output)])

    assert result == 0
    assert diagram_output.read_text(encoding="utf-8") == "diagram source"
    mocked_resolve_diagram.assert_called_once_with("module:diagram")
    mocked_build_renderer.assert_called_once()
    assert isinstance(mocked_build_renderer.call_args.args[0], RenderCLIOptions)
    mocked_renderer.render.assert_called_once_with(mocked_diagram)


def test_main_export_success(
    tmp_path: Path,
    mocker: MockerFixture,
    capsys,
):
    diagram_output = tmp_path / "diagram.png"
    mocked_renderer = mocker.create_autospec(spec=PlantUMLRenderer)
    mocked_diagram = mocker.create_autospec(spec=Diagram)
    mocked_resolve_diagram = mocker.patch(
        "c4.cli.commands.resolve_diagram",
        autospec=True,
        return_value=mocked_diagram,
    )
    mocked_build_exporter = mocker.patch(
        "c4.cli.commands.build_exporter",
        autospec=True,
        return_value=mocked_renderer,
    )
    mocked_renderer.render_bytes.return_value = b"diagram"

    result = main([
        "export",
        "module:diagram",
        "-f",
        SVG.value,
        "-o",
        str(diagram_output),
    ])

    assert result == 0, capsys.readouterr().err
    assert diagram_output.read_bytes() == b"diagram"
    mocked_resolve_diagram.assert_called_once_with("module:diagram")
    mocked_build_exporter.assert_called_once()
    assert isinstance(mocked_build_exporter.call_args.args[0], ExportCLIOptions)
    mocked_renderer.render_bytes.assert_called_once_with(
        mocked_diagram,
        format=SVG,
    )


@pytest.mark.parametrize(
    ("command", "handler"),
    [
        ("render", "handle_render"),
        ("export", "handle_export"),
    ],
)
def test_main_broken_pipe_error_returns_zero(
    mocker: MockerFixture, command: str, handler: str
):
    mocked_handler = mocker.patch(
        f"c4.cli.parser.{handler}", autospec=True, side_effect=BrokenPipeError()
    )

    result = main([command, "module:diagram"])

    assert result == 0
    mocked_handler.assert_called_once()
    args = mocked_handler.call_args.args[0]
    assert isinstance(args, argparse.Namespace)
    assert args.command == command
    assert args.target == "module:diagram"


@pytest.mark.parametrize(
    ("command", "handler"),
    [
        ("render", "handle_render"),
        ("export", "handle_export"),
    ],
)
def test_main_cli_error_returns_two(
    mocker: MockerFixture,
    command: str,
    handler: str,
    capsys: pytest.CaptureFixture[str],
):
    mocked_handler = mocker.patch(
        f"c4.cli.parser.{handler}",
        autospec=True,
        side_effect=CLIError("An error has occurred"),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        "c4: error: An error has occurred\n"
    )

    with pytest.raises(SystemExit) as exc_info:
        main([command, "module:diagram"])

    assert exc_info.value.code == 2
    mocked_handler.assert_called_once()
    args = mocked_handler.call_args.args[0]
    assert isinstance(args, argparse.Namespace)
    assert args.command == command
    assert args.target == "module:diagram"
    assert capsys.readouterr().err == expected_error


@pytest.mark.parametrize(
    ("command", "handler"),
    [
        ("render", "handle_render"),
        ("export", "handle_export"),
    ],
)
def test_main_exception_returns_two(
    mocker: MockerFixture,
    command: str,
    handler: str,
    capsys: pytest.CaptureFixture[str],
):
    mocked_handler = mocker.patch(
        f"c4.cli.parser.{handler}",
        autospec=True,
        side_effect=Exception("Unhandled error"),
    )
    expected_error = "Exception: Unhandled error"

    exit_code = main([command, "module:diagram"])

    stderr = capsys.readouterr().err
    assert exit_code == 2
    mocked_handler.assert_called_once()
    args = mocked_handler.call_args.args[0]
    assert isinstance(args, argparse.Namespace)
    assert args.command == command
    assert args.target == "module:diagram"
    assert expected_error in stderr
    assert "Traceback (most recent call last):" in stderr


def test_entrypoint(
    mocker: MockerFixture,
):
    main = mocker.patch("c4.cli.app.main", autospec=True, return_value=2)

    with pytest.raises(SystemExit) as exc_info:
        entrypoint()

    assert exc_info.value.code == 2
    main.assert_called_once_with()

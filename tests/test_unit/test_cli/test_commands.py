import argparse
from pathlib import Path

from pytest_mock import MockerFixture

from c4 import PNG
from c4.cli import commands
from c4.cli.commands import handle_export, handle_render
from c4.constants import LOCAL_BACKEND
from c4.diagrams.core import Diagram
from c4.renderers import BaseRenderer


def test_handle_render(
    tmp_path: Path,
    mocker: MockerFixture,
):
    diagram_output = tmp_path / "diagram.puml"
    args = argparse.Namespace(target="module:diagram", output=diagram_output)
    spied_build_render_cli_options = mocker.spy(
        commands, "build_render_cli_options"
    )
    diagram = Diagram()
    resolve_diagram = mocker.patch.object(
        commands,
        "resolve_diagram",
        autospec=True,
        return_value=diagram,
    )
    renderer = mocker.Mock(spec=BaseRenderer)
    renderer.render.return_value = "diagram-source"
    build_renderer = mocker.patch.object(
        commands,
        "build_renderer",
        autospec=True,
        return_value=renderer,
    )

    result = handle_render(args)

    assert result == 0
    resolve_diagram.assert_called_once_with("module:diagram")
    build_renderer.assert_called_once_with(
        spied_build_render_cli_options.spy_return
    )
    renderer.render.assert_called_once_with(diagram)
    assert diagram_output.read_text(encoding="utf-8") == "diagram-source"


def test_handle_export(
    mocker: MockerFixture,
    tmp_path: Path,
):
    diagram_output = tmp_path / "diagram.png"
    args = argparse.Namespace(
        target="module:diagram",
        format=PNG,
        output=diagram_output,
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url=None,
        plantuml_bin="plantuml",
        plantuml_jar=None,
        java_bin=None,
        plantuml_skinparam_dpi=None,
        timeout=None,
    )
    spied_build_export_cli_options = mocker.spy(
        commands, "build_export_cli_options"
    )
    diagram = Diagram()
    resolve_diagram = mocker.patch.object(
        commands,
        "resolve_diagram",
        autospec=True,
        return_value=diagram,
    )
    exporter = mocker.Mock(spec=["render_bytes"])
    exporter.render_bytes.return_value = b"content"
    build_exporter = mocker.patch.object(
        commands,
        "build_exporter",
        autospec=True,
        return_value=exporter,
    )

    result = handle_export(args)

    assert result == 0
    spied_build_export_cli_options.assert_called_once_with(args)
    resolve_diagram.assert_called_once_with("module:diagram")
    build_exporter.assert_called_once_with(
        spied_build_export_cli_options.spy_return
    )
    exporter.render_bytes.assert_called_once_with(diagram, format=PNG)
    assert diagram_output.read_bytes() == b"content"

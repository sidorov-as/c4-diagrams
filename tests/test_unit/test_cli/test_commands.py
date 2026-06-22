import argparse
import re
import textwrap
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from c4 import PNG
from c4.cli import commands
from c4.cli.commands import handle_convert, handle_export, handle_render
from c4.cli.context import CommandContext
from c4.cli.exceptions import CLIError
from c4.cli.options import (
    ExportCLIOptions,
    MermaidExportCLIOptions,
    PlantUMLRenderCLIOptions,
    RenderCLIOptions,
)
from c4.cli.watch import WatchOptions
from c4.constants import LOCAL_BACKEND, MERMAID, PLANTUML
from c4.diagrams.core import Diagram
from c4.renderers import BaseRenderer


def _context(
    args: argparse.Namespace,
    argv: tuple[str, ...] = (),
) -> CommandContext:
    return CommandContext(args=args, argv=argv)


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

    result = handle_render(_context(args))

    assert result == 0
    resolve_diagram.assert_called_once_with("module:diagram")
    build_renderer.assert_called_once_with(
        spied_build_render_cli_options.spy_return
    )
    renderer.render.assert_called_once_with(diagram)
    assert diagram_output.read_text(encoding="utf-8") == "diagram-source"


def test_handle_render__json_backend_mismatch_cli_renderer(
    mocker: MockerFixture,
    tmp_path: Path,
):
    diagram_output = tmp_path / "diagram.puml"
    args = argparse.Namespace(
        target="diagram.json",
        renderer="plantuml",
        output=diagram_output,
        plantuml_use_new_c4_style=False,
    )
    build_render_cli_options = mocker.patch.object(
        commands,
        "build_render_cli_options",
        autospec=True,
        side_effect=CLIError(
            "JSON diagram backend 'mermaid' does not match "
            "selected renderer 'plantuml'."
        ),
    )
    build_renderer = mocker.patch.object(
        commands,
        "build_renderer",
        autospec=True,
    )
    expected_error = (
        "JSON diagram backend 'mermaid' does not match "
        "selected renderer 'plantuml'."
    )

    with pytest.raises(CLIError, match=expected_error):
        handle_render(_context(args))

    build_render_cli_options.assert_called_once_with(args)
    build_renderer.assert_not_called()
    assert not diagram_output.exists()


def test_handle_render__watch_resolves_source_and_runs_watcher(
    mocker: MockerFixture,
    tmp_path: Path,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    diagram_output = tmp_path / "diagram.puml"
    args = argparse.Namespace(target=str(source_path), output=diagram_output)
    cli_options = RenderCLIOptions(
        renderer=PLANTUML,
        target=str(source_path),
        output=diagram_output,
        renderer_options=PlantUMLRenderCLIOptions(),
        watch=WatchOptions(enabled=True),
    )
    build_render_cli_options = mocker.patch.object(
        commands,
        "build_render_cli_options",
        autospec=True,
        return_value=cli_options,
    )
    render_once = mocker.patch.object(
        commands,
        "render_once",
        autospec=True,
        return_value=0,
    )
    validate_enabled_watch_options = mocker.spy(
        commands,
        "validate_enabled_watch_options",
    )
    run_with_watch = mocker.patch.object(
        commands,
        "run_with_watch",
        autospec=True,
        return_value=3,
    )

    result = handle_render(
        _context(
            args,
            (
                "render",
                str(source_path),
                "--output",
                str(diagram_output),
            ),
        )
    )

    assert result == 3
    build_render_cli_options.assert_called_once_with(args)
    validate_enabled_watch_options.assert_called_once_with(cli_options)
    assert cli_options.watch.path is None
    run_with_watch.assert_called_once_with(
        ["render", str(source_path), "--output", str(diagram_output)],
        WatchOptions(
            enabled=True,
            path=source_path.resolve(),
        ),
        diagram_output,
    )
    child_argv, watch_options, output = run_with_watch.call_args.args
    assert child_argv == [
        "render",
        str(source_path),
        "--output",
        str(diagram_output),
    ]
    assert watch_options == WatchOptions(
        enabled=True,
        path=source_path.resolve(),
    )
    assert output == diagram_output
    render_once.assert_not_called()


def test_handle_render__watch_preserves_context_argv(
    mocker: MockerFixture,
    tmp_path: Path,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    diagram_output = tmp_path / "diagram.puml"
    args = argparse.Namespace(target=str(source_path), output=diagram_output)
    cli_options = RenderCLIOptions(
        renderer=PLANTUML,
        target=str(source_path),
        output=diagram_output,
        renderer_options=PlantUMLRenderCLIOptions(),
        watch=WatchOptions(enabled=True),
    )
    mocker.patch.object(
        commands,
        "build_render_cli_options",
        autospec=True,
        return_value=cli_options,
    )
    run_with_watch = mocker.patch.object(
        commands,
        "run_with_watch",
        autospec=True,
        return_value=0,
    )

    result = handle_render(
        _context(
            args,
            (
                "render",
                str(source_path),
                "--watch",
                "--watch-delay",
                "0.5",
                "--output",
                str(diagram_output),
            ),
        )
    )

    assert result == 0
    run_with_watch.assert_called_once_with(
        ["render", str(source_path), "--output", str(diagram_output)],
        WatchOptions(enabled=True, path=source_path.resolve()),
        diagram_output,
    )


def test_handle_render__watch_requires_output(
    mocker: MockerFixture,
):
    args = argparse.Namespace(target="module:diagram", output=None)
    cli_options = RenderCLIOptions(
        renderer=PLANTUML,
        target="module:diagram",
        output=None,
        renderer_options=PlantUMLRenderCLIOptions(),
        watch=WatchOptions(enabled=True),
    )
    mocker.patch.object(
        commands,
        "build_render_cli_options",
        autospec=True,
        return_value=cli_options,
    )
    render_once = mocker.patch.object(commands, "render_once", autospec=True)
    run_with_watch = mocker.patch.object(
        commands,
        "run_with_watch",
        autospec=True,
    )

    with pytest.raises(CLIError, match=re.escape("--watch requires --output.")):
        handle_render(_context(args))

    render_once.assert_not_called()
    run_with_watch.assert_not_called()


def test_handle_render__watch_rejects_input_output_match_before_render(
    mocker: MockerFixture,
    tmp_path: Path,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    args = argparse.Namespace(target=str(source_path), output=source_path)
    cli_options = RenderCLIOptions(
        renderer=PLANTUML,
        target=str(source_path),
        output=source_path,
        renderer_options=PlantUMLRenderCLIOptions(),
        watch=WatchOptions(enabled=True),
    )
    mocker.patch.object(
        commands,
        "build_render_cli_options",
        autospec=True,
        return_value=cli_options,
    )
    render_once = mocker.patch.object(commands, "render_once", autospec=True)
    run_with_watch = mocker.patch.object(
        commands,
        "run_with_watch",
        autospec=True,
    )

    with pytest.raises(
        CLIError,
        match=re.escape(
            "--watch output must be different from the input file."
        ),
    ):
        handle_render(_context(args))

    render_once.assert_not_called()
    run_with_watch.assert_not_called()


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

    result = handle_export(_context(args))

    assert result == 0
    spied_build_export_cli_options.assert_called_once_with(args)
    resolve_diagram.assert_called_once_with("module:diagram")
    build_exporter.assert_called_once_with(
        spied_build_export_cli_options.spy_return
    )
    exporter.render_bytes.assert_called_once_with(diagram, format=PNG)
    assert diagram_output.read_bytes() == b"content"


def test_handle_export__json_backend_matches_cli_renderer(
    mocker: MockerFixture,
    tmp_path: Path,
):
    file_path = tmp_path / "diagram.json"
    file_path.write_text(
        """
        {"backend": "mermaid", "type": "SystemContextDiagram", "title": "Example"}
        """,
        encoding="utf-8",
    )
    diagram_output = tmp_path / "diagram.png"
    args = argparse.Namespace(
        target=str(file_path),
        renderer="mermaid",
        format=PNG,
        output=diagram_output,
        timeout=30.0,
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

    result = handle_export(_context(args))

    assert result == 0
    spied_build_export_cli_options.assert_called_once_with(args)
    resolve_diagram.assert_called_once_with(str(file_path))
    build_exporter.assert_called_once_with(
        spied_build_export_cli_options.spy_return
    )
    exporter.render_bytes.assert_called_once_with(diagram, format=PNG)
    assert diagram_output.read_bytes() == b"content"


def test_handle_export__json_backend_mismatch_cli_renderer(
    mocker: MockerFixture,
    tmp_path: Path,
):
    diagram_output = tmp_path / "diagram.png"
    args = argparse.Namespace(
        target="diagram.json",
        renderer="plantuml",
        format=PNG,
        output=diagram_output,
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url=None,
        plantuml_bin="plantuml",
        plantuml_jar=None,
        java_bin=None,
        plantuml_skinparam_dpi=None,
        timeout=30.0,
    )
    build_export_cli_options = mocker.patch.object(
        commands,
        "build_export_cli_options",
        autospec=True,
        side_effect=CLIError(
            "JSON diagram backend 'mermaid' does not match "
            "selected renderer 'plantuml'."
        ),
    )
    build_exporter = mocker.patch.object(
        commands,
        "build_exporter",
        autospec=True,
    )
    expected_error = (
        "JSON diagram backend 'mermaid' does not match "
        "selected renderer 'plantuml'."
    )

    with pytest.raises(CLIError, match=expected_error):
        handle_export(_context(args))

    build_export_cli_options.assert_called_once_with(args)
    build_exporter.assert_not_called()
    assert not diagram_output.exists()


def test_handle_export__watch_resolves_source_and_runs_watcher(
    mocker: MockerFixture,
    tmp_path: Path,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    diagram_output = tmp_path / "diagram.png"
    args = argparse.Namespace(target=str(source_path), output=diagram_output)
    cli_options = ExportCLIOptions(
        renderer=MERMAID,
        target=str(source_path),
        output=diagram_output,
        renderer_options=MermaidExportCLIOptions(),
        watch=WatchOptions(enabled=True),
    )
    build_export_cli_options = mocker.patch.object(
        commands,
        "build_export_cli_options",
        autospec=True,
        return_value=cli_options,
    )
    export_once = mocker.patch.object(
        commands,
        "export_once",
        autospec=True,
        return_value=0,
    )
    validate_enabled_watch_options = mocker.spy(
        commands,
        "validate_enabled_watch_options",
    )
    run_with_watch = mocker.patch.object(
        commands,
        "run_with_watch",
        autospec=True,
        return_value=3,
    )

    result = handle_export(
        _context(
            args,
            (
                "export",
                str(source_path),
                "--output",
                str(diagram_output),
            ),
        )
    )

    assert result == 3
    build_export_cli_options.assert_called_once_with(args)
    validate_enabled_watch_options.assert_called_once_with(cli_options)
    assert cli_options.watch.path is None
    run_with_watch.assert_called_once_with(
        ["export", str(source_path), "--output", str(diagram_output)],
        WatchOptions(
            enabled=True,
            path=source_path.resolve(),
        ),
        diagram_output,
    )
    child_argv, watch_options, output = run_with_watch.call_args.args
    assert child_argv == [
        "export",
        str(source_path),
        "--output",
        str(diagram_output),
    ]
    assert watch_options == WatchOptions(
        enabled=True,
        path=source_path.resolve(),
    )
    assert output == diagram_output
    export_once.assert_not_called()


def test_handle_export__watch_rejects_input_output_match_before_export(
    mocker: MockerFixture,
    tmp_path: Path,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    args = argparse.Namespace(target=str(source_path), output=source_path)
    cli_options = ExportCLIOptions(
        renderer=MERMAID,
        target=str(source_path),
        output=source_path,
        renderer_options=MermaidExportCLIOptions(),
        watch=WatchOptions(enabled=True),
    )
    mocker.patch.object(
        commands,
        "build_export_cli_options",
        autospec=True,
        return_value=cli_options,
    )
    export_once = mocker.patch.object(commands, "export_once", autospec=True)
    run_with_watch = mocker.patch.object(
        commands,
        "run_with_watch",
        autospec=True,
    )

    with pytest.raises(
        CLIError,
        match=re.escape(
            "--watch output must be different from the input file."
        ),
    ):
        handle_export(_context(args))

    export_once.assert_not_called()
    run_with_watch.assert_not_called()


def test_handle_export__watch_requires_output(
    mocker: MockerFixture,
):
    args = argparse.Namespace(target="module:diagram", output=None)
    cli_options = ExportCLIOptions(
        renderer=MERMAID,
        target="module:diagram",
        output=None,
        renderer_options=MermaidExportCLIOptions(),
        watch=WatchOptions(enabled=True),
    )
    mocker.patch.object(
        commands,
        "build_export_cli_options",
        autospec=True,
        return_value=cli_options,
    )
    export_once = mocker.patch.object(commands, "export_once", autospec=True)
    run_with_watch = mocker.patch.object(
        commands,
        "run_with_watch",
        autospec=True,
    )

    with pytest.raises(CLIError, match=re.escape("--watch requires --output.")):
        handle_export(_context(args))

    export_once.assert_not_called()
    run_with_watch.assert_not_called()


def test_handle_convert(
    mocker: MockerFixture,
    tmp_path: Path,
):
    file_path = tmp_path / "diagram.json"
    file_path.write_text(
        """
        {"type": "SystemContextDiagram", "title": "Example"}
        """
    )
    diagram_output = tmp_path / "diagram.py"
    args = argparse.Namespace(
        target=str(file_path),
        mode_shortcut="json_to_py",
        output=diagram_output,
    )
    spied_build_convert_cli_options = mocker.spy(
        commands, "build_convert_cli_options"
    )
    spied_load_json_diagram = mocker.spy(commands, "resolve_json_diagram")
    spied_diagram_to_python_code = mocker.spy(
        commands, "diagram_to_python_code"
    )
    expected_output = textwrap.dedent(
        """
        from c4 import (
            SystemContextDiagram,
        )


        with SystemContextDiagram(title='Example') as diagram:
            pass
        """
    ).strip()

    result = handle_convert(_context(args))

    assert result == 0
    spied_build_convert_cli_options.assert_called_once_with(args)
    spied_load_json_diagram.assert_called_once_with(str(file_path))
    diagram, backend = spied_load_json_diagram.spy_return
    spied_diagram_to_python_code.assert_called_once_with(
        diagram,
        backend,
    )
    assert diagram_output.read_text() == expected_output


def test_handle_convert__unsupported_conversion(
    mocker: MockerFixture,
    tmp_path: Path,
):
    file_path = tmp_path / "diagram.json"
    file_path.write_text(
        """
        {"type": "SystemContextDiagram", "title": "Example"}
        """
    )
    diagram_output = tmp_path / "diagram.py"
    args = argparse.Namespace(
        target=str(file_path),
        output=diagram_output,
        **{
            "from": "json",
            "to": "json",
        },
    )
    spied_build_convert_cli_options = mocker.spy(
        commands, "build_convert_cli_options"
    )
    spied_load_json_diagram = mocker.spy(commands, "resolve_json_diagram")
    spied_diagram_to_python_code = mocker.spy(
        commands, "diagram_to_python_code"
    )
    expected_error = "Unsupported conversion: json → json."

    with pytest.raises(CLIError, match=expected_error):
        handle_convert(_context(args))

    spied_build_convert_cli_options.assert_called_once_with(args)
    spied_load_json_diagram.assert_not_called()
    spied_diagram_to_python_code.assert_not_called()
    assert not diagram_output.exists()


def test_handle_convert__conversion_error(
    mocker: MockerFixture,
    tmp_path: Path,
):
    file_path = tmp_path / "diagram.json"
    file_path.write_text(
        """
        {"type": "Invalid diagram type"}
        """
    )
    diagram_output = tmp_path / "diagram.py"
    args = argparse.Namespace(
        target=str(file_path),
        output=diagram_output,
        **{
            "from": "json",
            "to": "py",
        },
    )
    spied_build_convert_cli_options = mocker.spy(
        commands, "build_convert_cli_options"
    )
    spied_load_json_diagram = mocker.spy(commands, "resolve_json_diagram")
    spied_diagram_to_python_code = mocker.spy(
        commands, "diagram_to_python_code"
    )
    expected_error = "JSON diagram schema validation failed"

    with pytest.raises(CLIError, match=expected_error):
        handle_convert(_context(args))

    spied_build_convert_cli_options.assert_called_once_with(args)
    spied_load_json_diagram.assert_called_once_with(str(file_path))
    spied_diagram_to_python_code.assert_not_called()
    assert not diagram_output.exists()

import argparse
import re
import sys
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from c4 import EPS, LATEX, PNG, SVG, TXT, UTXT
from c4.cli.exceptions import CLIError
from c4.cli.options import (
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    LOCAL_BACKEND,
    DiagramFormat,
    ExportCLIOptions,
    PlantUMLExportCLIOptions,
    PlantUMLRenderCLIOptions,
    RenderCLIOptions,
    RendererEnum,
    _build_plantuml_export_cli_options,
    _build_plantuml_exporter,
    _build_plantuml_render_cli_options,
    _build_plantuml_renderer,
    _get_renderer_name,
    _validate_output_format,
    build_export_cli_options,
    build_exporter,
    build_render_cli_options,
    build_renderer,
)
from c4.constants import (
    D2,
    DIAGRAM_FORMATS_BY_RENDERER,
    MERMAID,
    PLANTUML,
    REMOTE_BACKEND,
    STRUCTURIZR,
)
from c4.renderers import PlantUMLRenderer
from c4.renderers.plantuml import LocalPlantUMLBackend, RemotePlantUMLBackend


def test_render_cli_options_open_output(
    tmp_path: Path,
):
    output = tmp_path / "out.txt"
    cli_options = RenderCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="diagram",
        output=output,
        renderer_options=PlantUMLRenderCLIOptions(),
    )

    with cli_options.open_output() as out:
        out.write("hello")

    assert output.read_text(encoding="utf-8") == "hello"
    assert out.closed is True


def test_render_cli_options_open_output__output_is_none(
    tmp_path,
    capsys: pytest.CaptureFixture[str],
):
    cli_options = RenderCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="diagram",
        output=None,
        renderer_options=PlantUMLRenderCLIOptions(),
    )

    with cli_options.open_output() as out:
        out.write("hello")

    assert capsys.readouterr().out == "hello"
    assert out.closed is False
    assert out is sys.stdout


def test_export_cli_options_open_output(tmp_path: Path):
    out_path = tmp_path / "out.bin"
    renderer_options = PlantUMLExportCLIOptions()
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="diagram",
        renderer_options=renderer_options,
        output=out_path,
    )

    with cli_options.open_output() as out:
        out.write(b"abc")

    assert out_path.read_bytes() == b"abc"
    assert out.closed is True


def test_export_cli_options_open_output__output_is_none(
    capsys: pytest.CaptureFixture[str],
):
    renderer_options = PlantUMLExportCLIOptions()
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="diagram",
        renderer_options=renderer_options,
        output=None,
    )

    payload = b"abc"

    with cli_options.open_output() as out:
        out.write(payload)

    assert capsys.readouterr().out.encode() == payload
    assert out.closed is False
    assert out is sys.stdout.buffer


@pytest.mark.parametrize(
    ("cli_args", "flags", "expected"),
    [
        (
            {"renderer": PLANTUML.value},
            [],
            PLANTUML,
        ),
        (
            {"renderer": PLANTUML.value},
            [MERMAID.value],
            PLANTUML,
        ),
        (
            {"renderer": PLANTUML.value},
            [PLANTUML.value],
            PLANTUML,
        ),
        (
            {"renderer": PLANTUML.value},
            [STRUCTURIZR.value],
            PLANTUML,
        ),
        (
            {"renderer": PLANTUML.value},
            [D2.value],
            PLANTUML,
        ),
        (
            {},
            [PLANTUML.value],
            PLANTUML,
        ),
        (
            {},
            [],
            PLANTUML,
        ),
    ],
    ids=[
        "renderer_provided",
        "renderer_priority_over_plantuml",
        "renderer_priority_over_mermaid",
        "renderer_priority_over_structurizr",
        "renderer_priority_over_d2",
        "flag_provided",
        "default_renderer_is_plantuml",
    ],
)
def test_get_renderer_name(
    cli_args: dict[str, Any],
    flags: list[str],
    expected: RendererEnum,
):
    args = argparse.Namespace(**cli_args, **dict.fromkeys(flags, True))

    result = _get_renderer_name(args)

    assert result == expected


@pytest.mark.parametrize(
    ("cli_args", "flags", "renderer"),
    [
        (
            {"renderer": MERMAID.value},
            [],
            MERMAID.value,
        ),
        (
            {"renderer": STRUCTURIZR.value},
            [],
            STRUCTURIZR.value,
        ),
        (
            {"renderer": D2.value},
            [],
            D2.value,
        ),
        (
            {},
            [MERMAID.value],
            MERMAID.value,
        ),
        (
            {},
            [STRUCTURIZR.value],
            STRUCTURIZR.value,
        ),
        (
            {},
            [D2.value],
            D2.value,
        ),
        (
            {"renderer": "unknown"},
            [],
            "unknown",
        ),
    ],
)
def test_get_renderer_name_unknown(
    cli_args: dict[str, Any], flags: list[str], renderer: str
):
    args = argparse.Namespace(**cli_args, **dict.fromkeys(flags, True))
    expected_error = re.escape(
        f"Unknown renderer {renderer!r}. Allowed: plantuml."
    )

    with pytest.raises(CLIError, match=expected_error):
        _get_renderer_name(args)


@pytest.mark.parametrize(
    "renderer",
    [
        renderer
        for renderer in RendererEnum
        if renderer not in DIAGRAM_FORMATS_BY_RENDERER
    ],
)
def test_validate_output_format_unknown_renderer(
    renderer: RendererEnum, mocker: MockerFixture
):
    expected_error = (
        f"Renderer {str(renderer)!r} has no registered formats. "
        f"Allowed renderers: plantuml."
    )

    with pytest.raises(CLIError, match=expected_error):
        _validate_output_format(renderer, fmt=mocker.ANY)


@pytest.mark.parametrize(
    "fmt",
    [
        "unknown",
        *(
            fmt
            for fmt in DiagramFormat
            if fmt
            not in {
                EPS,
                LATEX,
                SVG,
                PNG,
                TXT,
                UTXT,
            }
        ),
    ],
)
def test_validate_output_format_plantuml_wrong_format(fmt: DiagramFormat):
    expected_error = (
        f"--format {str(fmt)!r} is not supported by renderer 'plantuml'. "
        "Allowed: eps, latex, png, svg, txt, utxt."
    )

    with pytest.raises(CLIError, match=expected_error):
        _validate_output_format(PLANTUML, fmt=fmt)


@pytest.mark.parametrize(
    "fmt",
    [
        EPS,
        LATEX,
        SVG,
        PNG,
        TXT,
        UTXT,
    ],
)
def test_validate_output_format_plantuml_allowed_format(fmt: DiagramFormat):
    assert _validate_output_format(PLANTUML, fmt=fmt) is fmt


def test_validate_output_format_enum_fmt_is_accepted():
    result = _validate_output_format(
        RendererEnum.PLANTUML, fmt=DiagramFormat.PNG
    )

    assert result == DiagramFormat.PNG


@pytest.mark.parametrize("output", [None, Path("/path/to/output.puml")])
def test_build_render_cli_options(mocker: MockerFixture, output: Path | None):
    mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=RendererEnum.PLANTUML,
    )
    renderer_options = PlantUMLRenderCLIOptions()
    args = argparse.Namespace(
        target="module:diagram",
        output=output,
    )

    result = build_render_cli_options(args)

    assert result.renderer == RendererEnum.PLANTUML
    assert result.target == "module:diagram"
    assert result.output is output
    assert result.renderer_options == renderer_options


@pytest.mark.parametrize("use_new_c4_style", [True, False])
def test_build_render_cli_options_c4_style(
    mocker: MockerFixture,
    use_new_c4_style: bool,
):
    mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=RendererEnum.PLANTUML,
    )
    args = argparse.Namespace(
        target="module:diagram",
        output=mocker.ANY,
        plantuml_use_new_c4_style=use_new_c4_style,
    )

    result = build_render_cli_options(args)

    assert result.renderer == RendererEnum.PLANTUML
    assert result.renderer_options.use_new_c4_style is use_new_c4_style


@pytest.mark.parametrize(
    "renderer", [renderer for renderer in RendererEnum if renderer != PLANTUML]
)
def test_build_render_cli_options_unsupported_renderer(
    mocker: MockerFixture,
    renderer: RendererEnum,
):
    mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=renderer,
    )
    args = argparse.Namespace(target="x")
    expected_error = (
        f"Renderer {renderer.value!r} is not supported by the 'render' command."
    )

    with pytest.raises(CLIError, match=expected_error):
        build_render_cli_options(args)


@pytest.mark.parametrize("use_new_c4_style", [True, False])
def test_build_plantuml_render_cli_options_c4_style(
    use_new_c4_style: bool,
):
    args = argparse.Namespace(
        plantuml_use_new_c4_style=use_new_c4_style,
    )

    result = _build_plantuml_render_cli_options(args)

    assert result.use_new_c4_style == use_new_c4_style


def test_build_renderer_plantuml():
    cli_options = RenderCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="x",
        renderer_options=PlantUMLRenderCLIOptions(),
    )

    result = build_renderer(cli_options)

    assert isinstance(result, PlantUMLRenderer)


@pytest.mark.parametrize(
    "renderer", [renderer for renderer in RendererEnum if renderer != PLANTUML]
)
def test_build_renderer_unsupported_renderer(renderer: RendererEnum):
    cli_options = RenderCLIOptions(
        renderer=renderer,
        target="x",
        renderer_options=PlantUMLRenderCLIOptions(),
    )
    expected_error = f"Unsupported renderer: {renderer.value!r}"

    with pytest.raises(CLIError, match=expected_error):
        build_renderer(cli_options)


def test_build_plantuml_renderer_new_c4_style():
    cli_options = RenderCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="x",
        renderer_options=PlantUMLRenderCLIOptions(
            use_new_c4_style=True,
        ),
    )

    result = _build_plantuml_renderer(cli_options)

    assert isinstance(result, PlantUMLRenderer)
    assert result._use_new_c4_style is True


@pytest.mark.parametrize(
    ("plantuml_bin", "plantuml_jar", "expected_bin", "expected_jar"),
    [
        ("plantuml", None, "plantuml", None),
        ("plantuml", "/path/to/plantuml.jar", None, "/path/to/plantuml.jar"),
    ],
)
def test_build_plantuml_export_cli_options_local_backend(
    plantuml_bin: str | None,
    plantuml_jar: str | None,
    expected_bin: str | None,
    expected_jar: str | None,
):
    args = argparse.Namespace(
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url=None,
        plantuml_bin=plantuml_bin,
        plantuml_jar=plantuml_jar,
        java_bin="java",
        plantuml_skinparam_dpi=300,
    )

    result = _build_plantuml_export_cli_options(args)

    assert result.plantuml_bin == expected_bin
    assert result.plantuml_jar == expected_jar
    assert result.plantuml_server_url is None
    assert result.plantuml_backend == "local"
    assert result.java_bin == "java"
    assert result.plantuml_skinparam_dpi == 300
    assert result.use_new_c4_style is False


@pytest.mark.parametrize("use_new_c4_style", [True, False])
def test_build_plantuml_export_cli_options_c4_style(
    use_new_c4_style: bool,
    mocker: MockerFixture,
):
    args = argparse.Namespace(
        plantuml_backend=mocker.ANY,
        plantuml_server_url=mocker.ANY,
        plantuml_bin=mocker.ANY,
        plantuml_jar=mocker.ANY,
        java_bin=mocker.ANY,
        plantuml_skinparam_dpi=mocker.ANY,
        plantuml_use_new_c4_style=use_new_c4_style,
    )

    result = _build_plantuml_export_cli_options(args)

    assert result.use_new_c4_style == use_new_c4_style


def test_build_plantuml_export_cli_options_remote_backend():
    args = argparse.Namespace(
        plantuml_backend=REMOTE_BACKEND,
        plantuml_server_url="https://plantuml.com",
        plantuml_bin=None,
        plantuml_jar=None,
        java_bin=None,
        plantuml_skinparam_dpi=300,
    )

    result = _build_plantuml_export_cli_options(args)

    assert result.plantuml_bin is None
    assert result.plantuml_jar is None
    assert result.plantuml_server_url == "https://plantuml.com"
    assert result.plantuml_backend == "remote"
    assert result.java_bin is None
    assert result.plantuml_skinparam_dpi == 300


def test_build_plantuml_exporter_local_backend(
    mocker: MockerFixture,
):
    mocker.patch("c4.cli.options.LocalPlantUMLBackend._resolve_backend")
    backend_init = mocker.spy(LocalPlantUMLBackend, "__init__")
    renderer_options = PlantUMLExportCLIOptions(
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url=None,
        plantuml_bin="plantuml",
        java_bin="java",
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.PNG,
        timeout=12.5,
    )

    result = _build_plantuml_exporter(cli_options)

    assert isinstance(result, PlantUMLRenderer)
    assert isinstance(result._plantuml_backend, LocalPlantUMLBackend)
    backend_init.assert_called_once_with(
        result._plantuml_backend,
        timeout_seconds=12.5,
        plantuml_bin="plantuml",
        plantuml_jar=None,
        java_bin="java",
    )


def test_build_plantuml_exporter_remote_backend(
    mocker: MockerFixture,
):
    backend_init = mocker.spy(RemotePlantUMLBackend, "__init__")
    renderer_options = PlantUMLExportCLIOptions(
        plantuml_backend=REMOTE_BACKEND,
        plantuml_server_url="https://plantuml.com",
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.PNG,
        timeout=12.5,
    )

    result = _build_plantuml_exporter(cli_options)

    assert isinstance(result, PlantUMLRenderer)
    assert isinstance(result._plantuml_backend, RemotePlantUMLBackend)
    backend_init.assert_called_once_with(
        result._plantuml_backend,
        timeout_seconds=12.5,
        server_url="https://plantuml.com",
    )


def test_build_plantuml_exporter_injects_dpi_include(mocker: MockerFixture):
    backend = mocker.create_autospec(spec=LocalPlantUMLBackend)
    mocker.patch("c4.cli.options.LocalPlantUMLBackend", return_value=backend)
    renderer_options = PlantUMLExportCLIOptions(
        plantuml_backend=LOCAL_BACKEND,
        plantuml_bin="plantuml",
        plantuml_skinparam_dpi=200,
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.PNG,
        timeout=DEFAULT_RENDERING_TIMEOUT_SECONDS,
    )
    expected_dpi_include = "skinparam dpi 200"

    result = _build_plantuml_exporter(cli_options)

    assert isinstance(result, PlantUMLRenderer)
    assert result._plantuml_backend == backend
    assert result._includes == [expected_dpi_include]


def test_build_plantuml_exporter_new_c4_style(mocker: MockerFixture):
    backend = mocker.create_autospec(spec=LocalPlantUMLBackend)
    mocker.patch("c4.cli.options.LocalPlantUMLBackend", return_value=backend)
    renderer_options = PlantUMLExportCLIOptions(
        plantuml_backend=LOCAL_BACKEND,
        plantuml_bin="plantuml",
        plantuml_skinparam_dpi=200,
        use_new_c4_style=True,
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.PNG,
        timeout=DEFAULT_RENDERING_TIMEOUT_SECONDS,
    )

    result = _build_plantuml_exporter(cli_options)

    assert isinstance(result, PlantUMLRenderer)
    assert result._plantuml_backend == backend
    assert result._use_new_c4_style is True


@pytest.mark.parametrize(
    "cli_args",
    [
        {"timeout": 10, "output": Path("/path/to/diagram.puml")},
        {"timeout": 10, "output": None},
    ],
)
def test_build_export_cli_options_maps_args_and_validates_format(
    mocker: MockerFixture,
    cli_args: dict[str, Any],
):
    mocked_get_renderer_name = mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=PLANTUML,
    )
    mocked_validate_output_format = mocker.patch(
        "c4.cli.options._validate_output_format",
        return_value=PNG,
    )
    render_options = PlantUMLExportCLIOptions()
    mocked_build_plantuml_export_cli_options = mocker.patch(
        "c4.cli.options._build_plantuml_export_cli_options",
        return_value=render_options,
    )
    expected_output = cli_args.get("output")
    expected_timeout = cli_args.get("timeout")
    args = argparse.Namespace(
        target="module:diagram",
        format=PNG,
        **cli_args,
    )

    result = build_export_cli_options(args)

    assert result.renderer == RendererEnum.PLANTUML
    assert result.target == "module:diagram"
    assert result.format == PNG
    assert result.timeout == expected_timeout
    assert result.output == expected_output
    assert result.renderer_options is render_options
    mocked_get_renderer_name.assert_called_once_with(args)
    mocked_validate_output_format.assert_called_once_with(
        result.renderer, fmt=PNG
    )
    assert result.format == mocked_validate_output_format.return_value
    mocked_build_plantuml_export_cli_options.assert_called_once_with(args)


@pytest.mark.parametrize(
    "renderer", [renderer for renderer in RendererEnum if renderer != PLANTUML]
)
def test_build_export_cli_options_unsupported_renderer(
    mocker: MockerFixture,
    renderer: RendererEnum,
):
    mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=renderer,
    )
    args = argparse.Namespace(target="x")
    expected_error = (
        f"Renderer {renderer.value!r} is not supported by the 'export' command."
    )

    with pytest.raises(CLIError, match=expected_error):
        build_export_cli_options(args)


def test_build_exporter_plantuml(
    mocker: MockerFixture,
):
    mocker.patch("c4.cli.options.LocalPlantUMLBackend._resolve_backend")
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="x",
        renderer_options=PlantUMLExportCLIOptions(),
        format=DiagramFormat.PNG,
        timeout=1.0,
    )

    result = build_exporter(cli_options)

    assert isinstance(result, PlantUMLRenderer)


@pytest.mark.parametrize(
    "renderer", [renderer for renderer in RendererEnum if renderer != PLANTUML]
)
def test_build_exporter_unsupported_renderer(renderer: RendererEnum):
    cli_options = ExportCLIOptions(
        renderer=renderer,
        target="x",
        renderer_options=PlantUMLExportCLIOptions(),
        format=DiagramFormat.PNG,
        timeout=1.0,
    )
    expected_error = f"Unsupported renderer: '{renderer.value}'"

    with pytest.raises(CLIError, match=expected_error):
        build_exporter(cli_options)

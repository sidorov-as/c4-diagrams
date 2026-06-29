import argparse
import re
import sys
from pathlib import Path
from typing import Any, Protocol

import pytest
from pytest_mock import MockerFixture

from c4 import EPS, LATEX, PNG, SVG, TXT, UTXT
from c4.cli.exceptions import CLIError, RendererBackendMismatchError
from c4.cli.options import (
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    LOCAL_BACKEND,
    ConvertCLIOptions,
    D2ExportCLIOptions,
    DiagramFormat,
    ExportCLIOptions,
    MermaidExportCLIOptions,
    PlantUMLExportCLIOptions,
    PlantUMLRenderCLIOptions,
    RenderCLIOptions,
    RendererEnum,
    _build_d2_export_cli_options,
    _build_d2_exporter,
    _build_mermaid_export_cli_options,
    _build_mermaid_exporter,
    _build_plantuml_export_cli_options,
    _build_plantuml_exporter,
    _build_plantuml_render_cli_options,
    _build_plantuml_renderer,
    _build_watch_options,
    _get_renderer_name,
    _validate_output_format,
    build_convert_cli_options,
    build_export_cli_options,
    build_exporter,
    build_render_cli_options,
    build_renderer,
    resolve_convert_formats,
)
from c4.cli.parser import build_parser
from c4.cli.watch import (
    WatchOptions,
    validate_watch_options,
    validate_watch_output,
)
from c4.constants import (
    D2,
    DEFAULT_D2_BIN,
    DEFAULT_JAVA_BIN,
    DEFAULT_MERMAID_BIN,
    DEFAULT_MERMAID_SCALE_FACTOR,
    DEFAULT_PLANTUML_BIN,
    DEFAULT_PLANTUML_SERVER_URL,
    DIAGRAM_FORMATS_BY_RENDERER,
    JAVA_BIN_ENV_VAR,
    KNOWN_RENDERERS,
    MERMAID,
    MERMAID_BIN_ENV_VAR,
    MERMAID_SCALE_FACTOR_ENV_VAR,
    PLANTUML,
    PLANTUML_BIN_ENV_VAR,
    PLANTUML_JAR_ENV_VAR,
    PLANTUML_SERVER_URL_ENV_VAR,
    PLANTUML_SKINPARAM_DPI_ENV_VAR,
    REMOTE_BACKEND,
    STRUCTURIZR,
)
from c4.enums import JSON, PDF, PY, ConvertShortcut, DiagramConvertionFormat
from c4.renderers import D2Renderer, MermaidRenderer, PlantUMLRenderer
from c4.renderers.d2 import LocalD2Backend
from c4.renderers.mermaid import LocalMermaidBackend
from c4.renderers.plantuml import LocalPlantUMLBackend, RemotePlantUMLBackend


class MakeConvertArgs(Protocol):
    def __call__(
        self,
        *,
        target: str = "diagram.json",
        output: Path | None = None,
        mode_shortcut: object = None,
        from_value: object = None,
        from_json: bool = False,
        to_value: object = None,
        to_py: bool = False,
    ) -> argparse.Namespace: ...


@pytest.fixture()
def make_convert_args() -> MakeConvertArgs:
    def _make_args(
        *,
        target: str = "diagram.json",
        output: Path | None = None,
        mode_shortcut: object = None,
        from_value: object = None,
        from_json: bool = False,
        to_value: object = None,
        to_py: bool = False,
    ) -> argparse.Namespace:
        return argparse.Namespace(
            mode_shortcut=mode_shortcut,
            **{
                "target": target,
                "output": output,
                "from": from_value,
                "from_json": from_json,
                "to": to_value,
                "to_py": to_py,
            },
        )

    return _make_args


class ParseExportArgs(Protocol):
    def __call__(
        self,
        *argv: str,
        which_result: str = "/usr/bin/fake-binary",
    ) -> argparse.Namespace: ...


@pytest.fixture()
def parse_export_args(monkeypatch: pytest.MonkeyPatch):
    def _parse_export_args(
        *argv: str,
        which_result: str = "/usr/bin/fake-binary",
    ) -> argparse.Namespace:
        monkeypatch.setattr(
            "c4.cli.parser.shutil.which",
            lambda value: which_result,
        )
        parser = build_parser()
        return parser.parse_args(["export", "diagram.py", *argv])

    return _parse_export_args


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


def test_convert_cli_options_open_output(
    tmp_path: Path,
):
    output = tmp_path / "out.txt"
    cli_options = ConvertCLIOptions(
        target="diagram.json",
        from_format=JSON,
        to_format=PY,
        output=output,
    )

    with cli_options.open_output() as out:
        out.write("hello")

    assert output.read_text(encoding="utf-8") == "hello"
    assert out.closed is True


def test_convert_cli_options_open_output__output_is_none(
    tmp_path,
    capsys: pytest.CaptureFixture[str],
):
    cli_options = ConvertCLIOptions(
        target="diagram.json",
        from_format=JSON,
        to_format=PY,
        output=None,
    )

    with cli_options.open_output() as out:
        out.write("hello")

    assert capsys.readouterr().out == "hello"
    assert out.closed is False
    assert out is sys.stdout


@pytest.mark.parametrize(
    ("cli_args", "flags", "expected"),
    [
        (
            {"renderer": PLANTUML.value},
            [],
            PLANTUML,
        ),
        (
            {"renderer": MERMAID.value},
            [],
            MERMAID,
        ),
        (
            {"renderer": D2.value},
            [],
            D2,
        ),
        (
            {},
            [MERMAID.value],
            MERMAID,
        ),
        (
            {},
            [D2.value],
            D2,
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
        "renderer_provided_plantuml",
        "renderer_provided_mermaid",
        "renderer_provided_d2",
        "renderer_provided_mermaid_flag",
        "renderer_provided_d2_flag",
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
            {"renderer": STRUCTURIZR.value},
            [],
            STRUCTURIZR.value,
        ),
        (
            {},
            [STRUCTURIZR.value],
            STRUCTURIZR.value,
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
        f"Unknown renderer {renderer!r}. Allowed: d2, mermaid, plantuml."
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
        f"Allowed renderers: d2, mermaid, plantuml."
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
                PDF,
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


@pytest.mark.parametrize("fmt", [SVG, PNG, PDF])
def test_validate_output_format_d2_allowed_format(fmt: DiagramFormat):
    assert _validate_output_format(D2, fmt=fmt) is fmt


@pytest.mark.parametrize(
    "fmt",
    [
        "unknown",
        *(fmt for fmt in DiagramFormat if fmt not in {SVG, PNG, PDF}),
    ],
)
def test_validate_output_format_d2_wrong_format(fmt: DiagramFormat):
    expected_error = (
        f"--format {str(fmt)!r} is not supported by renderer 'd2'. "
        "Allowed: pdf, png, svg."
    )

    with pytest.raises(CLIError, match=expected_error):
        _validate_output_format(D2, fmt=fmt)


@pytest.mark.parametrize("output", [None, Path("/path/to/output.puml")])
def test_build_render_cli_options__plantuml(
    mocker: MockerFixture, output: Path | None
):
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
def test_build_render_cli_options__plantuml__c4_style(
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


@pytest.mark.parametrize("output", [None, Path("/path/to/output.mmd")])
def test_build_render_cli_options__mermaid(
    mocker: MockerFixture, output: Path | None
):
    mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=RendererEnum.MERMAID,
    )
    args = argparse.Namespace(
        target="module:diagram",
        output=output,
    )

    result = build_render_cli_options(args)

    assert result.renderer == RendererEnum.MERMAID
    assert result.target == "module:diagram"
    assert result.output is output
    assert result.renderer_options is None


@pytest.mark.parametrize("output", [None, Path("/path/to/output.d2")])
def test_build_render_cli_options__d2(
    mocker: MockerFixture, output: Path | None
):
    mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=RendererEnum.D2,
    )
    args = argparse.Namespace(
        target="module:diagram",
        output=output,
    )

    result = build_render_cli_options(args)

    assert result.renderer == RendererEnum.D2
    assert result.target == "module:diagram"
    assert result.output is output
    assert result.renderer_options is None


def test_build_render_cli_options__builds_watch_options_without_validation(
    mocker: MockerFixture,
):
    mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=RendererEnum.PLANTUML,
    )
    args = argparse.Namespace(
        target="module:diagram",
        output=None,
        watch=True,
    )

    result = build_render_cli_options(args)

    assert result.output is None
    assert result.watch == WatchOptions(enabled=True)


def test_build_render_cli_options__json_backend_overrides_default_renderer(
    tmp_path: Path,
):
    diagram_path = tmp_path / "diagram.json"
    diagram_path.write_text(
        """
        {"backend": "mermaid", "type": "SystemContextDiagram", "title": "Example"}
        """,
        encoding="utf-8",
    )
    args = argparse.Namespace(
        target=str(diagram_path),
        output=None,
    )

    result = build_render_cli_options(args)

    assert result.renderer == RendererEnum.MERMAID
    assert result.renderer_options is None


def test_build_render_cli_options__json_backend_mismatched_renderer(
    tmp_path: Path,
):
    diagram_path = tmp_path / "diagram.json"
    diagram_path.write_text(
        """
        {"backend": "mermaid", "type": "SystemContextDiagram", "title": "Example"}
        """,
        encoding="utf-8",
    )
    args = argparse.Namespace(
        target=str(diagram_path),
        renderer=PLANTUML.value,
        output=None,
        plantuml_use_new_c4_style=False,
    )
    expected_error = (
        "JSON diagram backend 'mermaid' does not match "
        "selected renderer 'plantuml'."
    )

    with pytest.raises(RendererBackendMismatchError, match=expected_error):
        build_render_cli_options(args)


@pytest.mark.parametrize(
    "renderer",
    [renderer for renderer in RendererEnum if renderer not in KNOWN_RENDERERS],
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


def test_build_watch_options_defaults():
    args = argparse.Namespace()

    result = _build_watch_options(args)

    assert result == WatchOptions()


def test_build_watch_options_maps_parsed_args():
    args = argparse.Namespace(
        watch=True,
        watch_delay=1.5,
        watch_dir=["src", "assets"],
        watch_include=["*.py", "**/*.json"],
    )

    result = _build_watch_options(args)

    assert result == WatchOptions(
        enabled=True,
        delay=1.5,
        dirs=(Path("src"), Path("assets")),
        include=("*.py", "**/*.json"),
    )


def test_build_watch_options_converts_missing_repeatable_args_to_empty_tuples():
    args = argparse.Namespace(
        watch=True,
        watch_delay=0.5,
        watch_dir=None,
        watch_include=None,
    )

    result = _build_watch_options(args)

    assert result == WatchOptions(
        enabled=True,
        delay=0.5,
        dirs=(),
        include=(),
    )


@pytest.mark.parametrize("enabled", [False, True])
def test_validate_watch_output__allows_output(
    enabled: bool,
    tmp_path: Path,
):
    validate_watch_output(enabled, tmp_path / "diagram.puml")


def test_validate_watch_output__allows_missing_output_when_watch_is_disabled():
    validate_watch_output(False, None)


def test_validate_watch_output__watch_requires_output():
    with pytest.raises(CLIError, match=re.escape("--watch requires --output.")):
        validate_watch_output(True, None)


def test_validate_watch_options__disabled_options_are_ignored():
    validate_watch_options(
        WatchOptions(
            enabled=False,
            delay=0,
            dirs=(Path("missing"),),
            include=("*.py",),
        )
    )


def test_validate_watch_options__accepts_valid_options(tmp_path: Path):
    validate_watch_options(
        WatchOptions(
            enabled=True,
            delay=0.1,
            dirs=(tmp_path,),
            include=("*.py",),
        )
    )


def test_validate_watch_options__delay_must_be_positive():
    with pytest.raises(
        CLIError,
        match=re.escape("--watch-delay must be greater than 0."),
    ):
        validate_watch_options(WatchOptions(enabled=True, delay=0))


def test_validate_watch_options__watch_dirs_must_exist(tmp_path: Path):
    missing_dir = tmp_path / "missing"

    with pytest.raises(
        CLIError,
        match=re.escape(
            f"--watch-dir {str(missing_dir)!r} must be an existing directory."
        ),
    ):
        validate_watch_options(WatchOptions(enabled=True, dirs=(missing_dir,)))


def test_validate_watch_options__watch_dirs_must_be_directories(
    tmp_path: Path,
):
    file_path = tmp_path / "diagram.py"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(
        CLIError,
        match=re.escape(
            f"--watch-dir {str(file_path)!r} must be an existing directory."
        ),
    ):
        validate_watch_options(WatchOptions(enabled=True, dirs=(file_path,)))


def test_validate_watch_options__include_requires_watch_dir():
    with pytest.raises(
        CLIError,
        match=re.escape("--watch-include requires at least one --watch-dir."),
    ):
        validate_watch_options(WatchOptions(enabled=True, include=("*.py",)))


def test_build_renderer_plantuml():
    cli_options = RenderCLIOptions(
        renderer=RendererEnum.PLANTUML,
        target="x",
        renderer_options=PlantUMLRenderCLIOptions(),
    )

    result = build_renderer(cli_options)

    assert isinstance(result, PlantUMLRenderer)


def test_build_renderer_mermaid():
    cli_options = RenderCLIOptions(
        renderer=RendererEnum.MERMAID,
        target="x",
        renderer_options=None,
    )

    result = build_renderer(cli_options)

    assert isinstance(result, MermaidRenderer)


def test_build_renderer_d2():
    cli_options = RenderCLIOptions(
        renderer=RendererEnum.D2,
        target="x",
        renderer_options=None,
    )

    result = build_renderer(cli_options)

    assert isinstance(result, D2Renderer)


@pytest.mark.parametrize(
    "renderer",
    [renderer for renderer in RendererEnum if renderer not in KNOWN_RENDERERS],
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
    assert result.plantuml_server_url == "https://www.plantuml.com/plantuml"
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


@pytest.mark.parametrize("use_bundled_c4_plantuml", [True, False])
def test_build_plantuml_export_cli_options_use_bundled_c4_plantuml(
    use_bundled_c4_plantuml: bool,
    mocker: MockerFixture,
):
    args = argparse.Namespace(
        plantuml_backend=mocker.ANY,
        plantuml_server_url=mocker.ANY,
        plantuml_bin=mocker.ANY,
        plantuml_jar=mocker.ANY,
        java_bin=mocker.ANY,
        plantuml_skinparam_dpi=mocker.ANY,
        plantuml_use_bundled_c4_plantuml=use_bundled_c4_plantuml,
    )

    result = _build_plantuml_export_cli_options(args)

    assert result.use_bundled_c4_plantuml == use_bundled_c4_plantuml


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

    assert result.plantuml_bin == "plantuml"
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


def test_build_plantuml_exporter_local_backend__use_bundled_c4_plantuml(
    mocker: MockerFixture,
):
    mocker.patch("c4.cli.options.LocalPlantUMLBackend._resolve_backend")
    backend_init = mocker.spy(LocalPlantUMLBackend, "__init__")
    renderer_options = PlantUMLExportCLIOptions(
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url=None,
        plantuml_bin="plantuml",
        java_bin="java",
        use_bundled_c4_plantuml=True,
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
        plantuml_args=["-DRELATIVE_INCLUDE=."],
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


def test_build_mermaid_exporter(
    mocker: MockerFixture,
):
    mocker.patch("c4.cli.options.LocalMermaidBackend._resolve_backend")
    backend_init = mocker.spy(LocalMermaidBackend, "__init__")
    renderer_options = MermaidExportCLIOptions(
        mermaid_bin="mmdc",
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.MERMAID,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.PNG,
        timeout=12.5,
    )

    result = _build_mermaid_exporter(cli_options)

    assert isinstance(result, MermaidRenderer)
    assert isinstance(result._mermaid_backend, LocalMermaidBackend)
    backend_init.assert_called_once_with(
        result._mermaid_backend,
        timeout_seconds=12.5,
        mermaid_bin="mmdc",
        mermaid_args=["--scale=1"],
    )


def test_build_mermaid_exporter__puppeteer_options(
    mocker: MockerFixture,
    tmp_path: Path,
):
    mocker.patch("c4.cli.options.LocalMermaidBackend._resolve_backend")
    backend_init = mocker.spy(LocalMermaidBackend, "__init__")
    config_path = tmp_path / "puppeteer.json"
    renderer_options = MermaidExportCLIOptions(
        mermaid_bin="mmdc",
        puppeteer_config=config_path,
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.MERMAID,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.PNG,
        timeout=12.5,
    )

    result = _build_mermaid_exporter(cli_options)

    backend_init.assert_called_once_with(
        result._mermaid_backend,
        timeout_seconds=12.5,
        mermaid_bin="mmdc",
        mermaid_args=["--scale=1"],
        puppeteer_config=config_path,
    )


@pytest.mark.parametrize("headless", [True, False])
def test_build_mermaid_exporter__puppeteer_headless(
    mocker: MockerFixture,
    tmp_path: Path,
    headless: bool,
):
    mocker.patch("c4.cli.options.LocalMermaidBackend._resolve_backend")
    backend_init = mocker.spy(LocalMermaidBackend, "__init__")
    renderer_options = MermaidExportCLIOptions(
        mermaid_bin="mmdc",
        puppeteer_config=None,
        puppeteer_headless=headless,
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.MERMAID,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.PNG,
        timeout=12.5,
    )

    result = _build_mermaid_exporter(cli_options)

    backend_init.assert_called_once_with(
        result._mermaid_backend,
        timeout_seconds=12.5,
        mermaid_bin="mmdc",
        mermaid_args=["--scale=1"],
        puppeteer_headless=headless,
    )


def test_build_d2_exporter(
    mocker: MockerFixture,
):
    mocker.patch("c4.cli.options.LocalD2Backend._resolve_backend")
    backend_init = mocker.spy(LocalD2Backend, "__init__")
    renderer_options = D2ExportCLIOptions(
        d2_bin="d2",
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.D2,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.SVG,
        timeout=12.5,
    )

    result = _build_d2_exporter(cli_options)

    assert isinstance(result, D2Renderer)
    assert isinstance(result._d2_backend, LocalD2Backend)
    backend_init.assert_called_once_with(
        result._d2_backend,
        timeout_seconds=12.5,
        d2_bin="d2",
    )


def test_build_d2_exporter__layout(
    mocker: MockerFixture,
):
    mocker.patch("c4.cli.options.LocalD2Backend._resolve_backend")
    backend_init = mocker.spy(LocalD2Backend, "__init__")
    renderer_options = D2ExportCLIOptions(
        d2_bin="d2",
        layout="elk",
    )
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.D2,
        target="x",
        renderer_options=renderer_options,
        format=DiagramFormat.SVG,
        timeout=12.5,
    )

    result = _build_d2_exporter(cli_options)

    backend_init.assert_called_once_with(
        result._d2_backend,
        timeout_seconds=12.5,
        d2_bin="d2",
        layout="elk",
    )


def test_build_mermaid_export_cli_options():
    args = argparse.Namespace()

    result = _build_mermaid_export_cli_options(args)

    assert result.mermaid_bin == "mmdc"
    assert result.scale_factor == 1


def test_build_mermaid_export_cli_options__mermaid_bin():
    args = argparse.Namespace(
        mermaid_bin="mmdc",
    )

    result = _build_mermaid_export_cli_options(args)

    assert result.mermaid_bin == "mmdc"
    assert result.scale_factor == 1


def test_build_mermaid_export_cli_options__scale_factor():
    args = argparse.Namespace(
        mermaid_bin="mmdc",
        mermaid_scale_factor=5,
    )

    result = _build_mermaid_export_cli_options(args)

    assert result.mermaid_bin == "mmdc"
    assert result.scale_factor == 5


def test_build_mermaid_export_cli_options__puppeteer_config(tmp_path: Path):
    config_path = tmp_path / "puppeteer.json"
    args = argparse.Namespace(
        mermaid_bin="mmdc",
        mermaid_scale_factor=5,
        mermaid_puppeteer_config=config_path,
        mermaid_puppeteer_headless=None,
    )

    result = _build_mermaid_export_cli_options(args)

    assert result.puppeteer_config == config_path
    assert result.puppeteer_headless is None


@pytest.mark.parametrize("headless", [True, False])
def test_build_mermaid_export_cli_options__puppeteer_headless(
    tmp_path: Path,
    headless: bool,
):
    args = argparse.Namespace(
        mermaid_bin="mmdc",
        mermaid_scale_factor=5,
        mermaid_puppeteer_config=None,
        mermaid_puppeteer_headless=headless,
    )

    result = _build_mermaid_export_cli_options(args)

    assert result.puppeteer_config is None
    assert result.puppeteer_headless is headless


def test_build_d2_export_cli_options():
    args = argparse.Namespace()

    result = _build_d2_export_cli_options(args)

    assert result.d2_bin == DEFAULT_D2_BIN
    assert result.layout is None


def test_build_d2_export_cli_options__d2_bin():
    args = argparse.Namespace(
        d2_bin="custom-d2",
    )

    result = _build_d2_export_cli_options(args)

    assert result.d2_bin == "custom-d2"
    assert result.layout is None


def test_build_d2_export_cli_options__layout():
    args = argparse.Namespace(
        d2_bin="custom-d2",
        d2_layout="elk",
    )

    result = _build_d2_export_cli_options(args)

    assert result.d2_bin == "custom-d2"
    assert result.layout == "elk"


@pytest.mark.parametrize(
    "cli_args",
    [
        {"timeout": 10, "output": Path("/path/to/diagram.puml")},
        {"timeout": 10, "output": None},
    ],
)
def test_build_export_cli_options__plantuml__maps_args_and_validates_format(
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
    "cli_args",
    [
        {"timeout": 10, "output": Path("/path/to/diagram.puml")},
        {"timeout": 10, "output": None},
    ],
)
def test_build_export_cli_options__mermaid__maps_args_and_validates_format(
    mocker: MockerFixture,
    cli_args: dict[str, Any],
):
    mocked_get_renderer_name = mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=MERMAID,
    )
    mocked_validate_output_format = mocker.patch(
        "c4.cli.options._validate_output_format",
        return_value=PNG,
    )
    render_options = MermaidExportCLIOptions()
    mocked_build_mermaid_export_cli_options = mocker.patch(
        "c4.cli.options._build_mermaid_export_cli_options",
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

    assert result.renderer == RendererEnum.MERMAID
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
    mocked_build_mermaid_export_cli_options.assert_called_once_with(args)


@pytest.mark.parametrize(
    "cli_args",
    [
        {"timeout": 10, "output": Path("/path/to/diagram.svg")},
        {"timeout": 10, "output": None},
    ],
)
def test_build_export_cli_options__d2__maps_args_and_validates_format(
    mocker: MockerFixture,
    cli_args: dict[str, Any],
):
    mocked_get_renderer_name = mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=D2,
    )
    mocked_validate_output_format = mocker.patch(
        "c4.cli.options._validate_output_format",
        return_value=SVG,
    )
    render_options = D2ExportCLIOptions()
    mocked_build_d2_export_cli_options = mocker.patch(
        "c4.cli.options._build_d2_export_cli_options",
        return_value=render_options,
    )
    expected_output = cli_args.get("output")
    expected_timeout = cli_args.get("timeout")
    args = argparse.Namespace(
        target="module:diagram",
        format=SVG,
        **cli_args,
    )

    result = build_export_cli_options(args)

    assert result.renderer == RendererEnum.D2
    assert result.target == "module:diagram"
    assert result.format == SVG
    assert result.timeout == expected_timeout
    assert result.output == expected_output
    assert result.renderer_options is render_options
    mocked_get_renderer_name.assert_called_once_with(args)
    mocked_validate_output_format.assert_called_once_with(
        result.renderer, fmt=SVG
    )
    assert result.format == mocked_validate_output_format.return_value
    mocked_build_d2_export_cli_options.assert_called_once_with(args)


def test_build_export_cli_options__json_backend_validates_format_against_backend(
    tmp_path: Path,
):
    diagram_path = tmp_path / "diagram.json"
    diagram_path.write_text(
        """
        {"backend": "mermaid", "type": "SystemContextDiagram", "title": "Example"}
        """,
        encoding="utf-8",
    )
    args = argparse.Namespace(
        target=str(diagram_path),
        format=PDF,
        timeout=10.0,
        output=None,
    )

    result = build_export_cli_options(args)

    assert result.renderer == RendererEnum.MERMAID
    assert result.format == PDF
    assert isinstance(result.renderer_options, MermaidExportCLIOptions)


def test_build_export_cli_options__builds_watch_options_without_validation(
    mocker: MockerFixture,
):
    mocker.patch(
        "c4.cli.options._get_renderer_name",
        return_value=MERMAID,
    )
    args = argparse.Namespace(
        target="module:diagram",
        format=PNG,
        timeout=10.0,
        output=None,
        watch=True,
    )

    result = build_export_cli_options(args)

    assert result.output is None
    assert result.watch == WatchOptions(enabled=True)


def test_build_export_cli_options__json_backend_mismatched_renderer(
    tmp_path: Path,
):
    diagram_path = tmp_path / "diagram.json"
    diagram_path.write_text(
        """
        {"backend": "mermaid", "type": "SystemContextDiagram", "title": "Example"}
        """,
        encoding="utf-8",
    )
    args = argparse.Namespace(
        target=str(diagram_path),
        renderer=PLANTUML.value,
        format=PNG,
        timeout=10.0,
        output=None,
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url=None,
        plantuml_bin="plantuml",
        plantuml_jar=None,
        java_bin=None,
        plantuml_skinparam_dpi=None,
    )
    expected_error = (
        "JSON diagram backend 'mermaid' does not match "
        "selected renderer 'plantuml'."
    )

    with pytest.raises(RendererBackendMismatchError, match=expected_error):
        build_export_cli_options(args)


@pytest.mark.parametrize(
    "renderer",
    [renderer for renderer in RendererEnum if renderer not in KNOWN_RENDERERS],
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


def test_build_exporter_mermaid(
    mocker: MockerFixture,
):
    mocker.patch("c4.cli.options.LocalMermaidBackend._resolve_backend")
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.MERMAID,
        target="x",
        renderer_options=MermaidExportCLIOptions(),
        format=DiagramFormat.PNG,
        timeout=1.0,
    )

    result = build_exporter(cli_options)

    assert isinstance(result, MermaidRenderer)


def test_build_exporter_d2(
    mocker: MockerFixture,
):
    mocker.patch("c4.cli.options.LocalD2Backend._resolve_backend")
    cli_options = ExportCLIOptions(
        renderer=RendererEnum.D2,
        target="x",
        renderer_options=D2ExportCLIOptions(),
        format=DiagramFormat.SVG,
        timeout=1.0,
    )

    result = build_exporter(cli_options)

    assert isinstance(result, D2Renderer)


@pytest.mark.parametrize(
    "renderer",
    [renderer for renderer in RendererEnum if renderer not in KNOWN_RENDERERS],
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


def test_resolve_convert_formats__json_to_py_shortcut(
    make_convert_args: MakeConvertArgs,
):
    args = make_convert_args(mode_shortcut=ConvertShortcut.JSON_TO_PY)

    result = resolve_convert_formats(args)

    assert result == (JSON, PY)


@pytest.mark.parametrize(
    "from_value, from_json, to_value, to_py",
    [
        ("json", False, None, False),
        (None, True, None, False),
        (None, False, "py", False),
        (None, False, None, True),
    ],
)
def test_resolve_convert_formats__shortcut_conflict(
    make_convert_args: MakeConvertArgs,
    from_value: str | None,
    from_json: bool,
    to_value: str | None,
    to_py: bool,
):
    args = make_convert_args(
        mode_shortcut=ConvertShortcut.JSON_TO_PY,
        from_value=from_value,
        from_json=from_json,
        to_value=to_value,
        to_py=to_py,
    )
    expected_error = (
        "--json-to-py cannot be used with --from/--from-json/--to/--to-py"
    )

    with pytest.raises(CLIError, match=expected_error):
        resolve_convert_formats(args)


def test_resolve_convert_formats__unsupported_shortcut(
    make_convert_args: MakeConvertArgs,
):
    args = make_convert_args(mode_shortcut="unsupported")
    expected_error = "Unsupported conversion shortcut: 'unsupported'"

    with pytest.raises(CLIError, match=expected_error):
        resolve_convert_formats(args)


@pytest.mark.parametrize(
    ("from_value", "from_json", "to_value", "to_py", "expected"),
    [
        ("json", False, "py", False, (JSON, PY)),
        (None, True, "py", False, (JSON, PY)),
        ("json", False, None, True, (JSON, PY)),
        (
            DiagramConvertionFormat.JSON,
            False,
            DiagramConvertionFormat.PY,
            False,
            (JSON, PY),
        ),
    ],
)
def test_resolve_convert_formats__explicit_options(
    make_convert_args: MakeConvertArgs,
    from_value: str | DiagramConvertionFormat | None,
    from_json: bool,
    to_value: str | DiagramConvertionFormat | None,
    to_py: bool,
    expected: tuple[DiagramConvertionFormat, DiagramConvertionFormat],
):
    args = make_convert_args(
        from_value=from_value,
        from_json=from_json,
        to_value=to_value,
        to_py=to_py,
    )

    result = resolve_convert_formats(args)

    assert result == expected


def test_resolve_convert_formats__missing_from(
    make_convert_args: MakeConvertArgs,
):
    args = make_convert_args(to_value="py")
    expected_error = "one of the arguments --from --from-json is required"

    with pytest.raises(CLIError, match=expected_error):
        resolve_convert_formats(args)


def test_resolve_convert_formats__missing_to(
    make_convert_args: MakeConvertArgs,
):
    args = make_convert_args(from_value="json")
    expected_error = "one of the arguments --to --to-py is required"

    with pytest.raises(CLIError, match=expected_error):
        resolve_convert_formats(args)


def test_resolve_convert_formats__invalid_from(
    make_convert_args: MakeConvertArgs,
):
    args = make_convert_args(from_value="yaml", to_value="py")
    expected_error = "'yaml' is not a valid DiagramConvertionFormat"

    with pytest.raises(ValueError, match=expected_error):
        resolve_convert_formats(args)


def test_resolve_convert_formats__invalid_to(
    make_convert_args: MakeConvertArgs,
):
    args = make_convert_args(from_value="json", to_value="yaml")
    expected_error = "'yaml' is not a valid DiagramConvertionFormat"

    with pytest.raises(ValueError, match=expected_error):
        resolve_convert_formats(args)


@pytest.mark.parametrize("output", [None, Path("/path/to/output.py")])
def test_build_convert_cli_options(
    make_convert_args: MakeConvertArgs,
    output: Path | None,
):
    args = make_convert_args(
        mode_shortcut=ConvertShortcut.JSON_TO_PY,
        target="diagram.json",
        output=output,
    )

    cli_options = build_convert_cli_options(args)

    assert cli_options.target == "diagram.json"
    assert cli_options.from_format == JSON
    assert cli_options.to_format == PY
    assert cli_options.output == output


def test_build_plantuml_export_cli_options__parsed_defaults(
    parse_export_args: ParseExportArgs,
):
    args = parse_export_args()

    result = _build_plantuml_export_cli_options(args)

    assert result == PlantUMLExportCLIOptions(
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url=DEFAULT_PLANTUML_SERVER_URL,
        plantuml_bin=DEFAULT_PLANTUML_BIN,
        plantuml_jar=None,
        java_bin=DEFAULT_JAVA_BIN,
        plantuml_skinparam_dpi=None,
        use_new_c4_style=False,
        use_bundled_c4_plantuml=True,
    )


def test_build_plantuml_export_cli_options__parsed_from_env_bin(
    monkeypatch: pytest.MonkeyPatch,
    parse_export_args: ParseExportArgs,
):
    monkeypatch.setenv(PLANTUML_BIN_ENV_VAR, "plantuml-from-env")
    monkeypatch.setenv(
        PLANTUML_SERVER_URL_ENV_VAR,
        "https://plantuml-from-env.example.com",
    )
    monkeypatch.setenv(JAVA_BIN_ENV_VAR, "java-from-env")
    monkeypatch.setenv(PLANTUML_SKINPARAM_DPI_ENV_VAR, "250")
    args = parse_export_args()

    result = _build_plantuml_export_cli_options(args)

    assert result == PlantUMLExportCLIOptions(
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url="https://plantuml-from-env.example.com",
        plantuml_bin="plantuml-from-env",
        plantuml_jar=None,
        java_bin="java-from-env",
        plantuml_skinparam_dpi=250,
        use_new_c4_style=False,
        use_bundled_c4_plantuml=True,
    )


def test_build_plantuml_export_cli_options__parsed_from_env_jar_takes_precedence(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    parse_export_args: ParseExportArgs,
):
    jar_path = tmp_path / "plantuml.jar"
    jar_path.write_text("fake jar", encoding="utf-8")
    monkeypatch.setenv(PLANTUML_BIN_ENV_VAR, "plantuml-from-env")
    monkeypatch.setenv(PLANTUML_JAR_ENV_VAR, str(jar_path))
    args = parse_export_args()

    result = _build_plantuml_export_cli_options(args)

    assert result == PlantUMLExportCLIOptions(
        plantuml_backend=LOCAL_BACKEND,
        plantuml_server_url=DEFAULT_PLANTUML_SERVER_URL,
        plantuml_bin=None,
        plantuml_jar=jar_path,
        java_bin=DEFAULT_JAVA_BIN,
        plantuml_skinparam_dpi=None,
        use_new_c4_style=False,
        use_bundled_c4_plantuml=True,
    )


def test_build_plantuml_export_cli_options__parsed_cli_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    parse_export_args: ParseExportArgs,
):
    env_jar_path = tmp_path / "env-plantuml.jar"
    env_jar_path.write_text("fake jar", encoding="utf-8")
    cli_jar_path = tmp_path / "cli-plantuml.jar"
    cli_jar_path.write_text("fake jar", encoding="utf-8")
    monkeypatch.setenv(PLANTUML_BIN_ENV_VAR, "plantuml-from-env")
    monkeypatch.setenv(PLANTUML_JAR_ENV_VAR, str(env_jar_path))
    monkeypatch.setenv(PLANTUML_SKINPARAM_DPI_ENV_VAR, "150")
    args = parse_export_args(
        "--plantuml-backend",
        REMOTE_BACKEND,
        "--plantuml-server-url",
        "https://plantuml-from-cli.example.com",
        "--plantuml-jar",
        str(cli_jar_path),
        "--java-bin",
        "java-from-cli",
        "--plantuml-skinparam-dpi",
        "300",
        "--plantuml-use-new-c4-style",
        "--plantuml-use-bundled-c4-plantuml",
        "false",
    )

    result = _build_plantuml_export_cli_options(args)

    assert result == PlantUMLExportCLIOptions(
        plantuml_backend=REMOTE_BACKEND,
        plantuml_server_url="https://plantuml-from-cli.example.com",
        plantuml_bin=None,
        plantuml_jar=cli_jar_path,
        java_bin="java-from-cli",
        plantuml_skinparam_dpi=300,
        use_new_c4_style=True,
        use_bundled_c4_plantuml=False,
    )


def test_build_mermaid_export_cli_options__parsed_defaults(
    parse_export_args: ParseExportArgs,
):
    args = parse_export_args()

    result = _build_mermaid_export_cli_options(args)

    assert result == MermaidExportCLIOptions(
        mermaid_bin=DEFAULT_MERMAID_BIN,
        scale_factor=DEFAULT_MERMAID_SCALE_FACTOR,
    )


def test_build_mermaid_export_cli_options__parsed_from_env(
    monkeypatch: pytest.MonkeyPatch,
    parse_export_args: ParseExportArgs,
):
    monkeypatch.setenv(MERMAID_BIN_ENV_VAR, "mmdc-from-env")
    monkeypatch.setenv(MERMAID_SCALE_FACTOR_ENV_VAR, "4")
    args = parse_export_args()

    result = _build_mermaid_export_cli_options(args)

    assert result == MermaidExportCLIOptions(
        mermaid_bin="mmdc-from-env",
        scale_factor=4,
    )


def test_build_mermaid_export_cli_options__parsed_cli_overrides_env(
    monkeypatch: pytest.MonkeyPatch,
    parse_export_args: ParseExportArgs,
):
    monkeypatch.setenv(MERMAID_BIN_ENV_VAR, "mmdc-from-env")
    monkeypatch.setenv(MERMAID_SCALE_FACTOR_ENV_VAR, "4")
    args = parse_export_args(
        "--mermaid-bin",
        "mmdc-from-cli",
        "--mermaid-scale-factor",
        "7",
    )

    result = _build_mermaid_export_cli_options(args)

    assert result == MermaidExportCLIOptions(
        mermaid_bin="mmdc-from-cli",
        scale_factor=7,
    )

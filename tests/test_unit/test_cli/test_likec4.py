from __future__ import annotations

import argparse

import pytest
from pytest_mock import MockerFixture

from c4.cli.exceptions import CLIError
from c4.cli.options import (
    ExportCLIOptions,
    LikeC4ExportCLIOptions,
    _build_likec4_export_cli_options,
    _build_likec4_exporter,
    _get_renderer_name,
    build_export_cli_options,
    build_exporter,
    build_render_cli_options,
    build_renderer,
)
from c4.cli.parser import _likec4_bin_type, build_parser
from c4.constants import DEFAULT_LIKEC4_BIN, LIKEC4_BIN_ENV_VAR
from c4.contrib.likec4 import Project
from c4.contrib.likec4.renderer import LikeC4Renderer, LocalLikeC4Backend
from c4.enums import JPG, PNG, SVG, RendererEnum

WHICH = "c4.contrib.likec4.renderer.backends.shutil.which"


@pytest.fixture
def likec4_found(mocker: MockerFixture):
    return mocker.patch(WHICH, return_value="/usr/bin/likec4")


def _export_options(**kwargs) -> ExportCLIOptions:
    return ExportCLIOptions(
        renderer=RendererEnum.LIKEC4,
        target="x.py",
        renderer_options=LikeC4ExportCLIOptions(**kwargs),
        format=PNG,
        timeout=12.5,
    )


# --- parser ---------------------------------------------------------------


def test_likec4_bin_type_accepts_a_command(mocker: MockerFixture):
    which = mocker.patch("shutil.which", return_value="/usr/bin/npx")

    assert _likec4_bin_type("npx likec4@1.60.0") == "npx likec4@1.60.0"
    which.assert_called_once_with("npx")


def test_likec4_bin_type_rejects_missing_binary(mocker: MockerFixture):
    mocker.patch("shutil.which", return_value=None)

    with pytest.raises(
        argparse.ArgumentTypeError,
        match="LikeC4 binary 'likec4' was not found",
    ):
        _likec4_bin_type("likec4")


@pytest.mark.parametrize("value", ["", "   "])
def test_likec4_bin_type_rejects_empty_command(value):
    with pytest.raises(argparse.ArgumentTypeError, match="must not be empty"):
        _likec4_bin_type(value)


def test_likec4_bin_type_rejects_bad_quoting():
    with pytest.raises(argparse.ArgumentTypeError, match="not valid"):
        _likec4_bin_type("npx 'likec4")


def test_parser_reads_likec4_flags(mocker: MockerFixture):
    mocker.patch("shutil.which", return_value="/usr/bin/likec4")

    args = build_parser().parse_args([
        "export",
        "project.py",
        "--likec4",
        "--likec4-backend",
        "local",
        "--likec4-bin",
        "likec4",
        "--likec4-view-key",
        "index",
    ])

    assert args.likec4 is True
    assert args.likec4_backend == "local"
    assert args.likec4_bin == "likec4"
    assert args.likec4_view_key == "index"


def test_parser_reads_bin_from_environment(
    mocker: MockerFixture, monkeypatch: pytest.MonkeyPatch
):
    mocker.patch("shutil.which", return_value="/usr/bin/likec4")
    monkeypatch.setenv(LIKEC4_BIN_ENV_VAR, "likec4-from-env")

    args = build_parser().parse_args(["export", "project.py", "--likec4"])

    assert args.likec4_bin == "likec4-from-env"


def test_parser_rejects_other_likec4_backends(capsys):
    with pytest.raises(SystemExit):
        build_parser().parse_args([
            "export",
            "project.py",
            "--likec4",
            "--likec4-backend",
            "kroki",
        ])

    assert "invalid choice" in capsys.readouterr().err


def test_likec4_flag_conflicts_with_other_renderer_flags(capsys):
    with pytest.raises(SystemExit):
        build_parser().parse_args(["render", "p.py", "--likec4", "--d2"])

    assert "not allowed with argument" in capsys.readouterr().err


# --- renderer selection ----------------------------------------------------


def test_get_renderer_name_likec4_flag():
    args = argparse.Namespace(likec4=True)

    assert _get_renderer_name(args) is RendererEnum.LIKEC4


def test_get_renderer_name_explicit_likec4():
    args = argparse.Namespace(renderer="likec4")

    assert _get_renderer_name(args) is RendererEnum.LIKEC4


# --- render ---------------------------------------------------------------


def test_build_render_cli_options_likec4():
    args = argparse.Namespace(
        target="p.py", likec4=True, output=None, watch=False
    )

    options = build_render_cli_options(args)

    assert options.renderer is RendererEnum.LIKEC4
    assert options.renderer_options is None
    assert isinstance(build_renderer(options), LikeC4Renderer)


# --- export options -------------------------------------------------------


def test_build_likec4_export_cli_options_defaults():
    result = _build_likec4_export_cli_options(argparse.Namespace())

    assert result == LikeC4ExportCLIOptions(
        likec4_backend="local", likec4_bin=DEFAULT_LIKEC4_BIN, view_key=None
    )


def test_build_likec4_export_cli_options_values():
    args = argparse.Namespace(
        likec4_bin="npx likec4@1.60.0", likec4_view_key="index"
    )

    result = _build_likec4_export_cli_options(args)

    assert result.likec4_bin == "npx likec4@1.60.0"
    assert result.view_key == "index"
    assert result.local_backend_kwargs == {
        "likec4_bin": ["npx", "likec4@1.60.0"]
    }


def test_build_likec4_export_cli_options_rejects_other_backends():
    args = argparse.Namespace(likec4_backend="kroki")

    with pytest.raises(CLIError, match="--likec4-backend local"):
        _build_likec4_export_cli_options(args)


@pytest.mark.parametrize(("fmt", "expected"), [("png", PNG), ("jpg", JPG)])
def test_build_export_cli_options_likec4_formats(fmt, expected):
    args = argparse.Namespace(
        target="p.py",
        likec4=True,
        format=fmt,
        timeout=5.0,
        output=None,
        watch=False,
    )

    options = build_export_cli_options(args)

    assert options.renderer is RendererEnum.LIKEC4
    assert options.format is expected
    assert isinstance(options.renderer_options, LikeC4ExportCLIOptions)


def test_build_export_cli_options_rejects_svg_for_likec4():
    args = argparse.Namespace(
        target="p.py",
        likec4=True,
        format="svg",
        timeout=5.0,
        output=None,
        watch=False,
    )

    with pytest.raises(CLIError, match=f"--format '{SVG.value}'"):
        build_export_cli_options(args)


# --- exporter -------------------------------------------------------------


def test_build_likec4_exporter(mocker: MockerFixture, likec4_found):
    init = mocker.spy(LocalLikeC4Backend, "__init__")
    options = _export_options(likec4_bin="npx likec4@1.60.0", view_key="idx")

    result = _build_likec4_exporter(options)

    assert isinstance(result, LikeC4Renderer)
    assert result._view_key == "idx"
    assert isinstance(result._backend, LocalLikeC4Backend)
    init.assert_called_once_with(
        result._backend,
        timeout_seconds=12.5,
        likec4_bin=["npx", "likec4@1.60.0"],
    )


def test_build_exporter_dispatches_to_likec4(likec4_found):
    result = build_exporter(_export_options(), target=Project())

    assert isinstance(result, LikeC4Renderer)


def test_build_likec4_exporter_reports_missing_binary(
    mocker: MockerFixture,
):
    mocker.patch(WHICH, return_value=None)

    with pytest.raises(CLIError, match="LikeC4 is not available"):
        _build_likec4_exporter(_export_options())


def test_build_likec4_exporter_rejects_other_backends(likec4_found):
    options = _export_options()
    options.renderer_options.likec4_backend = "kroki"  # type: ignore[union-attr,assignment]

    with pytest.raises(CLIError, match="--likec4-backend local"):
        _build_likec4_exporter(options)

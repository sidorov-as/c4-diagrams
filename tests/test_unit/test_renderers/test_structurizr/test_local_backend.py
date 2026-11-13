from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from c4.constants import STRUCTURIZR_BIN_ENV_VAR
from c4.contrib.structurizr.renderer import (
    LocalStructurizrBackend,
    StructurizrBackendConfigurationError,
    StructurizrRenderingError,
)
from c4.enums import PDF, PNG, SVG

SUBPROCESS = "c4.contrib.structurizr.renderer.backends.subprocess.run"
WHICH = "c4.contrib.structurizr.renderer.backends.shutil.which"


@pytest.fixture(autouse=True)
def structurizr_on_path(mocker: MockerFixture) -> Any:
    return mocker.patch(WHICH, return_value="/usr/bin/structurizr")


def completed(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


def fake_run(
    mocker: MockerFixture,
    *,
    views: tuple[str, ...] = ("landscape", "containers"),
    result: subprocess.CompletedProcess[str] | None = None,
) -> dict[str, Any]:
    """Mock ``subprocess.run`` writing one image (and legend) per view."""
    calls: dict[str, Any] = {}

    def run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls["cmd"] = cmd
        calls["kwargs"] = kwargs
        workspace = Path(cmd[cmd.index("-w") + 1])
        out = Path(cmd[cmd.index("-o") + 1])
        fmt = cmd[cmd.index("-f") + 1]
        calls["workspace"] = workspace.read_text("utf-8")
        calls["tmp"] = out.parent
        if result is None or result.returncode == 0:
            if views:
                out.mkdir(parents=True, exist_ok=True)
            for view in views:
                (out / f"{view}.{fmt}").write_bytes(f"{view}-image".encode())
                (out / f"{view}-key.{fmt}").write_bytes(b"legend")
        return result or completed()

    mocker.patch(SUBPROCESS, side_effect=run)
    return calls


def test_to_bytes__exports_selected_view_and_cleans_up(mocker: MockerFixture):
    calls = fake_run(mocker)

    data = LocalStructurizrBackend(view_key="containers").to_bytes(
        "workspace {}", format=PNG
    )

    assert data == b"containers-image"
    cmd = calls["cmd"]
    assert cmd[:2] == ["structurizr", "export"]
    assert cmd[cmd.index("-f") + 1] == "png"
    assert calls["workspace"] == "workspace {}"
    assert calls["kwargs"]["timeout"] == 30.0
    assert not calls["tmp"].exists()


def test_to_bytes__accepts_string_format(mocker: MockerFixture):
    calls = fake_run(mocker)

    LocalStructurizrBackend(view_key="landscape").to_bytes("x", format="svg")

    assert calls["cmd"][calls["cmd"].index("-f") + 1] == SVG.value


def test_to_bytes__single_view_needs_no_view_key(mocker: MockerFixture):
    fake_run(mocker, views=("landscape",))

    data = LocalStructurizrBackend().to_bytes("x", format=PNG)

    assert data == b"landscape-image"


def test_to_bytes__several_views_need_a_view_key(mocker: MockerFixture):
    fake_run(mocker)

    with pytest.raises(
        StructurizrBackendConfigurationError,
        match=r"several views.*containers, landscape",
    ):
        LocalStructurizrBackend().to_bytes("x", format=PNG)


def test_to_bytes__unknown_view_lists_available_views(mocker: MockerFixture):
    fake_run(mocker)

    with pytest.raises(
        StructurizrRenderingError,
        match=r"View 'nope' was not exported \(available views: .*landscape",
    ):
        LocalStructurizrBackend(view_key="nope").to_bytes("x", format=PNG)


def test_to_bytes__legend_is_not_a_view(mocker: MockerFixture):
    fake_run(mocker, views=("landscape",))

    with pytest.raises(StructurizrRenderingError, match="'landscape-key'"):
        LocalStructurizrBackend(view_key="landscape-key").to_bytes(
            "x", format=PNG
        )


def test_to_bytes__dsl_errors_are_reported_without_log_noise(
    mocker: MockerFixture,
):
    fake_run(
        mocker,
        views=(),
        result=completed(
            stderr=(
                "12:00:00.000 [main] INFO Starting\n"
                "12:00:00.001 [main] ERROR Cmd -- Unexpected end of DSL"
            )
        ),
    )

    with pytest.raises(StructurizrRenderingError) as exc_info:
        LocalStructurizrBackend().to_bytes("workspace {", format=PNG)

    assert "no views" in str(exc_info.value)
    assert "Unexpected end of DSL" in str(exc_info.value)
    assert "Starting" not in str(exc_info.value)


def test_to_bytes__nonzero_exit_raises_with_output(mocker: MockerFixture):
    fake_run(mocker, result=completed(returncode=2, stderr="boom"))

    with pytest.raises(StructurizrRenderingError, match="boom"):
        LocalStructurizrBackend().to_bytes("x", format=PNG)


def test_to_bytes__timeout(mocker: MockerFixture):
    mocker.patch(SUBPROCESS, side_effect=subprocess.TimeoutExpired("c", 5))

    with pytest.raises(StructurizrRenderingError, match="timed out after 5"):
        LocalStructurizrBackend(timeout_seconds=5).to_bytes("x", format=PNG)


@pytest.mark.parametrize("format", [PDF, "eps", "nonsense"])
def test_to_bytes__rejects_unsupported_format(format: str):  # noqa: A002
    with pytest.raises(ValueError, match="Unsupported Structurizr local"):
        LocalStructurizrBackend().to_bytes("x", format=format)


def test_to_file__writes_exported_view(mocker: MockerFixture, tmp_path: Path):
    fake_run(mocker)

    output = LocalStructurizrBackend(view_key="landscape").to_file(
        "x", tmp_path / "nested" / "out.png", format=None
    )

    assert output.read_bytes() == b"landscape-image"


def test_init__command_prefix_and_env(mocker: MockerFixture):
    calls = fake_run(mocker, views=("landscape",))

    LocalStructurizrBackend(
        structurizr_bin=["npx", "structurizr"], env={"FOO": "bar"}
    ).to_bytes("x", format=PNG)

    assert calls["cmd"][:3] == ["npx", "structurizr", "export"]
    assert calls["kwargs"]["env"]["FOO"] == "bar"


def test_init__reads_bin_and_timeout_from_environment(
    monkeypatch: pytest.MonkeyPatch, mocker: MockerFixture
):
    monkeypatch.setenv(STRUCTURIZR_BIN_ENV_VAR, "my-structurizr")
    monkeypatch.setenv("RENDERING_TIMEOUT_SECONDS", "7")
    calls = fake_run(mocker, views=("landscape",))

    LocalStructurizrBackend().to_bytes("x", format=PNG)

    assert calls["cmd"][0] == "my-structurizr"
    assert calls["kwargs"]["timeout"] == 7.0


def test_init__missing_binary(mocker: MockerFixture):
    mocker.patch(WHICH, return_value=None)

    with pytest.raises(
        StructurizrBackendConfigurationError,
        match="Structurizr CLI is not available",
    ):
        LocalStructurizrBackend()


def test_init__invalid_timeout():
    with pytest.raises(
        StructurizrBackendConfigurationError, match="Invalid timeout"
    ):
        LocalStructurizrBackend(timeout_seconds="soon")  # type: ignore[arg-type]

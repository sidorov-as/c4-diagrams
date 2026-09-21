from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from c4.contrib.likec4.renderer import (
    LikeC4BackendConfigurationError,
    LikeC4LocalRenderingError,
    LocalLikeC4Backend,
)
from c4.enums import JPG, PNG, SVG

SUBPROCESS = "c4.contrib.likec4.renderer.backends.subprocess.run"
WHICH = "c4.contrib.likec4.renderer.backends.shutil.which"


@pytest.fixture(autouse=True)
def likec4_on_path(mocker: MockerFixture) -> Any:
    return mocker.patch(WHICH, return_value="/usr/bin/likec4")


def completed(
    returncode: int = 0, stdout: str = "", stderr: str = ""
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


def fake_run(
    mocker: MockerFixture,
    *,
    write: bool = True,
    result: subprocess.CompletedProcess[str] | None = None,
) -> Any:
    """Mock ``subprocess.run`` writing the file named by ``-o`` and ``-f``."""
    calls: dict[str, Any] = {}

    def run(cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        calls["cmd"] = cmd
        calls["kwargs"] = kwargs
        out = Path(cmd[cmd.index("-o") + 1])
        source = Path(cmd[-1])
        calls["source_dir"] = source
        calls["source"] = (source / "workspace.c4").read_text("utf-8")
        calls["tmp"] = out.parent
        if write and (result is None or result.returncode == 0):
            out.mkdir(parents=True, exist_ok=True)
            fmt = cmd[cmd.index("export") + 1]
            (out / f"{cmd[cmd.index('-f') + 1]}.{fmt}").write_bytes(b"img")
        return result or completed()

    mocker.patch(SUBPROCESS, side_effect=run)
    return calls


def test_to_bytes_runs_export_and_cleans_up(mocker: MockerFixture):
    calls = fake_run(mocker)

    data = LocalLikeC4Backend().to_bytes("model {}", format=PNG, view_key="idx")

    assert data == b"img"
    cmd = calls["cmd"]
    assert cmd[:4] == ["likec4", "export", "png", "--flat"]
    assert cmd[cmd.index("-f") + 1] == "idx"
    assert calls["source"] == "model {}"
    assert calls["kwargs"]["timeout"] == 30.0
    assert not calls["tmp"].exists()


def test_jpg_format_and_string_format(mocker: MockerFixture):
    calls = fake_run(mocker)

    LocalLikeC4Backend().to_bytes("x", format="jpg", view_key="v")

    assert calls["cmd"][2] == JPG.value


def test_custom_command_prefix(mocker: MockerFixture, likec4_on_path: Any):
    calls = fake_run(mocker)
    backend = LocalLikeC4Backend(likec4_bin=["npx", "likec4@1.60.0"])

    backend.to_bytes("x", format=PNG, view_key="v")

    assert calls["cmd"][:3] == ["npx", "likec4@1.60.0", "export"]
    likec4_on_path.assert_called_once_with("npx")


def test_bin_from_environment(mocker: MockerFixture, likec4_on_path: Any):
    LocalLikeC4Backend(env={"LIKEC4_BIN": "/opt/likec4"})

    likec4_on_path.assert_called_once_with("/opt/likec4")


def test_missing_binary(likec4_on_path: Any):
    likec4_on_path.return_value = None

    with pytest.raises(LikeC4BackendConfigurationError, match="npm install"):
        LocalLikeC4Backend()


def test_empty_command():
    with pytest.raises(LikeC4BackendConfigurationError):
        LocalLikeC4Backend(likec4_bin=[])


def test_invalid_timeout():
    with pytest.raises(LikeC4BackendConfigurationError, match="number"):
        LocalLikeC4Backend(env={"RENDERING_TIMEOUT_SECONDS": "soon"})


def test_timeout_argument(mocker: MockerFixture):
    calls = fake_run(mocker)

    LocalLikeC4Backend(timeout_seconds=5).to_bytes(
        "x", format=PNG, view_key="v"
    )

    assert calls["kwargs"]["timeout"] == 5.0


@pytest.mark.parametrize("view_key", [None, ""])
def test_view_key_is_required(mocker: MockerFixture, view_key):
    run = mocker.patch(SUBPROCESS)

    with pytest.raises(LikeC4BackendConfigurationError, match="view key"):
        LocalLikeC4Backend().to_bytes("x", format=PNG, view_key=view_key)
    run.assert_not_called()


@pytest.mark.parametrize("fmt", [SVG, "pdf", "nonsense"])
def test_unsupported_format(mocker: MockerFixture, fmt):
    run = mocker.patch(SUBPROCESS)

    with pytest.raises(ValueError, match="Unsupported LikeC4 format"):
        LocalLikeC4Backend().to_bytes("x", format=fmt, view_key="v")
    run.assert_not_called()


def test_cli_failure_carries_output(mocker: MockerFixture):
    calls = fake_run(
        mocker, result=completed(1, stdout="out text", stderr="boom")
    )

    with pytest.raises(LikeC4LocalRenderingError, match="boom\nout text"):
        LocalLikeC4Backend().to_bytes("x", format=PNG, view_key="v")
    assert not calls["tmp"].exists()


def test_cli_failure_without_output(mocker: MockerFixture):
    fake_run(mocker, result=completed(2))

    with pytest.raises(LikeC4LocalRenderingError, match="LikeC4 failed"):
        LocalLikeC4Backend().to_bytes("x", format=PNG, view_key="v")


@pytest.mark.parametrize(
    "stderr",
    [
        "browserType.launch: Executable doesn't exist at /x",
        "Please run: npx playwright install",
    ],
)
def test_missing_chromium(mocker: MockerFixture, stderr):
    fake_run(mocker, result=completed(1, stderr=stderr))

    with pytest.raises(
        LikeC4BackendConfigurationError, match="playwright install chromium"
    ):
        LocalLikeC4Backend().to_bytes("x", format=PNG, view_key="v")


def test_unmatched_view_filter(mocker: MockerFixture):
    fake_run(mocker, write=False)

    with pytest.raises(LikeC4LocalRenderingError, match="'ghost'"):
        LocalLikeC4Backend().to_bytes("x", format=PNG, view_key="ghost")


def test_timeout(mocker: MockerFixture):
    mocker.patch(
        SUBPROCESS,
        side_effect=subprocess.TimeoutExpired(cmd="likec4", timeout=1),
    )

    with pytest.raises(LikeC4LocalRenderingError, match="timed out"):
        LocalLikeC4Backend(timeout_seconds=1).to_bytes(
            "x", format=PNG, view_key="v"
        )


def test_to_file_passes_view_key(mocker: MockerFixture, tmp_path: Path):
    calls = fake_run(mocker)

    target = LocalLikeC4Backend().to_file(
        "x", tmp_path / "a.png", format=None, view_key="main"
    )

    assert target.read_bytes() == b"img"
    assert calls["cmd"][calls["cmd"].index("-f") + 1] == "main"

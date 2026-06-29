from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from c4 import PNG, DiagramFormat
from c4.exceptions import (
    D2BackendConfigurationError,
    D2LocalRenderingError,
)
from c4.renderers.d2.backends import BaseD2Backend, LocalD2Backend
from c4.renderers.d2.options import D2RenderOptions


class DummyD2Backend(BaseD2Backend):
    def __init__(self, content: bytes = b"rendered") -> None:
        self.content = content
        self.calls: list[tuple[str, Any]] = []

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = PNG,  # noqa: A002
        render_options: D2RenderOptions | None = None,
    ) -> bytes:
        self.calls.append((diagram, format))
        return self.content


@pytest.mark.parametrize(
    ("output_name", "expected_format"),
    [
        ("diagram.svg", DiagramFormat.SVG),
        ("diagram.png", DiagramFormat.PNG),
        ("diagram.pdf", DiagramFormat.PDF),
    ],
)
def test_base_d2_backend__to_file__infers_format(
    tmp_path: Path,
    output_name: str,
    expected_format: DiagramFormat,
):
    backend = DummyD2Backend(content=b"rendered")
    output_path = tmp_path / output_name

    result = backend.to_file(
        "direction: right\ncustomer: Customer",
        output_path,
        format=None,
    )

    assert result == output_path
    assert output_path.read_bytes() == b"rendered"
    assert backend.calls == [
        ("direction: right\ncustomer: Customer", expected_format)
    ]


def test_base_d2_backend__to_file__empty_format_and_extension(
    tmp_path: Path,
):
    backend = DummyD2Backend()
    output_path = tmp_path / "diagram"
    expected_error = "format is None and output_path has no extension."

    with pytest.raises(ValueError, match=expected_error):
        backend.to_file("diagram source", output_path, format=None)


def test_base_d2_backend__to_file__output_exists_error(
    tmp_path: Path,
):
    backend = DummyD2Backend()
    output_path = tmp_path / "diagram.svg"
    output_path.write_text("existing", encoding="utf-8")
    expected_error = f"Output file already exists: {output_path!s}"

    with pytest.raises(FileExistsError, match=expected_error):
        backend.to_file(
            "diagram source",
            output_path,
            format=DiagramFormat.SVG,
            overwrite=False,
        )


def test_base_d2_backend__ensure_format_supported_error(
    mocker: MockerFixture,
):
    backend = DummyD2Backend()
    unknown_format = mocker.MagicMock()
    unknown_format.value = "Unknown"

    with pytest.raises(ValueError, match="'Unknown' format is not supported"):
        backend._ensure_format_supported(unknown_format)


def test_local_d2_backend__init__invalid_timeout_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    with pytest.raises(
        D2BackendConfigurationError,
        match="expected a number of seconds",
    ):
        LocalD2Backend(env={"RENDERING_TIMEOUT_SECONDS": "not-a-number"})


def test_local_d2_backend__resolve_backend__binary_available(
    mocker: MockerFixture,
):
    which_mock = mocker.patch(
        "c4.renderers.d2.backends.shutil.which",
        return_value="/usr/bin/d2",
    )

    LocalD2Backend(d2_bin="d2")

    which_mock.assert_called_once_with("d2")


def test_local_d2_backend__resolve_backend__not_available(
    mocker: MockerFixture,
):
    mocker.patch(
        "c4.renderers.d2.backends.shutil.which",
        return_value=None,
    )

    with pytest.raises(
        D2BackendConfigurationError,
        match="D2 is not available",
    ):
        LocalD2Backend(d2_bin="d2")


def test_local_d2_backend__build_cmd(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(
        d2_bin="d2",
        d2_args=("--theme", "101"),
    )

    result = backend._build_cmd(
        input_path=Path("diagram.d2"),
        output_path=Path("diagram.svg"),
    )

    assert result == [
        "d2",
        "diagram.d2",
        "diagram.svg",
        "--theme",
        "101",
    ]


def test_local_d2_backend__build_cmd__uses_render_options_layout(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(d2_bin="d2")

    result = backend._build_cmd(
        input_path=Path("diagram.d2"),
        output_path=Path("diagram.svg"),
        render_options=D2RenderOptions(layout="elk"),
    )

    assert result == [
        "d2",
        "diagram.d2",
        "diagram.svg",
        "--layout=elk",
    ]


def test_local_d2_backend__build_cmd__uses_default_render_options_layout(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(d2_bin="d2")

    result = backend._build_cmd(
        input_path=Path("diagram.d2"),
        output_path=Path("diagram.svg"),
        render_options=D2RenderOptions(),
    )

    assert result == [
        "d2",
        "diagram.d2",
        "diagram.svg",
        "--layout=dagre",
    ]


def test_local_d2_backend__build_cmd__explicit_layout_overrides_render_options(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(d2_bin="d2", layout="dagre")

    result = backend._build_cmd(
        input_path=Path("diagram.d2"),
        output_path=Path("diagram.svg"),
        render_options=D2RenderOptions(layout="elk"),
    )

    assert result == [
        "d2",
        "diagram.d2",
        "diagram.svg",
        "--layout=dagre",
    ]


def test_local_d2_backend__to_bytes__generated_file_content(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(d2_bin="d2")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["d2", "diagram.d2", "diagram.svg"],
    )

    def run_side_effect(
        *args: Any,
        **kwargs: Any,
    ) -> subprocess.CompletedProcess:
        output_path = Path(kwargs["cwd"]) / "diagram.svg"
        output_path.write_bytes(b"<svg>generated</svg>")
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout="",
            stderr="",
        )

    mocker.patch(
        "c4.renderers.d2.backends.subprocess.run",
        side_effect=run_side_effect,
    )

    result = backend.to_bytes(
        "direction: right\ncustomer: Customer",
        format=DiagramFormat.SVG,
    )

    assert result == b"<svg>generated</svg>"


def test_local_d2_backend__to_bytes__nonzero_return_code__uses_stderr(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(d2_bin="d2")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["d2", "diagram.d2", "diagram.svg"],
    )
    mocker.patch(
        "c4.renderers.d2.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["d2"],
            returncode=1,
            stdout="",
            stderr="boom",
        ),
    )

    with pytest.raises(D2LocalRenderingError, match="boom"):
        backend.to_bytes(
            "direction: right\ncustomer: Customer",
            format=DiagramFormat.SVG,
        )


def test_local_d2_backend__to_bytes__nonzero_return_code__uses_stdout(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(d2_bin="d2")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["d2", "diagram.d2", "diagram.svg"],
    )
    mocker.patch(
        "c4.renderers.d2.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["d2"],
            returncode=1,
            stdout="boom",
            stderr="",
        ),
    )

    with pytest.raises(D2LocalRenderingError, match="boom"):
        backend.to_bytes(
            "direction: right\ncustomer: Customer",
            format=DiagramFormat.SVG,
        )


def test_local_d2_backend__to_bytes__nonzero_return_code__fallback_message(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(d2_bin="d2")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["d2", "diagram.d2", "diagram.svg"],
    )
    mocker.patch(
        "c4.renderers.d2.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["d2"],
            returncode=1,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(D2LocalRenderingError, match="D2 failed"):
        backend.to_bytes(
            "direction: right\ncustomer: Customer",
            format=DiagramFormat.SVG,
        )


def test_local_d2_backend__to_bytes__output_not_generated(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(d2_bin="d2")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["d2", "diagram.d2", "diagram.svg"],
    )
    mocker.patch(
        "c4.renderers.d2.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["d2"],
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(
        D2LocalRenderingError,
        match="Expected output was not generated",
    ):
        backend.to_bytes(
            "direction: right\ncustomer: Customer",
            format=DiagramFormat.SVG,
        )


def test_local_d2_backend__init__uses_explicit_d2_bin_over_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalD2Backend(
        d2_bin="explicit-d2",
        env={"D2_BIN": "env-d2"},
    )

    assert backend._d2_bin == "explicit-d2"


def test_local_d2_backend__init__uses_env_d2_bin_when_not_explicit(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalD2Backend(env={"D2_BIN": "env-d2"})

    assert backend._d2_bin == "env-d2"


def test_local_d2_backend__init__uses_explicit_timeout_over_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalD2Backend(
        d2_bin="d2",
        timeout_seconds=12.5,
        env={"RENDERING_TIMEOUT_SECONDS": "30"},
    )

    assert backend._timeout_seconds == 12.5


def test_local_d2_backend__init__uses_env_timeout_when_not_explicit(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalD2Backend(
        d2_bin="d2",
        env={"RENDERING_TIMEOUT_SECONDS": "30"},
    )

    assert backend._timeout_seconds == 30.0


def test_local_d2_backend__to_bytes__passes_expected_subprocess_args(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalD2Backend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalD2Backend(
        d2_bin="d2",
        timeout_seconds=12.5,
        env={"A": "B"},
    )
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["d2", "diagram.d2", "diagram.svg"],
    )
    run_mock = mocker.patch(
        "c4.renderers.d2.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["d2"],
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(
        D2LocalRenderingError,
        match="Expected output was not generated",
    ):
        backend.to_bytes(
            "direction: right\ncustomer: Customer",
            format=DiagramFormat.SVG,
        )

    run_mock.assert_called_once()
    _, kwargs = run_mock.call_args
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["timeout"] == 12.5
    assert kwargs["env"]["A"] == "B"

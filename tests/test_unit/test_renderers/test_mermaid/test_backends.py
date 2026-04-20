from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from c4 import PNG, DiagramFormat
from c4.exceptions import (
    MermaidBackendConfigurationError,
    MermaidLocalRenderingError,
)
from c4.renderers.mermaid.backends import (
    BaseMermaidBackend,
    LocalMermaidBackend,
)


class DummyMermaidBackend(BaseMermaidBackend):
    def __init__(self, content: bytes = b"rendered") -> None:
        self.content = content
        self.calls: list[tuple[str, Any]] = []

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = PNG,  # noqa: A002
    ) -> bytes:
        self.calls.append((diagram, format))
        return self.content


@pytest.mark.parametrize(
    ("output_name", "expected_format"),
    [
        ("diagram.svg", DiagramFormat.SVG),
        ("diagram.png", DiagramFormat.PNG),
    ],
)
def test_base_mermaid_backend__to_file__infers_format(
    tmp_path: Path,
    output_name: str,
    expected_format: DiagramFormat,
):
    backend = DummyMermaidBackend(content=b"rendered")
    output_path = tmp_path / output_name

    result = backend.to_file(
        "C4Context\ntitle System Context diagram",
        output_path,
        format=None,
    )

    assert result == output_path
    assert output_path.read_bytes() == b"rendered"
    assert backend.calls == [
        ("C4Context\ntitle System Context diagram", expected_format)
    ]


def test_base_mermaid_backend__to_file__empty_format_and_extension(
    tmp_path: Path,
):
    backend = DummyMermaidBackend()
    output_path = tmp_path / "diagram"
    expected_error = "format is None and output_path has no extension."

    with pytest.raises(ValueError, match=expected_error):
        backend.to_file("diagram source", output_path, format=None)


def test_base_mermaid_backend__to_file__output_exists_error(
    tmp_path: Path,
):
    backend = DummyMermaidBackend()
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


def test_base_mermaid_backend__ensure_format_supported_error(
    mocker: MockerFixture,
):
    backend = DummyMermaidBackend()
    unknown_format = mocker.MagicMock()
    unknown_format.value = "Unknown"

    with pytest.raises(ValueError, match="'Unknown' format is not supported"):
        backend._ensure_format_supported(unknown_format)


def test_local_mermaid_backend__init__invalid_timeout_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    with pytest.raises(
        MermaidBackendConfigurationError,
        match="expected a number of seconds",
    ):
        LocalMermaidBackend(env={"RENDERING_TIMEOUT_SECONDS": "not-a-number"})


def test_local_mermaid_backend__resolve_backend__binary_available(
    mocker: MockerFixture,
):
    which_mock = mocker.patch(
        "c4.renderers.mermaid.backends.shutil.which",
        return_value="/usr/bin/mmdc",
    )

    LocalMermaidBackend(mermaid_bin="mmdc")

    which_mock.assert_called_once_with("mmdc")


def test_local_mermaid_backend__resolve_backend__not_available(
    mocker: MockerFixture,
):
    mocker.patch(
        "c4.renderers.mermaid.backends.shutil.which",
        return_value=None,
    )

    with pytest.raises(
        MermaidBackendConfigurationError,
        match="Mermaid is not available",
    ):
        LocalMermaidBackend(mermaid_bin="mmdc")


def test_local_mermaid_backend__build_cmd(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalMermaidBackend(
        mermaid_bin="mmdc",
        mermaid_args=("--backgroundColor", "transparent"),
    )

    result = backend._build_cmd(
        input_path=Path("diagram.mmd"),
        output_path=Path("diagram.svg"),
    )

    assert result == [
        "mmdc",
        "-i",
        "diagram.mmd",
        "-o",
        "diagram.svg",
        "--backgroundColor",
        "transparent",
    ]


def test_local_mermaid_backend__to_bytes__generated_file_content(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalMermaidBackend(mermaid_bin="mmdc")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["mmdc", "-i", "diagram.mmd", "-o", "diagram.svg"],
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
        "c4.renderers.mermaid.backends.subprocess.run",
        side_effect=run_side_effect,
    )

    result = backend.to_bytes(
        "C4Context\ntitle System Context diagram", format=DiagramFormat.SVG
    )

    assert result == b"<svg>generated</svg>"


def test_local_mermaid_backend__to_bytes__nonzero_return_code__uses_stderr(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalMermaidBackend(mermaid_bin="mmdc")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["mmdc", "-i", "diagram.mmd", "-o", "diagram.svg"],
    )
    mocker.patch(
        "c4.renderers.mermaid.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["mmdc"],
            returncode=1,
            stdout="",
            stderr="boom",
        ),
    )

    with pytest.raises(MermaidLocalRenderingError, match="boom"):
        backend.to_bytes(
            "C4Context\ntitle System Context diagram",
            format=DiagramFormat.SVG,
        )


def test_local_mermaid_backend__to_bytes__nonzero_return_code__uses_stdout(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalMermaidBackend(mermaid_bin="mmdc")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["mmdc", "-i", "diagram.mmd", "-o", "diagram.svg"],
    )
    mocker.patch(
        "c4.renderers.mermaid.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["mmdc"],
            returncode=1,
            stdout="boom",
            stderr="",
        ),
    )

    with pytest.raises(MermaidLocalRenderingError, match="boom"):
        backend.to_bytes(
            "C4Context\ntitle System Context diagram",
            format=DiagramFormat.SVG,
        )


def test_local_mermaid_backend__to_bytes__nonzero_return_code__fallback_message(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalMermaidBackend(mermaid_bin="mmdc")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["mmdc", "-i", "diagram.mmd", "-o", "diagram.svg"],
    )
    mocker.patch(
        "c4.renderers.mermaid.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["mmdc"],
            returncode=1,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(MermaidLocalRenderingError, match="Mermaid failed"):
        backend.to_bytes(
            "C4Context\ntitle System Context diagram",
            format=DiagramFormat.SVG,
        )


def test_local_mermaid_backend__to_bytes__output_not_generated(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalMermaidBackend(mermaid_bin="mmdc")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["mmdc", "-i", "diagram.mmd", "-o", "diagram.svg"],
    )
    mocker.patch(
        "c4.renderers.mermaid.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["mmdc"],
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(
        MermaidLocalRenderingError,
        match="Expected output was not generated",
    ):
        backend.to_bytes(
            "C4Context\ntitle System Context diagram", format=DiagramFormat.SVG
        )


def test_local_mermaid_backend__init__uses_explicit_mermaid_bin_over_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalMermaidBackend(
        mermaid_bin="explicit-mmdc",
        env={"MERMAID_BIN": "env-mmdc"},
    )

    assert backend._mermaid_bin == "explicit-mmdc"


def test_local_mermaid_backend__init__uses_explicit_timeout_over_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalMermaidBackend(
        mermaid_bin="mmdc",
        timeout_seconds=12.5,
        env={"RENDERING_TIMEOUT_SECONDS": "30"},
    )

    assert backend._timeout_seconds == 12.5


def test_local_mermaid_backend__init__uses_env_mermaid_bin_when_not_explicit(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalMermaidBackend(env={"MERMAID_BIN": "env-mmdc"})

    assert backend._mermaid_bin == "env-mmdc"


def test_local_mermaid_backend__init__uses_env_timeout_when_not_explicit(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalMermaidBackend(
        mermaid_bin="mmdc",
        env={"RENDERING_TIMEOUT_SECONDS": "30"},
    )

    assert backend._timeout_seconds == 30.0


def test_local_mermaid_backend__to_bytes__passes_expected_subprocess_args(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalMermaidBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalMermaidBackend(
        mermaid_bin="mmdc",
        timeout_seconds=12.5,
        env={"A": "B"},
    )
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["mmdc", "-i", "diagram.mmd", "-o", "diagram.svg"],
    )
    run_mock = mocker.patch(
        "c4.renderers.mermaid.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["mmdc"],
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(
        MermaidLocalRenderingError,
        match="Expected output was not generated",
    ):
        backend.to_bytes(
            "C4Context\ntitle System Context diagram",
            format=DiagramFormat.SVG,
        )

    run_mock.assert_called_once()
    _, kwargs = run_mock.call_args
    assert kwargs["capture_output"] is True
    assert kwargs["text"] is True
    assert kwargs["timeout"] == 12.5
    assert kwargs["env"]["A"] == "B"

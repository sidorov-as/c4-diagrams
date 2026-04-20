from __future__ import annotations

import io
import subprocess
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError

import pytest
from pytest_mock import MockerFixture

from c4 import PNG, DiagramFormat
from c4.exceptions import (
    PlantUMLBackendConfigurationError,
    PlantUMLLocalRenderingError,
    PlantUMLRemoteRenderingError,
)
from c4.renderers.plantuml.backends import (
    BasePlantUMLBackend,
    LocalPlantUMLBackend,
    RemotePlantUMLBackend,
)


class DummyPlantUMLBackend(BasePlantUMLBackend):
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
def test_base_plantuml_backend__to_file__infers_format(
    tmp_path: Path,
    output_name: str,
    expected_format: DiagramFormat,
):
    backend = DummyPlantUMLBackend(content=b"rendered")
    output_path = tmp_path / output_name

    result = backend.to_file(
        "@startuml\nAlice -> Bob\n@enduml",
        output_path,
        format=None,
    )

    assert result == output_path
    assert output_path.read_bytes() == b"rendered"
    assert backend.calls == [
        ("@startuml\nAlice -> Bob\n@enduml", expected_format)
    ]


def test_base_plantuml_backend__to_file__empty_format_and_extension(
    tmp_path: Path,
):
    backend = DummyPlantUMLBackend()
    output_path = tmp_path / "diagram"
    expected_error = "format is None and output_path has no extension."

    with pytest.raises(ValueError, match=expected_error):
        backend.to_file("diagram source", output_path, format=None)


def test_base_plantuml_backend__to_file__output_exists_error(
    tmp_path: Path,
):
    backend = DummyPlantUMLBackend()
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


def test_base_plantuml_backend__ensure_format_supported_error(
    mocker: MockerFixture,
):
    backend = DummyPlantUMLBackend()
    unknown_format = mocker.MagicMock()
    unknown_format.value = "Unknown"

    with pytest.raises(ValueError, match="'Unknown' format is not supported"):
        backend._ensure_format_supported(unknown_format)


def test_remote_plantuml_backend__init__strips_trailing_slash():
    backend = RemotePlantUMLBackend(server_url="https://example.com/plantuml/")

    assert backend._server_url == "https://example.com/plantuml"


def test_remote_plantuml_backend__encode_text_diagram():
    backend = RemotePlantUMLBackend()
    text_diagram = "@startuml\n@enduml"
    expected_encoded_diagram = b"SoWkIImgAStDuN98pKi1qW0="

    encoded = backend._encode_text_diagram(text_diagram)

    assert encoded == expected_encoded_diagram


def test_remote_plantuml_backend__to_bytes__returns_response_body(
    mocker: MockerFixture,
):
    backend = RemotePlantUMLBackend(server_url="https://example.com/plantuml")
    mocker.patch.object(
        backend,
        "_encode_text_diagram",
        return_value=b"encoded-diagram",
    )
    response = mocker.MagicMock()
    response.read.return_value = b"<svg>ok</svg>"
    response_cm = mocker.MagicMock()
    response_cm.__enter__.return_value = response
    response_cm.__exit__.return_value = None
    urlopen_mock = mocker.patch(
        "c4.renderers.plantuml.backends.urlopen",
        return_value=response_cm,
    )

    result = backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)

    assert result == b"<svg>ok</svg>"
    request = urlopen_mock.call_args.args[0]
    assert request.full_url == (
        "https://example.com/plantuml/svg/encoded-diagram"
    )


def test_remote_plantuml_backend__to_bytes__http_error(
    mocker: MockerFixture,
):
    backend = RemotePlantUMLBackend(server_url="https://example.com/plantuml")
    mocker.patch.object(
        backend,
        "_encode_text_diagram",
        return_value=b"encoded-diagram",
    )
    http_error = HTTPError(
        url="https://example.com/plantuml/svg/encoded-diagram",
        code=500,
        msg="Internal Server Error",
        hdrs=None,
        fp=io.BytesIO(b"server exploded"),
    )
    mocker.patch(
        "c4.renderers.plantuml.backends.urlopen",
        side_effect=http_error,
    )

    with pytest.raises(
        PlantUMLRemoteRenderingError,
        match="HTTP 500 Internal Server Error",
    ):
        backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)


def test_remote_plantuml_backend__to_bytes__url_error(
    mocker: MockerFixture,
):
    backend = RemotePlantUMLBackend(server_url="https://example.com/plantuml")
    mocker.patch.object(
        backend,
        "_encode_text_diagram",
        return_value=b"encoded-diagram",
    )
    mocker.patch(
        "c4.renderers.plantuml.backends.urlopen",
        side_effect=URLError("connection refused"),
    )

    with pytest.raises(
        PlantUMLRemoteRenderingError,
        match="connection refused",
    ):
        backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)


def test_local_plantuml_backend__init__invalid_timeout_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    with pytest.raises(
        PlantUMLBackendConfigurationError,
        match="expected a number of seconds",
    ):
        LocalPlantUMLBackend(env={"RENDERING_TIMEOUT_SECONDS": "not-a-number"})


@pytest.mark.parametrize(
    ("format", "expected_name"),
    [
        (DiagramFormat.SVG, "diagram.svg"),
        (DiagramFormat.TXT, "diagram.atxt"),
    ],
)
def test_local_plantuml_backend__build_output_path__returns_expected_suffix(
    mocker: MockerFixture,
    format: DiagramFormat,  # noqa: A002
    expected_name: str,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalPlantUMLBackend(plantuml_bin="plantuml")
    input_path = Path("diagram.puml")

    result = backend._build_output_path(input_path, format)

    assert result == Path(expected_name)


def test_local_plantuml_backend__resolve_backend__prefers_binary(
    mocker: MockerFixture,
    tmp_path: Path,
):
    jar_path = tmp_path / "plantuml.jar"
    jar_path.write_text("jar", encoding="utf-8")
    which_mock = mocker.patch(
        "c4.renderers.plantuml.backends.shutil.which",
        return_value="/usr/bin/plantuml",
    )

    backend = LocalPlantUMLBackend(
        plantuml_bin="plantuml",
        plantuml_jar=jar_path,
    )

    assert backend._use_jar is False
    which_mock.assert_called_once_with("plantuml")


def test_local_plantuml_backend__resolve_backend__missing_binary(
    mocker: MockerFixture,
    tmp_path: Path,
):
    jar_path = tmp_path / "plantuml.jar"
    jar_path.write_text("jar", encoding="utf-8")
    mocker.patch(
        "c4.renderers.plantuml.backends.shutil.which",
        return_value=None,
    )

    backend = LocalPlantUMLBackend(
        plantuml_bin="plantuml",
        plantuml_jar=jar_path,
    )

    assert backend._use_jar is True


def test_local_plantuml_backend__resolve_backend__not_available(
    mocker: MockerFixture,
):
    mocker.patch(
        "c4.renderers.plantuml.backends.shutil.which",
        return_value=None,
    )

    with pytest.raises(
        PlantUMLBackendConfigurationError,
        match="PlantUML is not available",
    ):
        LocalPlantUMLBackend(
            plantuml_bin="plantuml",
            plantuml_jar=Path("/missing/plantuml.jar"),
        )


def test_local_plantuml_backend__build_cmd__binary_command(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalPlantUMLBackend(
        plantuml_bin="plantuml",
        plantuml_args=("-charset", "UTF-8"),
    )
    backend._use_jar = False

    result = backend._build_cmd(
        input_path=Path("diagram.puml"),
        format=DiagramFormat.SVG,
    )

    assert result == [
        "plantuml",
        "-tsvg",
        "-charset",
        "UTF-8",
        "diagram.puml",
    ]


def test_local_plantuml_backend__build_cmd__jar_command(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalPlantUMLBackend(
        plantuml_bin=None,
        plantuml_jar=Path("/tmp/plantuml.jar"),  # noqa: S108
        java_bin="java",
        java_args=("-Xmx256m",),
        plantuml_args=("-charset", "UTF-8"),
    )
    backend._use_jar = True

    result = backend._build_cmd(
        input_path=Path("diagram.puml"),
        format=DiagramFormat.SVG,
    )

    assert result == [
        "java",
        "-Xmx256m",
        "-jar",
        "/tmp/plantuml.jar",  # noqa: S108
        "-tsvg",
        "-charset",
        "UTF-8",
        "diagram.puml",
    ]


def test_local_plantuml_backend__to_bytes__generated_file_content(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalPlantUMLBackend(plantuml_bin="plantuml")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["plantuml", "-tsvg", "diagram.puml"],
    )

    def run_side_effect(
        *args: Any, **kwargs: Any
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
        "c4.renderers.plantuml.backends.subprocess.run",
        side_effect=run_side_effect,
    )

    result = backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)

    assert result == b"<svg>generated</svg>"


def test_local_plantuml_backend__to_bytes__nonzero_return_code(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalPlantUMLBackend(plantuml_bin="plantuml")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["plantuml", "-tsvg", "diagram.puml"],
    )
    mocker.patch(
        "c4.renderers.plantuml.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["plantuml"],
            returncode=1,
            stdout="",
            stderr="boom",
        ),
    )

    with pytest.raises(PlantUMLLocalRenderingError, match="boom"):
        backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)


def test_local_plantuml_backend__to_bytes__output_not_generated(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    backend = LocalPlantUMLBackend(plantuml_bin="plantuml")
    mocker.patch.object(
        backend,
        "_build_cmd",
        return_value=["plantuml", "-tsvg", "diagram.puml"],
    )
    mocker.patch(
        "c4.renderers.plantuml.backends.subprocess.run",
        return_value=subprocess.CompletedProcess(
            args=["plantuml"],
            returncode=0,
            stdout="",
            stderr="",
        ),
    )

    with pytest.raises(
        PlantUMLLocalRenderingError,
        match="Expected output was not generated",
    ):
        backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)


def test_local_plantuml_backend__init__uses_explicit_plantuml_bin_over_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalPlantUMLBackend(
        plantuml_bin="explicit-plantuml",
        env={"PLANTUML_BIN": "env-plantuml"},
    )

    assert backend._plantuml_bin == "explicit-plantuml"


def test_local_plantuml_backend__init__uses_env_plantuml_bin_when_not_explicit(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalPlantUMLBackend(env={"PLANTUML_BIN": "env-plantuml"})

    assert backend._plantuml_bin == "env-plantuml"


def test_local_plantuml_backend__init__uses_explicit_plantuml_jar_over_env(
    mocker: MockerFixture,
    tmp_path: Path,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    explicit_jar = tmp_path / "explicit.jar"
    env_jar = tmp_path / "env.jar"

    backend = LocalPlantUMLBackend(
        plantuml_jar=explicit_jar,
        env={"PLANTUML_JAR": str(env_jar)},
    )

    assert backend._plantuml_jar == explicit_jar


def test_local_plantuml_backend__init__uses_env_plantuml_jar_when_not_explicit(
    mocker: MockerFixture,
    tmp_path: Path,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )
    env_jar = tmp_path / "env.jar"

    backend = LocalPlantUMLBackend(
        env={"PLANTUML_JAR": str(env_jar)},
    )

    assert backend._plantuml_jar == env_jar


def test_local_plantuml_backend__init__uses_explicit_timeout_over_env(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalPlantUMLBackend(
        timeout_seconds=12.5,
        env={"RENDERING_TIMEOUT_SECONDS": "30"},
    )

    assert backend._timeout_seconds == 12.5


def test_local_plantuml_backend__init__uses_env_timeout_when_not_explicit(
    mocker: MockerFixture,
):
    mocker.patch.object(
        LocalPlantUMLBackend,
        "_resolve_backend",
        autospec=True,
        return_value=None,
    )

    backend = LocalPlantUMLBackend(
        env={"RENDERING_TIMEOUT_SECONDS": "30"},
    )

    assert backend._timeout_seconds == 30.0

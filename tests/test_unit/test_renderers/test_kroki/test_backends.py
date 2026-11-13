from __future__ import annotations

import base64
import io
import zlib
from urllib.error import HTTPError, URLError

import pytest
from pytest_mock import MockerFixture

from c4 import DiagramFormat
from c4.constants import (
    KROKI_SERVER_URL_ENV_VAR,
    RENDERING_TIMEOUT_SECONDS_ENV_VAR,
)
from c4.exceptions import KrokiRemoteRenderingError
from c4.renderers.kroki import KrokiBackend
from c4.renderers.kroki.backends import DEFAULT_KROKI_HEADERS


def test_kroki_backend__init__strips_trailing_slash():
    backend = KrokiBackend(server_url="https://kroki.example/")

    assert backend._server_url == "https://kroki.example"


def test_kroki_backend__uses_default_headers():
    backend = KrokiBackend()

    assert backend._headers == DEFAULT_KROKI_HEADERS


def test_kroki_backend__custom_headers_override_defaults():
    backend = KrokiBackend(
        headers={
            "User-Agent": "custom-agent",
            "X-Trace": "1",
        }
    )

    assert backend._headers == {
        **DEFAULT_KROKI_HEADERS,
        "User-Agent": "custom-agent",
        "X-Trace": "1",
    }


def test_kroki_backend__uses_environment_configuration(monkeypatch):
    monkeypatch.setenv(KROKI_SERVER_URL_ENV_VAR, "https://env-kroki.example/")
    monkeypatch.setenv(RENDERING_TIMEOUT_SECONDS_ENV_VAR, "12.5")

    backend = KrokiBackend()

    assert backend._server_url == "https://env-kroki.example"
    assert backend._timeout_seconds == 12.5


def test_kroki_backend__encode_text_diagram_uses_zlib_urlsafe_base64():
    backend = KrokiBackend()
    source = "A -> B"
    expected = base64.urlsafe_b64encode(
        zlib.compress(source.encode("utf-8"), 9)
    ).decode("ascii")

    assert backend._encode_text_diagram(source) == expected


@pytest.mark.parametrize("value", ["", "plant/uml", "plantuml?x", "plantuml#x"])
def test_kroki_backend__invalid_path_part(value: str):
    backend = KrokiBackend()

    with pytest.raises(ValueError, match="Invalid Kroki diagram_type"):
        backend._normalize_path_part(value, name="diagram_type")


def test_kroki_backend__get_request_url_and_query_params(
    mocker: MockerFixture,
):
    backend = KrokiBackend(
        server_url="https://kroki.example",
        diagram_type="mermaid",
        diagram_options={"view-key": "main view"},
    )
    mocker.patch.object(
        backend,
        "_encode_text_diagram",
        return_value="encoded",
    )
    response = mocker.MagicMock()
    response.read.return_value = b"rendered"
    response_cm = mocker.MagicMock()
    response_cm.__enter__.return_value = response
    response_cm.__exit__.return_value = None
    urlopen_mock = mocker.patch(
        "c4.renderers.kroki.backends.urlopen",
        return_value=response_cm,
    )

    result = backend.to_bytes("diagram", format=DiagramFormat.SVG)

    assert result == b"rendered"
    request = urlopen_mock.call_args.args[0]
    assert request.full_url == (
        "https://kroki.example/mermaid/svg/encoded?view-key=main+view"
    )
    assert request.get_method() == "GET"
    assert request.headers["User-agent"] == "c4-diagrams"


def test_kroki_backend__post_request_sends_text_body_and_options_headers(
    mocker: MockerFixture,
):
    backend = KrokiBackend(
        server_url="https://kroki.example",
        diagram_type="structurizr",
        use_post=True,
        diagram_options={"view-key": "main"},
    )
    response = mocker.MagicMock()
    response.read.return_value = b"rendered"
    response_cm = mocker.MagicMock()
    response_cm.__enter__.return_value = response
    response_cm.__exit__.return_value = None
    urlopen_mock = mocker.patch(
        "c4.renderers.kroki.backends.urlopen",
        return_value=response_cm,
    )

    result = backend.to_bytes("workspace", format=DiagramFormat.PNG)

    assert result == b"rendered"
    request = urlopen_mock.call_args.args[0]
    assert request.full_url == "https://kroki.example/structurizr/png"
    assert request.data == b"workspace"
    assert request.get_method() == "POST"
    assert request.headers["Content-type"] == "text/plain; charset=utf-8"
    assert request.headers["Kroki-diagram-options-view-key"] == "main"


def test_kroki_backend__call_options_override_default_options_and_type(
    mocker: MockerFixture,
):
    backend = KrokiBackend(
        server_url="https://kroki.example",
        diagram_type="plantuml",
        diagram_options={"theme": "base", "view-key": "old"},
    )
    mocker.patch.object(
        backend,
        "_encode_text_diagram",
        return_value="encoded",
    )
    response = mocker.MagicMock()
    response.read.return_value = b"rendered"
    response_cm = mocker.MagicMock()
    response_cm.__enter__.return_value = response
    response_cm.__exit__.return_value = None
    urlopen_mock = mocker.patch(
        "c4.renderers.kroki.backends.urlopen",
        return_value=response_cm,
    )

    result = backend.to_bytes(
        "workspace",
        format="SVG",
        diagram_type="Structurizr",
        diagram_options={"view-key": "new"},
    )

    assert result == b"rendered"
    request = urlopen_mock.call_args.args[0]
    assert request.full_url == (
        "https://kroki.example/structurizr/svg/encoded?theme=base&view-key=new"
    )


def test_kroki_backend__http_error_includes_body(mocker: MockerFixture):
    backend = KrokiBackend(server_url="https://kroki.example")
    http_error = HTTPError(
        url="https://kroki.example/plantuml/svg/encoded",
        code=500,
        msg="Internal Server Error",
        hdrs=None,
        fp=io.BytesIO(b"server exploded"),
    )
    mocker.patch(
        "c4.renderers.kroki.backends.urlopen",
        side_effect=http_error,
    )

    with pytest.raises(
        KrokiRemoteRenderingError,
        match="HTTP 500 Internal Server Error",
    ):
        backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)


def test_kroki_backend__url_error(mocker: MockerFixture):
    backend = KrokiBackend(server_url="https://kroki.example")
    mocker.patch(
        "c4.renderers.kroki.backends.urlopen",
        side_effect=URLError("connection refused"),
    )

    with pytest.raises(
        KrokiRemoteRenderingError,
        match="connection refused",
    ):
        backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)

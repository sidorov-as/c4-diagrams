from __future__ import annotations

import pytest

from c4 import DiagramFormat
from c4.contrib.structurizr.renderer import KrokiStructurizrBackend
from c4.exceptions import D2BackendConfigurationError
from c4.renderers.d2 import D2RenderOptions, KrokiD2Backend
from c4.renderers.mermaid import KrokiMermaidBackend
from c4.renderers.plantuml import KrokiPlantUMLBackend


def test_kroki_plantuml_backend__uses_plantuml_diagram_type(mocker):
    kroki = mocker.patch("c4.renderers.plantuml.backends.KrokiBackend")
    backend = KrokiPlantUMLBackend(server_url="https://kroki.example")

    backend.to_bytes("@startuml\n@enduml", format=DiagramFormat.SVG)

    kroki.assert_called_once_with(
        server_url="https://kroki.example",
        diagram_type="plantuml",
        timeout_seconds=30.0,
        use_post=False,
        diagram_options=None,
        headers=None,
    )
    kroki.return_value.to_bytes.assert_called_once_with(
        "@startuml\n@enduml",
        format=DiagramFormat.SVG,
    )


def test_kroki_d2_backend__uses_d2_diagram_type(mocker):
    kroki = mocker.patch("c4.renderers.d2.backends.KrokiBackend")
    backend = KrokiD2Backend(server_url="https://kroki.example")

    backend.to_bytes("a -> b", format=DiagramFormat.SVG)

    kroki.assert_called_once()
    assert kroki.call_args.kwargs["diagram_type"] == "d2"
    kroki.return_value.to_bytes.assert_called_once_with(
        "a -> b",
        format=DiagramFormat.SVG,
    )


def test_kroki_d2_backend__rejects_layout():
    backend = KrokiD2Backend(server_url="https://kroki.example")

    with pytest.raises(
        D2BackendConfigurationError,
        match="does not support D2 layout",
    ):
        backend.to_bytes(
            "a -> b",
            format=DiagramFormat.SVG,
            render_options=D2RenderOptions(layout="elk"),
        )


def test_kroki_mermaid_backend__uses_mermaid_diagram_type(mocker):
    kroki = mocker.patch("c4.renderers.mermaid.backends.KrokiBackend")
    backend = KrokiMermaidBackend(server_url="https://kroki.example")

    backend.to_bytes("C4Context", format=DiagramFormat.PNG)

    kroki.assert_called_once()
    assert kroki.call_args.kwargs["diagram_type"] == "mermaid"
    kroki.return_value.to_bytes.assert_called_once_with(
        "C4Context",
        format=DiagramFormat.PNG,
    )


def test_kroki_structurizr_backend__uses_view_key_option(mocker):
    kroki = mocker.patch(
        "c4.contrib.structurizr.renderer.backends.KrokiBackend"
    )
    backend = KrokiStructurizrBackend(
        server_url="https://kroki.example",
        view_key="container-view",
    )

    backend.to_bytes("workspace", format=DiagramFormat.SVG)

    kroki.assert_called_once()
    assert kroki.call_args.kwargs["diagram_type"] == "structurizr"
    assert kroki.call_args.kwargs["diagram_options"] == {
        "view-key": "container-view"
    }
    kroki.return_value.to_bytes.assert_called_once_with(
        "workspace",
        format=DiagramFormat.SVG,
    )

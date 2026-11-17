"""Offline smoke test: runs the exporter against a canned catalog response.

Run from the repository root:  python -m pytest examples/backstage
"""

from __future__ import annotations

import importlib.util
import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import pytest

from c4.converters.json.converter import diagram_from_dict

HERE = Path(__file__).parent
CATALOG = json.loads((HERE / "fixtures" / "catalog.json").read_text())
EXPORTER = HERE.parent / "scripts" / "export_c4_from_backstage.py"
PAGE_SIZE = 5  # force pagination: the fixture has more than one page

spec = importlib.util.spec_from_file_location(
    "export_c4_from_backstage", EXPORTER
)
exporter = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exporter)


class FakeCatalog(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        url = urlparse(self.path)
        query = parse_qs(url.query)
        if url.path.endswith("/entities/by-query"):
            start = int(query["cursor"][0]) if "cursor" in query else 0
            items = CATALOG["items"][start : start + PAGE_SIZE]
            nxt = start + PAGE_SIZE
            body = {
                "items": items,
                "pageInfo": {"nextCursor": str(nxt)}
                if nxt < len(CATALOG["items"])
                else {},
            }
        elif url.path.endswith(
            "/entities/by-name/system/default/order-processing"
        ):
            body = CATALOG["system"]
        else:
            self.send_error(404)
            return
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args: object) -> None:
        pass


@pytest.fixture(scope="module")
def base_url():
    server = HTTPServer(("127.0.0.1", 0), FakeCatalog)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/api/catalog"
    server.shutdown()


def export(
    base_url: str, backend: str, capsys: pytest.CaptureFixture[str]
) -> dict:
    assert exporter.main(["--base-url", base_url, "--backend", backend]) == 0
    return json.loads(capsys.readouterr().out)


@pytest.mark.parametrize("backend", ["plantuml", "core"])
def test_export_round_trip(base_url, capsys, backend):
    data = export(base_url, backend, capsys)

    diagram, _ = diagram_from_dict(data)
    assert diagram is not None

    boundary = data["boundaries"][0]
    assert boundary["label"] == "Order Processing API"
    assert len(boundary["elements"]) == 7  # 4 components + 3 resources
    assert data["title"] == "Order Processing API - Component Diagram"


def test_relationships_and_pagination(base_url, capsys):
    data = export(base_url, "core", capsys)
    edges = {(r["from"], r["to"]): r["label"] for r in data["relationships"]}
    assert edges == {
        ("order_controller", "order_app_service"): "Invokes",
        ("order_app_service", "inventory_checker"): "Depends on",
        ("order_app_service", "payment_adapter"): "Depends on",
        ("order_app_service", "order_db"): "Reads and writes",
        ("order_app_service", "order_events_bus"): "Publishes events to",
        ("payment_adapter", "payment_gateway_api"): "Authorizes payment via",
    }


def test_core_backend_drops_plantuml_fields(base_url, capsys):
    data = export(base_url, "core", capsys)
    assert "backend" not in data
    for element in data["boundaries"][0]["elements"]:
        assert not {"sprite", "tags", "stereotype"} & element.keys()

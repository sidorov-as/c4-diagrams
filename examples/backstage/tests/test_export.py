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
        elif "/entities/by-name/" in url.path:
            kind, _, name = url.path.split("/entities/by-name/")[1].split("/")
            known = [*CATALOG["items"], *CATALOG["external"], CATALOG["system"]]
            body = next(
                (
                    e
                    for e in known
                    if e["kind"].lower() == kind and e["metadata"]["name"] == name
                ),
                None,
            )
            if body is None:
                self.send_error(404)
                return
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

    assert data["type"] == "ContainerDiagram"
    assert data["title"] == "Order Processing - Container Diagram"
    boundary = data["boundaries"][0]
    assert boundary["type"] == "SystemBoundary"
    assert boundary["label"] == "Order Processing"
    # 3 services + database + queue inside the system; the gateway is not owned
    # by the system (no spec.system), it is fetched by reference and drawn outside
    assert {e["alias"]: e["type"] for e in boundary["elements"]} == {
        "order_api": "Container",
        "inventory_service": "Container",
        "payment_service": "Container",
        "order_db": "ContainerDb",
        "order_events_bus": "ContainerQueue",
    }
    assert [(e["alias"], e["type"]) for e in data["elements"]] == [
        ("payment_gateway", "SystemExt")
    ]


def test_relationships_and_pagination(base_url, capsys):
    data = export(base_url, "core", capsys)
    edges = {(r["from"], r["to"]): r["label"] for r in data["relationships"]}
    assert edges == {
        ("order_api", "inventory_service"): "Checks stock availability",
        ("order_api", "payment_service"): "Requests payment",
        ("order_api", "order_db"): "Reads and writes",
        ("order_api", "order_events_bus"): "Publishes events to",
        ("payment_service", "payment_gateway"): "Authorizes payment via",
    }


def test_core_backend_drops_plantuml_fields(base_url, capsys):
    data = export(base_url, "core", capsys)
    assert "backend" not in data
    for element in data["boundaries"][0]["elements"]:
        assert not {"sprite", "tags", "stereotype"} & element.keys()


def test_foreign_entity_without_ext_type_is_drawn_outside():
    service = {
        "kind": "Component",
        "metadata": {"name": "svc", "namespace": "default"},
        "spec": {},
        "relations": [
            {"type": "dependsOn", "targetRef": "resource:default/other-db"}
        ],
    }
    foreign_db = {
        "kind": "Resource",
        "metadata": {
            "name": "other-db",
            "namespace": "default",
            "annotations": {"c4.io/type": "ContainerDb"},
        },
        "spec": {},
        "relations": [],
    }
    data = exporter.build_diagram(
        [service], None, "sys", None, "core", [foreign_db]
    )
    assert [e["alias"] for e in data["boundaries"][0]["elements"]] == ["svc"]
    assert [(e["alias"], e["type"]) for e in data["elements"]] == [
        ("other_db", "ContainerDbExt")
    ]
    assert [(r["from"], r["to"], r["label"]) for r in data["relationships"]] == [
        ("svc", "other_db", "Reads and writes")
    ]

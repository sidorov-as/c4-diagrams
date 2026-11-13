import json
import textwrap
from collections.abc import Iterator
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from tests.conftest import CLI, MakeTmpPyFile


def _write_workspace_json(tmp_path) -> str:
    path = tmp_path / "workspace.json"
    path.write_text(
        json.dumps({
            "backend": "structurizr",
            "name": "Payments",
            "model": {
                "people": [{"id": "customer", "name": "Customer"}],
                "software_systems": [{"id": "payments", "name": "Payments"}],
                "relationships": [
                    {
                        "from": "customer",
                        "to": "payments",
                        "description": "Uses",
                    }
                ],
            },
            "views": {"items": [{"type": "system_landscape"}]},
        }),
        encoding="utf-8",
    )
    return str(path)


@contextmanager
def _kroki_server() -> Iterator[tuple[str, type[BaseHTTPRequestHandler]]]:
    class Handler(BaseHTTPRequestHandler):
        request_path: str | None = None
        view_key: str | None = None
        workspace: str | None = None

        def do_POST(self) -> None:
            type(self).request_path = self.path
            type(self).view_key = self.headers.get(
                "Kroki-Diagram-Options-view-key"
            )
            length = int(self.headers["Content-Length"])
            type(self).workspace = self.rfile.read(length).decode("utf-8")
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"workspace image")

        def log_message(self, *_: object) -> None:
            return None

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = server.server_address
        yield f"http://{host}:{port}", Handler
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_render_structurizr_workspace_to_stdout_with_ref(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
):
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4.contrib.structurizr import Workspace

            with Workspace("Payments") as workspace:
                with workspace.model as model:
                    customer = model.Person("Customer", alias="customer")
                    payments = model.SoftwareSystem("Payments", alias="payments")
                    api = payments.Container(
                        "API",
                        alias="api",
                    )
                    customer.uses(api, "Uses")

                with workspace.views as views:
                    views.SystemLandscapeView(key="landscape")
                    views.ContainerView(payments, key="containers")
            """
        ),
    )

    result = cli([
        "render",
        f"{module_path!s}:workspace",
        "--renderer",
        "structurizr",
        "--structurizr-style-preset",
        "none",
    ])

    assert result.exit_code == 0
    assert (
        result.stdout.strip()
        == textwrap.dedent(
            """
        workspace "Payments" {
          model {
            customer = person "Customer" {
              tags "Person"
            }
            payments = softwareSystem "Payments" {
              tags "Software System"
              api = container "API" {
                tags "Container"
              }
            }
            customer -> api "Uses" {
              tags "Relationship"
            }
          }
          views {
            systemLandscape "landscape" {
              include *
              autoLayout lr
            }
            container payments "containers" {
              include *
              autoLayout lr
            }
          }
        }
        """
        ).strip()
    )
    assert not result.stderr


def test_export_structurizr_workspace_through_kroki(
    tmp_path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
):
    module_path = make_tmp_py_file(
        "workspace.py",
        textwrap.dedent(
            """
            from c4.contrib.structurizr import Workspace

            workspace = Workspace("Payments")
            """
        ),
    )
    output_path = tmp_path / "workspace.png"

    with _kroki_server() as (server_url, handler):
        result = cli([
            "export",
            str(module_path),
            "--renderer",
            "structurizr",
            "--kroki-url",
            server_url,
            "--kroki-method",
            "post",
            "--structurizr-view-key",
            "landscape",
            "--format",
            "png",
            "--output",
            str(output_path),
        ])

    assert result.exit_code == 0, result.stderr
    assert not result.stdout
    assert not result.stderr
    assert output_path.read_bytes() == b"workspace image"
    assert handler.request_path == "/structurizr/png"
    assert handler.view_key == "landscape"
    assert handler.workspace is not None
    assert 'workspace "Payments"' in handler.workspace


def test_render_structurizr_json_workspace(tmp_path, cli: CLI):
    result = cli([
        "render",
        _write_workspace_json(tmp_path),
        "--renderer",
        "structurizr",
    ])

    assert result.exit_code == 0, result.stderr
    assert 'workspace "Payments"' in result.stdout
    assert not result.stderr


def test_export_structurizr_json_workspace_through_kroki(tmp_path, cli: CLI):
    output_path = tmp_path / "workspace.png"

    with _kroki_server() as (server_url, handler):
        result = cli([
            "export",
            _write_workspace_json(tmp_path),
            "--renderer",
            "structurizr",
            "--kroki-url",
            server_url,
            "--kroki-method",
            "post",
            "--format",
            "png",
            "--output",
            str(output_path),
        ])

    assert result.exit_code == 0, result.stderr
    assert output_path.read_bytes() == b"workspace image"
    assert handler.workspace is not None
    assert 'workspace "Payments"' in handler.workspace


def test_render_rejects_malformed_structurizr_json_workspace(
    tmp_path, cli: CLI
):
    path = tmp_path / "workspace.json"
    path.write_text('{"backend": "structurizr", "model": {}}', encoding="utf-8")

    result = cli(["render", str(path), "--renderer", "structurizr"])

    assert result.exit_code != 0
    assert "views" in result.stderr

from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDiagram,
    ContainerExt,
    ContainerQueue,
    Person,
    Rel,
    SystemExt,
)

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_container_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with ContainerDiagram(title="Internet Banking Containers") as diagram:
        customer = Person("Customer", alias="customer")
        email = SystemExt("Email System", alias="email_system")

        with ContainerBoundary("Internet Banking", alias="internet_banking"):
            spa = Container(
                "Single-Page App",
                technology="TypeScript",
                alias="spa",
            )
            api = ContainerExt(
                "API Application",
                technology="Java",
                alias="api",
            )
            db = ContainerDb(
                "Database",
                technology="PostgreSQL",
                alias="database",
            )
            queue = ContainerQueue(
                "Command Queue",
                technology="RabbitMQ",
                alias="command_queue",
            )

        customer >> Rel("Uses", technology="HTTPS") >> spa
        spa >> Rel("Calls", technology="JSON/HTTPS") >> api
        api >> "Reads and writes" >> db
        api >> "Publishes commands" >> queue
        api >> "Sends email using" >> email

    assert_match_snapshot(
        snapshot_name="d2/container_diagram.d2",
        diagram_code=diagram.as_d2(),
    )

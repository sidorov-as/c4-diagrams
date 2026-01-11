from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Container,
    ContainerDb,
    DynamicDiagram,
    Index,
    LastIndex,
    Person,
    Rel,
    RelDown,
    RelLeft,
    RelRight,
    RelUp,
    SetIndex,
    SystemBoundary,
)
from c4.renderers.plantuml import LayoutOptions

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_dynamic_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DynamicDiagram() as diagram:
        customer = Person("customer", "Customer", "A customer")

        with SystemBoundary("c1", "Customer Information"):
            app = Container(
                "app",
                "Customer Application",
                "Javascript, Angular",
                "Allows customers to manage their profile",
            )
            customer_service = Container(
                "customer_service",
                "Customer Service",
                "Java, Spring Boot",
                "The point of access for customer information",
            )
            message_bus = Container(
                "message_bus",
                "Message Bus",
                "RabbitMQ",
                "Transport for business events",
            )
            reporting_service = Container(
                "reporting_service",
                "Reporting Service",
                "Ruby",
                "Creates normalised data for reporting purposes",
            )
            audit_service = Container(
                "audit_service",
                "Audit Service",
                "C#/.NET",
                "Provides organisation-wide auditing facilities",
            )
            customer_db = ContainerDb(
                "customer_db",
                "Customer Database",
                "Oracle 12c",
                "Stores customer information",
            )
            reporting_db = ContainerDb(
                "reporting_db",
                "Reporting Database",
                "MySQL",
                "Stores a normalized version of all business data for ad hoc reporting purposes",
            )
            audit_store = Container(
                "audit_store",
                "Audit Store",
                "Event Store",
                "Stores information about events that have happened",
            )

        customer >> RelDown("Updates his profile using", "HTTPS") >> app
        (
            app
            >> Rel("Updates customer information using", "JSON/HTTPS")
            >> customer_service
        )
        customer_service >> RelRight("Stores data in", "JDBC") >> customer_db

        (
            customer_service
            >> RelDown(
                "Sends customer update events to", "async", index=f"{Index()}-1"
            )
            >> message_bus
        )
        (
            customer_service
            >> RelUp("Confirm update to", "async", index=LastIndex() + "-2")
            >> app
        )

        (
            message_bus
            >> RelLeft(
                "Sends customer update events to", "async", index=f"{Index()}-1"
            )
            >> reporting_service
        )
        (
            reporting_service
            >> Rel("Stores data in", index=f"{Index()}-1")
            >> reporting_db
        )

        (
            message_bus
            >> RelRight(
                "Sends customer update events to",
                "async",
                index=f"{SetIndex(5)}-2",
            )
            >> audit_service
        )
        (
            audit_service
            >> Rel("Stores events in", index=f"{Index()}-2")
            >> audit_store
        )

        layout_options = (
            LayoutOptions().layout_top_down(with_legend=True).show_legend()
        )

    diagram_code = diagram.as_plantuml(layout_options=layout_options)

    assert_match_snapshot(
        snapshot="plantuml/dynamic_diagram.puml",
        diagram_code=diagram_code,
    )

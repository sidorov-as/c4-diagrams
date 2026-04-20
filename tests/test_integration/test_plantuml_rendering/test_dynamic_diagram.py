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
from c4.renderers.plantuml import PlantUMLRenderOptionsBuilder

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_dynamic_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DynamicDiagram() as diagram:
        customer = Person("Customer", "A customer", alias="customer")

        with SystemBoundary("Customer Information", alias="c1"):
            app = Container(
                "Customer Application",
                "Allows customers to manage their profile",
                "Javascript, Angular",
                alias="app",
            )
            customer_service = Container(
                "Customer Service",
                "The point of access for customer information",
                "Java, Spring Boot",
                alias="customer_service",
            )
            message_bus = Container(
                "Message Bus",
                "Transport for business events",
                "RabbitMQ",
                alias="message_bus",
            )
            reporting_service = Container(
                "Reporting Service",
                "Creates normalised data for reporting purposes",
                "Ruby",
                alias="reporting_service",
            )
            audit_service = Container(
                "Audit Service",
                "Provides organisation-wide auditing facilities",
                "C#/.NET",
                alias="audit_service",
            )
            customer_db = ContainerDb(
                "Customer Database",
                "Stores customer information",
                "Oracle 12c",
                alias="customer_db",
            )
            reporting_db = ContainerDb(
                "Reporting Database",
                "Stores a normalized version of all business data for ad hoc reporting purposes",
                "MySQL",
                alias="reporting_db",
            )
            audit_store = Container(
                "Audit Store",
                "Stores information about events that have happened",
                "Event Store",
                alias="audit_store",
            )

        (
            customer
            >> RelDown("Updates his profile using", technology="HTTPS")
            >> app
        )
        (
            app
            >> Rel(
                "Updates customer information using", technology="JSON/HTTPS"
            )
            >> customer_service
        )
        (
            customer_service
            >> RelRight("Stores data in", technology="JDBC")
            >> customer_db
        )

        (
            customer_service
            >> RelDown(
                "Sends customer update events to",
                technology="async",
                index=f"{Index()}-1",
            )
            >> message_bus
        )
        (
            customer_service
            >> RelUp(
                "Confirm update to",
                technology="async",
                index=LastIndex() + "-2",
            )
            >> app
        )

        (
            message_bus
            >> RelLeft(
                "Sends customer update events to",
                technology="async",
                index=f"{Index()}-1",
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
                technology="async",
                index=f"{SetIndex(5)}-2",
            )
            >> audit_service
        )
        (
            audit_service
            >> Rel("Stores events in", index=f"{Index()}-2")
            >> audit_store
        )

        render_options = (
            PlantUMLRenderOptionsBuilder()
            .layout_top_down(with_legend=True)
            .show_legend()
            .build()
        )

    diagram_code = diagram.as_plantuml(render_options=render_options)

    assert_match_snapshot(
        snapshot_name="plantuml/dynamic_diagram.puml",
        diagram_code=diagram_code,
    )

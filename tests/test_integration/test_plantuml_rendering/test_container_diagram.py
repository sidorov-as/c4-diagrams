from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Container,
    ContainerDb,
    ContainerDiagram,
    ContainerQueue,
    LayRight,
    Person,
    Rel,
    RelDown,
    RelUp,
    SystemBoundary,
)
from c4.renderers.plantuml import LayoutOptions

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_container_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with ContainerDiagram() as diagram:
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
                tags=["microService"],
                alias="customer_service",
            )
            message_bus = ContainerQueue(
                "Message Bus",
                "Transport for business events",
                "RabbitMQ",
                alias="message_bus",
            )
            reporting_service = Container(
                "Reporting Service",
                "Creates normalised data for reporting purposes",
                "Ruby",
                tags=["microService"],
                alias="reporting_service",
            )
            audit_service = Container(
                "Audit Service",
                "Provides organisation-wide auditing facilities",
                "C#/.NET",
                tags=["microService"],
                alias="audit_service",
            )
            customer_db = ContainerDb(
                "Customer Database",
                "Stores customer information",
                "Oracle 12c",
                tags=["storage"],
                alias="customer_db",
            )
            reporting_db = ContainerDb(
                "Reporting Database",
                "Stores a normalized version of all business data for ad hoc reporting purposes",
                "MySQL",
                tags=["storage"],
                alias="reporting_db",
            )
            audit_store = Container(
                "Audit Store",
                "Stores information about events that have happened",
                "Event Store",
                tags=["storage"],
                alias="audit_store",
            )

            customer >> RelDown("Uses", technology="HTTPS") >> app
            app >> RelDown('Updates customer information using', technology='async, JSON/HTTPS') >> customer_service  # fmt: off

            (
                customer_service
                >> RelUp("Sends events to", technology="WebSocket")
                >> app
            )
            customer_service >> RelUp('Sends customer update events to') >> message_bus  # fmt: off

            (
                customer_service
                >> Rel("Stores data in", technology="JDBC")
                >> customer_db
            )

            message_bus >> Rel('Sends customer update events to') >> [reporting_service, audit_service]  # fmt: off

            reporting_service >> Rel("Stores data in") >> reporting_db
            audit_service >> Rel("Stores events in") >> audit_store

        LayRight(reporting_service, audit_service)

        layout_config = (
            LayoutOptions()
            .add_element_tag(
                "microService",
                shape="EightSidedShape",
                bg_color="CornflowerBlue",
                font_color="white",
                legend_text="micro service\neight sided",
            )
            .add_element_tag(
                "storage",
                shape="RoundedBoxShape",
                bg_color="lightSkyBlue",
                font_color="white",
            )
            .show_person_outline()
            .show_legend()
        ).build()

    diagram_code = diagram.as_plantuml(layout_config=layout_config)

    assert_match_snapshot(
        snapshot_name="plantuml/container_diagram.puml",
        diagram_code=diagram_code,
    )

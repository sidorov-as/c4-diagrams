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
                tags="microService",
            )
            message_bus = ContainerQueue(
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
                tags="microService",
            )
            audit_service = Container(
                "audit_service",
                "Audit Service",
                "C#/.NET",
                "Provides organisation-wide auditing facilities",
                tags="microService",
            )
            customer_db = ContainerDb(
                "customer_db",
                "Customer Database",
                "Oracle 12c",
                "Stores customer information",
                tags="storage",
            )
            reporting_db = ContainerDb(
                "reporting_db",
                "Reporting Database",
                "MySQL",
                "Stores a normalized version of all business data for ad hoc reporting purposes",
                tags="storage",
            )
            audit_store = Container(
                "audit_store",
                "Audit Store",
                "Event Store",
                "Stores information about events that have happened",
                tags="storage",
            )

            customer >> RelDown("Uses", "HTTPS") >> app
            app >> RelDown('Updates customer information using', 'async, JSON/HTTPS') >> customer_service  # fmt: off

            customer_service >> RelUp("Sends events to", "WebSocket") >> app
            customer_service >> RelUp('Sends customer update events to') >> message_bus  # fmt: off

            customer_service >> Rel("Stores data in", "JDBC") >> customer_db

            message_bus >> Rel('Sends customer update events to') >> [reporting_service, audit_service]  # fmt: off

            reporting_service >> Rel("Stores data in") >> reporting_db
            audit_service >> Rel("Stores events in") >> audit_store

        LayRight(reporting_service, audit_service)

        layout_options = (
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
        )

    diagram_code = diagram.as_plantuml(layout_options=layout_options)

    assert_match_snapshot(
        snapshot="plantuml/container_diagram.puml",
        diagram_code=diagram_code,
    )

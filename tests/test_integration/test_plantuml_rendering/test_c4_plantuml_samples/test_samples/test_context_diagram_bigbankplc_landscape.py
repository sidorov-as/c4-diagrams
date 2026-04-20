from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    EnterpriseBoundary,
    LayD,
    LayU,
    Person,
    PersonExt,
    RelBack,
    RelD,
    RelNeighbor,
    RelR,
    RelU,
    System,
    SystemExt,
    SystemLandscapeDiagram,
)
from c4.renderers.plantuml import PlantUMLRenderOptionsBuilder

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    """
    # https://github.com/plantuml-stdlib/C4-PlantUML
    # samples/C4_Context Diagram Sample - bigbankplc-landscape.puml
    """
    with SystemLandscapeDiagram(
        title="System Landscape diagram for Big Bank plc"
    ) as diagram:
        customer = Person(
            "Personal Banking Customer",
            "A customer of the bank, with personal bank accounts.",
            alias="customer",
        )

        with EnterpriseBoundary("Big Bank plc", alias="c0"):
            banking_system = System(
                "Internet Banking System",
                "Allows customers to view information about their bank accounts, and make payments.",
                alias="banking_system",
            )

            atm = SystemExt(
                "ATM", "Allows customers to withdraw cash.", alias="atm"
            )
            mail_system = SystemExt(
                "E-mail system",
                "The internal Microsoft Exchange e-mail system.",
                alias="mail_system",
            )

            mainframe = SystemExt(
                "Mainframe Banking System",
                "Stores all of the core banking information about customers, accounts, transactions, etc.",
                alias="mainframe",
            )

            customer_service = PersonExt(
                "Customer Service Staff",
                "Customer service staff within the bank.",
                alias="customer_service",
            )
            back_office = PersonExt(
                "Back Office Staff",
                "Administration and support staff within the bank.",
                alias="back_office",
            )

        customer >> RelNeighbor("Uses") >> banking_system
        customer >> RelR("Withdraws cash using") >> atm
        customer >> RelBack("Sends e-mails to") >> mail_system

        (
            customer
            >> RelR("Asks questions to", technology="Telephone")
            >> customer_service
        )

        banking_system >> RelD("Sends e-mail using") >> mail_system
        atm >> RelR("Uses") >> mainframe
        banking_system >> RelR("Uses") >> mainframe
        customer_service >> RelD("Uses") >> mainframe
        back_office >> RelU("Uses") >> mainframe

        LayD(atm, banking_system)

        LayD(atm, customer)
        LayU(mail_system, customer)

        render_options = (
            PlantUMLRenderOptionsBuilder().layout_with_legend().build()
        )

    diagram_code = diagram.as_plantuml(render_options=render_options)

    assert_match_snapshot(
        snapshot_name="plantuml/samples/c4_context-diagram-sample-bigbankplc-landscape.puml",
        diagram_code=diagram_code,
    )

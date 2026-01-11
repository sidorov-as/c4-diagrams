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
from c4.renderers.plantuml import LayoutOptions

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_system_landscape_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with SystemLandscapeDiagram(
        title="System Landscape diagram for Big Bank plc"
    ) as diagram:
        customer = Person(
            "customer",
            "Personal Banking Customer",
            "A customer of the bank, with personal bank accounts.",
        )

        with EnterpriseBoundary("c0", "Big Bank plc"):
            banking_system = System(
                "banking_system",
                "Internet Banking System",
                "Allows customers to view information about their bank accounts, and make payments.",
            )

            atm = SystemExt("atm", "ATM", "Allows customers to withdraw cash.")
            mail_system = SystemExt(
                "mail_system",
                "E-mail system",
                "The internal Microsoft Exchange e-mail system.",
            )

            mainframe = SystemExt(
                "mainframe",
                "Mainframe Banking System",
                "Stores all of the core banking information about customers, accounts, transactions, etc.",
            )

            customer_service = PersonExt(
                "customer_service",
                "Customer Service Staff",
                "Customer service staff within the bank.",
            )
            back_office = PersonExt(
                "back_office",
                "Back Office Staff",
                "Administration and support staff within the bank.",
            )

        customer >> RelNeighbor("Uses") >> banking_system
        customer >> RelR("Withdraws cash using") >> atm
        customer >> RelBack("Sends e-mails to") >> mail_system

        customer >> RelR("Asks questions to", "Telephone") >> customer_service

        banking_system >> RelD("Sends e-mail using") >> mail_system
        atm >> RelR("Uses") >> mainframe
        banking_system >> RelR("Uses") >> mainframe
        customer_service >> RelD("Uses") >> mainframe
        back_office >> RelU("Uses") >> mainframe

        LayD(atm, banking_system)

        LayD(atm, customer)
        LayU(mail_system, customer)

        layout_options = LayoutOptions().layout_with_legend()

    diagram_code = diagram.as_plantuml(layout_options=layout_options)

    assert_match_snapshot(
        snapshot="plantuml/system_landscape_diagram.puml",
        diagram_code=diagram_code,
    )

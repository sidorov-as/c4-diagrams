from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Person,
    Rel,
    RelBack,
    RelNeighbor,
    System,
    SystemContextDiagram,
    SystemExt,
)
from c4.renderers.plantuml import LayoutOptions

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    """
    # https://github.com/plantuml-stdlib/C4-PlantUML
    # samples/C4_Context Diagram Sample - bigbankplc.puml
    """
    with SystemContextDiagram(
        title="System Context diagram for Internet Banking System"
    ) as diagram:
        customer = Person(
            "customer",
            "Personal Banking Customer",
            "A customer of the bank, with personal bank accounts.",
        )

        banking_system = System(
            "banking_system",
            "Internet Banking System",
            "Allows customers to view information about their bank accounts, and make payments.",
        )
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

        customer >> Rel("Uses") >> banking_system
        customer >> RelBack("Sends e-mails to") >> mail_system
        banking_system >> RelNeighbor("Sends e-mails", "SMTP") >> mail_system
        banking_system >> Rel("Uses") >> mainframe

        layout_options = LayoutOptions().layout_with_legend()

    diagram_code = diagram.as_plantuml(layout_options=layout_options)

    assert_match_snapshot(
        snapshot="plantuml/samples/c4_context-diagram-sample-bigbankplc.puml",
        diagram_code=diagram_code,
    )

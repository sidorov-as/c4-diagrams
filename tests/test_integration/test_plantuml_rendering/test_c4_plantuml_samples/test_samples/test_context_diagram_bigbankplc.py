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
            "Personal Banking Customer",
            "A customer of the bank, with personal bank accounts.",
            alias="customer",
        )

        banking_system = System(
            "Internet Banking System",
            "Allows customers to view information about their bank accounts, and make payments.",
            alias="banking_system",
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

        customer >> Rel("Uses") >> banking_system
        customer >> RelBack("Sends e-mails to") >> mail_system
        (
            banking_system
            >> RelNeighbor("Sends e-mails", technology="SMTP")
            >> mail_system
        )
        banking_system >> Rel("Uses") >> mainframe

        layout_config = LayoutOptions().layout_with_legend().build()

    diagram_code = diagram.as_plantuml(layout_config=layout_config)

    assert_match_snapshot(
        snapshot="plantuml/samples/c4_context-diagram-sample-bigbankplc.puml",
        diagram_code=diagram_code,
    )

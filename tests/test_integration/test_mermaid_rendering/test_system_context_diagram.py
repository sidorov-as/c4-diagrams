from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemQueue,
    SystemQueueExt,
)
from c4.diagrams.core import BiRel, Boundary
from c4.renderers import MermaidRenderOptionsBuilder

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_system_context_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with SystemContextDiagram(
        title="System Context diagram for Internet Banking System"
    ) as diagram:
        with EnterpriseBoundary("BankBoundary0", alias="b0"):
            customer_a = Person(
                "Banking Customer A",
                "A customer of the bank, with personal bank accounts.",
                alias="customerA",
            )
            Person("Banking Customer B", alias="customerB")
            PersonExt("Banking Customer C", "desc", alias="customerC")
            Person(
                "Banking Customer D",
                "A customer of the bank, <br/> with personal bank accounts.",
                alias="customerD",
            )

            system_aa = System(
                "Internet Banking System",
                "Allows customers to view information about their bank accounts, and make payments.",
                alias="SystemAA",
            )

            with EnterpriseBoundary("BankBoundary", alias="b1"):
                system_e = SystemDbExt(
                    "Mainframe Banking System",
                    "Stores all of the core banking information about customers, accounts, transactions, etc.",
                    alias="SystemE",
                )

                with SystemBoundary("BankBoundary2", alias="b2"):
                    System("Banking System A", alias="SystemA")
                    System(
                        "Banking System B",
                        "A system of the bank, with personal bank accounts. next line.",
                        alias="SystemB",
                    )

                system_c = SystemExt(
                    "E-mail system",
                    "The internal Microsoft Exchange e-mail system.",
                    alias="SystemC",
                )
                SystemDb(
                    "Banking System D Database",
                    "A system of the bank, with personal bank accounts.",
                    alias="SystemD",
                )

                with Boundary("BankBoundary3", alias="b3", type_="boundary"):
                    SystemQueue(
                        "Banking System F Queue",
                        "A system of the bank.",
                        alias="SystemF",
                    )
                    SystemQueueExt(
                        "Banking System G Queue",
                        "A system of the bank, with personal bank accounts.",
                        alias="SystemG",
                    )

        customer_a >> BiRel("Uses") >> system_aa
        system_aa >> BiRel("Uses") >> system_e
        system_aa >> Rel("Sends e-mails", technology="SMTP") >> system_c
        system_c >> Rel("Sends e-mails to") >> customer_a

        render_options = (
            MermaidRenderOptionsBuilder()
            .update_element_style(
                customer_a,
                font_color="red",
                bg_color="grey",
                border_color="red",
            )
            .update_rel_style(
                customer_a,
                system_aa,
                text_color="blue",
                line_color="blue",
                offset_x=5,
            )
            .update_rel_style(
                system_aa,
                system_e,
                text_color="blue",
                line_color="blue",
                offset_x=-10,
            )
            .update_rel_style(
                system_aa,
                system_c,
                text_color="blue",
                line_color="blue",
                offset_x=-40,
                offset_y=-50,
            )
            .update_rel_style(
                system_c,
                customer_a,
                text_color="red",
                line_color="red",
                offset_x=-50,
                offset_y=20,
            )
            .update_layout_config(c4_shape_in_row=3, c4_boundary_in_row=1)
            .build()
        )

    diagram_code = diagram.as_mermaid(render_options=render_options)

    assert_match_snapshot(
        snapshot_name="mermaid/system_context_diagram.mmd",
        diagram_code=diagram_code,
    )

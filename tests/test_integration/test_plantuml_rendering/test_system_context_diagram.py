from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    EnterpriseBoundary,
    LayDown,
    Person,
    Rel,
    RelDown,
    RelLeft,
    RelRight,
    System,
    SystemContextDiagram,
)
from c4.renderers.plantuml import LayoutOptions

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_system_context_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with SystemContextDiagram() as diagram:
        customer = Person(
            "Customer",
            "A customer of Widgets Limited.",
            alias="customer",
        )

        with EnterpriseBoundary("Widgets Limited", alias="c0"):
            csa = Person(
                "Customer Service Agent",
                "Deals with customer enquiries.",
                alias="csa",
            )

            ecommerce = System(
                "E-commerce System",
                "Allows customers to buy widgets online via the widgets.com website.",
                alias="ecommerce",
            )

            fulfillment = System(
                "Fulfillment System",
                "Responsible for processing and shipping of customer orders.",
                alias="fulfillment",
            )

        taxamo = System(
            "Taxamo",
            "Calculates local tax and acts as a front-end for Braintree Payments.",
            alias="taxamo",
        )

        braintree = System(
            "Braintree Payments",
            "Processes credit card payments on behalf of Widgets Limited.",
            alias="braintree",
        )

        post = System(
            "Jersey Post",
            "Calculates worldwide shipping costs for packages.",
            alias="post",
        )

        customer >> RelRight("Asks questions to", technology="Telephone") >> csa
        customer >> RelRight("Places orders for widgets using") >> ecommerce
        csa >> Rel("Looks up order information using") >> ecommerce
        ecommerce >> RelRight("Sends order information to") >> fulfillment
        fulfillment >> RelDown("Gets shipping charges from") >> post
        ecommerce >> RelDown("Delegates credit card processing to") >> taxamo
        taxamo >> RelLeft("Uses for credit card processing") >> braintree

        LayDown(customer, braintree)

        layout_options = LayoutOptions().layout_top_down(with_legend=True)

    diagram_code = diagram.as_plantuml(layout_options=layout_options)

    assert_match_snapshot(
        snapshot="plantuml/system_context_diagram.puml",
        diagram_code=diagram_code,
    )

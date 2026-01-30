from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    EnterpriseBoundary,
    LayD,
    Person,
    Rel,
    RelD,
    RelL,
    RelR,
    System,
    SystemContextDiagram,
)
from c4.renderers.plantuml import LayoutOptions

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    """
    # https://github.com/plantuml-stdlib/C4-PlantUML
    # samples/C4_Context Diagram Sample - enterprise.puml
    """
    with SystemContextDiagram() as diagram:
        customer = Person(
            "customer", "Customer", "A customer of Widgets Limited."
        )

        with EnterpriseBoundary("c0", "Widgets Limited"):
            csa = Person(
                "csa",
                "Customer Service Agent",
                "Deals with customer enquiries.",
            )

            ecommerce = System(
                "ecommerce",
                "E-commerce System",
                "Allows customers to buy widgets online via the widgets.com website.",
            )

            fulfillment = System(
                "fulfillment",
                "Fulfillment System",
                "Responsible for processing and shipping of customer orders.",
            )

        taxamo = System(
            "taxamo",
            "Taxamo",
            "Calculates local tax and acts as a front-end for Braintree Payments.",
        )

        braintree = System(
            "braintree",
            "Braintree Payments",
            "Processes credit card payments on behalf of Widgets Limited.",
        )

        post = System(
            "post",
            "Jersey Post",
            "Calculates worldwide shipping costs for packages.",
        )

        customer >> RelR("Asks questions to", technology="Telephone") >> csa
        customer >> RelR("Places orders for widgets using") >> ecommerce
        csa >> Rel("Looks up order information using") >> ecommerce
        ecommerce >> RelR("Sends order information to") >> fulfillment
        fulfillment >> RelD("Gets shipping charges from") >> post
        ecommerce >> RelD("Delegates credit card processing to") >> taxamo
        taxamo >> RelL("Uses for credit card processing") >> braintree

        LayD(customer, braintree)

        layout_options = LayoutOptions().layout_top_down(with_legend=True)

    diagram_code = diagram.as_plantuml(layout_options=layout_options)

    assert_match_snapshot(
        snapshot="plantuml/samples/c4_context-diagram-sample-enterprise.puml",
        diagram_code=diagram_code,
    )

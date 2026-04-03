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

        customer >> RelR("Asks questions to", technology="Telephone") >> csa
        customer >> RelR("Places orders for widgets using") >> ecommerce
        csa >> Rel("Looks up order information using") >> ecommerce
        ecommerce >> RelR("Sends order information to") >> fulfillment
        fulfillment >> RelD("Gets shipping charges from") >> post
        ecommerce >> RelD("Delegates credit card processing to") >> taxamo
        taxamo >> RelL("Uses for credit card processing") >> braintree

        LayD(customer, braintree)

        layout_config = (
            LayoutOptions().layout_top_down(with_legend=True).build()
        )

    diagram_code = diagram.as_plantuml(layout_config=layout_config)

    assert_match_snapshot(
        snapshot_name="plantuml/samples/c4_context-diagram-sample-enterprise.puml",
        diagram_code=diagram_code,
    )

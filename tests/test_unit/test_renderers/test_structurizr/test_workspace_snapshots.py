from __future__ import annotations

from c4.contrib.structurizr import RawSelector, ViewTag, Workspace
from c4.contrib.structurizr.renderer import (
    AutoLayout,
    StructurizrRenderer,
    StructurizrRenderOptions,
)
from tests.conftest import AssertMatchSnapshot


def test_render_complete_workspace_snapshot(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with Workspace(
        "Payments",
        description="Payments architecture",
    ) as workspace:
        with workspace.model as model:
            customer = model.Person(
                "Customer",
                alias="customer",
                tags=["External"],
                properties={"segment": "retail"},
                url="https://example.com/customer",
            )
            payments = model.SoftwareSystem(
                "Payments",
                alias="payments",
                description="Collects money.",
            )

            with payments:
                web = payments.Container(
                    "Web App",
                    alias="web",
                    technology="Django",
                    description="Customer checkout UI.",
                )
                api = payments.Container(
                    "API",
                    alias="api",
                    technology="FastAPI",
                    description="Checkout API.",
                    tags=["Critical"],
                )
                database = payments.Container(
                    "Database",
                    alias="database",
                    technology="PostgreSQL",
                ).tag("Storage")

                with api:
                    checkout = api.Component(
                        "Checkout",
                        alias="checkout",
                        technology="Python",
                    )

            customer.uses(web, "Uses", technology="HTTPS")
            web.uses(api, "Calls", technology="JSON/HTTPS")
            api.uses(
                database,
                "Reads from and writes to",
                technology="SQL",
                tags=["Persistent"],
            )

            with model.DeploymentEnvironment("Production") as production:
                with production.DeploymentNode(
                    "Kubernetes",
                    alias="k8s",
                ) as k8s:
                    k8s.InfrastructureNode("Ingress", alias="ingress")
                    k8s.ContainerInstance(api)

        with workspace.views as views:
            views.SystemLandscapeView(key="landscape")
            views.SystemContextView(
                payments,
                key="context",
                include=[customer, payments],
                exclude=[RawSelector("relationship.tag==Deprecated")],
            )
            views.ContainerView(
                payments,
                key="containers",
                include=[RawSelector("*"), ViewTag("Storage")],
                auto_layout=AutoLayout("TopBottom"),
                animation=[[customer, web], [api, database]],
            )
            views.ComponentView(api, key="components")
            flow = views.DynamicView(payments, key="checkout-flow")
            flow.step(
                customer,
                web,
                "Starts checkout",
                technology="HTTPS",
            )
            flow.step(
                web,
                api,
                "Submits checkout",
                technology="JSON/HTTPS",
            )
            flow.step(
                api,
                database,
                "Persists checkout",
                technology="SQL",
            )
            views.DeploymentView(
                payments,
                environment="Production",
                key="production",
            )

        workspace.styles.element(
            "Critical",
            background="#ffcc00",
            color="#111111",
        ).relationship("Persistent", thickness=4)
    assert_match_snapshot(
        snapshot_name="structurizr/workspace.complete.dsl",
        diagram_code=StructurizrRenderer(
            StructurizrRenderOptions(style_preset=None),
        ).render(workspace),
    )

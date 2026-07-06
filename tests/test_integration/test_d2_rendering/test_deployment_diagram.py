from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Container,
    ContainerDb,
    DeploymentDiagram,
    DeploymentNode,
    Node,
    Rel,
)

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_deployment_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DeploymentDiagram(title="Live Deployment") as diagram:
        with Node("Customer Device", alias="customer_device"):
            mobile = Container(
                "Mobile App",
                technology="Swift",
                alias="mobile_app",
            )

        with Node("Cloud", alias="cloud"):
            with DeploymentNode("Kubernetes Cluster", alias="cluster"):
                api = Container(
                    "API Application",
                    technology="Java",
                    alias="api",
                )

            with DeploymentNode("Database Server", alias="database_server"):
                database = ContainerDb(
                    "Database",
                    technology="PostgreSQL",
                    alias="database",
                )

        mobile >> Rel("Makes API calls", technology="HTTPS") >> api
        api >> Rel("Reads from and writes to", technology="JDBC") >> database

    assert_match_snapshot(
        snapshot_name="d2/deployment_diagram.d2",
        diagram_code=diagram.as_d2(),
    )

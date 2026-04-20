from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Container,
    ContainerDb,
    DeploymentDiagram,
    DeploymentNode,
    Rel,
    RelRight,
    RelUp,
)
from c4.renderers import MermaidRenderOptionsBuilder

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_deployment_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DeploymentDiagram(
        title="Deployment Diagram for Internet Banking System - Live"
    ) as diagram:
        with DeploymentNode(
            "Customer's mobile device", "Apple IOS or Android", alias="mob"
        ):
            mobile = Container(
                "Mobile App",
                "Provides a limited subset of the Internet Banking functionality to customers via their mobile device.",
                technology="Xamarin",
                alias="mobile",
            )

        with DeploymentNode(
            "Customer's computer",
            "Microsoft Windows or Apple macOS",
            alias="comp",
        ):
            with DeploymentNode(
                "Web Browser",
                "Google Chrome, Mozilla Firefox,<br/> Apple Safari or Microsoft Edge",
                alias="browser",
            ):
                spa = Container(
                    "Single Page Application",
                    "Provides all of the Internet Banking functionality to customers via their web browser.",
                    technology="JavaScript and Angular",
                    alias="spa",
                )

        with DeploymentNode(
            "Big Bank plc", "Big Bank plc data center", alias="plc"
        ):
            with DeploymentNode(
                "bigbank-api*** x8", "Ubuntu 16.04 LTS", alias="dn"
            ):
                with DeploymentNode(
                    "Apache Tomcat", "Apache Tomcat 8.x", alias="apache"
                ):
                    api = Container(
                        "API Application",
                        "Provides Internet Banking functionality via a JSON/HTTPS API.",
                        technology="Java and Spring MVC",
                        alias="api",
                    )
                with DeploymentNode(
                    "bigbank-web*** x4", "Ubuntu 16.04 LTS", alias="bb2"
                ):
                    with DeploymentNode(
                        "Apache Tomcat", "Apache Tomcat 8.x", alias="apache2"
                    ):
                        web = Container(
                            "Web Application",
                            "Delivers the static content and the Internet Banking single page application.",
                            technology="Java and Spring MVC",
                            alias="web",
                        )
                with DeploymentNode(
                    "bigbank-db01", "Ubuntu 16.04 LTS", alias="bigbankdb01"
                ):
                    with DeploymentNode(
                        "Oracle - Primary", "Oracle 12c", alias="oracle"
                    ):
                        db = ContainerDb(
                            "Database",
                            "Stores user registration information, hashed authentication credentials, access logs, etc.",
                            technology="Relational Database Schema",
                            alias="db",
                        )
                with DeploymentNode(
                    "bigbank-db02", "Ubuntu 16.04 LTS", alias="bigbankdb02"
                ):
                    with DeploymentNode(
                        "Oracle - Secondary", "Oracle 12c", alias="oracle2"
                    ):
                        db2 = ContainerDb(
                            "Database",
                            "Stores user registration information, hashed authentication credentials, access logs, etc.",
                            technology="Relational Database Schema",
                            alias="db2",
                        )

        (
            [mobile, spa]
            >> Rel("Makes API calls to", technology="json/HTTPS")
            >> api
        )
        web >> RelUp("Delivers to the customer's web browser") >> spa
        api >> Rel("Reads from and writes to", technology="JDBC") >> [db, db2]
        db >> RelRight("Replicates data to") >> db2

        render_options = (
            MermaidRenderOptionsBuilder()
            .update_rel_style(spa, api, offset_y=-40)
            .update_rel_style(web, spa, offset_y=-40)
            .update_rel_style(api, db, offset_x=5, offset_y=-20)
            .update_rel_style(api, db2, offset_x=-40, offset_y=-20)
            .update_rel_style(db, db2, offset_y=-10)
            .build()
        )

    diagram_code = diagram.as_mermaid(render_options=render_options)

    assert_match_snapshot(
        snapshot_name="mermaid/deployment_diagram.mmd",
        diagram_code=diagram_code,
    )

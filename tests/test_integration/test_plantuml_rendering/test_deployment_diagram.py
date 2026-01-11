from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Container,
    ContainerDb,
    DeploymentDiagram,
    DeploymentNode,
    DeploymentNodeLeft,
    DeploymentNodeRight,
    Rel,
    RelRight,
    RelUp,
)
from c4.renderers.plantuml import LayoutOptions

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_deployment_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DeploymentDiagram(
        title="Deployment Diagram for Internet Banking System - Live"
    ) as diagram:
        with DeploymentNode("plc", "Big Bank plc", "Big Bank plc data center"):
            with DeploymentNode(
                "dn", "bigbank-api***\\tx8", "Ubuntu 16.04 LTS"
            ):
                with DeploymentNode(
                    "apache", "Apache Tomcat", "Apache Tomcat 8.x"
                ):
                    api = Container(
                        "api",
                        "API Application",
                        "Java and Spring MVC",
                        "Provides Internet Banking functionality via a JSON/HTTPS API.",
                    )

            with DeploymentNode(
                "bigbankdb01", "bigbank-db01", "Ubuntu 16.04 LTS"
            ):
                with DeploymentNode("oracle", "Oracle - Primary", "Oracle 12c"):
                    db = ContainerDb(
                        "db",
                        "Database",
                        "Relational Database Schema",
                        "Stores user registration information, hashed authentication credentials, access logs, etc.",
                    )

            with DeploymentNode(
                "bigbankdb02",
                "bigbank-db02",
                "Ubuntu 16.04 LTS",
                tags="fallback",
            ):
                with DeploymentNode(
                    "oracle2",
                    "Oracle - Secondary",
                    "Oracle 12c",
                    tags="fallback",
                ):
                    db2 = ContainerDb(
                        "db2",
                        "Database",
                        "Relational Database Schema",
                        "Stores user registration information, hashed authentication credentials, access logs, etc.",
                        tags="fallback",
                    )

            with DeploymentNode(
                "bb2", "bigbank-web***\\tx4", "Ubuntu 16.04 LTS"
            ):
                with DeploymentNode(
                    "apache2", "Apache Tomcat", "Apache Tomcat 8.x"
                ):
                    web = Container(
                        "web",
                        "Web Application",
                        "Java and Spring MVC",
                        "Delivers the static content and the Internet Banking single page application.",
                    )

        with DeploymentNode(
            "mob", "Customer's mobile device", "Apple IOS or Android"
        ):
            mobile = Container(
                "mobile",
                "Mobile App",
                "Xamarin",
                "Provides a limited subset of the Internet Banking functionality to customers via their mobile device.",
            )

        with DeploymentNode(
            "comp", "Customer's computer", "Microsoft Windows or Apple macOS"
        ):
            with DeploymentNode(
                "browser",
                "Web Browser",
                "Google Chrome, Mozilla Firefox, Apple Safari or Microsoft Edge",
            ):
                spa = Container(
                    "spa",
                    "Single Page Application",
                    "JavaScript and Angular",
                    "Provides all of the Internet Banking functionality to customers via their web browser.",
                )

        [mobile, spa] >> Rel("Makes API calls to", "json/HTTPS") >> api
        web >> RelUp("Delivers to the customer's web browser") >> spa
        api >> Rel("Reads from and writes to", "JDBC") >> db
        api >> Rel("Reads from and writes to", "JDBC", tags="fallback") >> db2
        db >> RelRight("Replicates data to") >> db2

        layout_options = (
            LayoutOptions()
            .add_element_tag("fallback", bg_color="#c0c0c0")
            .add_rel_tag("fallback", text_color="#c0c0c0", line_color="#438DD5")
            .show_legend()
        )

    diagram_code = diagram.as_plantuml(layout_options=layout_options)

    assert_match_snapshot(
        snapshot="plantuml/deployment_diagram.puml",
        diagram_code=diagram_code,
    )


def test_render_deployment_diagram_with_properties(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DeploymentDiagram(
        title="Deployment Diagram for Internet Banking System - Live"
    ) as diagram:
        with DeploymentNode(
            "plc", "Live", "Big Bank plc", "Big Bank plc data center"
        ):
            with DeploymentNodeLeft(
                "dn",
                "bigbank-api***\\tx8",
                "Ubuntu 16.04 LTS",
                "A web server residing in the web server farm, accessed via F5 BIG-IP LTMs.",
            ) as dn:
                dn.add_property("Location", "London and Reading")

                with DeploymentNodeLeft(
                    "apache",
                    "Apache Tomcat",
                    "Apache Tomcat 8.x",
                    "An open source Java EE web server.",
                ) as apache:
                    apache.add_property("Java Version", "8")
                    apache.add_property("Xmx", "512M")
                    apache.add_property("Xms", "1024M")

                    api = Container(
                        "api",
                        "API Application",
                        "Java and Spring MVC",
                        "Provides Internet Banking functionality via a JSON/HTTPS API.",
                    )

            with DeploymentNodeLeft(
                "bigbankdb01",
                "bigbank-db01",
                "Ubuntu 16.04 LTS",
                "The primary database server.",
            ) as bigbankdb01:
                bigbankdb01.add_property("Location", "London")

                with DeploymentNodeLeft(
                    "oracle",
                    "Oracle - Primary",
                    "Oracle 12c",
                    "The primary, live database server.",
                ):
                    db = ContainerDb(
                        "db",
                        "Database",
                        "Relational Database Schema",
                        "Stores user registration information, hashed authentication credentials, access logs, etc.",
                    )

            with DeploymentNodeRight(
                "bigbankdb02",
                "bigbank-db02",
                "Ubuntu 16.04 LTS",
                "The secondary database server.",
                tags="fallback",
            ) as bigbankdb02:
                bigbankdb02.add_property("Location", "Reading")

                with DeploymentNodeRight(
                    "oracle2",
                    "Oracle - Secondary",
                    "Oracle 12c",
                    "A secondary, standby database server, used for failover purposes only.",
                    tags="fallback",
                ):
                    db2 = ContainerDb(
                        "db2",
                        "Database",
                        "Relational Database Schema",
                        "Stores user registration information, hashed authentication credentials, access logs, etc.",
                        tags="fallback",
                    )

            with DeploymentNodeRight(
                "bb2",
                "bigbank-web***\\tx4",
                "Ubuntu 16.04 LTS",
                "A web server residing in the web server farm, accessed via F5 BIG-IP LTMs.",
            ) as bb2:
                bb2.add_property("Location", "London and Reading")

                with DeploymentNodeRight(
                    "apache2",
                    "Apache Tomcat",
                    "Apache Tomcat 8.x",
                    "An open source Java EE web server.",
                ) as apache2:
                    apache2.add_property("Java Version", "8")
                    apache2.add_property("Xmx", "512M")
                    apache2.add_property("Xms", "1024M")

                    web = Container(
                        "web",
                        "Web Application",
                        "Java and Spring MVC",
                        "Delivers the static content and the Internet Banking single page application.",
                    )

        with DeploymentNode(
            "mob", "Customer's mobile device", "Apple IOS or Android"
        ):
            mobile = Container(
                "mobile",
                "Mobile App",
                "Xamarin",
                "Provides a limited subset of the Internet Banking functionality to customers via their mobile device.",
            )

        with DeploymentNode(
            "comp", "Customer's computer", "Microsoft Windows or Apple macOS"
        ):
            with DeploymentNode(
                "browser",
                "Web Browser",
                "Google Chrome, Mozilla Firefox, Apple Safari or Microsoft Edge",
            ):
                spa = Container(
                    "spa",
                    "Single Page Application",
                    "JavaScript and Angular",
                    "Provides all of the Internet Banking functionality to customers via their web browser.",
                )

        [mobile, spa] >> Rel("Makes API calls to", "json/HTTPS") >> api
        web >> RelUp("Delivers to the customer's web browser") >> spa
        api >> Rel("Reads from and writes to", "JDBC") >> db
        api >> Rel("Reads from and writes to", "JDBC", tags="fallback") >> db2
        db >> RelRight("Replicates data to") >> db2

        layout_options = (
            LayoutOptions()
            .without_property_header()
            .add_element_tag("fallback", bg_color="#c0c0c0")
            .add_rel_tag("fallback", text_color="#c0c0c0", line_color="#438DD5")
            .show_legend()
        )

    diagram_code = diagram.as_plantuml(layout_options=layout_options)

    assert_match_snapshot(
        snapshot="plantuml/deployment_diagram_with_properties.puml",
        diagram_code=diagram_code,
    )

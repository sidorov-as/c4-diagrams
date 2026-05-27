from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Container,
    ContainerDb,
    DeploymentDiagram,
    DeploymentNode,
    Rel,
)
from c4.contrib.plantuml import (
    DeploymentNodeLeft,
    DeploymentNodeRight,
    RelRight,
    RelUp,
)
from c4.renderers.plantuml import PlantUMLRenderOptionsBuilder

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def plantuml_extensions(
    type_: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, dict[str, str | list[str] | None]]:
    return {"plantuml": {"type": type_, "tags": tags}}


def test_render_deployment_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DeploymentDiagram(
        title="Deployment Diagram for Internet Banking System - Live"
    ) as diagram:
        with DeploymentNode(
            "Big Bank plc",
            extensions=plantuml_extensions(type_="Big Bank plc data center"),
            alias="plc",
        ):
            with DeploymentNode(
                "bigbank-api***\\tx8",
                extensions=plantuml_extensions(type_="Ubuntu 16.04 LTS"),
                alias="dn",
            ):
                with DeploymentNode(
                    "Apache Tomcat",
                    extensions=plantuml_extensions(type_="Apache Tomcat 8.x"),
                    alias="apache",
                ):
                    api = Container(
                        "API Application",
                        "Provides Internet Banking functionality via a JSON/HTTPS API.",
                        "Java and Spring MVC",
                        alias="api",
                    )

            with DeploymentNode(
                "bigbank-db01",
                extensions=plantuml_extensions(type_="Ubuntu 16.04 LTS"),
                alias="bigbankdb01",
            ):
                with DeploymentNode(
                    "Oracle - Primary",
                    extensions=plantuml_extensions(type_="Oracle 12c"),
                    alias="oracle",
                ):
                    db = ContainerDb(
                        "Database",
                        "Stores user registration information, hashed authentication credentials, access logs, etc.",
                        "Relational Database Schema",
                        alias="db",
                    )

            with DeploymentNode(
                "bigbank-db02",
                extensions=plantuml_extensions(
                    type_="Ubuntu 16.04 LTS",
                    tags=["fallback"],
                ),
                alias="bigbankdb02",
            ):
                with DeploymentNode(
                    "Oracle - Secondary",
                    extensions=plantuml_extensions(
                        type_="Oracle 12c",
                        tags=["fallback"],
                    ),
                    alias="oracle2",
                ):
                    db2 = ContainerDb(
                        "Database",
                        "Stores user registration information, hashed authentication credentials, access logs, etc.",
                        "Relational Database Schema",
                        extensions={"plantuml": {"tags": ["fallback"]}},
                        alias="db2",
                    )

            with DeploymentNode(
                "bigbank-web***\\tx4",
                extensions=plantuml_extensions(type_="Ubuntu 16.04 LTS"),
                alias="bb2",
            ):
                with DeploymentNode(
                    "Apache Tomcat",
                    extensions=plantuml_extensions(type_="Apache Tomcat 8.x"),
                    alias="apache2",
                ):
                    web = Container(
                        "Web Application",
                        "Delivers the static content and the Internet Banking single page application.",
                        "Java and Spring MVC",
                        alias="web",
                    )

        with DeploymentNode(
            "Customer's mobile device",
            extensions=plantuml_extensions(type_="Apple IOS or Android"),
            alias="mob",
        ):
            mobile = Container(
                "Mobile App",
                "Provides a limited subset of the Internet Banking functionality to customers via their mobile device.",
                "Xamarin",
                alias="mobile",
            )

        with DeploymentNode(
            "Customer's computer",
            extensions=plantuml_extensions(
                type_="Microsoft Windows or Apple macOS"
            ),
            alias="comp",
        ):
            with DeploymentNode(
                "Web Browser",
                extensions=plantuml_extensions(
                    type_="Google Chrome, Mozilla Firefox, Apple Safari or Microsoft Edge"
                ),
                alias="browser",
            ):
                spa = Container(
                    "Single Page Application",
                    "Provides all of the Internet Banking functionality to customers via their web browser.",
                    "JavaScript and Angular",
                    alias="spa",
                )

        (
            [mobile, spa]
            >> Rel("Makes API calls to", technology="json/HTTPS")
            >> api
        )
        web >> RelUp("Delivers to the customer's web browser") >> spa
        api >> Rel("Reads from and writes to", technology="JDBC") >> db
        (
            api
            >> Rel(
                "Reads from and writes to",
                technology="JDBC",
                extensions={"plantuml": {"tags": ["fallback"]}},
            )
            >> db2
        )
        db >> RelRight("Replicates data to") >> db2

        render_options = (
            PlantUMLRenderOptionsBuilder()
            .add_element_tag("fallback", bg_color="#c0c0c0")
            .add_rel_tag("fallback", text_color="#c0c0c0", line_color="#438DD5")
            .show_legend()
            .build()
        )

    diagram_code = diagram.as_plantuml(render_options=render_options)

    assert_match_snapshot(
        snapshot_name="plantuml/deployment_diagram.puml",
        diagram_code=diagram_code,
    )


def test_render_deployment_diagram_with_properties(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DeploymentDiagram(
        title="Deployment Diagram for Internet Banking System - Live"
    ) as diagram:
        with DeploymentNode(
            "Live",
            "Big Bank plc data center",
            extensions=plantuml_extensions(type_="Big Bank plc"),
            alias="plc",
        ):
            with DeploymentNodeLeft(
                "bigbank-api***\\tx8",
                "A web server residing in the web server farm, accessed via F5 BIG-IP LTMs.",
                extensions=plantuml_extensions(type_="Ubuntu 16.04 LTS"),
                alias="dn",
            ) as dn:
                dn.add_property("Location", "London and Reading")

                with DeploymentNodeLeft(
                    "Apache Tomcat",
                    "An open source Java EE web server.",
                    extensions=plantuml_extensions(type_="Apache Tomcat 8.x"),
                    alias="apache",
                ) as apache:
                    apache.add_property("Java Version", "8")
                    apache.add_property("Xmx", "512M")
                    apache.add_property("Xms", "1024M")

                    api = Container(
                        "API Application",
                        "Provides Internet Banking functionality via a JSON/HTTPS API.",
                        "Java and Spring MVC",
                        alias="api",
                    )

            with DeploymentNodeLeft(
                "bigbank-db01",
                "The primary database server.",
                extensions=plantuml_extensions(type_="Ubuntu 16.04 LTS"),
                alias="bigbankdb01",
            ) as bigbankdb01:
                bigbankdb01.add_property("Location", "London")

                with DeploymentNodeLeft(
                    "Oracle - Primary",
                    "The primary, live database server.",
                    extensions=plantuml_extensions(type_="Oracle 12c"),
                    alias="oracle",
                ):
                    db = ContainerDb(
                        "Database",
                        "Stores user registration information, hashed authentication credentials, access logs, etc.",
                        "Relational Database Schema",
                        alias="db",
                    )

            with DeploymentNodeRight(
                "bigbank-db02",
                "The secondary database server.",
                alias="bigbankdb02",
                extensions=plantuml_extensions(
                    type_="Ubuntu 16.04 LTS",
                    tags=["fallback"],
                ),
            ) as bigbankdb02:
                bigbankdb02.add_property("Location", "Reading")

                with DeploymentNodeRight(
                    "Oracle - Secondary",
                    "A secondary, standby database server, used for failover purposes only.",
                    alias="oracle2",
                    extensions=plantuml_extensions(
                        type_="Oracle 12c",
                        tags=["fallback"],
                    ),
                ):
                    db2 = ContainerDb(
                        "Database",
                        "Stores user registration information, hashed authentication credentials, access logs, etc.",
                        "Relational Database Schema",
                        alias="db2",
                        extensions={"plantuml": {"tags": ["fallback"]}},
                    )

            with DeploymentNodeRight(
                "bigbank-web***\\tx4",
                "A web server residing in the web server farm, accessed via F5 BIG-IP LTMs.",
                extensions=plantuml_extensions(type_="Ubuntu 16.04 LTS"),
                alias="bb2",
            ) as bb2:
                bb2.add_property("Location", "London and Reading")

                with DeploymentNodeRight(
                    "Apache Tomcat",
                    "An open source Java EE web server.",
                    alias="apache2",
                    extensions=plantuml_extensions(type_="Apache Tomcat 8.x"),
                ) as apache2:
                    apache2.add_property("Java Version", "8")
                    apache2.add_property("Xmx", "512M")
                    apache2.add_property("Xms", "1024M")

                    web = Container(
                        "Web Application",
                        "Delivers the static content and the Internet Banking single page application.",
                        "Java and Spring MVC",
                        alias="web",
                    )

        with DeploymentNode(
            "Customer's mobile device",
            extensions=plantuml_extensions(type_="Apple IOS or Android"),
            alias="mob",
        ):
            mobile = Container(
                "Mobile App",
                "Provides a limited subset of the Internet Banking functionality to customers via their mobile device.",
                "Xamarin",
                alias="mobile",
            )

        with DeploymentNode(
            "Customer's computer",
            extensions=plantuml_extensions(
                type_="Microsoft Windows or Apple macOS"
            ),
            alias="comp",
        ):
            with DeploymentNode(
                "Web Browser",
                extensions=plantuml_extensions(
                    type_="Google Chrome, Mozilla Firefox, Apple Safari or Microsoft Edge"
                ),
                alias="browser",
            ):
                spa = Container(
                    "Single Page Application",
                    "Provides all of the Internet Banking functionality to customers via their web browser.",
                    "JavaScript and Angular",
                    alias="spa",
                )

        (
            [mobile, spa]
            >> Rel("Makes API calls to", technology="json/HTTPS")
            >> api
        )
        web >> RelUp("Delivers to the customer's web browser") >> spa
        api >> Rel("Reads from and writes to", technology="JDBC") >> db
        (
            api
            >> Rel(
                "Reads from and writes to",
                technology="JDBC",
                extensions={"plantuml": {"tags": ["fallback"]}},
            )
            >> db2
        )
        db >> RelRight("Replicates data to") >> db2

        render_options = (
            PlantUMLRenderOptionsBuilder()
            .without_property_header()
            .add_element_tag("fallback", bg_color="#c0c0c0")
            .add_rel_tag("fallback", text_color="#c0c0c0", line_color="#438DD5")
            .show_legend()
            .build()
        )

    diagram_code = diagram.as_plantuml(render_options=render_options)

    assert_match_snapshot(
        snapshot_name="plantuml/deployment_diagram_with_properties.puml",
        diagram_code=diagram_code,
    )

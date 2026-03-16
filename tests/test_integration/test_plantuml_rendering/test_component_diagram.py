from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Component,
    ComponentDiagram,
    Container,
    ContainerBoundary,
    ContainerDb,
    Rel,
    SystemExt,
)
from c4.renderers.plantuml import LayoutOptions

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_component_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with ComponentDiagram(
        title="Component diagram for Internet Banking System - API Application"
    ) as diagram:
        spa = Container(
            "Single Page Application",
            "Provides all the internet banking functionality to customers via their web browser.",
            "javascript and angular",
            alias="spa",
        )
        ma = Container(
            "Mobile App",
            "Provides a limited subset ot the internet banking functionality to customers via their mobile mobile device.",
            "Xamarin",
            alias="ma",
        )
        db = ContainerDb(
            "Database",
            "Stores user registration information, hashed authentication credentials, access logs, etc.",
            "Relational Database Schema",
            alias="db",
        )
        mbs = SystemExt(
            "Mainframe Banking System",
            "Stores all of the core banking information about customers, accounts, transactions, etc.",
            alias="mbs",
        )

        with ContainerBoundary("API Application", alias="api"):
            sign = Component(
                "Sign In Controller",
                "Allows users to sign in to the internet banking system",
                "MVC Rest Controller",
                alias="sign",
            )
            accounts = Component(
                "Accounts Summary Controller",
                "Provides customers with a summary of their bank accounts",
                "MVC Rest Controller",
                alias="accounts",
            )
            security = Component(
                "Security Component",
                "Provides functionality related to singing in, changing passwords, etc.",
                "Spring Bean",
                alias="security",
            )
            mbsfacade = Component(
                "Mainframe Banking System Facade",
                "A facade onto the mainframe banking system.",
                "Spring Bean",
                alias="mbsfacade",
            )

            sign >> Rel("Uses") >> security
            accounts >> Rel("Uses") >> mbsfacade
            security >> Rel("Read & write to", technology="JDBC") >> db
            mbsfacade >> Rel("Uses", technology="XML/HTTPS") >> mbs

        spa >> Rel("Uses", technology="JSON/HTTPS") >> sign
        spa >> Rel("Uses", technology="JSON/HTTPS") >> accounts

        ma >> Rel("Uses", technology="JSON/HTTPS") >> sign
        ma >> Rel("Uses", technology="JSON/HTTPS") >> accounts

        layout_config = LayoutOptions().layout_with_legend().build()

    diagram_code = diagram.as_plantuml(layout_config=layout_config)

    assert_match_snapshot(
        snapshot="plantuml/component_diagram.puml",
        diagram_code=diagram_code,
    )

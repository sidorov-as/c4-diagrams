from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Component,
    ComponentDiagram,
    Container,
    ContainerBoundary,
    ContainerDb,
    Rel,
    RelBack,
    SystemExt,
)
from c4.renderers import MermaidRenderOptionsBuilder

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_component_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
) -> None:
    with ComponentDiagram(
        title="Component diagram for Internet Banking System - API Application"
    ) as diagram:
        spa = Container(
            "Single Page Application",
            "Provides all the internet banking functionality to customers via their web browser.",
            technology="javascript and angular",
            alias="spa",
        )
        ma = Container(
            "Mobile App",
            "Provides a limited subset to the internet banking functionality to customers via their mobile device.",
            technology="Xamarin",
            alias="ma",
        )
        db = ContainerDb(
            "Database",
            "Stores user registration information, hashed authentication credentials, access logs, etc.",
            technology="Relational Database Schema",
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
                technology="MVC Rest Controller",
                alias="sign",
            )
            accounts = Component(
                "Accounts Summary Controller",
                "Provides customers with a summary of their bank accounts",
                technology="MVC Rest Controller",
                alias="accounts",
            )
            security = Component(
                "Security Component",
                "Provides functionality related to singing in, changing passwords, etc.",
                technology="Spring Bean",
                alias="security",
            )
            mbsfacade = Component(
                "Mainframe Banking System Facade",
                "A facade onto the mainframe banking system.",
                technology="Spring Bean",
                alias="mbsfacade",
            )

            sign >> "Uses" >> security
            accounts >> "Uses" >> mbsfacade
            security >> Rel("Read & write to", technology="JDBC") >> db
            mbsfacade >> Rel("Uses", technology="XML/HTTPS") >> mbs

        spa >> RelBack("Uses", technology="JSON/HTTPS") >> sign
        spa >> Rel("Uses", technology="JSON/HTTPS") >> accounts

        ma >> Rel("Uses", technology="JSON/HTTPS") >> sign
        ma >> Rel("Uses", technology="JSON/HTTPS") >> accounts

        render_options = (
            MermaidRenderOptionsBuilder()
            .update_rel_style(spa, sign, offset_y=-40)
            .update_rel_style(spa, accounts, offset_x=40, offset_y=40)
            .update_rel_style(ma, sign, offset_x=-90, offset_y=40)
            .update_rel_style(ma, accounts, offset_y=-40)
            .update_rel_style(sign, security, offset_x=-160, offset_y=10)
            .update_rel_style(accounts, mbsfacade, offset_x=140, offset_y=10)
            .update_rel_style(security, db, offset_y=-40)
            .update_rel_style(mbsfacade, mbs, offset_y=-40)
            .build()
        )

    diagram_code = diagram.as_mermaid(render_options=render_options)

    assert_match_snapshot(
        snapshot_name="mermaid/component_diagram.mmd",
        diagram_code=diagram_code,
    )

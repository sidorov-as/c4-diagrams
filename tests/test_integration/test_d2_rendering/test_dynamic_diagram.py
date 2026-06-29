from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Component,
    Container,
    ContainerBoundary,
    ContainerDb,
    DynamicDiagram,
    Rel,
)

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_dynamic_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with DynamicDiagram(title="Sign In Flow") as diagram:
        browser = Container(
            "Single-Page App",
            technology="TypeScript",
            alias="spa",
        )
        database = ContainerDb(
            "Database",
            technology="PostgreSQL",
            alias="database",
        )

        with ContainerBoundary("API Application", alias="api_application"):
            controller = Component(
                "Sign In Controller",
                technology="Spring MVC",
                alias="controller",
            )
            security = Component(
                "Security Component",
                technology="Spring Bean",
                alias="security",
            )

        (
            browser
            >> Rel("Submits credentials", technology="JSON/HTTPS")
            >> controller
        )
        controller >> "Calls isAuthenticated() on" >> security
        security >> Rel("select * from users", technology="JDBC") >> database

    assert_match_snapshot(
        snapshot_name="d2/dynamic_diagram.d2",
        diagram_code=diagram.as_d2(),
    )

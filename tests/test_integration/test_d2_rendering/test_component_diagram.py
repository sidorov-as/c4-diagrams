from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentExt,
    ComponentQueue,
    Container,
    ContainerBoundary,
    Rel,
)

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_component_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with ComponentDiagram(title="API Components") as diagram:
        browser = Container(
            "Single-Page App",
            technology="TypeScript",
            alias="spa",
        )

        with ContainerBoundary("API Application", alias="api_application"):
            controller = Component(
                "Sign In Controller",
                technology="Spring MVC",
                alias="sign_in_controller",
            )
            service = ComponentExt(
                "Authentication Service",
                technology="Spring Bean",
                alias="auth_service",
            )
            users = ComponentDb(
                "User Repository",
                technology="JPA",
                alias="user_repository",
            )
            events = ComponentQueue(
                "Login Events",
                technology="Kafka",
                alias="login_events",
            )

        (
            browser
            >> Rel("Submits credentials", technology="JSON/HTTPS")
            >> controller
        )
        controller >> "Authenticates with" >> service
        service >> "Loads user" >> users
        service >> "Publishes" >> events

    assert_match_snapshot(
        snapshot_name="d2/component_diagram.d2",
        diagram_code=diagram.as_d2(),
    )

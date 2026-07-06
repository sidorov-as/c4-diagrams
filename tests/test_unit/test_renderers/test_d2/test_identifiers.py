import re

import pytest

from c4.diagrams.container import Container, ContainerDiagram
from c4.diagrams.system_context import (
    Person,
    System,
    SystemBoundary,
    SystemContextDiagram,
)
from c4.enums import STRICT
from c4.renderers.d2 import D2Renderer
from c4.renderers.d2.identifiers import (
    D2IdentifierCollisionError,
    D2IdentifierPolicy,
)


@pytest.mark.parametrize(
    ("alias", "expected"),
    [
        ("api", "api"),
        ("api-service", "api_service"),
        ("api.service", "api_service"),
        ("api service", "api_service"),
        ("123_api", "_123_api"),
        ("", "element"),
        ("Тест", "_"),
        ("api___service", "api_service"),
    ],
)
def test_identifier_policy_sanitizes_aliases(
    alias: str,
    expected: str,
):
    assert D2IdentifierPolicy.sanitize(alias) == expected


def test_identifier_policy_uses_aliases_not_labels():
    with SystemContextDiagram() as diagram:
        Person("Customer", alias="user")

    identifiers = D2IdentifierPolicy().build(diagram, D2Renderer())

    assert identifiers["user"].identifier == "user"
    assert "customer" not in identifiers


def test_identifier_policy_builds_stable_nested_paths():
    with ContainerDiagram() as diagram:
        customer = Person("Customer", alias="customer")
        with SystemBoundary("Store", alias="store") as store:
            web = Container("Web App", alias="web")
            with SystemBoundary("Backend", alias="backend") as backend:
                api = Container("API", alias="api")

        customer >> "Uses" >> web
        web >> "Calls" >> api

    identifiers = D2IdentifierPolicy().build(diagram, D2Renderer())

    assert identifiers[customer.alias].d2_path == "customer"
    assert identifiers[store.alias].d2_path == "store"
    assert identifiers[web.alias].d2_path == "store.web"
    assert identifiers[backend.alias].d2_path == "store.backend"
    assert identifiers[api.alias].d2_path == "store.backend.api"


def test_identifier_policy_suffixes_sanitized_collisions():
    with SystemContextDiagram() as diagram:
        first = Person("First", alias="first")
        second = System("Second", alias="second")
        third = System("Third", alias="third")

    first.alias = "api.service"
    second.alias = "api-service"
    third.alias = "api service"

    identifiers = D2IdentifierPolicy().build(diagram, D2Renderer())

    assert identifiers["api.service"].identifier == "api_service"
    assert identifiers["api-service"].identifier == "api_service_1"
    assert identifiers["api service"].identifier == "api_service_2"


def test_identifier_policy_reports_sanitized_collisions_in_strict_mode():
    with SystemContextDiagram() as diagram:
        first = Person("First", alias="first")
        second = System("Second", alias="second")

    first.alias = "api.service"
    second.alias = "api-service"

    with pytest.raises(
        D2IdentifierCollisionError,
        match=re.escape(
            "D2 identifier collision after sanitizing aliases: "
            "'api.service' and 'api-service' both map to 'api_service'."
        ),
    ):
        D2IdentifierPolicy(strict=True).build(diagram, D2Renderer())


def test_identifier_policy_cannot_emit_generated_title_identifier():
    with SystemContextDiagram() as diagram:
        System("Title", alias="__title")

    identifiers = D2IdentifierPolicy(strict=True).build(diagram, D2Renderer())

    assert identifiers["__title"].identifier == "_title"
    assert (
        identifiers["__title"].identifier != D2IdentifierPolicy.TITLE_IDENTIFIER
    )


def test_renderer_validate_uses_strict_identifier_policy_by_default():
    with SystemContextDiagram() as diagram:
        first = Person("First", alias="first")
        second = System("Second", alias="second")

    first.alias = "api.service"
    second.alias = "api-service"

    renderer = D2Renderer()

    with pytest.raises(D2IdentifierCollisionError):
        renderer.validate(diagram)


def test_identifier_collisions_fail_in_strict_extension_mode():
    with SystemContextDiagram() as diagram:
        first = Person("First", alias="first")
        second = System("Second", alias="second")

    first.alias = "api.service"
    second.alias = "api-service"
    renderer = D2Renderer(extension_validation_mode=STRICT)

    with pytest.raises(D2IdentifierCollisionError):
        renderer.validate(diagram)

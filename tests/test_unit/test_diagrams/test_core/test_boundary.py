import uuid

import pytest
from pytest_mock import MockerFixture

from c4.diagrams import core
from c4.diagrams.core import (
    Boundary,
    Diagram,
    Element,
    current_boundary,
    get_boundary,
)


def test_create_boundary_outside_the_diagram_context():
    expected_error = "Element must be created within a diagram context"

    with pytest.raises(ValueError, match=expected_error):
        Boundary(label="example")


def test_boundary_adds_itself_to_diagram():
    with Diagram() as diagram:
        boundary = Boundary(label="example")

    assert diagram.boundaries == [boundary]


def test_boundary_check_label_valid():
    with Diagram():
        boundary = Boundary(label="example")

    assert boundary.label == "example"


def test_boundary_label_not_provided():
    expected_error = "The 'label' argument is required"

    with Diagram(), pytest.raises(ValueError, match=expected_error):
        Boundary()


def test_boundary_check_alias():
    with Diagram():
        boundary = Boundary(alias="example", label="...")

    assert boundary.alias == "example"


def test_current_boundary_without_context():
    expected_error = "Element must be created within a boundary context"
    with Diagram():
        boundary = Boundary(alias="example", label="...")

        with pytest.raises(ValueError, match=expected_error):
            current_boundary()

    assert boundary.alias == "example"


def test_boundary_generate_alias(
    mocker: MockerFixture,
):
    expected_uuid = uuid.UUID("12340000-0000-0000-0000-000000000000")
    mocker.patch.object(core, "uuid4", return_value=expected_uuid)
    with Diagram():
        boundary = Boundary(label="example")

    assert boundary.alias == "example_1234"


def test_boundary_attrs():
    alias = "boundary1"
    label = "Boundary"
    description = "A boundary"
    tags = "foo,bar"
    link = "https://example.com"
    type_ = "stereotype"

    with Diagram():
        boundary = Boundary(
            alias=alias,
            label=label,
            description=description,
            tags=tags,
            link=link,
            type_=type_,
        )

    assert boundary.alias == alias
    assert boundary.label == label
    assert boundary.description == description
    assert boundary.tags == tags
    assert boundary.link == link
    assert boundary.type == type_
    # reserved for other elements
    assert boundary.base_shape == ""
    assert boundary.technology == ""
    assert boundary.sprite == ""


def test_nested_boundaries():
    with Diagram() as diagram:
        boundary1 = Boundary(label="boundary1")
        boundary_before = get_boundary()

        with boundary1:
            boundary2 = Boundary(label="boundary2")
            boundary_context = current_boundary()

    assert diagram.boundaries == [boundary1]
    assert boundary1.boundaries == [boundary2]
    assert boundary_before is None
    assert boundary_context == boundary1
    assert get_boundary() is None


def test_nested_boundaries_with_elements_and_relationships():
    with Diagram() as diagram:
        user = Element(label="person")
        bank = Boundary(label="web-site")

        with bank:
            frontend = Element(label="frontend")
            backend = Boundary(label="backend")

            with backend:
                auth_service = Element(label="auth-service")
                api_service = Element(label="api-service")
                cache_service = Element(label="api-service")

                rel_cache = api_service >> "Uses" >> cache_service

            rels_frontend = frontend >> "Calls" >> [auth_service, api_service]

        rel_user = user >> "Interacts with" >> frontend

    assert diagram.boundaries == [bank]
    assert diagram.relationships == [rel_user]
    assert bank.boundaries == [backend]
    assert bank.elements == [frontend]
    assert bank.relationships == rels_frontend
    assert not backend.boundaries
    assert backend.relationships == [rel_cache]
    assert backend.elements == [auth_service, api_service, cache_service]


def test_boundary_context():
    with Diagram():
        boundary = Boundary(label="boundary")
        boundary_before = get_boundary()

        with boundary:
            boundary_context = get_boundary()

        boundary_after = get_boundary()

    assert boundary_before is None
    assert boundary_context == boundary
    assert boundary_after is None

import uuid

import pytest
from pytest_mock import MockFixture

from c4.diagrams import core
from c4.diagrams.core import Diagram, Element, ElementWithTechnology


@pytest.mark.parametrize("element_class", [Element, ElementWithTechnology])
def test_create_element_outside_the_diagram_context(
    element_class: type[Element],
):
    expected_error = "Element must be created within a diagram context"

    with pytest.raises(ValueError, match=expected_error):
        element_class(label="example")


@pytest.mark.parametrize("element_class", [Element, ElementWithTechnology])
def test_element_adds_itself_to_diagram(element_class: type[Element]):
    with Diagram() as diagram:
        element = element_class(label="example")

    assert diagram.elements == [element]


@pytest.mark.parametrize("element_class", [Element, ElementWithTechnology])
def test_element_check_label_valid(element_class: type[Element]):
    with Diagram():
        element = element_class(label="example")

    assert element.label == "example"


@pytest.mark.parametrize("element_class", [Element, ElementWithTechnology])
def test_element_label_not_provided(element_class: type[Element]):
    expected_error = "The 'label' argument is required"

    with Diagram(), pytest.raises(ValueError, match=expected_error):
        element_class()


@pytest.mark.parametrize("element_class", [Element, ElementWithTechnology])
def test_element_check_alias(element_class: type[Element]):
    with Diagram():
        element = element_class(alias="example", label="...")

    assert element.alias == "example"


@pytest.mark.parametrize("element_class", [Element, ElementWithTechnology])
def test_element_generate_alias(
    element_class: type[Element],
    mocker: MockFixture,
):
    expected_uuid = uuid.UUID("12340000-0000-0000-0000-000000000000")
    mocker.patch.object(core, "uuid4", return_value=expected_uuid)
    with Diagram():
        element = element_class(label="example")

    assert element.alias == "example_1234"


@pytest.mark.parametrize("element_class", [Element, ElementWithTechnology])
def test_element_repr(
    element_class: type[Element],
):
    class_name = element_class.__name__

    with Diagram():
        element = element_class(alias="element1", label="Element")

    assert str(element) == f"{class_name}(alias='element1', label='Element')"


def test_element_attrs():
    alias = "element1"
    label = "Element"
    description = "An element"
    sprite = "$foo1"
    tags = "foo,bar"
    link = "https://example.com"
    type_ = "stereotype"

    with Diagram():
        element = Element(
            alias=alias,
            label=label,
            description=description,
            sprite=sprite,
            tags=tags,
            link=link,
            type_=type_,
        )

    assert element.alias == alias
    assert element.label == label
    assert element.description == description
    assert element.sprite == sprite
    assert element.tags == tags
    assert element.link == link
    assert element.type == type_
    # reserved for other elements
    assert element.base_shape == ""
    assert element.technology == ""


def test_element_with_technology_attrs():
    alias = "element1"
    label = "Element"
    technology = "nanotechnology"
    description = "An element"
    sprite = "$foo1"
    tags = "foo,bar"
    link = "https://example.com"

    with Diagram():
        element = ElementWithTechnology(
            alias=alias,
            label=label,
            technology=technology,
            description=description,
            sprite=sprite,
            tags=tags,
            link=link,
        )

    assert element.alias == alias
    assert element.label == label
    assert element.description == description
    assert element.sprite == sprite
    assert element.tags == tags
    assert element.link == link
    assert element.type == ""
    assert element.base_shape == ""
    assert element.technology == technology

from typing import Any

import pytest

from c4 import Component, ComponentDiagram
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
):
    with Diagram():
        element = element_class(label="example")
        element2 = element_class(label="example")
        element3 = element_class(label="example", alias="element3")

    assert element.alias == "example"
    assert element2.alias == "example_1"
    assert element3.alias == "element3"


@pytest.mark.parametrize(
    ("element_class", "expected_alias"),
    [
        (Element, "element"),
        (ElementWithTechnology, "element_with_technology"),
    ],
)
def test_element_generate_alias_uses_element_type_as_fallback(
    element_class: type[Element],
    expected_alias: str,
):
    with Diagram():
        element = element_class(label="Пример")

    assert element.alias == expected_alias


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
    extensions = {
        "plantuml": {
            "sprite": "$foo1",
            "tags": ["foo", "bar"],
            "link": "https://example.com",
            "type": "stereotype",
        }
    }

    with Diagram():
        element = Element(
            alias=alias,
            label=label,
            description=description,
            extensions=extensions,
        )

    assert element.alias == alias
    assert element.label == label
    assert element.description == description
    assert element.extensions == extensions
    assert element.technology is None


def test_element_backend_kwargs_are_merged_into_extensions():
    with Diagram():
        element = Element(
            "Element",
            plantuml={"sprite": "$foo"},
            mermaid={"shape": "rect"},
        )

    assert element.extensions == {
        "plantuml": {"sprite": "$foo"},
        "mermaid": {"shape": "rect"},
    }


def test_element_backend_kwargs_reject_duplicate_extension_data():
    with Diagram():
        with pytest.raises(
            ValueError,
            match="Extension data for 'plantuml' was provided twice",
        ):
            Element(
                "Element",
                extensions={"plantuml": {"sprite": "$foo"}},
                plantuml={"sprite": "$bar"},
            )


def test_element_with_technology_attrs():
    alias = "element1"
    label = "Element"
    technology = "nanotechnology"
    description = "An element"
    extensions = {
        "plantuml": {
            "sprite": "$foo1",
            "tags": ["foo", "bar"],
            "link": "https://example.com",
        }
    }

    with Diagram():
        element = ElementWithTechnology(
            alias=alias,
            label=label,
            technology=technology,
            description=description,
            extensions=extensions,
        )

    assert element.alias == alias
    assert element.label == label
    assert element.description == description
    assert element.extensions == extensions
    assert element.technology == technology


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    [
        (
            {"label": "User", "alias": "user"},
            "Element('User', alias='user')",
        ),
        (
            {"label": "User", "description": "A person", "alias": "user"},
            "Element('User', 'A person', alias='user')",
        ),
        (
            {
                "label": "User",
                "plantuml": {"sprite": "person"},
                "alias": "user",
            },
            "Element('User', plantuml={'sprite': 'person'}, alias='user')",
        ),
        (
            {
                "label": "Service",
                "description": "Does things",
                "plantuml": {
                    "sprite": "service",
                    "type": "System",
                    "tags": ["core", "backend"],
                    "link": "https://svc.example.com",
                },
                "alias": "service",
            },
            "Element('Service', 'Does things', plantuml={"
            "'sprite': 'service', 'type': 'System', "
            "'tags': ['core', 'backend'], "
            "'link': 'https://svc.example.com'}, alias='service')",
        ),
    ],
)
def test_element_repr_formats_optional_fields_in_defined_order(
    kwargs: dict[str, Any],
    expected: str,
    diagram: Diagram,
):
    element = Element(**kwargs)

    result = repr(element)

    assert result == expected


def test_element_with_technology_repr(diagram: Diagram):
    kwargs = {
        "label": "Service",
        "description": "Does things",
        "plantuml": {
            "sprite": "service",
            "tags": ["core", "backend"],
            "link": "https://svc.example.com",
        },
        "technology": "Python",
        "alias": "service",
    }
    element = ElementWithTechnology(**kwargs)
    expected = (
        "ElementWithTechnology('Service', 'Does things', "
        "plantuml={'sprite': 'service', "
        "'tags': ['core', 'backend'], "
        "'link': 'https://svc.example.com'}, "
        "technology='Python', alias='service')"
    )

    result = repr(element)

    assert result == expected


def test_element_with_base_shape_repr(component_diagram: ComponentDiagram):
    kwargs = {
        "label": "Service",
        "description": "Does things",
        "plantuml": {
            "sprite": "service",
            "tags": ["core", "backend"],
            "link": "https://svc.example.com",
            "base_shape": "rect",
        },
        "technology": "Python",
        "alias": "service",
    }
    element = Component(**kwargs)
    expected = (
        "Component('Service', 'Does things', plantuml={"
        "'sprite': 'service', 'tags': ['core', 'backend'], "
        "'link': 'https://svc.example.com', 'base_shape': 'rect'}, "
        "technology='Python', alias='service')"
    )

    result = repr(element)

    assert result == expected

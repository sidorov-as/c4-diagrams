import re
from functools import partial

import pytest

from c4 import ComponentDiagram, Person, SystemContextDiagram
from c4.diagrams.core import (
    BaseDiagramElement,
    Diagram,
    DiagramElementProperties,
    DiagramType,
    with_properties,
)


def test_create_base_diagram_element_outside_the_diagram_context():
    expected_error = "Element must be created within a diagram context"

    with pytest.raises(ValueError, match=expected_error):
        BaseDiagramElement()


def test_base_diagram_element_adds_itself_to_diagram():
    with Diagram() as diagram:
        base_element = BaseDiagramElement()

    assert diagram.ordered_elements == [base_element]
    assert base_element.diagram == diagram


def test_base_diagram_element_add_property(diagram: Diagram):
    base_element = BaseDiagramElement()
    show_header_before = base_element.properties.show_header
    header_before = base_element.properties.header
    properties_before = list(base_element.properties.properties)

    base_element.add_property("Property Name", "Property Value")

    assert show_header_before is True
    assert base_element.properties.show_header is True
    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]
    assert properties_before == []
    assert base_element.properties.properties == [
        ["Property Name", "Property Value"]
    ]


def test_base_diagram_element_add_property_header_len_mismatch_error(
    diagram: Diagram,
):
    base_element = BaseDiagramElement()
    show_header_before = base_element.properties.show_header
    header_before = base_element.properties.header
    properties_before = list(base_element.properties.properties)
    expected_error = "The number of values does not match the header length"

    with pytest.raises(ValueError, match=expected_error):
        base_element.add_property("Property Name")

    assert show_header_before is True
    assert base_element.properties.show_header is True
    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]
    assert properties_before == []
    assert base_element.properties.properties == []


def test_base_diagram_element_add_properties(diagram: Diagram):
    base_element = BaseDiagramElement()
    show_header_before = base_element.properties.show_header
    header_before = base_element.properties.header
    base_element.add_property("Property 1", "Property 1 Value")
    properties_before = list(base_element.properties.properties)

    base_element.add_property("Property 2", "Property 2 Value")

    assert show_header_before is True
    assert base_element.properties.show_header is True
    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]
    assert properties_before == [["Property 1", "Property 1 Value"]]
    assert base_element.properties.properties == [
        ["Property 1", "Property 1 Value"],
        ["Property 2", "Property 2 Value"],
    ]


def test_base_diagram_element_without_property_header(diagram: Diagram):
    base_element = BaseDiagramElement()

    base_element.without_property_header()

    assert base_element.properties.show_header is False


def test_diagram_element_properties_add_rows_adds_one_row():
    properties = DiagramElementProperties()

    result = properties.add_rows("Role", "Operator")

    assert result is properties
    assert properties.properties == [["Role", "Operator"]]


def test_diagram_element_properties_add_rows_adds_multiple_rows():
    properties = DiagramElementProperties()

    properties.add_rows(
        ("Role", "Operator"),
        ("Shift", "Daytime"),
    )

    assert properties.properties == [
        ["Role", "Operator"],
        ["Shift", "Daytime"],
    ]


def test_diagram_element_properties_with_rows_sets_options():
    properties = DiagramElementProperties()

    properties.with_rows(
        ("Name", "Role", "Operator"),
        header=("Key", "Type", "Value"),
        show_header=False,
    )

    assert properties.header == ["Key", "Type", "Value"]
    assert properties.show_header is False
    assert properties.properties == [["Name", "Role", "Operator"]]


def test_base_diagram_element_with_properties_adds_one_row(diagram: Diagram):
    base_element = BaseDiagramElement()

    result = base_element.with_properties("Role", "Operator")

    assert result is base_element
    assert base_element.properties.properties == [["Role", "Operator"]]


def test_base_diagram_element_with_properties_adds_multiple_rows(
    diagram: Diagram,
):
    base_element = BaseDiagramElement()

    base_element.with_properties(
        ("Role", "Operator"),
        ("Shift", "Daytime"),
    )

    assert base_element.properties.properties == [
        ["Role", "Operator"],
        ["Shift", "Daytime"],
    ]


def test_base_diagram_element_with_properties_rejects_mixed_rows(
    diagram: Diagram,
):
    base_element = BaseDiagramElement()
    expected_error = (
        "Properties must be passed either as string values for one row "
        "or as row sequences"
    )

    with pytest.raises(ValueError, match=expected_error):
        base_element.with_properties(("Role", "Operator"), "Shift")


def test_with_properties_adds_rows_to_element():
    with SystemContextDiagram():
        crm_operator = with_properties(
            Person("CRM Operator"),
            ("Role", "Operator"),
            ("Shift", "Daytime"),
        )

    assert crm_operator.properties.properties == [
        ["Role", "Operator"],
        ["Shift", "Daytime"],
    ]


def test_with_properties_wraps_element_factory():
    CRMAdmin = with_properties(
        partial(
            Person,
            label="CRM Admin",
            description="Administrator working with CRM",
        ),
        "Role",
        "Admin",
    )

    with SystemContextDiagram():
        crm_admin = CRMAdmin()

    assert crm_admin.label == "CRM Admin"
    assert crm_admin.description == "Administrator working with CRM"
    assert crm_admin.properties.properties == [["Role", "Admin"]]


def test_base_diagram_element_set_property_header(diagram: Diagram):
    base_element = BaseDiagramElement()
    header_before = base_element.properties.header

    base_element.set_property_header("Key", "Value")

    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Key", "Value"]


def test_base_diagram_element_set_property_header_same_length(diagram: Diagram):
    base_element = BaseDiagramElement()
    header_before = base_element.properties.header
    base_element.add_property("Property 1", "Property 1 Value")

    base_element.set_property_header("Key", "Value")

    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Key", "Value"]


def test_base_diagram_element_set_property_header_error(diagram: Diagram):
    base_element = BaseDiagramElement()
    header_before = base_element.properties.header
    base_element.add_property("Property 1", "Property 1 Value")
    expected_error = re.escape(
        "The header length does not match the number of values"
    )

    with pytest.raises(ValueError, match=expected_error):
        base_element.set_property_header("Key", "Value", "Extra")

    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]


def test_base_diagram_element_set_empty_property_header_error(diagram: Diagram):
    base_element = BaseDiagramElement()
    header_before = base_element.properties.header
    expected_error = "The header cannot be empty"

    with pytest.raises(ValueError, match=expected_error):
        base_element.set_property_header()

    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]


def test_base_diagram_element_check_diagram_type(
    component_diagram: ComponentDiagram,
):
    class Element(BaseDiagramElement):
        allowed_diagram_types = (DiagramType.COMPONENT_DIAGRAM,)

    element = Element()

    assert component_diagram.ordered_elements == [element]


def test_base_diagram_element_check_diagram_type_skip_validation(
    component_diagram: ComponentDiagram,
):
    class Element(BaseDiagramElement):
        allowed_diagram_types = None

    element = Element()

    assert component_diagram.ordered_elements == [element]


def test_base_diagram_element_check_diagram_type_not_allowed(
    component_diagram: ComponentDiagram,
):
    class Element(BaseDiagramElement):
        allowed_diagram_types = (
            DiagramType.SYSTEM_CONTEXT_DIAGRAM,
            DiagramType.SYSTEM_LANDSCAPE_DIAGRAM,
        )

    expected_error = (
        "Element is not allowed in ComponentDiagram. "
        "Allowed diagram types: SystemContextDiagram, SystemLandscapeDiagram."
    )

    with pytest.raises(ValueError, match=expected_error):
        Element()

    assert not component_diagram.ordered_elements

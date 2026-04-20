import re
from collections.abc import Callable
from typing import Any

import pytest

from c4 import (
    Component,
    ComponentDb,
    ComponentDbExt,
    ComponentExt,
    ComponentQueue,
    ComponentQueueExt,
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDbExt,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
    DeploymentNode,
    DeploymentNodeLeft,
    DeploymentNodeRight,
    EnterpriseBoundary,
    Node,
    NodeLeft,
    NodeRight,
    Person,
    PersonExt,
    System,
    SystemBoundary,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemQueue,
    SystemQueueExt,
)
from c4.diagrams.core import (
    Boundary,
    Element,
    ElementWithTechnology,
    Relationship,
    RelationshipType,
)
from c4.renderers.macros import BaseMacro
from c4.renderers.mermaid.macros import (
    ELEMENT_TO_MERMAID_MACRO_MAP,
    RELATIONSHIP_TO_MERMAID_MACRO_MAP,
    BoundaryMermaidMacro,
    ElementMermaidMacro,
    ElementWithTechnologyMermaidMacro,
    RelationshipMermaidMacro,
    UpdateElementStyleMermaidMacro,
    UpdateLayoutConfigMermaidMacro,
    UpdateRelStyleMermaidMacro,
)
from c4.renderers.mermaid.options import (
    ElementStyle,
    RelStyle,
    UpdateLayoutConfig,
)
from tests.utils import ParametrizeArgs


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [(key, value) for key, value in ELEMENT_TO_MERMAID_MACRO_MAP.items()],
)
def test_element_mermaid_macro_get_macro(
    element_class: type[Element],
    expected_macro: str,
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    element = element_class(label="example")
    macro = ElementMermaidMacro(element)

    assert macro.get_macro() == expected_macro


@pytest.mark.usefixtures("diagram")
def test_element_plantuml_macro_get_macro_none():
    macro = ElementMermaidMacro(...)

    assert macro.get_macro() is None


@pytest.mark.parametrize(
    "element_class",
    list(ELEMENT_TO_MERMAID_MACRO_MAP),
)
def test_element_plantuml_macro_get_data(
    element_class: type[Element],
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
    }
    element = element_class(**kwargs)
    macro = ElementMermaidMacro(element)

    assert macro.get_data() == kwargs


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [
        (Person, "Person"),
        (PersonExt, "Person_Ext"),
        (System, "System"),
        (SystemDb, "SystemDb"),
        (SystemQueue, "SystemQueue"),
        (SystemExt, "System_Ext"),
        (SystemDbExt, "SystemDb_Ext"),
        (SystemQueueExt, "SystemQueue_Ext"),
        (Boundary, "Boundary"),
        (EnterpriseBoundary, "Enterprise_Boundary"),
        (SystemBoundary, "System_Boundary"),
        (Container, "Container"),
        (ContainerDb, "ContainerDb"),
        (ContainerQueue, "ContainerQueue"),
        (ContainerExt, "Container_Ext"),
        (ContainerDbExt, "ContainerDb_Ext"),
        (ContainerQueueExt, "ContainerQueue_Ext"),
        (ContainerBoundary, "Container_Boundary"),
        (Component, "Component"),
        (ComponentDb, "ComponentDb"),
        (ComponentQueue, "ComponentQueue"),
        (ComponentExt, "Component_Ext"),
        (ComponentDbExt, "ComponentDb_Ext"),
        (ComponentQueueExt, "ComponentQueue_Ext"),
        (Node, "Node"),
        (NodeLeft, "Node_L"),
        (NodeRight, "Node_R"),
        (DeploymentNode, "Deployment_Node"),
        (DeploymentNodeLeft, "Deployment_Node"),
        (DeploymentNodeRight, "Deployment_Node"),
    ],
)
@pytest.mark.usefixtures("diagram")
def test_element_mermaid_macro_render(
    element_class: type[Element],
    expected_macro: str,
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
    }
    element = element_class(**kwargs)
    macro = ElementMermaidMacro(element)
    expected_macro = f'{expected_macro}(element1, "Element", "An element")'

    result = macro.render()

    assert result == expected_macro


def __element_mermaid_macro__from_element__parametrize() -> ParametrizeArgs:

    arg_names = (
        "element_class",
        "override_kwargs",
        "expected_macro_class",
        "expected_rendered_macro",
    )
    arg_values = [
        (
            Boundary,
            {"type_": "Element type"},
            BoundaryMermaidMacro,
            'Boundary(element1, "Element", "Element type")',
        ),
        (
            Container,
            {
                "technology": "Technology",
            },
            ElementWithTechnologyMermaidMacro,
            'Container(element1, "Element", "Technology", "Description")',
        ),
        (
            ContainerExt,
            {
                "technology": "Technology",
            },
            ElementWithTechnologyMermaidMacro,
            'Container_Ext(element1, "Element", "Technology", "Description")',
        ),
    ]
    ids = ["boundary", "container", "container_ext"]

    seen_elements = [item[0] for item in arg_values]

    elements_with_technology = (
        Container,
        ContainerExt,
        Component,
        ElementWithTechnology,
    )

    for cls, marco in ELEMENT_TO_MERMAID_MACRO_MAP.items():
        if cls in seen_elements:
            continue

        if issubclass(cls, elements_with_technology):
            arg_values.append((
                cls,
                {
                    "technology": "Technology",
                },
                ElementWithTechnologyMermaidMacro,
                f'{marco}(element1, "Element", "Technology", "Description")',
            ))
        else:
            arg_values.append((
                cls,
                {},
                ElementMermaidMacro,
                f'{marco}(element1, "Element", "Description")',
            ))

        seen_elements.append(cls)
        ids.append(cls.__name__.lower())

    return ParametrizeArgs(argnames=arg_names, argvalues=arg_values, ids=ids)


@pytest.mark.parametrize(**__element_mermaid_macro__from_element__parametrize())
@pytest.mark.usefixtures("diagram")
def test_element_mermaid_macro__from_element(
    element_class: type[Element],
    override_kwargs: dict[str, Any],
    expected_macro_class: type[BaseMacro],
    expected_rendered_macro: str,
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "Description",
        **override_kwargs,
    }
    element = element_class(**kwargs)
    macro = ElementMermaidMacro.from_element(element)

    result = macro.render()

    assert isinstance(macro, expected_macro_class)
    assert result == expected_rendered_macro


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_MERMAID_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_mermaid_macro_get_macro(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )
    relationship = relationship_class(label="example")
    macro = RelationshipMermaidMacro(relationship)

    assert macro.get_macro() == expected_macro


@pytest.mark.parametrize(
    "relationship_type",
    [
        rel_type
        for rel_type in list(RelationshipType)
        if rel_type not in RELATIONSHIP_TO_MERMAID_MACRO_MAP
    ],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_mermaid_macro_get_macro__fallback(
    relationship_type: RelationshipType,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )
    relationship = relationship_class(label="example")
    macro = RelationshipMermaidMacro(relationship)

    assert macro.get_macro() == "Rel"


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_MERMAID_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_mermaid_macro_get_data_no_from_element_error(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )
    relationship = relationship_class(
        label="example", to_element=Element(label="example")
    )
    macro = RelationshipMermaidMacro(relationship)
    expected_error = "from_element not provided"

    with pytest.raises(ValueError, match=re.escape(expected_error)):
        macro.get_data()


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_MERMAID_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_mermaid_macro_get_data_no_to_element_error(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )
    relationship = relationship_class(
        label="example", from_element=Element(label="example")
    )
    macro = RelationshipMermaidMacro(relationship)
    expected_error = "to_element not provided"

    with pytest.raises(ValueError, match=re.escape(expected_error)):
        macro.get_data()


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_MERMAID_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_mermaid_macro_get_data(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    attrs = {
        "label": "example",
        "technology": "technology",
    }
    relationship = Relationship(
        **attrs,
        from_element=Element(alias="from", label="From element"),
        to_element=Element(alias="to", label="To element"),
        relationship_type=relationship_type,
    )
    macro = RelationshipMermaidMacro(relationship)
    expected_data = {
        **attrs,
        "from": "from",
        "to": "to",
    }

    result = macro.get_data()

    assert result == expected_data


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_MERMAID_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_mermaid_macro_render(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    attrs = {
        "label": "example",
        "technology": "technology",
    }
    signature = '(from, to, "example", "technology")'
    relationship = Relationship(
        **attrs,
        from_element=Element(alias="from", label="From element"),
        to_element=Element(alias="to", label="To element"),
        relationship_type=relationship_type,
    )
    macro = RelationshipMermaidMacro(relationship)
    expected_macro = f"{expected_macro}{signature}"

    result = macro.render()

    assert result == expected_macro


def test_update_element_style_mermaid_macro_render():
    element = ElementStyle(
        element="user",
        bg_color="#ffffff",
        font_color="#000000",
        border_color="#333333",
    )
    macro = UpdateElementStyleMermaidMacro(element)
    expected_macro = (
        "UpdateElementStyle("
        "user, "
        '$fontColor="#000000", '
        '$bgColor="#ffffff", '
        '$borderColor="#333333"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_element_style_mermaid_macro_render__no_bg_color():
    element = ElementStyle(
        element="user",
        font_color="#000000",
        border_color="#333333",
    )
    macro = UpdateElementStyleMermaidMacro(element)
    expected_macro = (
        'UpdateElementStyle(user, $fontColor="#000000", $borderColor="#333333")'
    )

    assert macro.render() == expected_macro


def test_update_element_style_mermaid_macro_render__no_font_color():
    element = ElementStyle(
        element="user",
        bg_color="#ffffff",
        border_color="#333333",
    )
    macro = UpdateElementStyleMermaidMacro(element)
    expected_macro = (
        'UpdateElementStyle(user, $bgColor="#ffffff", $borderColor="#333333")'
    )

    assert macro.render() == expected_macro


def test_update_element_style_mermaid_macro_render__no_border_color():
    element = ElementStyle(
        element="user",
        bg_color="#ffffff",
        font_color="#000000",
    )
    macro = UpdateElementStyleMermaidMacro(element)
    expected_macro = (
        'UpdateElementStyle(user, $fontColor="#000000", $bgColor="#ffffff")'
    )

    assert macro.render() == expected_macro


def test_update_rel_style_mermaid_macro_render():
    rel_style = RelStyle(
        from_element="user",
        to_element="system",
        text_color="#000000",
        line_color="#333333",
    )
    macro = UpdateRelStyleMermaidMacro(rel_style)
    expected_macro = (
        "UpdateRelStyle("
        "user, "
        "system, "
        '$textColor="#000000", '
        '$lineColor="#333333"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_rel_style_mermaid_macro_render__no_text_color():
    rel_style = RelStyle(
        from_element="user",
        to_element="system",
        line_color="#333333",
    )
    macro = UpdateRelStyleMermaidMacro(rel_style)
    expected_macro = 'UpdateRelStyle(user, system, $lineColor="#333333")'

    assert macro.render() == expected_macro


def test_update_rel_style_mermaid_macro_render__no_line_color():
    relationship = RelStyle(
        from_element="user",
        to_element="system",
        text_color="#000000",
    )
    macro = UpdateRelStyleMermaidMacro(relationship)
    expected_macro = 'UpdateRelStyle(user, system, $textColor="#000000")'

    assert macro.render() == expected_macro


def test_update_rel_style_mermaid_macro_render__offset():
    relationship = RelStyle(
        from_element="user",
        to_element="system",
        text_color="#000000",
        line_color="#333333",
        offset_x=10,
        offset_y=-20,
    )
    macro = UpdateRelStyleMermaidMacro(relationship)
    expected_macro = (
        "UpdateRelStyle("
        "user, "
        "system, "
        '$textColor="#000000", '
        '$lineColor="#333333", '
        '$offsetX="10", '
        '$offsetY="-20"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_rel_style_mermaid_macro_render__offset_x():
    relationship = RelStyle(
        from_element="user",
        to_element="system",
        text_color="#000000",
        line_color="#333333",
        offset_x=10,
    )
    macro = UpdateRelStyleMermaidMacro(relationship)
    expected_macro = (
        "UpdateRelStyle("
        "user, "
        "system, "
        '$textColor="#000000", '
        '$lineColor="#333333", '
        '$offsetX="10"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_rel_style_mermaid_macro_render__offset_y():
    relationship = RelStyle(
        from_element="user",
        to_element="system",
        text_color="#000000",
        line_color="#333333",
        offset_y=-20,
    )
    macro = UpdateRelStyleMermaidMacro(relationship)
    expected_macro = (
        "UpdateRelStyle("
        "user, "
        "system, "
        '$textColor="#000000", '
        '$lineColor="#333333", '
        '$offsetY="-20"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_layout_config_mermaid_macro_render():
    element = UpdateLayoutConfig(
        c4_shape_in_row=2,
        c4_boundary_in_row=4,
    )
    macro = UpdateLayoutConfigMermaidMacro(element)
    expected_macro = (
        'UpdateLayoutConfig($c4ShapeInRow="2", $c4BoundaryInRow="4")'
    )

    assert macro.render() == expected_macro


def test_update_layout_config_mermaid_macro_render__no_shape():
    element = UpdateLayoutConfig(
        c4_boundary_in_row=4,
    )
    macro = UpdateLayoutConfigMermaidMacro(element)
    expected_macro = 'UpdateLayoutConfig($c4BoundaryInRow="4")'

    assert macro.render() == expected_macro


def test_update_layout_config_mermaid_macro_render__no_boundary():
    element = UpdateLayoutConfig(
        c4_boundary_in_row=4,
    )
    macro = UpdateLayoutConfigMermaidMacro(element)
    expected_macro = 'UpdateLayoutConfig($c4BoundaryInRow="4")'

    assert macro.render() == expected_macro

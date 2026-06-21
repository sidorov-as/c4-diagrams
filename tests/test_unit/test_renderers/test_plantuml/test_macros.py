import re
from collections.abc import Callable
from typing import Any

import pytest
from pytest_mock import MockerFixture

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
    EnterpriseBoundary,
    Node,
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
from c4.contrib.c4_macros import NodeLeft, NodeRight
from c4.contrib.plantuml import (
    DeploymentNodeLeft,
    DeploymentNodeRight,
    Index,
    LayD,
    LayDown,
    LayL,
    LayLeft,
    Layout,
    LayR,
    LayRight,
    LayU,
    LayUp,
    increment,
    set_index,
)
from c4.diagrams.core import (
    Boundary,
    DiagramElementProperties,
    Element,
    ElementWithTechnology,
    Relationship,
    RelationshipType,
)
from c4.renderers.plantuml.macros import (
    ELEMENT_TO_PLANTUML_MACRO_MAP,
    RELATIONSHIP_TO_PLANTUML_MACRO_MAP,
    BoundaryPlantUMLMacro,
    ComponentPlantUMLMacro,
    ContainerPlantUMLMacro,
    DiagramLayoutPlantUMLMacro,
    ElementPlantUMLMacro,
    ElementWithTechnologyPlantUMLMacro,
    HidePersonSpritePlantUMLMacro,
    HideStereotypePlantUMLMacro,
    IncrementPlantUMLMacro,
    LayoutAsSketchPlantUMLMacro,
    LayoutPlantUMLMacro,
    LayoutWithLegendPlantUMLMacro,
    NodePlantUMLMacro,
    PlantUMLMacro,
    PlantUMLMacroWithoutArgs,
    RelationshipPlantUMLMacro,
    SetIndexPlantUMLMacro,
    SetSketchStylePlantUMLMacro,
    ShowFloatingLegendPlantUMLMacro,
    ShowLegendPlantUMLMacro,
    ShowPersonOutlinePlantUMLMacro,
    ShowPersonSpritePlantUMLMacro,
    SystemPlantUMLMacro,
    UpdateLegendTitlePlantUMLMacro,
    WithoutPropertyHeaderPlantUMLMacro,
)
from c4.renderers.plantuml.options import (
    DiagramLayout,
    SetSketchStyle,
    ShowFloatingLegend,
    ShowLegend,
    ShowPersonSprite,
)


def plantuml_extensions(**kwargs: Any) -> dict[str, dict[str, Any]]:
    return {"plantuml": kwargs}


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_get_properties_base_element_no_properties():
    element = Element(label="example")
    macro = PlantUMLMacro(element)

    result = macro.get_properties()

    assert isinstance(result, DiagramElementProperties)
    assert result.properties == []


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_get_properties_base_element_with_properties():
    element = Element(label="example")
    element.add_property("foo", "bar")
    macro = PlantUMLMacro(element)

    result = macro.get_properties()

    assert isinstance(result, DiagramElementProperties)
    assert result.properties == [["foo", "bar"]]


def test_plantuml_macro_get_properties_not_a_base_element(
    mocker: MockerFixture,
):
    element = mocker.ANY
    macro = PlantUMLMacro(element)

    result = macro.get_properties()

    assert result is None


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_render_properties_not_a_base_element():
    macro = PlantUMLMacro(...)

    result = macro.render_properties()

    assert result == []


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_render_properties_element_with_no_properties():
    element = Element(label="example")
    macro = PlantUMLMacro(element)

    result = macro.render_properties()

    assert result == []


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_render_properties_element_with_properties():
    element = Element(label="example")
    element.add_property("foo", "bar")
    element.add_property("key", "value")
    macro = PlantUMLMacro(element)
    expected_result = [
        'SetPropertyHeader("Property", "Value")',
        'AddProperty("foo", "bar")',
        'AddProperty("key", "value")',
    ]

    result = macro.render_properties()

    assert result == expected_result


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_render_properties_global_without_property_header():
    element = Element(label="example")
    element.add_property("foo", "bar")
    element.add_property("key", "value")
    macro = PlantUMLMacro(element)
    expected_result = [
        'AddProperty("foo", "bar")',
        'AddProperty("key", "value")',
    ]

    result = macro.render_properties(
        global_without_property_header=True,
    )

    assert result == expected_result


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_render_properties_show_header_false():
    element = Element(label="example")
    element.add_property("foo", "bar")
    element.add_property("key", "value")
    element.without_property_header()
    macro = PlantUMLMacro(element)
    expected_result = [
        "WithoutPropertyHeader()",
        'AddProperty("foo", "bar")',
        'AddProperty("key", "value")',
    ]

    result = macro.render_properties()

    assert result == expected_result


def test_plantuml_macro_without_args():
    class TestPlantUMLMacroWithoutArgs(PlantUMLMacroWithoutArgs):
        macro = "example"

    macro = TestPlantUMLMacroWithoutArgs()

    assert macro._diagram_element is None
    assert macro.get_data() == {}
    assert macro.render() == "example()"


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [(key, value) for key, value in ELEMENT_TO_PLANTUML_MACRO_MAP.items()],
)
def test_element_plantuml_macro_get_macro(
    element_class: type[Element],
    expected_macro: str,
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    element = element_class(label="example")
    macro = ElementPlantUMLMacro(element)

    assert macro.get_macro() == expected_macro


@pytest.mark.usefixtures("diagram")
def test_element_plantuml_macro_get_macro_none():
    macro = ElementPlantUMLMacro(...)

    assert macro.get_macro() is None


@pytest.mark.parametrize(
    (
        "element_class",
        "override_kwargs",
    ),
    [
        (
            Person,
            {
                "type_": "stereotype",
            },
        ),
        (
            PersonExt,
            {
                "type_": "stereotype",
            },
        ),
        (
            SystemDb,
            {
                "type_": "stereotype",
            },
        ),
        (
            SystemQueue,
            {
                "type_": "stereotype",
            },
        ),
        (
            SystemExt,
            {
                "type_": "stereotype",
            },
        ),
        (
            SystemDbExt,
            {
                "type_": "stereotype",
            },
        ),
        (
            SystemQueueExt,
            {
                "type_": "stereotype",
            },
        ),
        (
            ContainerDb,
            {"technology": "example"},
        ),
        (
            ContainerQueue,
            {"technology": "example"},
        ),
        (
            ContainerExt,
            {"technology": "example"},
        ),
        (
            ContainerDbExt,
            {"technology": "example"},
        ),
        (
            ContainerQueueExt,
            {"technology": "example"},
        ),
        (
            ComponentDb,
            {"technology": "example"},
        ),
        (
            ComponentQueue,
            {"technology": "example"},
        ),
        (
            ComponentExt,
            {"technology": "example"},
        ),
        (
            ComponentDbExt,
            {"technology": "example"},
        ),
        (
            ComponentQueueExt,
            {"technology": "example"},
        ),
    ],
)
def test_element_plantuml_macro_get_data(
    element_class: type[Element],
    override_kwargs: dict[str, Any],
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    plantuml_kwargs = {
        "sprite": "$foo1",
        "tags": ["foo", "bar"],
        "link": "https://example.com",
    }
    if "type_" in override_kwargs:
        plantuml_kwargs["type"] = override_kwargs["type_"]

    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "extensions": plantuml_extensions(**plantuml_kwargs),
        **{
            key: value
            for key, value in override_kwargs.items()
            if key != "type_"
        },
    }
    element = element_class(**kwargs)
    macro = ElementPlantUMLMacro(element)
    expected_kwargs = {
        "alias": kwargs["alias"],
        "label": kwargs["label"],
        "description": kwargs["description"],
        **plantuml_kwargs,
        "technology": kwargs.get("technology"),
    }
    result = macro.get_data()
    if "base_shape" in result:
        expected_kwargs["base_shape"] = None

    assert result == expected_kwargs


@pytest.mark.parametrize(
    ("element_class", "expected_macro_class"),
    [
        (System, SystemPlantUMLMacro),
        (SystemExt, SystemPlantUMLMacro),
        (Boundary, BoundaryPlantUMLMacro),
        (SystemBoundary, BoundaryPlantUMLMacro),
        (ContainerBoundary, BoundaryPlantUMLMacro),
        (EnterpriseBoundary, BoundaryPlantUMLMacro),
        (Node, NodePlantUMLMacro),
        (NodeLeft, NodePlantUMLMacro),
        (NodeRight, NodePlantUMLMacro),
        (DeploymentNode, NodePlantUMLMacro),
        (DeploymentNodeLeft, NodePlantUMLMacro),
        (DeploymentNodeRight, NodePlantUMLMacro),
        (Container, ContainerPlantUMLMacro),
        (ElementWithTechnology, ElementWithTechnologyPlantUMLMacro),
        (Component, ComponentPlantUMLMacro),
        (Person, ElementPlantUMLMacro),
        (PersonExt, ElementPlantUMLMacro),
        (SystemDb, ElementPlantUMLMacro),
        (SystemQueue, ElementPlantUMLMacro),
        (SystemDbExt, ElementPlantUMLMacro),
        (SystemQueueExt, ElementPlantUMLMacro),
        (ContainerDb, ElementWithTechnologyPlantUMLMacro),
        (ContainerQueue, ElementWithTechnologyPlantUMLMacro),
        (ContainerExt, ContainerPlantUMLMacro),
        (ContainerDbExt, ElementWithTechnologyPlantUMLMacro),
        (ContainerQueueExt, ElementWithTechnologyPlantUMLMacro),
        (ComponentDb, ElementWithTechnologyPlantUMLMacro),
        (ComponentQueue, ElementWithTechnologyPlantUMLMacro),
        (ComponentExt, ComponentPlantUMLMacro),
        (ComponentDbExt, ElementWithTechnologyPlantUMLMacro),
        (ComponentQueueExt, ElementWithTechnologyPlantUMLMacro),
    ],
)
def test_element_plantuml_macro_from_element(
    element_class: type[Element],
    expected_macro_class: str,
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    element = element_class(label="example")
    macro = ElementPlantUMLMacro(element)

    element_macro = macro.from_element(element)

    assert type(element_macro) is expected_macro_class


@pytest.mark.usefixtures("diagram")
def test_element_with_technology_plantuml_macro_get_data():
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "technology": "tech",
        "extensions": plantuml_extensions(
            sprite="$foo1",
            tags=["foo", "bar"],
            link="https://example.com",
        ),
    }
    element = ElementWithTechnology(**kwargs)
    macro = ElementWithTechnologyPlantUMLMacro(element)
    expected_kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "sprite": "$foo1",
        "tags": ["foo", "bar"],
        "link": "https://example.com",
        "technology": "tech",
    }

    assert macro.get_data() == expected_kwargs


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [
        (
            Person,
            "Person",
        ),
        (
            PersonExt,
            "Person_Ext",
        ),
        (
            SystemDb,
            "SystemDb",
        ),
        (
            SystemQueue,
            "SystemQueue",
        ),
        (
            SystemDbExt,
            "SystemDb_Ext",
        ),
        (
            SystemQueueExt,
            "SystemQueue_Ext",
        ),
    ],
)
@pytest.mark.usefixtures("diagram")
def test_element_plantuml_macro_render(
    element_class: type[Element], expected_macro: str
):
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "extensions": plantuml_extensions(
            sprite="$spriteValue",
            tags=["foo", "bar"],
            link="https://example.com",
            type="stereotype",
        ),
    }
    element = element_class(**kwargs)
    macro = ElementPlantUMLMacro(element)
    expected_macro = (
        f"{expected_macro}("
        "element1, "
        '"Element", '
        '"An element", '
        '$sprite="$spriteValue", '
        '$tags="foo+bar", '
        '$link="https://example.com", '
        '$type="stereotype"'
        ")"
    )

    result = macro.render()

    assert result == expected_macro


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [
        (ContainerDb, "ContainerDb"),
        (ContainerDbExt, "ContainerDb_Ext"),
        (ContainerQueue, "ContainerQueue"),
        (ContainerQueueExt, "ContainerQueue_Ext"),
        (ComponentDb, "ComponentDb"),
        (ComponentDbExt, "ComponentDb_Ext"),
        (ComponentQueue, "ComponentQueue"),
        (ComponentQueueExt, "ComponentQueue_Ext"),
    ],
)
def test_element_with_technology_plantuml_macro_render(
    element_class: type[Element],
    expected_macro: str,
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "technology": "tech",
        "extensions": plantuml_extensions(
            sprite="$spriteValue",
            tags=["foo", "bar"],
            link="https://example.com",
        ),
    }
    element = element_class(**kwargs)
    macro = ElementWithTechnologyPlantUMLMacro(element)
    expected_macro = (
        f"{expected_macro}("
        "element1, "
        '"Element", '
        '"tech", '
        '"An element", '
        '$sprite="$spriteValue", '
        '$tags="foo+bar", '
        '$link="https://example.com"'
        ")"
    )

    result = macro.render()

    assert result == expected_macro


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [
        (
            System,
            "System",
        ),
        (
            SystemExt,
            "System_Ext",
        ),
    ],
)
@pytest.mark.usefixtures("diagram")
def test_system_plantuml_macro_render(
    element_class: type[Element], expected_macro: str
):
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "extensions": plantuml_extensions(
            sprite="$spriteValue",
            tags=["foo", "bar"],
            link="https://example.com",
            type="stereotype",
            base_shape="rectangle",
        ),
    }
    element = element_class(**kwargs)
    macro = SystemPlantUMLMacro(element)
    expected_macro = (
        f"{expected_macro}("
        "element1, "
        '"Element", '
        '"An element", '
        '$sprite="$spriteValue", '
        '$tags="foo+bar", '
        '$link="https://example.com", '
        '$type="stereotype", '
        '$baseShape="rectangle"'
        ")"
    )

    result = macro.render()

    assert result == expected_macro


@pytest.mark.parametrize(
    ("element_class", "override_kwargs", "expected_macro"),
    [
        (
            Boundary,
            {"type": "stereotype"},
            'Boundary(element1, "Element", $type="stereotype", $tags="foo+bar", $link="https://example.com", $descr="An element")',
        ),
        (
            ContainerBoundary,
            {},
            'Container_Boundary(element1, "Element", $tags="foo+bar", $link="https://example.com", $descr="An element")',
        ),
        (
            EnterpriseBoundary,
            {},
            'Enterprise_Boundary(element1, "Element", $tags="foo+bar", $link="https://example.com", $descr="An element")',
        ),
        (
            SystemBoundary,
            {},
            'System_Boundary(element1, "Element", $tags="foo+bar", $link="https://example.com", $descr="An element")',
        ),
    ],
)
def test_boundary_plantuml_macro_render(
    element_class: type[Element],
    override_kwargs: dict[str, Any],
    expected_macro: str,
    set_current_diagram: Callable[[type[Element]], ...],
):
    set_current_diagram(element_class)
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "extensions": {
            "plantuml": {
                "tags": ["foo", "bar"],
                "link": "https://example.com",
                **override_kwargs,
            }
        },
    }
    element = element_class(**kwargs)
    macro = BoundaryPlantUMLMacro(element)

    result = macro.render()

    assert result == expected_macro


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [
        (
            Container,
            'Container(element1, "Element", "tech", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com", $baseShape="rectangle")',
        ),
        (
            ContainerExt,
            'Container_Ext(element1, "Element", "tech", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com", $baseShape="rectangle")',
        ),
    ],
)
@pytest.mark.usefixtures("container_diagram")
def test_container_plantuml_macro_render(
    element_class: type[Element],
    expected_macro: str,
):
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "technology": "tech",
        "extensions": plantuml_extensions(
            tags=["foo", "bar"],
            link="https://example.com",
            sprite="$foo",
            base_shape="rectangle",
        ),
    }
    element = element_class(**kwargs)
    macro = ContainerPlantUMLMacro(element)

    result = macro.render()

    assert result == expected_macro


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [
        (
            Component,
            'Component(element1, "Element", "tech", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com", $baseShape="rectangle")',
        ),
        (
            ComponentExt,
            'Component_Ext(element1, "Element", "tech", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com", $baseShape="rectangle")',
        ),
    ],
)
@pytest.mark.usefixtures("component_diagram")
def test_component_plantuml_macro_render(
    element_class: type[Element],
    expected_macro: str,
):
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "technology": "tech",
        "extensions": plantuml_extensions(
            tags=["foo", "bar"],
            link="https://example.com",
            sprite="$foo",
            base_shape="rectangle",
        ),
    }
    element = element_class(**kwargs)
    macro = ComponentPlantUMLMacro(element)

    result = macro.render()

    assert result == expected_macro


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_PLANTUML_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_plantuml_macro_get_macro(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )
    relationship = relationship_class(label="example")
    macro = RelationshipPlantUMLMacro(relationship)

    assert macro.get_macro() == expected_macro


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_PLANTUML_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_plantuml_macro_get_data_no_from_element_error(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )
    relationship = relationship_class(
        label="example", to_element=Element(label="example")
    )
    macro = RelationshipPlantUMLMacro(relationship)
    expected_error = "from_element not provided"

    with pytest.raises(ValueError, match=re.escape(expected_error)):
        macro.get_data()


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_PLANTUML_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_plantuml_macro_get_data_no_to_element_error(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )
    relationship = relationship_class(
        label="example", from_element=Element(label="example")
    )
    macro = RelationshipPlantUMLMacro(relationship)
    expected_error = "to_element not provided"

    with pytest.raises(ValueError, match=re.escape(expected_error)):
        macro.get_data()


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_PLANTUML_MACRO_MAP.items()],
)
@pytest.mark.parametrize(
    "index",
    ["1", Index(1), None],
    ids=["str", "index-object", "no-index"],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_plantuml_macro_get_data(
    relationship_type: RelationshipType,
    index: str | Index | None,
    expected_macro: str,
):
    attrs = {
        "label": "example",
        "technology": "technology",
        "description": "Description",
        "extensions": plantuml_extensions(
            sprite="$sprite",
            tags=["tag1", "tag2"],
            link="https://example.com",
            index=index,
        ),
    }
    from_element = Element(alias="from", label="From element")
    to_element = Element(alias="to", label="To element")
    relationship = Relationship(
        **attrs,
        from_element=from_element,
        to_element=to_element,
        relationship_type=relationship_type,
    )
    macro = RelationshipPlantUMLMacro(relationship)
    expected_data = {
        "from": "from",
        "to": "to",
        "label": attrs["label"],
        "technology": attrs["technology"],
        "description": attrs["description"],
        "sprite": "$sprite",
        "tags": ["tag1", "tag2"],
        "link": "https://example.com",
        "index": index,
    }

    result = macro.get_data()

    assert result == expected_data


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_PLANTUML_MACRO_MAP.items()],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_plantuml_macro_render(
    relationship_type: RelationshipType,
    expected_macro: str,
):
    attrs = {
        "label": "example",
        "technology": "technology",
        "description": "Description",
        "extensions": plantuml_extensions(
            sprite="$sprite",
            tags=["tag1", "tag2"],
            link="https://example.com",
        ),
    }
    signature = (
        '(from, to, "example", '
        '"technology", '
        '"Description", '
        '$sprite="$sprite", '
        '$tags="tag1+tag2", '
        '$link="https://example.com"'
        ")"
    )
    from_element = Element(alias="from", label="From element")
    to_element = Element(alias="to", label="To element")
    relationship = Relationship(
        **attrs,
        from_element=from_element,
        to_element=to_element,
        relationship_type=relationship_type,
    )
    macro = RelationshipPlantUMLMacro(relationship)
    expected_macro = f"{expected_macro}{signature}"

    result = macro.render()

    assert result == expected_macro


@pytest.mark.parametrize(
    ("relationship_type", "expected_macro"),
    [(key, value) for key, value in RELATIONSHIP_TO_PLANTUML_MACRO_MAP.items()],
)
@pytest.mark.parametrize(
    "index",
    ["1", Index(1)],
    ids=["str", "index-object"],
)
@pytest.mark.usefixtures("diagram")
def test_relationship_plantuml_macro_render_with_index(
    relationship_type: RelationshipType,
    index: str | Index | None,
    expected_macro: str,
):
    attrs = {
        "label": "example",
        "technology": "technology",
        "description": "Description",
        "extensions": plantuml_extensions(
            sprite="$sprite",
            tags=["tag1", "tag2"],
            link="https://example.com",
            index=index,
        ),
    }
    signature = (
        '(from, to, "example", '
        '"technology", '
        '"Description", '
        '$sprite="$sprite", '
        '$tags="tag1+tag2", '
        '$link="https://example.com", '
        f"$index={index}"
        ")"
    )
    from_element = Element(alias="from", label="From element")
    to_element = Element(alias="to", label="To element")
    relationship = Relationship(
        **attrs,
        from_element=from_element,
        to_element=to_element,
        relationship_type=relationship_type,
    )
    macro = RelationshipPlantUMLMacro(relationship)
    expected_macro = f"{expected_macro}{signature}"

    result = macro.render()

    assert result == expected_macro


@pytest.mark.parametrize(
    ("layout_class", "expected_macro"),
    [
        (LayD, "Lay_D"),
        (LayDown, "Lay_Down"),
        (LayU, "Lay_U"),
        (LayUp, "Lay_Up"),
        (LayR, "Lay_R"),
        (LayRight, "Lay_Right"),
        (LayL, "Lay_L"),
        (LayLeft, "Lay_Left"),
    ],
)
@pytest.mark.usefixtures("diagram")
def test_layout_plantuml_macro_get_macro(
    layout_class: type[Layout],
    expected_macro: str,
):
    from_element = Element(label="from")
    to_element = Element(label="to")
    layout = layout_class(from_element=from_element, to_element=to_element)
    macro = LayoutPlantUMLMacro(layout)

    assert macro.get_macro() == expected_macro


@pytest.mark.parametrize(
    "layout_class",
    [
        LayD,
        LayDown,
        LayU,
        LayUp,
        LayR,
        LayRight,
        LayL,
        LayLeft,
    ],
)
@pytest.mark.usefixtures("diagram")
def test_layout_plantuml_macro_get_data(
    layout_class: type[Layout],
):
    from_element = Element(alias="from_elem", label="From elem")
    to_element = Element(alias="to_elem", label="To elem")
    layout = layout_class(from_element=from_element, to_element=to_element)
    macro = LayoutPlantUMLMacro(layout)

    assert macro.get_data() == {"from": "from_elem", "to": "to_elem"}


@pytest.mark.parametrize(
    ("layout_class", "expected_macro"),
    [
        (LayD, "Lay_D(from_elem, to_elem)"),
        (LayDown, "Lay_Down(from_elem, to_elem)"),
        (LayU, "Lay_U(from_elem, to_elem)"),
        (LayUp, "Lay_Up(from_elem, to_elem)"),
        (LayR, "Lay_R(from_elem, to_elem)"),
        (LayRight, "Lay_Right(from_elem, to_elem)"),
        (LayL, "Lay_L(from_elem, to_elem)"),
        (LayLeft, "Lay_Left(from_elem, to_elem)"),
    ],
)
@pytest.mark.usefixtures("diagram")
def test_layout_plantuml_macro_render(
    layout_class: type[Layout],
    expected_macro: str,
):
    from_element = Element(alias="from_elem", label="From elem")
    to_element = Element(alias="to_elem", label="To elem")
    layout = layout_class(from_element=from_element, to_element=to_element)
    macro = LayoutPlantUMLMacro(layout)

    assert macro.render() == expected_macro


@pytest.mark.parametrize(
    ("element_class", "expected_macro"),
    [
        (
            Node,
            'Node(element1, "Element", "type", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com")',
        ),
        (
            NodeLeft,
            'Node_L(element1, "Element", "type", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com")',
        ),
        (
            NodeRight,
            'Node_R(element1, "Element", "type", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com")',
        ),
        (
            DeploymentNode,
            'Deployment_Node(element1, "Element", "type", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com")',
        ),
        (
            DeploymentNodeLeft,
            'Deployment_Node_L(element1, "Element", "type", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com")',
        ),
        (
            DeploymentNodeRight,
            'Deployment_Node_R(element1, "Element", "type", "An element", $sprite="$foo", $tags="foo+bar", $link="https://example.com")',
        ),
    ],
)
@pytest.mark.usefixtures("deployment_diagram")
def test_node_plantuml_macro_render(
    element_class: type[Element],
    expected_macro: str,
):
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "extensions": plantuml_extensions(
            tags=["foo", "bar"],
            link="https://example.com",
            type="type",
            sprite="$foo",
        ),
    }
    element = element_class(**kwargs)
    macro = NodePlantUMLMacro(element)

    result = macro.render()

    assert result == expected_macro


@pytest.mark.usefixtures("dynamic_diagram")
def test_increment_plantuml_macro_render():
    macro = IncrementPlantUMLMacro(increment())
    expected_macro = "increment()"

    assert macro.render() == expected_macro


@pytest.mark.usefixtures("dynamic_diagram")
def test_set_index_plantuml_macro_render():
    macro = SetIndexPlantUMLMacro(set_index(5))
    expected_macro = "setIndex(5)"

    assert macro.render() == expected_macro


@pytest.mark.parametrize("layout", list(DiagramLayout))
def test_diagram_layout_plantuml_macro_render(
    layout: DiagramLayout,
):
    macro = DiagramLayoutPlantUMLMacro(layout)
    expected_macro = f"{layout.value}()"

    assert macro.render() == expected_macro


@pytest.mark.parametrize(
    ("macro_class", "expected_macro"),
    [
        (LayoutWithLegendPlantUMLMacro, "LAYOUT_WITH_LEGEND()"),
        (LayoutAsSketchPlantUMLMacro, "LAYOUT_AS_SKETCH()"),
        (HidePersonSpritePlantUMLMacro, "HIDE_PERSON_SPRITE()"),
        (ShowPersonOutlinePlantUMLMacro, "SHOW_PERSON_OUTLINE()"),
        (HideStereotypePlantUMLMacro, "HIDE_STEREOTYPE()"),
        (WithoutPropertyHeaderPlantUMLMacro, "WithoutPropertyHeader()"),
    ],
)
def test_plantuml_macro_without_args_render(
    macro_class: type[PlantUMLMacroWithoutArgs],
    expected_macro: str,
):
    macro = macro_class()

    assert macro.render() == expected_macro


def test_update_legend_title_plantuml_macro_render():
    macro = UpdateLegendTitlePlantUMLMacro("example")
    expected_macro = 'UpdateLegendTitle("example")'

    assert macro.render() == expected_macro


def test_set_sketch_style_plantuml_macro_render():
    element = SetSketchStyle(
        bg_color="#white",
        font_color="#black",
        warning_color="#yellow",
        font_name="#Arial",
        footer_warning="footer-warning",
        footer_text="footer-text",
    )
    macro = SetSketchStylePlantUMLMacro(element)
    expected_macro = (
        "SET_SKETCH_STYLE("
        '$bgColor="#white", $fontColor="#black", $warningColor="#yellow", '
        '$fontName="#Arial", $footerWarning="footer-warning", '
        '$footerText="footer-text"'
        ")"
    )

    assert macro.render() == expected_macro


def test_show_legend_plantuml_macro_render_empty():
    element = ShowLegend(hide_stereotype=None, details=None)
    macro = ShowLegendPlantUMLMacro(element)
    expected_macro = "SHOW_LEGEND()"

    assert macro.render() == expected_macro


def test_show_legend_plantuml_macro_render():
    element = ShowLegend(hide_stereotype=True, details="None")
    macro = ShowLegendPlantUMLMacro(element)
    expected_macro = 'SHOW_LEGEND($hideStereotype="true", $details=None())'

    assert macro.render() == expected_macro


def test_show_floating_legend_plantuml_macro_render_empty():
    element = ShowFloatingLegend(alias=None, hide_stereotype=None, details=None)
    macro = ShowFloatingLegendPlantUMLMacro(element)
    expected_macro = "SHOW_FLOATING_LEGEND()"

    assert macro.render() == expected_macro


def test_show_floating_legend_plantuml_macro_render():
    element = ShowFloatingLegend(
        alias="legend", hide_stereotype=True, details="Small"
    )
    macro = ShowFloatingLegendPlantUMLMacro(element)
    expected_macro = 'SHOW_FLOATING_LEGEND("legend", $hideStereotype="true", $details=Small())'

    assert macro.render() == expected_macro


def test_show_person_sprite_plantuml_macro_render_empty():
    element = ShowPersonSprite(alias=None)
    macro = ShowPersonSpritePlantUMLMacro(element)
    expected_macro = "SHOW_PERSON_SPRITE()"

    assert macro.render() == expected_macro


def test_show_person_sprite_plantuml_macro_render():
    element = ShowPersonSprite(alias="example")
    macro = ShowPersonSpritePlantUMLMacro(element)
    expected_macro = 'SHOW_PERSON_SPRITE("example")'

    assert macro.render() == expected_macro

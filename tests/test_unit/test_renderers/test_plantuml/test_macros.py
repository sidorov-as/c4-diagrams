import re
from collections.abc import Callable
from typing import Any, ClassVar

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
    DiagramElementProperties,
    Element,
    ElementWithTechnology,
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
    Relationship,
    RelationshipType,
    increment,
    set_index,
)
from c4.renderers.plantuml.layout_options import (
    BaseStyle,
    BaseTag,
    BoundaryStyle,
    BoundaryTag,
    ComponentTag,
    ContainerBoundaryStyle,
    ContainerTag,
    DiagramLayout,
    ElementStyle,
    ElementTag,
    EnterpriseBoundaryStyle,
    ExternalComponentTag,
    ExternalContainerTag,
    ExternalPersonTag,
    ExternalSystemTag,
    NodeTag,
    PersonTag,
    RelStyle,
    RelTag,
    SetSketchStyle,
    ShowFloatingLegend,
    ShowLegend,
    ShowPersonSprite,
    SystemBoundaryStyle,
    SystemTag,
)
from c4.renderers.plantuml.macros import (
    ELEMENT_TO_PLANTUML_MACRO_MAP,
    RELATIONSHIP_TO_PLANTUML_MACRO_MAP,
    AddBoundaryTagPlantUMLMacro,
    AddComponentTagPlantUMLMacro,
    AddContainerTagPlantUMLMacro,
    AddElementTagPlantUMLMacro,
    AddExternalComponentTagPlantUMLMacro,
    AddExternalContainerTagPlantUMLMacro,
    AddExternalPersonTagPlantUMLMacro,
    AddExternalSystemTagPlantUMLMacro,
    AddNodeTagPlantUMLMacro,
    AddPersonTagPlantUMLMacro,
    AddRelTagPlantUMLMacro,
    AddSystemTagPlantUMLMacro,
    Argument,
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
    StylePlantUMLMacro,
    SystemPlantUMLMacro,
    TagPlantUMLMacro,
    UpdateBoundaryStylePlantUMLMacro,
    UpdateContainerBoundaryStylePlantUMLMacro,
    UpdateElementStylePlantUMLMacro,
    UpdateEnterpriseBoundaryStylePlantUMLMacro,
    UpdateLegendTitlePlantUMLMacro,
    UpdateRelStylePlantUMLMacro,
    UpdateSystemBoundaryStylePlantUMLMacro,
    WithoutPropertyHeaderPlantUMLMacro,
    force_str,
    macro_call,
    quote,
    quote_and_escape,
    quote_and_lower,
    str_or_empty,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("a", '"a"'),
        ('a"b', '"a\\"b"'),
        ("a\nb", '"a\\nb"'),
        ('a"\n"b', '"a\\"\\n\\"b"'),
    ],
)
def test_quote_and_escape(value: str, expected: str):
    result = quote_and_escape(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        (None, ""),
        (True, "True"),
        (False, "False"),
    ],
)
def test_str_or_empty(value: str, expected: str):
    result = str_or_empty(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", '""'),
        ("a", '"a"'),
        ('a"b', '"a"b"'),
        ("a\nb", '"a\nb"'),
        ("  spaced  ", '"  spaced  "'),
    ],
)
def test_quote(value: str, expected: str):
    result = quote(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", '""'),
        ("A", '"a"'),
        ("AbC", '"abc"'),
        ("A B", '"a b"'),
        ('A"b', '"a"b"'),
    ],
)
def test_quote_and_lower(value: str, expected: str):
    result = quote_and_lower(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("x", "x"),
        ("", ""),
        (0, "0"),
        (1, "1"),
        (True, "True"),
        (False, "False"),
        (None, "None"),
        (["a", 1], "['a', 1]"),
        ({"a": 1}, "{'a': 1}"),
    ],
)
def test_force_str(value: str, expected: str):
    result = force_str(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Rel", "Rel()"),
        ("", "()"),
        ("  X  ", "  X  ()"),
        ("My_Macro", "My_Macro()"),
    ],
)
def test_macro_call(value: str, expected: str):
    result = macro_call(value)

    assert result == expected


def test_plantuml_macro_check_macro():
    class TestPlantUMLMacro(PlantUMLMacro[...]):
        macro = "example"

    macro = TestPlantUMLMacro(...)

    result = macro.check_macro()

    assert result == "example"


def test_plantuml_macro_get_macro():
    class TestPlantUMLMacro(PlantUMLMacro[...]):
        macro = "example"

    macro = TestPlantUMLMacro(...)

    result = macro.get_macro()

    assert result == "example"


def test_plantuml_macro_get_macro_not_provided():
    class TestPlantUMLMacro(PlantUMLMacro[...]): ...

    macro = TestPlantUMLMacro(...)

    result = macro.get_macro()

    assert result is None


def test_plantuml_macro_check_macro_not_provided_error():
    class TestPlantUMLMacro(PlantUMLMacro[...]): ...

    macro = TestPlantUMLMacro(...)
    expected_error = "Attribute `macro` not provided for TestPlantUMLMacro"

    with pytest.raises(AttributeError, match=expected_error):
        macro.check_macro()


def test_plantuml_macro_get_data_no_args():
    class TestPlantUMLMacro(PlantUMLMacro[...]): ...

    macro = TestPlantUMLMacro(...)

    result = macro.get_data()

    assert result == {}


def test_plantuml_macro_get_data_not_implemented_error():
    class TestPlantUMLMacro(PlantUMLMacro[...]):
        macro = "example"
        args: ClassVar[list[Argument]] = [
            Argument(name="arg1"),
        ]

    macro = TestPlantUMLMacro(...)
    expected_error = re.escape(
        "TestPlantUMLMacro.get_data() must be overridden "
        "when 'args' are defined"
    )

    with pytest.raises(NotImplementedError, match=expected_error):
        macro.get_data()


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


class PlantUMLMacroWithArgsAndNoData(PlantUMLMacro):
    macro = "example"
    args: ClassVar[list[Argument]] = [
        Argument(name="arg1"),
    ]

    def get_data(self) -> dict[str, Any]:
        return {}


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_render_args_and_no_data_error():
    element = Element(label="example")
    macro = PlantUMLMacroWithArgsAndNoData(element)
    expected_error = re.escape(
        f"Cannot render PlantUML macro for element "
        f"{element!r}: "
        f"arguments are defined (['arg1']), but "
        f"no input data was provided."
    )

    with pytest.raises(ValueError, match=expected_error):
        macro.render()


class PlantUMLMacroWithArgsAndData(PlantUMLMacro):
    macro = "example"
    args: ClassVar[list[Argument]] = [
        Argument(name="arg1"),
        Argument(name="arg2", source="argument2", format=quote),
        Argument(name="arg3", format=quote_and_lower),
        Argument(name="arg4", format=quote),
        Argument(name="arg5", forced_keyword=True, format=quote),
        Argument(name="arg6", format=quote),
    ]

    def get_data(self) -> dict[str, Any]:
        return {
            "arg1": "arg1",
            "argument2": "Arg2 value",
            "arg3": "Arg3 value",
            "arg4": "Arg4 value",
            "arg5": "Arg5 value",
            "arg6": "Arg6 value",
        }


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_render():
    element = Element(label="example")
    macro = PlantUMLMacroWithArgsAndData(element)
    expected_result = (
        'example(arg1, "Arg2 value", "arg3 value", "Arg4 value", '
        '$arg5="Arg5 value", $arg6="Arg6 value")'
    )

    result = macro.render()

    assert result == expected_result


class PlantUMLMacroForceKeyword(PlantUMLMacroWithArgsAndData):
    def get_data(self) -> dict[str, Any]:
        return {
            "arg1": "arg1",
            "argument2": "Arg2 value",
            "arg4": "Arg4 value",
            "arg5": "Arg5 value",
            "arg6": "Arg6 value",
            "arg7": "Arg7 value",
        }


@pytest.mark.usefixtures("diagram")
def test_plantuml_macro_render_force_keyword():
    element = Element(label="example")
    macro = PlantUMLMacroForceKeyword(element)
    expected_result = (
        'example(arg1, "Arg2 value", $arg4="Arg4 value", '
        '$arg5="Arg5 value", $arg6="Arg6 value")'
    )

    result = macro.render()

    assert result == expected_result


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
    kwargs = {
        "alias": "element1",
        "label": "Element",
        "description": "An element",
        "sprite": "$foo1",
        "tags": ["foo", "bar"],
        "link": "https://example.com",
        **override_kwargs,
    }
    element = element_class(**kwargs)
    macro = ElementPlantUMLMacro(element)
    expected_kwargs = {
        **{
            key: value
            for key, value in kwargs.items()
            if key not in ("type_", "technology")
        },
        "type": kwargs.get("type_"),
        "technology": kwargs.get("technology"),
        "base_shape": None,
    }

    assert macro.get_data() == expected_kwargs


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
        "sprite": "$foo1",
        "tags": ["foo", "bar"],
        "link": "https://example.com",
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
        "type": None,
        "technology": "tech",
        "base_shape": None,
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
        "sprite": "$spriteValue",
        "tags": ["foo", "bar"],
        "link": "https://example.com",
        "type_": "stereotype",
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
        "sprite": "$spriteValue",
        "tags": ["foo", "bar"],
        "link": "https://example.com",
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
        "sprite": "$spriteValue",
        "tags": ["foo", "bar"],
        "link": "https://example.com",
        "type_": "stereotype",
        "base_shape": "rectangle",
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
            {"type_": "stereotype"},
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
        "tags": ["foo", "bar"],
        "link": "https://example.com",
        "description": "An element",
        **override_kwargs,
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
        "tags": ["foo", "bar"],
        "link": "https://example.com",
        "description": "An element",
        "technology": "tech",
        "sprite": "$foo",
        "base_shape": "rectangle",
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
        "tags": ["foo", "bar"],
        "link": "https://example.com",
        "description": "An element",
        "technology": "tech",
        "sprite": "$foo",
        "base_shape": "rectangle",
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
    expected_error = f"Empty `from_element` for relationship {relationship}"

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
    expected_error = f"Empty `to_element` for relationship {relationship}"

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
        "sprite": "$sprite",
        "tags": ["tag1", "tag2"],
        "link": "https://example.com",
        "index": index,
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
        **attrs,
        "from": "from",
        "to": "to",
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
        "sprite": "$sprite",
        "tags": ["tag1", "tag2"],
        "link": "https://example.com",
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
        "sprite": "$sprite",
        "tags": ["tag1", "tag2"],
        "link": "https://example.com",
        "index": index,
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
        "tags": ["foo", "bar"],
        "link": "https://example.com",
        "description": "An element",
        "type_": "type",
        "sprite": "$foo",
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


def test_tag_plantuml_macro_init_subclass_without_tag_error():
    expected_error = re.escape(
        "TestMacro must specify exactly one generic tag type, got: []"
    )

    with pytest.raises(TypeError, match=expected_error):

        class TestMacro(TagPlantUMLMacro): ...


def test_tag_plantuml_macro_init_subclass_already_registered_error():
    class TestTag: ...

    class TestTagMacro(TagPlantUMLMacro[TestTag]): ...

    expected_error = re.escape("Macro for 'TestTag' already registered")

    with pytest.raises(TypeError, match=expected_error):

        class TestMacro(TagPlantUMLMacro[TestTag]): ...


def test_tag_plantuml_macro_get_data_not_dataclass():
    class TestTag: ...

    class TestTagMacro(TagPlantUMLMacro[TestTag]): ...

    macro = TestTagMacro(diagram_element=TestTag())
    expected_error = re.escape(
        "TestTag must be a dataclass to extract macro data"
    )

    with pytest.raises(TypeError, match=expected_error):
        macro.get_data()


def test_tag_plantuml_macro_get_macro_by_tag_unknown_type_error():
    class TestTag: ...

    unregistered_tag = TestTag()
    expected_error = "No macro registered for tag type TestTag"

    with pytest.raises(ValueError, match=expected_error):
        TagPlantUMLMacro.get_macro_by_tag(unregistered_tag)


SAMPLE_TAG_ARGS = {
    "tag_stereo": "SERVICE",
    "legend_text": "Core backend service",
    "legend_sprite": "server",
    "sprite": "cloud",
}

SAMPLE_ELEMENT_TAG_ARGS = {
    "bg_color": "#FDF6E3",
    "font_color": "#073642",
    "border_color": "#586E75",
    "shadowing": "true",
    "shape": "RoundedBoxShape",
    "technology": "Python / FastAPI",
    "border_style": "DashedLine",
    "border_thickness": "2",
    **SAMPLE_TAG_ARGS,
}

SAMPLE_REL_TAG_ARGS = {
    "text_color": "#073642",
    "line_color": "#586E75",
    "line_style": "DashedLine",
    "line_thickness": "2",
    "technology": "Python / FastAPI",
    **SAMPLE_TAG_ARGS,
}

SAMPLE_PERSON_TAG_ARGS = {
    "bg_color": "#FDF6E3",
    "font_color": "#073642",
    "border_color": "#586E75",
    "shadowing": "true",
    "shape": "RoundedBoxShape",
    "type_": "person",
    "border_style": "DashedLine",
    "border_thickness": "2",
    **SAMPLE_TAG_ARGS,
}

SAMPLE_SYSTEM_TAG_ARGS = {
    "bg_color": "#FDF6E3",
    "font_color": "#073642",
    "border_color": "#586E75",
    "shadowing": "true",
    "shape": "RoundedBoxShape",
    "type_": "person",
    "border_style": "DashedLine",
    "border_thickness": "2",
    **SAMPLE_TAG_ARGS,
}


@pytest.mark.parametrize(
    ("tag", "expected_macro"),
    [
        (ElementTag(**SAMPLE_ELEMENT_TAG_ARGS), AddElementTagPlantUMLMacro),
        (RelTag(**SAMPLE_REL_TAG_ARGS), AddRelTagPlantUMLMacro),
        (BoundaryTag(**SAMPLE_ELEMENT_TAG_ARGS), AddBoundaryTagPlantUMLMacro),
        (ComponentTag(**SAMPLE_ELEMENT_TAG_ARGS), AddComponentTagPlantUMLMacro),
        (
            ExternalComponentTag(**SAMPLE_ELEMENT_TAG_ARGS),
            AddExternalComponentTagPlantUMLMacro,
        ),
        (ContainerTag(**SAMPLE_ELEMENT_TAG_ARGS), AddContainerTagPlantUMLMacro),
        (
            ExternalContainerTag(**SAMPLE_ELEMENT_TAG_ARGS),
            AddExternalContainerTagPlantUMLMacro,
        ),
        (NodeTag(**SAMPLE_ELEMENT_TAG_ARGS), AddNodeTagPlantUMLMacro),
        (PersonTag(**SAMPLE_PERSON_TAG_ARGS), AddPersonTagPlantUMLMacro),
        (
            ExternalPersonTag(**SAMPLE_PERSON_TAG_ARGS),
            AddExternalPersonTagPlantUMLMacro,
        ),
        (SystemTag(**SAMPLE_SYSTEM_TAG_ARGS), AddSystemTagPlantUMLMacro),
        (
            ExternalSystemTag(**SAMPLE_SYSTEM_TAG_ARGS),
            AddExternalSystemTagPlantUMLMacro,
        ),
    ],
)
def test_tag_plantuml_macro_get_macro_by_tag(
    tag: BaseTag,
    expected_macro: type[TagPlantUMLMacro],
):
    macro = TagPlantUMLMacro.get_macro_by_tag(tag)

    assert type(macro) is expected_macro


def test_add_element_tag_plantuml_macro_render():
    element = ElementTag(**SAMPLE_ELEMENT_TAG_ARGS)
    macro = AddElementTagPlantUMLMacro(element)
    expected_macro = (
        "AddElementTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$techn="Python / FastAPI", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_rel_tag_plantuml_macro_render():
    element = RelTag(**SAMPLE_REL_TAG_ARGS)
    macro = AddRelTagPlantUMLMacro(element)
    expected_macro = (
        "AddRelTag("
        '"SERVICE", '
        '$textColor="#073642", '
        '$lineColor="#586E75", '
        "$lineStyle=DashedLine(), "
        '$lineThickness="2", '
        '$techn="Python / FastAPI"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_boundary_tag_plantuml_macro_render():
    element = BoundaryTag(**SAMPLE_ELEMENT_TAG_ARGS)
    macro = AddBoundaryTagPlantUMLMacro(element)
    expected_macro = (
        "AddBoundaryTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$techn="Python / FastAPI", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_component_tag_plantuml_macro_render():
    element = ComponentTag(**SAMPLE_ELEMENT_TAG_ARGS)
    macro = AddComponentTagPlantUMLMacro(element)
    expected_macro = (
        "AddComponentTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$techn="Python / FastAPI", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_external_component_tag_plantuml_macro_render():
    element = ExternalComponentTag(**SAMPLE_ELEMENT_TAG_ARGS)
    macro = AddExternalComponentTagPlantUMLMacro(element)
    expected_macro = (
        "AddExternalComponentTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$techn="Python / FastAPI", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_container_tag_plantuml_macro_render():
    element = ContainerTag(**SAMPLE_ELEMENT_TAG_ARGS)
    macro = AddContainerTagPlantUMLMacro(element)
    expected_macro = (
        "AddContainerTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$techn="Python / FastAPI", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_external_container_tag_plantuml_macro_render():
    element = ExternalContainerTag(**SAMPLE_ELEMENT_TAG_ARGS)
    macro = AddExternalContainerTagPlantUMLMacro(element)
    expected_macro = (
        "AddExternalContainerTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$techn="Python / FastAPI", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_node_tag_plantuml_macro_render():
    element = NodeTag(**SAMPLE_ELEMENT_TAG_ARGS)
    macro = AddNodeTagPlantUMLMacro(element)
    expected_macro = (
        "AddNodeTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$techn="Python / FastAPI", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_person_tag_plantuml_macro_render():
    element = PersonTag(**SAMPLE_PERSON_TAG_ARGS)
    macro = AddPersonTagPlantUMLMacro(element)
    expected_macro = (
        "AddPersonTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$type="person", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_external_person_tag_plantuml_macro_render():
    element = ExternalPersonTag(**SAMPLE_PERSON_TAG_ARGS)
    macro = AddExternalPersonTagPlantUMLMacro(element)
    expected_macro = (
        "AddExternalPersonTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$type="person", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_system_tag_plantuml_macro_render():
    element = SystemTag(**SAMPLE_SYSTEM_TAG_ARGS)
    macro = AddSystemTagPlantUMLMacro(element)
    expected_macro = (
        "AddSystemTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$type="person", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_external_system_tag_plantuml_macro_render():
    element = ExternalSystemTag(**SAMPLE_SYSTEM_TAG_ARGS)
    macro = AddExternalSystemTagPlantUMLMacro(element)
    expected_macro = (
        "AddExternalSystemTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="cloud", '
        '$type="person", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_style_plantuml_macro_init_subclass_without_style_error():
    expected_error = re.escape(
        "TestMacro must specify exactly one generic style type, got: []"
    )

    with pytest.raises(TypeError, match=expected_error):

        class TestMacro(StylePlantUMLMacro): ...


def test_style_plantuml_macro_init_subclass_already_registered_error():
    class TestStyle: ...

    class TestStyleMacro(StylePlantUMLMacro[TestStyle]): ...

    expected_error = re.escape("Macro for 'TestStyle' already registered")

    with pytest.raises(TypeError, match=expected_error):

        class TestMacro(StylePlantUMLMacro[TestStyle]): ...


def test_style_plantuml_macro_get_data_not_dataclass():
    class TestStyle: ...

    class TestStyleMacro(StylePlantUMLMacro[TestStyle]): ...

    macro = TestStyleMacro(diagram_element=TestStyle())
    expected_error = re.escape(
        "TestStyle must be a dataclass to extract macro data"
    )

    with pytest.raises(TypeError, match=expected_error):
        macro.get_data()


def test_style_plantuml_macro_get_macro_by_style_unknown_type_error():
    class TestStyle: ...

    unregistered_style = TestStyle()
    expected_error = "No macro registered for style type TestStyle"

    with pytest.raises(ValueError, match=expected_error):
        StylePlantUMLMacro.get_macro_by_style(unregistered_style)


SAMPLE_ELEMENT_STYLE_ARGS = {
    "element_name": "UserService",
    "bg_color": "#ffffff",
    "font_color": "#000000",
    "border_color": "#333333",
    "shadowing": "true",
    "shape": "RoundedBoxShape",
    "sprite": "user",
    "technology": "Python",
    "legend_text": "User Service",
    "legend_sprite": "user_icon",
    "border_style": "DashedLine",
    "border_thickness": "2",
}

SAMPLE_REL_STYLE_ARGS = {
    "text_color": "#000000",
    "line_color": "#333333",
}

SAMPLE_BOUNDARY_STYLE_ARGS = {
    **SAMPLE_ELEMENT_STYLE_ARGS,
    "element_name": "Boundary",
    "type_": "System",
}


@pytest.mark.parametrize(
    ("style", "expected_macro"),
    [
        (
            ElementStyle(**SAMPLE_ELEMENT_STYLE_ARGS),
            UpdateElementStylePlantUMLMacro,
        ),
        (
            RelStyle(**SAMPLE_REL_STYLE_ARGS),
            UpdateRelStylePlantUMLMacro,
        ),
        (
            BoundaryStyle(**SAMPLE_BOUNDARY_STYLE_ARGS),
            UpdateBoundaryStylePlantUMLMacro,
        ),
        (
            ContainerBoundaryStyle(**SAMPLE_BOUNDARY_STYLE_ARGS),
            UpdateContainerBoundaryStylePlantUMLMacro,
        ),
        (
            SystemBoundaryStyle(**SAMPLE_BOUNDARY_STYLE_ARGS),
            UpdateSystemBoundaryStylePlantUMLMacro,
        ),
        (
            EnterpriseBoundaryStyle(**SAMPLE_BOUNDARY_STYLE_ARGS),
            UpdateEnterpriseBoundaryStylePlantUMLMacro,
        ),
    ],
)
def test_style_plantuml_macro_get_macro_by_style(
    style: BaseStyle,
    expected_macro: type[StylePlantUMLMacro],
):
    macro = StylePlantUMLMacro.get_macro_by_style(style)

    assert type(macro) is expected_macro


def test_update_element_style_plantuml_macro_render():
    element = ElementStyle(**SAMPLE_ELEMENT_STYLE_ARGS)
    macro = UpdateElementStylePlantUMLMacro(element)
    expected_macro = (
        "UpdateElementStyle("
        '"UserService", '
        '$bgColor="#ffffff", '
        '$fontColor="#000000", '
        '$borderColor="#333333", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$sprite="user", '
        '$techn="Python", '
        '$legendText="User Service", '
        '$legendSprite="user_icon", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_rel_style_plantuml_macro_render():
    element = RelStyle(**SAMPLE_REL_STYLE_ARGS)
    macro = UpdateRelStylePlantUMLMacro(element)
    expected_macro = (
        'UpdateRelStyle($textColor="#000000", $lineColor="#333333")'
    )

    assert macro.render() == expected_macro


def test_update_boundary_style_plantuml_macro_render():
    element = BoundaryStyle(**SAMPLE_BOUNDARY_STYLE_ARGS)
    macro = UpdateBoundaryStylePlantUMLMacro(element)
    expected_macro = (
        "UpdateBoundaryStyle("
        '"Boundary", '
        '$bgColor="#ffffff", '
        '$fontColor="#000000", '
        '$borderColor="#333333", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$type="System", '
        '$sprite="user", '
        '$techn="Python", '
        '$legendText="User Service", '
        '$legendSprite="user_icon", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_container_boundary_style_plantuml_macro_render():
    element = ContainerBoundaryStyle(**SAMPLE_BOUNDARY_STYLE_ARGS)
    macro = UpdateContainerBoundaryStylePlantUMLMacro(element)
    expected_macro = (
        "UpdateContainerBoundaryStyle("
        '"Boundary", '
        '$bgColor="#ffffff", '
        '$fontColor="#000000", '
        '$borderColor="#333333", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$type="System", '
        '$sprite="user", '
        '$techn="Python", '
        '$legendText="User Service", '
        '$legendSprite="user_icon", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_system_boundary_style_plantuml_macro_render():
    element = SystemBoundaryStyle(**SAMPLE_BOUNDARY_STYLE_ARGS)
    macro = UpdateSystemBoundaryStylePlantUMLMacro(element)
    expected_macro = (
        "UpdateSystemBoundaryStyle("
        '"Boundary", '
        '$bgColor="#ffffff", '
        '$fontColor="#000000", '
        '$borderColor="#333333", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$type="System", '
        '$sprite="user", '
        '$techn="Python", '
        '$legendText="User Service", '
        '$legendSprite="user_icon", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_enterprise_boundary_style_plantuml_macro_render():
    element = EnterpriseBoundaryStyle(**SAMPLE_BOUNDARY_STYLE_ARGS)
    macro = UpdateEnterpriseBoundaryStylePlantUMLMacro(element)
    expected_macro = (
        "UpdateEnterpriseBoundaryStyle("
        '"Boundary", '
        '$bgColor="#ffffff", '
        '$fontColor="#000000", '
        '$borderColor="#333333", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$type="System", '
        '$sprite="user", '
        '$techn="Python", '
        '$legendText="User Service", '
        '$legendSprite="user_icon", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro

import re

import pytest

from c4.renderers.plantuml.macros import (
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
    TagPlantUMLMacro,
)
from c4.renderers.plantuml.options import (
    BaseTag,
    BoundaryTag,
    ComponentTag,
    ContainerTag,
    ElementTag,
    ExternalComponentTag,
    ExternalContainerTag,
    ExternalPersonTag,
    ExternalSystemTag,
    NodeTag,
    PersonTag,
    RelTag,
    SystemTag,
)


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

SAMPLE_BOUNDARY_TAG_ARGS = {
    key: value
    for key, value in SAMPLE_ELEMENT_TAG_ARGS.items()
    if key != "technology"
}
SAMPLE_BOUNDARY_TAG_ARGS["type_"] = "System"

SAMPLE_NODE_TAG_ARGS = {
    key: value
    for key, value in SAMPLE_ELEMENT_TAG_ARGS.items()
    if key != "technology"
}
SAMPLE_NODE_TAG_ARGS.update({
    "type_": "Node",
})

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
        (BoundaryTag(**SAMPLE_BOUNDARY_TAG_ARGS), AddBoundaryTagPlantUMLMacro),
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
        (NodeTag(**SAMPLE_NODE_TAG_ARGS), AddNodeTagPlantUMLMacro),
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
        '$sprite="cloud", '
        '$techn="Python / FastAPI", '
        '$legendText="Core backend service", '
        '$legendSprite="server", '
        '$lineThickness="2"'
        ")"
    )

    assert macro.render() == expected_macro


def test_add_boundary_tag_plantuml_macro_render():
    element = BoundaryTag(**SAMPLE_BOUNDARY_TAG_ARGS)
    macro = AddBoundaryTagPlantUMLMacro(element)
    expected_macro = (
        "AddBoundaryTag("
        '"SERVICE", '
        '$bgColor="#FDF6E3", '
        '$fontColor="#073642", '
        '$borderColor="#586E75", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$type="System", '
        '$legendText="Core backend service", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2", '
        '$sprite="cloud", '
        '$legendSprite="server"'
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
    element = NodeTag(**SAMPLE_NODE_TAG_ARGS)
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
        '$type="Node", '
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

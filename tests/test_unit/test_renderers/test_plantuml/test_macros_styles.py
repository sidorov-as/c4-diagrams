import re

import pytest

from c4.renderers.plantuml.macros import (
    StylePlantUMLMacro,
    UpdateBoundaryStylePlantUMLMacro,
    UpdateContainerBoundaryStylePlantUMLMacro,
    UpdateElementStylePlantUMLMacro,
    UpdateEnterpriseBoundaryStylePlantUMLMacro,
    UpdateRelStylePlantUMLMacro,
    UpdateSystemBoundaryStylePlantUMLMacro,
)
from c4.renderers.plantuml.options import (
    BaseStyle,
    BoundaryStyle,
    ContainerBoundaryStyle,
    ElementStyle,
    EnterpriseBoundaryStyle,
    RelStyle,
    SystemBoundaryStyle,
)


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
SAMPLE_BOUNDARY_STYLE_ARGS.pop("technology")

SAMPLE_SPECIFIC_BOUNDARY_STYLE_ARGS = {
    key: value
    for key, value in SAMPLE_BOUNDARY_STYLE_ARGS.items()
    if key != "element_name"
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
            ContainerBoundaryStyle(**SAMPLE_SPECIFIC_BOUNDARY_STYLE_ARGS),
            UpdateContainerBoundaryStylePlantUMLMacro,
        ),
        (
            SystemBoundaryStyle(**SAMPLE_SPECIFIC_BOUNDARY_STYLE_ARGS),
            UpdateSystemBoundaryStylePlantUMLMacro,
        ),
        (
            EnterpriseBoundaryStyle(**SAMPLE_SPECIFIC_BOUNDARY_STYLE_ARGS),
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
        '$legendText="User Service", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2", '
        '$sprite="user", '
        '$legendSprite="user_icon"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_container_boundary_style_plantuml_macro_render():
    element = ContainerBoundaryStyle(**SAMPLE_SPECIFIC_BOUNDARY_STYLE_ARGS)
    macro = UpdateContainerBoundaryStylePlantUMLMacro(element)
    expected_macro = (
        "UpdateContainerBoundaryStyle("
        '$bgColor="#ffffff", '
        '$fontColor="#000000", '
        '$borderColor="#333333", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$type="System", '
        '$legendText="User Service", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2", '
        '$sprite="user", '
        '$legendSprite="user_icon"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_system_boundary_style_plantuml_macro_render():
    element = SystemBoundaryStyle(**SAMPLE_SPECIFIC_BOUNDARY_STYLE_ARGS)
    macro = UpdateSystemBoundaryStylePlantUMLMacro(element)
    expected_macro = (
        "UpdateSystemBoundaryStyle("
        '$bgColor="#ffffff", '
        '$fontColor="#000000", '
        '$borderColor="#333333", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$type="System", '
        '$legendText="User Service", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2", '
        '$sprite="user", '
        '$legendSprite="user_icon"'
        ")"
    )

    assert macro.render() == expected_macro


def test_update_enterprise_boundary_style_plantuml_macro_render():
    element = EnterpriseBoundaryStyle(**SAMPLE_SPECIFIC_BOUNDARY_STYLE_ARGS)
    macro = UpdateEnterpriseBoundaryStylePlantUMLMacro(element)
    expected_macro = (
        "UpdateEnterpriseBoundaryStyle("
        '$bgColor="#ffffff", '
        '$fontColor="#000000", '
        '$borderColor="#333333", '
        '$shadowing="true", '
        "$shape=RoundedBoxShape(), "
        '$type="System", '
        '$legendText="User Service", '
        "$borderStyle=DashedLine(), "
        '$borderThickness="2", '
        '$sprite="user", '
        '$legendSprite="user_icon"'
        ")"
    )

    assert macro.render() == expected_macro

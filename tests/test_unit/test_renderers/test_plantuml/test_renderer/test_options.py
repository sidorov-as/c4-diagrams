from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

import c4.renderers.plantuml.renderer as renderer_module
from c4.renderers.plantuml.options import (
    PlantUMLRenderOptions,
    SetSketchStyle,
    ShowFloatingLegend,
    ShowLegend,
)
from c4.renderers.plantuml.renderer import PlantUMLRenderOptionsRenderer


@pytest.mark.parametrize(
    ("tags", "rendered_values", "expected"),
    [
        (
            ["tag-1"],
            ["TAG_1"],
            "TAG_1",
        ),
        (
            ["tag-1", "tag-2"],
            ["TAG_1", "TAG_2"],
            "TAG_1\nTAG_2",
        ),
    ],
)
def test_plantuml_render_options_renderer__render_tags__renders_tag_macros_in_order(
    mocker: MockerFixture,
    tags: list[str],
    rendered_values: list[str],
    expected: str,
):
    options = PlantUMLRenderOptions(tags=tags)
    renderer = PlantUMLRenderOptionsRenderer(
        includes=[], render_options=options
    )
    macros = [
        mocker.Mock(render=mocker.Mock(return_value=value))
        for value in rendered_values
    ]
    get_macro_by_tag = mocker.patch.object(
        renderer_module.TagPlantUMLMacro,
        "get_macro_by_tag",
        side_effect=macros,
    )

    result = renderer._render_tags()

    assert result == expected
    assert get_macro_by_tag.call_args_list == [mocker.call(tag) for tag in tags]
    assert all(macro.render.call_count == 1 for macro in macros)


@pytest.mark.parametrize(
    ("styles", "rendered_values", "expected"),
    [
        (
            ["style-1"],
            ["STYLE_1"],
            "STYLE_1",
        ),
        (
            ["style-1", "style-2"],
            ["STYLE_1", "STYLE_2"],
            "STYLE_1\nSTYLE_2",
        ),
    ],
)
def test_plantuml_render_options_renderer__render_styles__renders_style_macros_in_order(
    mocker: MockerFixture,
    styles: list[str],
    rendered_values: list[str],
    expected: str,
):
    options = PlantUMLRenderOptions(styles=styles)
    renderer = PlantUMLRenderOptionsRenderer(
        includes=[], render_options=options
    )
    macros = [
        mocker.Mock(render=mocker.Mock(return_value=value))
        for value in rendered_values
    ]
    get_macro_by_style = mocker.patch.object(
        renderer_module.StylePlantUMLMacro,
        "get_macro_by_style",
        side_effect=macros,
    )

    result = renderer._render_styles()

    assert result == expected
    assert get_macro_by_style.call_args_list == [
        mocker.call(style) for style in styles
    ]
    assert all(macro.render.call_count == 1 for macro in macros)


def test_plantuml_render_options_renderer__render_layout__empty():
    renderer = PlantUMLRenderOptionsRenderer(includes=[])

    result = renderer._render_layout()

    assert result == ""


def test_plantuml_render_options_renderer__render_layout__renders_enabled_macros(
    mocker: MockerFixture,
):
    options = PlantUMLRenderOptions(
        layout="LAYOUT_TOP_DOWN",  # type: ignore[arg-type]
        layout_with_legend=True,
        layout_as_sketch=True,
        hide_person_sprite=True,
        show_person_sprite="person-sprite-config",  # type: ignore[arg-type]
        show_person_outline=True,
        legend_title="Legend title",
        hide_stereotype=True,
        without_property_header=True,
    )
    renderer = PlantUMLRenderOptionsRenderer(
        includes=[], render_options=options
    )
    diagram_layout_macro = mocker.patch.object(
        renderer_module,
        "DiagramLayoutPlantUMLMacro",
        return_value=mocker.Mock(render=mocker.Mock(return_value="LAYOUT")),
    )
    layout_with_legend_macro = mocker.patch.object(
        renderer_module,
        "LayoutWithLegendPlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="LAYOUT_WITH_LEGEND")
        ),
    )
    layout_as_sketch_macro = mocker.patch.object(
        renderer_module,
        "LayoutAsSketchPlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="LAYOUT_AS_SKETCH")
        ),
    )
    hide_person_sprite_macro = mocker.patch.object(
        renderer_module,
        "HidePersonSpritePlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="HIDE_PERSON_SPRITE")
        ),
    )
    show_person_sprite_macro = mocker.patch.object(
        renderer_module,
        "ShowPersonSpritePlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="SHOW_PERSON_SPRITE")
        ),
    )
    show_person_outline_macro = mocker.patch.object(
        renderer_module,
        "ShowPersonOutlinePlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="SHOW_PERSON_OUTLINE")
        ),
    )
    update_legend_title_macro = mocker.patch.object(
        renderer_module,
        "UpdateLegendTitlePlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="UPDATE_LEGEND_TITLE")
        ),
    )
    hide_stereotype_macro = mocker.patch.object(
        renderer_module,
        "HideStereotypePlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="HIDE_STEREOTYPE")
        ),
    )
    without_property_header_macro = mocker.patch.object(
        renderer_module,
        "WithoutPropertyHeaderPlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="WITHOUT_PROPERTY_HEADER")
        ),
    )

    result = renderer._render_layout()

    assert result == (
        "LAYOUT\n"
        "LAYOUT_WITH_LEGEND\n"
        "LAYOUT_AS_SKETCH\n"
        "HIDE_PERSON_SPRITE\n"
        "SHOW_PERSON_SPRITE\n"
        "SHOW_PERSON_OUTLINE\n"
        "UPDATE_LEGEND_TITLE\n"
        "HIDE_STEREOTYPE\n"
        "WITHOUT_PROPERTY_HEADER"
    )
    diagram_layout_macro.assert_called_once_with("LAYOUT_TOP_DOWN")
    layout_with_legend_macro.assert_called_once_with()
    layout_as_sketch_macro.assert_called_once_with()
    hide_person_sprite_macro.assert_called_once_with()
    show_person_sprite_macro.assert_called_once_with("person-sprite-config")
    show_person_outline_macro.assert_called_once_with()
    update_legend_title_macro.assert_called_once_with("Legend title")
    hide_stereotype_macro.assert_called_once_with()
    without_property_header_macro.assert_called_once_with()


def test_plantuml_render_options_renderer_render_sketch_style__renders_macro(
    mocker: MockerFixture,
):
    sketch_style = SetSketchStyle()
    options = PlantUMLRenderOptions(set_sketch_style=sketch_style)
    renderer = PlantUMLRenderOptionsRenderer(
        includes=[], render_options=options
    )
    sketch_style_macro = mocker.patch.object(
        renderer_module,
        "SetSketchStylePlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="SET_SKETCH_STYLE")
        ),
    )

    result = renderer._render_sketch_style()

    assert result == "SET_SKETCH_STYLE"
    sketch_style_macro.assert_called_once_with(sketch_style)


def test_plantuml_render_options_renderer__render_sketch_style__empty():
    renderer = PlantUMLRenderOptionsRenderer(includes=[])

    result = renderer._render_sketch_style()

    assert result == ""


def test_plantuml_render_options_renderer__render_header__renders_sections_and_title(
    mocker: MockerFixture,
):
    renderer = PlantUMLRenderOptionsRenderer(
        includes=["!include a", "!include b"]
    )
    diagram = SimpleNamespace(title="Orders Diagram")
    render_tags = mocker.patch.object(
        renderer,
        "_render_tags",
        return_value="TAGS",
    )
    render_styles = mocker.patch.object(
        renderer,
        "_render_styles",
        return_value="STYLES",
    )
    render_layout = mocker.patch.object(
        renderer,
        "_render_layout",
        return_value="LAYOUT",
    )
    render_sketch_style = mocker.patch.object(
        renderer,
        "_render_sketch_style",
        return_value="SKETCH",
    )

    result = renderer.render_header(diagram)

    assert result == (
        "!include a\n"
        "!include b\n"
        "\n"
        "TAGS\n"
        "\n"
        "STYLES\n"
        "\n"
        "LAYOUT\n"
        "\n"
        "SKETCH\n"
        "\n"
        "title Orders Diagram\n"
    )
    render_tags.assert_called_once_with()
    render_styles.assert_called_once_with()
    render_layout.assert_called_once_with()
    render_sketch_style.assert_called_once_with()


def test_plantuml_render_options_renderer__render_header__skips_title(
    mocker: MockerFixture,
):
    renderer = PlantUMLRenderOptionsRenderer(includes=["!include a"])
    diagram = SimpleNamespace(title="")
    mocker.patch.object(renderer, "_render_tags", return_value="")
    mocker.patch.object(renderer, "_render_styles", return_value="")
    mocker.patch.object(renderer, "_render_layout", return_value="")
    mocker.patch.object(renderer, "_render_sketch_style", return_value="")

    result = renderer.render_header(diagram)

    assert result == "!include a\n"


def test_plantuml_render_options_renderer__render_footer(
    mocker: MockerFixture,
):
    show_legend = ShowLegend()
    show_floating_legend = ShowFloatingLegend()
    options = PlantUMLRenderOptions(
        show_legend=show_legend,
        show_floating_legend=show_floating_legend,
    )
    renderer = PlantUMLRenderOptionsRenderer(
        includes=[], render_options=options
    )
    show_legend_macro = mocker.patch.object(
        renderer_module,
        "ShowLegendPlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="SHOW_LEGEND")
        ),
    )
    show_floating_legend_macro = mocker.patch.object(
        renderer_module,
        "ShowFloatingLegendPlantUMLMacro",
        return_value=mocker.Mock(
            render=mocker.Mock(return_value="SHOW_FLOATING_LEGEND")
        ),
    )

    result = renderer.render_footer()

    assert result == "SHOW_LEGEND\n\nSHOW_FLOATING_LEGEND\n"
    show_legend_macro.assert_called_once_with(show_legend)
    show_floating_legend_macro.assert_called_once_with(show_floating_legend)


def test_plantuml_render_options_renderer__render_footer__empty():
    renderer = PlantUMLRenderOptionsRenderer(includes=[])

    result = renderer.render_footer()

    assert result == ""


def test_plantuml_render_options_renderer__init__uses_default_render_options():
    default_options = PlantUMLRenderOptions()
    renderer = PlantUMLRenderOptionsRenderer(includes=["!include default"])

    assert renderer._includes == ["!include default"]
    assert renderer._render_options == default_options


def test_plantuml_render_options_renderer__init__uses_provided_render_options():
    options = PlantUMLRenderOptions(layout_with_legend=True)

    renderer = PlantUMLRenderOptionsRenderer(
        includes=["!include custom"],
        render_options=options,
    )

    assert renderer._includes == ["!include custom"]
    assert renderer._render_options is options

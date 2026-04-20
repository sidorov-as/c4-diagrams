import textwrap
from typing import Any

import pytest

from c4.converters.python.renderers.plantuml import (
    PlantUMLRenderOptionsCodegen,
    _resolve_method,
)
from c4.renderers.plantuml.options import (
    BoundaryStyle,
    ContainerTag,
    DiagramLayout,
    ElementStyle,
    ExternalPersonTag,
    PersonTag,
    PlantUMLRenderOptions,
    RelStyle,
    RelTag,
    SetSketchStyle,
    ShowFloatingLegend,
    ShowLegend,
    ShowPersonSprite,
)

ANY_TAG = ExternalPersonTag("", "", "", "", "", "", "", "", "", "", "", "")

ANY_STYLE = ElementStyle("", "", "", "", "", "", "", "", "", "", "", "")


@pytest.fixture()
def codegen() -> PlantUMLRenderOptionsCodegen:
    return PlantUMLRenderOptionsCodegen()


def test_resolve_method__success():
    mapping = {PersonTag: "x"}
    obj = ExternalPersonTag("", "", "", "", "", "", "", "", "", "", "", "")
    expected = "x"

    result = _resolve_method(mapping, obj)

    assert result == expected


def test_resolve_method__key_error():
    mapping = {PersonTag: "x"}
    obj = object()

    with pytest.raises(KeyError):
        _resolve_method(mapping, obj)


@pytest.mark.parametrize(
    ("layout", "expected"),
    [
        (DiagramLayout.LAYOUT_TOP_DOWN, "layout_top_down"),
        (DiagramLayout.LAYOUT_LEFT_RIGHT, "layout_left_right"),
        (DiagramLayout.LAYOUT_LANDSCAPE, "layout_landscape"),
    ],
)
def test_render_options_codegen__layout_method_name(
    layout: DiagramLayout,
    expected: str,
):
    result = PlantUMLRenderOptionsCodegen._layout_method_name(layout)

    assert result == expected


def test_render_options_codegen__layout_method_name_raises_value_error():
    layout = object()
    expected_error = rf"Unsupported DiagramLayout: {layout!r}"

    with pytest.raises(ValueError, match=expected_error):
        PlantUMLRenderOptionsCodegen._layout_method_name(layout)  # type: ignore[arg-type]


def test_render_options_codegen__generate_single_line_for_single_call(
    codegen: PlantUMLRenderOptionsCodegen,
):
    config = PlantUMLRenderOptions(layout_as_sketch=True)
    expected_result = textwrap.dedent(
        """
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .layout_as_sketch()
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected_result


def test_render_options_codegen_generate_single_line_le_79(
    codegen: PlantUMLRenderOptionsCodegen,
):
    config = PlantUMLRenderOptions(
        layout_as_sketch=True,
        layout_with_legend=True,
    )
    expected = textwrap.dedent(
        """
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .layout_with_legend()
            .layout_as_sketch()
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected


def test_render_options_codegen__call_with_filtered_kwargs_raises_error(
    codegen: PlantUMLRenderOptionsCodegen,
):
    obj = object()
    expected_error = (
        rf"Expected dataclass for set_sketch_style, got {type(obj)!r}"
    )

    with pytest.raises(TypeError, match=expected_error):
        codegen._call_with_filtered_kwargs(
            "set_sketch_style",
            obj,
            defaults={"bg_color": None},
        )


def test_render_options_codegen__call_with_filtered_kwargs_filters_defaults(
    codegen: PlantUMLRenderOptionsCodegen,
):
    obj = SetSketchStyle(bg_color="white")

    result = codegen._call_with_filtered_kwargs(
        "set_sketch_style",
        obj,
        defaults={
            "bg_color": None,
            "font_color": None,
            "warning_color": None,
            "font_name": None,
            "footer_warning": None,
            "footer_text": None,
        },
    )

    assert result == ".set_sketch_style(bg_color='white')"


def test_render_options_codegen__call_from_optional_dataclass_raises_error(
    codegen: PlantUMLRenderOptionsCodegen,
):
    obj = object()
    expected_error = rf"Expected dataclass for show_legend, got {type(obj)!r}"

    with pytest.raises(TypeError, match=expected_error):
        codegen._call_from_optional_dataclass(
            "show_legend",
            obj,
            none_means_default={
                "hide_stereotype": True,
                "details": "Small",
            },
        )


def test_render_options_codegen__call_from_optional_dataclass_emits_only_diffs(
    codegen: PlantUMLRenderOptionsCodegen,
):
    obj = ShowLegend(hide_stereotype=None, details="Normal")

    result = codegen._call_from_optional_dataclass(
        "show_legend",
        obj,
        none_means_default={"hide_stereotype": True, "details": "Small"},
    )

    assert result == ".show_legend(details='Normal')"


@pytest.mark.parametrize(
    ("kwargs", "drop_values", "keep", "expected"),
    [
        ({"a": "", "b": 1}, {"", None}, set(), {"b": 1}),
        (
            {"tag_stereo": "", "b": 1},
            {"", None},
            {"tag_stereo"},
            {"tag_stereo": "", "b": 1},
        ),
        ({"a": None, "b": "x"}, {"", None}, set(), {"b": "x"}),
    ],
)
def test_render_options_codegen__filtered_kwargs_drops_values_unless_keep(
    kwargs: dict[str, Any],
    drop_values: dict[str, Any],
    keep: set[Any],
    expected: dict[str, Any],
):
    result = PlantUMLRenderOptionsCodegen._filtered_kwargs(
        kwargs,
        drop_values=drop_values,
        keep=keep,
    )

    assert result == expected


def test_render_options_codegen__generate_renders_tags_and_styles(
    codegen: PlantUMLRenderOptionsCodegen,
):
    config = PlantUMLRenderOptions(
        tags=[
            ExternalPersonTag(
                "person", "", "", "", "", "", "", "", "", "", "", ""
            )
        ],
        styles=[RelStyle(text_color="red", line_color="")],
    )
    expected = textwrap.dedent(
        """
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .add_external_person_tag(
                tag_stereo='person',
            )
            .update_rel_style(
                text_color='red',
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected


def test_render_options_codegen__generate_renders_element_style_with_name(
    codegen,
):
    element_name = "very very long element name that fits 79 chars"
    style = ElementStyle(
        element_name=element_name,
        bg_color="",
        font_color="",
        border_color="",
        shadowing="",
        shape="",
        sprite="",
        technology="",
        legend_text="",
        legend_sprite="",
        border_style="",
        border_thickness="",
    )
    config = PlantUMLRenderOptions(styles=[style])
    expected = textwrap.dedent(
        f"""
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .update_element_style(
                element_name='{element_name}',
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected


@pytest.mark.parametrize(
    ("layout", "with_legend", "expected_result"),
    [
        (
            None,
            True,
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .layout_with_legend()
                    .build()
                )
                """
            ).strip(),
        ),
        (
            None,
            False,
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().build()
                """
            ).strip(),
        ),
        (
            DiagramLayout.LAYOUT_TOP_DOWN,
            True,
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .layout_top_down(
                        with_legend=True,
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            DiagramLayout.LAYOUT_TOP_DOWN,
            False,
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .layout_top_down()
                    .build()
                )
                """
            ).strip(),
        ),
        (
            DiagramLayout.LAYOUT_LEFT_RIGHT,
            True,
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .layout_left_right(
                        with_legend=True,
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            DiagramLayout.LAYOUT_LEFT_RIGHT,
            False,
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .layout_left_right()
                    .build()
                )
                """
            ).strip(),
        ),
        (
            DiagramLayout.LAYOUT_LANDSCAPE,
            True,
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .layout_landscape(
                        with_legend=True,
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            DiagramLayout.LAYOUT_LANDSCAPE,
            False,
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .layout_landscape()
                    .build()
                )
                """
            ).strip(),
        ),
    ],
)
def test_render_options_codegen__render_layout_with_legend(
    codegen: PlantUMLRenderOptionsCodegen,
    layout: DiagramLayout | None,
    with_legend: bool,
    expected_result: str,
):
    config = PlantUMLRenderOptions(
        layout=layout,
        layout_with_legend=with_legend,
    )

    result = codegen.generate(config)

    assert result == expected_result


@pytest.mark.parametrize(
    ("set_sketch_style", "expected_result"),
    [
        (
            None,
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().build()
                """
            ).strip(),
        ),
        (
            SetSketchStyle(),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .set_sketch_style()
                    .build()
                )
                """
            ).strip(),
        ),
        (
            SetSketchStyle(bg_color="red"),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .set_sketch_style(
                        bg_color='red',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            SetSketchStyle(
                bg_color="very-long-color-name",
            ),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .set_sketch_style(
                        bg_color='very-long-color-name',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            SetSketchStyle(
                bg_color="very-long-color-name",
                footer_text="very-long-footer-text",
            ),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .set_sketch_style(
                        bg_color='very-long-color-name',
                        footer_text='very-long-footer-text',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
    ],
)
def test_render_options_codegen__render_set_sketch_style(
    codegen: PlantUMLRenderOptionsCodegen,
    set_sketch_style: SetSketchStyle | None,
    expected_result: str,
):
    config = PlantUMLRenderOptions(set_sketch_style=set_sketch_style)

    result = codegen.generate(config)

    assert result == expected_result


@pytest.mark.parametrize(
    ("show_legend", "expected_result"),
    [
        (
            None,
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().build()
                """
            ).strip(),
        ),
        (
            ShowLegend(),
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().show_legend().build()
                """
            ).strip(),
        ),
        (
            ShowLegend(hide_stereotype=True),
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().show_legend().build()
                """
            ).strip(),
        ),
        (
            ShowLegend(hide_stereotype=False),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_legend(
                        hide_stereotype=False,
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowLegend(details="Small"),
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().show_legend().build()
                """
            ).strip(),
        ),
        (
            ShowLegend(details="Normal"),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_legend(
                        details='Normal',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowLegend(hide_stereotype=False, details="Normal"),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_legend(
                        hide_stereotype=False,
                        details='Normal',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
    ],
)
def test_render_options_codegen__render_show_legend(
    codegen: PlantUMLRenderOptionsCodegen,
    show_legend: ShowLegend | None,
    expected_result: str,
):
    config = PlantUMLRenderOptions(show_legend=show_legend)

    result = codegen.generate(config)

    assert result == expected_result


@pytest.mark.parametrize(
    ("show_floating_legend", "expected_result"),
    [
        (
            None,
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().build()
                """
            ).strip(),
        ),
        (
            ShowFloatingLegend(),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_floating_legend()
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowFloatingLegend(alias="foo"),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_floating_legend(
                        alias='foo',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowFloatingLegend(hide_stereotype=True),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_floating_legend()
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowFloatingLegend(hide_stereotype=False),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_floating_legend(
                        hide_stereotype=False,
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowFloatingLegend(details="Small"),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_floating_legend()
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowFloatingLegend(details="Normal"),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_floating_legend(
                        details='Normal',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowFloatingLegend(
                hide_stereotype=False, details="Normal", alias="foo"
            ),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_floating_legend(
                        alias='foo',
                        hide_stereotype=False,
                        details='Normal',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
    ],
)
def test_render_options_codegen__render_show_floating_legend(
    codegen: PlantUMLRenderOptionsCodegen,
    show_floating_legend: ShowFloatingLegend | None,
    expected_result: str,
):
    config = PlantUMLRenderOptions(show_floating_legend=show_floating_legend)

    result = codegen.generate(config)

    assert result == expected_result


@pytest.mark.parametrize(
    ("legend_title", "expected_result"),
    [
        (
            None,
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().build()
                """
            ).strip(),
        ),
        (
            "Example",
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .update_legend_title(
                        'Example',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            "the given title is too long",
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .update_legend_title(
                        'the given title is too long',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
    ],
)
def test_render_options_codegen__render_legend_title(
    codegen: PlantUMLRenderOptionsCodegen,
    legend_title: str | None,
    expected_result: str,
):
    config = PlantUMLRenderOptions(legend_title=legend_title)

    result = codegen.generate(config)

    assert result == expected_result


@pytest.mark.parametrize(
    ("show_person_sprite", "expected_result"),
    [
        (
            None,
            textwrap.dedent(
                """
                plantuml_render_options = PlantUMLRenderOptionsBuilder().build()
                """
            ).strip(),
        ),
        (
            ShowPersonSprite(alias="foo"),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_person_sprite(
                        'foo',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
        (
            ShowPersonSprite(
                alias="the given alias is too long",
            ),
            textwrap.dedent(
                """
                plantuml_render_options = (
                    PlantUMLRenderOptionsBuilder()
                    .show_person_sprite(
                        'the given alias is too long',
                    )
                    .build()
                )
                """
            ).strip(),
        ),
    ],
)
def test_render_options_codegen__render_show_person_sprite(
    codegen: PlantUMLRenderOptionsCodegen,
    show_person_sprite: ShowPersonSprite | None,
    expected_result: str,
):
    config = PlantUMLRenderOptions(show_person_sprite=show_person_sprite)

    result = codegen.generate(config)

    assert result == expected_result


def test__tag_to_call__unknown_tag_type(
    codegen: PlantUMLRenderOptionsCodegen,
):
    tag = object()
    expected_error = f"Unsupported tag type: {type(tag)!r}"

    with pytest.raises(TypeError, match=expected_error):
        codegen._tag_to_call(tag)


def test__tag_to_call__rel_tag(
    codegen: PlantUMLRenderOptionsCodegen,
):
    tag = RelTag(
        text_color="#073642",
        line_color="#586E75",
        line_style="DashedLine",
        line_thickness="2",
        technology="Python / FastAPI",
        tag_stereo="SERVICE",
        legend_text="Core backend service",
        legend_sprite="server",
        sprite="cloud",
    )
    config = PlantUMLRenderOptions(tags=[tag])
    expected_result = textwrap.dedent(
        """
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .add_rel_tag(
                tag_stereo='SERVICE',
                text_color='#073642',
                line_color='#586E75',
                sprite='cloud',
                technology='Python / FastAPI',
                legend_text='Core backend service',
                legend_sprite='server',
                line_style='DashedLine',
                line_thickness='2',
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected_result


def test__tag_to_call__element_tag(
    codegen: PlantUMLRenderOptionsCodegen,
):
    tag = ContainerTag(
        tag_stereo="SERVICE",
        legend_text="Core backend service",
        legend_sprite="server",
        sprite="cloud",
        bg_color="#FDF6E3",
        font_color="#073642",
        border_color="#586E75",
        shadowing="true",
        shape="RoundedBoxShape",
        technology="Python / FastAPI",
        border_style="DashedLine",
        border_thickness="2",
    )
    config = PlantUMLRenderOptions(tags=[tag])
    expected_result = textwrap.dedent(
        """
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .add_container_tag(
                tag_stereo='SERVICE',
                bg_color='#FDF6E3',
                font_color='#073642',
                border_color='#586E75',
                shadowing='true',
                shape='RoundedBoxShape',
                sprite='cloud',
                technology='Python / FastAPI',
                legend_text='Core backend service',
                legend_sprite='server',
                border_style='DashedLine',
                border_thickness='2',
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected_result


def test__style_to_call__unknown_style_type(
    codegen: PlantUMLRenderOptionsCodegen,
):
    style = object()
    expected_error = f"Unsupported style type: {type(style)!r}"

    with pytest.raises(TypeError, match=expected_error):
        codegen._style_to_call(style)


def test__style_to_call__boundary(
    codegen: PlantUMLRenderOptionsCodegen,
):
    style = BoundaryStyle(
        element_name="Boundary",
        type_="System",
        bg_color="#ffffff",
        font_color="#000000",
        border_color="#333333",
        shadowing="true",
        shape="RoundedBoxShape",
        sprite="user",
        technology="Python",
        legend_text="User Service",
        legend_sprite="user_icon",
        border_style="DashedLine",
        border_thickness="2",
    )
    config = PlantUMLRenderOptions(styles=[style])
    expected_result = textwrap.dedent(
        """
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .update_boundary_style(
                element_name='Boundary',
                bg_color='#ffffff',
                font_color='#000000',
                border_color='#333333',
                shadowing='true',
                shape='RoundedBoxShape',
                type_='System',
                sprite='user',
                technology='Python',
                legend_text='User Service',
                legend_sprite='user_icon',
                border_style='DashedLine',
                border_thickness='2',
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected_result


@pytest.mark.parametrize(
    ("kwargs", "expected_method"),
    [
        ({"hide_stereotype": True}, "hide_stereotype"),
        ({"hide_person_sprite": True}, "hide_person_sprite"),
        ({"show_person_portrait": True}, "show_person_portrait"),
        ({"show_person_outline": True}, "show_person_outline"),
        ({"without_property_header": True}, "without_property_header"),
    ],
)
def test__render_bool_calls(
    codegen: PlantUMLRenderOptionsCodegen,
    kwargs: dict[str, Any],
    expected_method: str,
):
    config = PlantUMLRenderOptions(**kwargs)
    expected_result = textwrap.dedent(
        f"""
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .{expected_method}()
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected_result


def test__render_includes(
    codegen: PlantUMLRenderOptionsCodegen,
):
    config = PlantUMLRenderOptions(includes=["!foo", "!bar"])
    expected_result = textwrap.dedent(
        """
        plantuml_render_options = (
            PlantUMLRenderOptionsBuilder()
            .add_includes(
                '!foo',
                '!bar',
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected_result

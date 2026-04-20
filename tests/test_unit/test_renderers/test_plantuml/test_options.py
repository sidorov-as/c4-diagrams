from dataclasses import asdict
from typing import Any

import pytest

from c4.renderers.plantuml import PlantUMLRenderOptionsBuilder
from c4.renderers.plantuml.options import (
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
    PlantUMLRenderOptions,
    RelStyle,
    SetSketchStyle,
    ShowFloatingLegend,
    ShowLegend,
    ShowPersonSprite,
    SystemBoundaryStyle,
    SystemTag,
)


def test_render_options_default():
    options_builder = PlantUMLRenderOptionsBuilder()
    expected_render_options = PlantUMLRenderOptions(
        layout=None,
        layout_with_legend=False,
        layout_as_sketch=False,
        set_sketch_style=None,
        show_legend=None,
        show_floating_legend=None,
        hide_stereotype=False,
        hide_person_sprite=False,
        show_person_sprite=None,
        show_person_portrait=False,
        show_person_outline=False,
        without_property_header=False,
        legend_title=None,
        tags=[],
        styles=[],
        includes=[],
    )

    render_options = options_builder.build()

    assert render_options == expected_render_options


@pytest.fixture()
def options_builder() -> PlantUMLRenderOptionsBuilder:
    return PlantUMLRenderOptionsBuilder()


@pytest.mark.parametrize(
    ("method_name", "expected_layout", "with_legend"),
    [
        ("layout_top_down", DiagramLayout.LAYOUT_TOP_DOWN, False),
        ("layout_top_down", DiagramLayout.LAYOUT_TOP_DOWN, True),
        ("layout_left_right", DiagramLayout.LAYOUT_LEFT_RIGHT, False),
        ("layout_left_right", DiagramLayout.LAYOUT_LEFT_RIGHT, True),
        ("layout_landscape", DiagramLayout.LAYOUT_LANDSCAPE, False),
        ("layout_landscape", DiagramLayout.LAYOUT_LANDSCAPE, True),
    ],
)
def test_render_options_layout_methods_set_layout_and_legend(
    options_builder: PlantUMLRenderOptionsBuilder,
    method_name: str,
    expected_layout: DiagramLayout,
    with_legend: bool,
) -> None:
    method = getattr(options_builder, method_name)

    result = method(with_legend=with_legend)

    assert result is options_builder
    cfg = options_builder.build()
    assert cfg.layout == expected_layout
    assert cfg.layout_with_legend is with_legend


@pytest.mark.parametrize(
    ("call_chain", "expected"),
    [
        (("layout_with_legend",), True),
        (("layout_with_legend", "layout_with_legend"), True),
    ],
)
def test_render_options_layout_with_legend_sets_flag(
    options_builder: PlantUMLRenderOptionsBuilder,
    call_chain: tuple[str, ...],
    expected: bool,
) -> None:
    for name in call_chain:
        getattr(options_builder, name)()

    cfg = options_builder.build()
    assert cfg.layout_with_legend is expected


@pytest.mark.parametrize(
    ("call_chain", "expected"),
    [
        (("layout_as_sketch",), True),
        (("layout_as_sketch", "layout_as_sketch"), True),
    ],
)
def test_render_options_layout_as_sketch_sets_flag(
    options_builder: PlantUMLRenderOptionsBuilder,
    call_chain: tuple[str, ...],
    expected: bool,
) -> None:
    for name in call_chain:
        getattr(options_builder, name)()

    cfg = options_builder.build()
    assert cfg.layout_as_sketch is expected


@pytest.mark.parametrize(
    ("call_chain", "expected"),
    [
        (("without_property_header",), True),
        (("without_property_header", "without_property_header"), True),
    ],
)
def test_render_options_without_property_header_sets_flag(
    options_builder: PlantUMLRenderOptionsBuilder,
    call_chain: tuple[str, ...],
    expected: bool,
) -> None:
    for name in call_chain:
        getattr(options_builder, name)()

    cfg = options_builder.build()
    assert cfg.without_property_header is expected


@pytest.mark.parametrize(
    ("call_chain", "expected"),
    [
        (("hide_stereotype",), True),
        (("hide_stereotype", "hide_stereotype"), True),
    ],
)
def test_render_options_hide_stereotype_sets_flag(
    options_builder: PlantUMLRenderOptionsBuilder,
    call_chain: tuple[str, ...],
    expected: bool,
) -> None:
    for name in call_chain:
        getattr(options_builder, name)()

    cfg = options_builder.build()
    assert cfg.hide_stereotype is expected


@pytest.mark.parametrize(
    ("call_chain", "expected"),
    [
        (("hide_person_sprite",), True),
        (("hide_person_sprite", "hide_person_sprite"), True),
    ],
)
def test_render_options_hide_person_sprite_sets_flag(
    options_builder: PlantUMLRenderOptionsBuilder,
    call_chain: tuple[str, ...],
    expected: bool,
) -> None:
    for name in call_chain:
        getattr(options_builder, name)()

    cfg = options_builder.build()
    assert cfg.hide_person_sprite is expected


@pytest.mark.parametrize(
    ("call_chain", "expected"),
    [
        (("show_person_portrait",), True),
        (("show_person_portrait", "show_person_portrait"), True),
    ],
)
def test_render_options_show_person_portrait_sets_flag(
    call_chain: tuple[str, ...],
    expected: bool,
) -> None:
    options_builder = PlantUMLRenderOptionsBuilder()

    for name in call_chain:
        getattr(options_builder, name)()

    cfg = options_builder.build()
    assert cfg.show_person_portrait is expected


@pytest.mark.parametrize(
    ("call_chain", "expected"),
    [
        (("show_person_outline",), True),
        (("show_person_outline", "show_person_outline"), True),
    ],
)
def test_render_options_show_person_outline_sets_flag(
    options_builder: PlantUMLRenderOptionsBuilder,
    call_chain: tuple[str, ...],
    expected: bool,
) -> None:
    for name in call_chain:
        getattr(options_builder, name)()

    cfg = options_builder.build()
    assert cfg.show_person_outline is expected


@pytest.mark.parametrize(
    ("new_title",),
    [
        ("Legend",),
        ("",),
    ],
)
def test_render_options_update_legend_title_sets_value(
    options_builder: PlantUMLRenderOptionsBuilder,
    new_title: str,
) -> None:
    result = options_builder.update_legend_title(new_title)

    cfg = options_builder.build()
    assert result is options_builder
    assert cfg.legend_title == new_title


@pytest.mark.parametrize(
    ("args", "expected_kwargs"),
    [
        ({}, {}),
        ({"bg_color": "white"}, {"bg_color": "white"}),
        ({"font_color": "black"}, {"font_color": "black"}),
        (
            {"bg_color": "w", "font_name": "Arial"},
            {"bg_color": "w", "font_name": "Arial"},
        ),
        (
            {
                "bg_color": "w",
                "font_color": "b",
                "warning_color": "y",
                "font_name": "Arial",
                "footer_warning": "warn",
                "footer_text": "text",
            },
            {
                "bg_color": "w",
                "font_color": "b",
                "warning_color": "y",
                "font_name": "Arial",
                "footer_warning": "warn",
                "footer_text": "text",
            },
        ),
    ],
)
def test_render_options_set_sketch_style(
    options_builder: PlantUMLRenderOptionsBuilder,
    args: dict[str, Any],
    expected_kwargs: dict[str, Any],
) -> None:
    expected_sketch_style = {
        "bg_color": None,
        "font_color": None,
        "warning_color": None,
        "font_name": None,
        "footer_warning": None,
        "footer_text": None,
        **expected_kwargs,
    }

    result = options_builder.set_sketch_style(**args)

    cfg = options_builder.build()
    assert result is options_builder
    assert cfg.set_sketch_style is not None
    assert isinstance(cfg.set_sketch_style, SetSketchStyle)
    assert asdict(cfg.set_sketch_style) == expected_sketch_style


@pytest.mark.parametrize(
    ("args", "expected_kwargs"),
    [
        ({}, {}),
        ({"hide_stereotype": False}, {"hide_stereotype": False}),
        ({"details": "Normal"}, {"details": "Normal"}),
        (
            {"hide_stereotype": False, "details": "None"},
            {"hide_stereotype": False, "details": "None"},
        ),
    ],
)
def test_render_options_show_legend(
    options_builder: PlantUMLRenderOptionsBuilder,
    args: dict[str, Any],
    expected_kwargs: dict[str, Any],
) -> None:
    expected_show_legend = {
        "details": None,
        "hide_stereotype": None,
        **expected_kwargs,
    }

    result = options_builder.show_legend(**args)

    cfg = options_builder.build()
    assert result is options_builder
    assert cfg.show_legend is not None
    assert isinstance(cfg.show_legend, ShowLegend)
    assert asdict(cfg.show_legend) == expected_show_legend


@pytest.mark.parametrize(
    ("args", "expected_kwargs"),
    [
        ({}, {}),
        ({"alias": "L"}, {"alias": "L"}),
        ({"hide_stereotype": False}, {"hide_stereotype": False}),
        ({"details": "Normal"}, {"details": "Normal"}),
        (
            {"alias": "L", "hide_stereotype": False, "details": "None"},
            {"alias": "L", "hide_stereotype": False, "details": "None"},
        ),
    ],
)
def test_render_options_show_floating_legend(
    options_builder: PlantUMLRenderOptionsBuilder,
    args: dict[str, Any],
    expected_kwargs: dict[str, Any],
) -> None:
    expected_show_floating_legend = {
        "alias": None,
        "details": None,
        "hide_stereotype": None,
        **expected_kwargs,
    }

    result = options_builder.show_floating_legend(**args)

    cfg = options_builder.build()
    assert result is options_builder
    assert cfg.show_floating_legend is not None
    assert isinstance(cfg.show_floating_legend, ShowFloatingLegend)
    assert asdict(cfg.show_floating_legend) == expected_show_floating_legend


@pytest.mark.parametrize(
    ("alias", "expected_kwargs"),
    [
        (None, {}),
        ("p", {"alias": "p"}),
    ],
)
def test_render_options_show_person_sprite(
    options_builder: PlantUMLRenderOptionsBuilder,
    alias: str | None,
    expected_kwargs: dict[str, Any],
) -> None:
    expected_show_person_sprite = {
        "alias": None,
        **expected_kwargs,
    }

    result = options_builder.show_person_sprite(alias=alias)

    cfg = options_builder.build()
    assert result is options_builder
    assert cfg.show_person_sprite is not None
    assert isinstance(cfg.show_person_sprite, ShowPersonSprite)
    assert asdict(cfg.show_person_sprite) == expected_show_person_sprite


@pytest.mark.parametrize(
    ("method_name", "tag_cls", "expected_kwargs"),
    [
        (
            "add_element_tag",
            ElementTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "technology": "tech",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_boundary_tag",
            BoundaryTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "technology": "tech",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_component_tag",
            ComponentTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "technology": "tech",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_external_component_tag",
            ExternalComponentTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "technology": "tech",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_container_tag",
            ContainerTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "technology": "tech",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_external_container_tag",
            ExternalContainerTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "technology": "tech",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_node_tag",
            NodeTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "technology": "tech",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_person_tag",
            PersonTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "type_": "person",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_external_person_tag",
            ExternalPersonTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "type_": "person",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_system_tag",
            SystemTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "type_": "person",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "add_external_system_tag",
            ExternalSystemTag,
            {
                "tag_stereo": "t",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "type_": "person",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
    ],
)
def test_render_options_add_tag(
    options_builder: PlantUMLRenderOptionsBuilder,
    method_name: str,
    tag_cls: type,
    expected_kwargs: dict[str, Any],
) -> None:
    method = getattr(options_builder, method_name)

    result = method(**expected_kwargs)

    cfg = options_builder.build()
    assert result is options_builder
    assert len(cfg.tags) == 1
    assert isinstance(cfg.tags[0], tag_cls)
    assert asdict(cfg.tags[0]) == expected_kwargs


def test_render_options_add_includes(
    options_builder: PlantUMLRenderOptionsBuilder,
) -> None:
    result = options_builder.add_includes("!first", "!second")

    cfg = options_builder.build()
    assert result is options_builder
    assert cfg.includes == ["!first", "!second"]


@pytest.mark.parametrize(
    ("method_name", "style_cls", "expected_kwargs"),
    [
        (
            "update_element_style",
            ElementStyle,
            {
                "element_name": "e",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "sprite": "sp",
                "technology": "t",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "SolidLine",
                "border_thickness": "2",
            },
        ),
        (
            "update_boundary_style",
            BoundaryStyle,
            {
                "element_name": "e",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "type_": "System",
                "sprite": "sp",
                "technology": "t",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "BoldLine",
                "border_thickness": "2",
            },
        ),
        (
            "update_container_boundary_style",
            ContainerBoundaryStyle,
            {
                "element_name": "e",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "type_": "Container",
                "sprite": "sp",
                "technology": "t",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DottedLine",
                "border_thickness": "2",
            },
        ),
        (
            "update_system_boundary_style",
            SystemBoundaryStyle,
            {
                "element_name": "e",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "type_": "System",
                "sprite": "sp",
                "technology": "t",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "update_enterprise_boundary_style",
            EnterpriseBoundaryStyle,
            {
                "element_name": "e",
                "bg_color": "bg",
                "font_color": "fc",
                "border_color": "bc",
                "shadowing": "s",
                "shape": "RoundedBoxShape",
                "type_": "System",
                "sprite": "sp",
                "technology": "t",
                "legend_text": "lt",
                "legend_sprite": "ls",
                "border_style": "DashedLine",
                "border_thickness": "2",
            },
        ),
        (
            "update_rel_style",
            RelStyle,
            {"text_color": "tc", "line_color": "lc"},
        ),
    ],
)
def test_render_options_update_style(
    options_builder: PlantUMLRenderOptionsBuilder,
    method_name: str,
    style_cls: type,
    expected_kwargs: dict[str, Any],
) -> None:
    method = getattr(options_builder, method_name)

    result = method(**expected_kwargs)

    cfg = options_builder.build()
    assert result is options_builder
    assert len(cfg.styles) == 1
    assert isinstance(cfg.styles[0], style_cls)
    assert asdict(cfg.styles[0]) == expected_kwargs


def test_render_options_declare_and_build() -> None:
    options_builder = PlantUMLRenderOptionsBuilder()

    (
        options_builder
        .add_element_tag(tag_stereo="a")
        .add_rel_tag(tag_stereo="r")
        .update_rel_style(text_color="t", line_color="l")
        .layout_left_right(with_legend=True)
    )

    cfg = options_builder.build()
    assert isinstance(cfg, PlantUMLRenderOptions)
    assert cfg.layout == DiagramLayout.LAYOUT_LEFT_RIGHT
    assert cfg.layout_with_legend is True
    assert [t.tag_stereo for t in cfg.tags] == ["a", "r"]
    assert len(cfg.styles) == 1
    assert isinstance(cfg.styles[0], RelStyle)

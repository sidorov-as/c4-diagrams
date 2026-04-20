import pytest

from c4.renderers.mermaid import MermaidRenderOptionsBuilder
from c4.renderers.mermaid.options import (
    ElementStyle,
    MermaidRenderOptions,
    RelStyle,
    UpdateLayoutConfig,
)


def test_render_options_default() -> None:
    options_builder = MermaidRenderOptionsBuilder()
    expected_render_options = MermaidRenderOptions(
        styles=[],
        update_layout_config=None,
    )

    render_options = options_builder.build()

    assert render_options == expected_render_options


@pytest.fixture()
def options_builder() -> MermaidRenderOptionsBuilder:
    return MermaidRenderOptionsBuilder()


def test_render_options_update_element_style_adds_style(
    options_builder: MermaidRenderOptionsBuilder,
) -> None:
    result = options_builder.update_element_style("api")

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.styles == [
        ElementStyle(
            element="api",
            bg_color=None,
            font_color=None,
            border_color=None,
        )
    ]


@pytest.mark.parametrize(
    ("kwargs", "expected_style"),
    [
        (
            {"element": "api"},
            ElementStyle(
                element="api",
                bg_color=None,
                font_color=None,
                border_color=None,
            ),
        ),
        (
            {"element": "api", "bg_color": "#ffffff"},
            ElementStyle(
                element="api",
                bg_color="#ffffff",
                font_color=None,
                border_color=None,
            ),
        ),
        (
            {"element": "api", "font_color": "#000000"},
            ElementStyle(
                element="api",
                bg_color=None,
                font_color="#000000",
                border_color=None,
            ),
        ),
        (
            {"element": "api", "border_color": "#cccccc"},
            ElementStyle(
                element="api",
                bg_color=None,
                font_color=None,
                border_color="#cccccc",
            ),
        ),
        (
            {
                "element": "api",
                "bg_color": "#ffffff",
                "font_color": "#000000",
                "border_color": "#cccccc",
            },
            ElementStyle(
                element="api",
                bg_color="#ffffff",
                font_color="#000000",
                border_color="#cccccc",
            ),
        ),
    ],
)
def test_render_options_update_element_style_sets_values(
    options_builder: MermaidRenderOptionsBuilder,
    kwargs: dict[str, str],
    expected_style: ElementStyle,
) -> None:
    result = options_builder.update_element_style(**kwargs)

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.styles == [expected_style]


def test_render_options_update_rel_style_adds_style(
    options_builder: MermaidRenderOptionsBuilder,
) -> None:
    result = options_builder.update_rel_style("api", "db")

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.styles == [
        RelStyle(
            from_element="api",
            to_element="db",
            text_color=None,
            line_color=None,
            offset_x=None,
            offset_y=None,
        )
    ]


@pytest.mark.parametrize(
    ("kwargs", "expected_style"),
    [
        (
            {"from_element": "api", "to_element": "db"},
            RelStyle(
                from_element="api",
                to_element="db",
                text_color=None,
                line_color=None,
                offset_x=None,
                offset_y=None,
            ),
        ),
        (
            {
                "from_element": "api",
                "to_element": "db",
                "text_color": "#111111",
            },
            RelStyle(
                from_element="api",
                to_element="db",
                text_color="#111111",
                line_color=None,
                offset_x=None,
                offset_y=None,
            ),
        ),
        (
            {
                "from_element": "api",
                "to_element": "db",
                "line_color": "#222222",
            },
            RelStyle(
                from_element="api",
                to_element="db",
                text_color=None,
                line_color="#222222",
                offset_x=None,
                offset_y=None,
            ),
        ),
        (
            {
                "from_element": "api",
                "to_element": "db",
                "offset_x": 10,
            },
            RelStyle(
                from_element="api",
                to_element="db",
                text_color=None,
                line_color=None,
                offset_x=10,
                offset_y=None,
            ),
        ),
        (
            {
                "from_element": "api",
                "to_element": "db",
                "offset_y": -5,
            },
            RelStyle(
                from_element="api",
                to_element="db",
                text_color=None,
                line_color=None,
                offset_x=None,
                offset_y=-5,
            ),
        ),
        (
            {
                "from_element": "api",
                "to_element": "db",
                "text_color": "#111111",
                "line_color": "#222222",
                "offset_x": 10,
                "offset_y": -5,
            },
            RelStyle(
                from_element="api",
                to_element="db",
                text_color="#111111",
                line_color="#222222",
                offset_x=10,
                offset_y=-5,
            ),
        ),
    ],
)
def test_render_options_update_rel_style_sets_values(
    options_builder: MermaidRenderOptionsBuilder,
    kwargs: dict[str, str | int],
    expected_style: RelStyle,
) -> None:
    result = options_builder.update_rel_style(**kwargs)

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.styles == [expected_style]


@pytest.mark.parametrize(
    ("kwargs", "expected_layout_config"),
    [
        (
            {},
            UpdateLayoutConfig(
                c4_shape_in_row=None,
                c4_boundary_in_row=None,
            ),
        ),
        (
            {"c4_shape_in_row": 3},
            UpdateLayoutConfig(
                c4_shape_in_row=3,
                c4_boundary_in_row=None,
            ),
        ),
        (
            {"c4_boundary_in_row": 1},
            UpdateLayoutConfig(
                c4_shape_in_row=None,
                c4_boundary_in_row=1,
            ),
        ),
        (
            {"c4_shape_in_row": 3, "c4_boundary_in_row": 1},
            UpdateLayoutConfig(
                c4_shape_in_row=3,
                c4_boundary_in_row=1,
            ),
        ),
    ],
)
def test_render_options_update_layout_config_sets_values(
    options_builder: MermaidRenderOptionsBuilder,
    kwargs: dict[str, int],
    expected_layout_config: UpdateLayoutConfig,
) -> None:
    result = options_builder.update_layout_config(**kwargs)

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.update_layout_config == expected_layout_config


def test_render_options_builder_accumulates_styles_in_order(
    options_builder: MermaidRenderOptionsBuilder,
) -> None:
    (
        options_builder.update_element_style(
            "api", bg_color="#ffffff"
        ).update_rel_style("api", "db", line_color="#222222")
    )

    cfg = options_builder.build()

    assert cfg.styles == [
        ElementStyle(
            element="api",
            bg_color="#ffffff",
            font_color=None,
            border_color=None,
        ),
        RelStyle(
            from_element="api",
            to_element="db",
            text_color=None,
            line_color="#222222",
            offset_x=None,
            offset_y=None,
        ),
    ]


def test_render_options_update_layout_config_overrides(
    options_builder: MermaidRenderOptionsBuilder,
) -> None:
    (
        options_builder.update_layout_config(
            c4_shape_in_row=3
        ).update_layout_config(c4_shape_in_row=5, c4_boundary_in_row=2)
    )

    cfg = options_builder.build()

    assert cfg.update_layout_config == UpdateLayoutConfig(
        c4_shape_in_row=5,
        c4_boundary_in_row=2,
    )

import textwrap

import pytest
from pytest_mock import MockerFixture

import c4.renderers.mermaid.renderer as renderer_module
from c4.renderers.mermaid.options import (
    BaseStyle,
    ElementStyle,
    MermaidRenderOptions,
    RelStyle,
    UpdateLayoutConfig,
)
from c4.renderers.mermaid.renderer import MermaidRenderOptionsRenderer


@pytest.mark.parametrize(
    ("styles", "rendered_values", "expected"),
    [
        (
            [
                ElementStyle(element="api"),
            ],
            ["ELEMENT_STYLE_1"],
            "ELEMENT_STYLE_1",
        ),
        (
            [
                ElementStyle(element="api"),
                ElementStyle(element="db"),
            ],
            ["ELEMENT_STYLE_1", "ELEMENT_STYLE_2"],
            "ELEMENT_STYLE_1\nELEMENT_STYLE_2",
        ),
    ],
)
def test_mermaid_render_options_renderer__render_footer__renders_element_styles_in_order(
    mocker: MockerFixture,
    styles: list[ElementStyle],
    rendered_values: list[str],
    expected: str,
) -> None:
    options = MermaidRenderOptions(styles=styles)
    renderer = MermaidRenderOptionsRenderer(render_options=options)
    macros = [
        mocker.Mock(render=mocker.Mock(return_value=value))
        for value in rendered_values
    ]
    update_element_style_macro = mocker.patch.object(
        renderer_module,
        "UpdateElementStyleMermaidMacro",
        side_effect=macros,
    )

    result = renderer.render_footer()

    assert result == expected
    assert update_element_style_macro.call_args_list == [
        mocker.call(style) for style in styles
    ]
    assert all(macro.render.call_count == 1 for macro in macros)


@pytest.mark.parametrize(
    ("styles", "rendered_values", "expected"),
    [
        (
            [
                RelStyle(from_element="api", to_element="db"),
            ],
            ["REL_STYLE_1"],
            "REL_STYLE_1",
        ),
        (
            [
                RelStyle(from_element="api", to_element="db"),
                RelStyle(from_element="web", to_element="api"),
            ],
            ["REL_STYLE_1", "REL_STYLE_2"],
            "REL_STYLE_1\nREL_STYLE_2",
        ),
    ],
)
def test_mermaid_render_options_renderer__render_footer__renders_rel_styles_in_order(
    mocker: MockerFixture,
    styles: list[RelStyle],
    rendered_values: list[str],
    expected: str,
) -> None:
    options = MermaidRenderOptions(styles=styles)
    renderer = MermaidRenderOptionsRenderer(render_options=options)
    macros = [
        mocker.Mock(render=mocker.Mock(return_value=value))
        for value in rendered_values
    ]
    update_rel_style_macro = mocker.patch.object(
        renderer_module,
        "UpdateRelStyleMermaidMacro",
        side_effect=macros,
    )

    result = renderer.render_footer()

    assert result == expected
    assert update_rel_style_macro.call_args_list == [
        mocker.call(style) for style in styles
    ]
    assert all(macro.render.call_count == 1 for macro in macros)


def test_mermaid_render_options_renderer__render_footer__empty() -> None:
    renderer = MermaidRenderOptionsRenderer()

    result = renderer.render_footer()

    assert result == ""


def test_mermaid_render_options_renderer__render_footer__complex() -> None:
    element_style = ElementStyle(
        element="api",
        bg_color="#ffffff",
        font_color="#000000",
        border_color="#cccccc",
    )
    rel_style = RelStyle(
        from_element="user",
        to_element="system",
        text_color="#000000",
        line_color="#333333",
    )
    layout_config = UpdateLayoutConfig(
        c4_shape_in_row=3,
        c4_boundary_in_row=2,
    )
    options = MermaidRenderOptions(
        styles=[element_style, rel_style],
        update_layout_config=layout_config,
    )
    renderer = MermaidRenderOptionsRenderer(render_options=options)
    expected_result = textwrap.dedent(
        """
        UpdateElementStyle(api, $fontColor="#000000", $bgColor="#ffffff", $borderColor="#cccccc")
        UpdateRelStyle(user, system, $textColor="#000000", $lineColor="#333333")
        UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
        """
    )

    result = renderer.render_footer()

    assert result.strip() == expected_result.strip()


def test_mermaid_render_options_renderer__render_footer__styles() -> None:
    element_style = ElementStyle(
        element="api",
        bg_color="#ffffff",
        font_color="#000000",
        border_color="#cccccc",
    )
    rel_style = RelStyle(
        from_element="user",
        to_element="system",
        text_color="#000000",
        line_color="#333333",
    )
    options = MermaidRenderOptions(
        styles=[element_style, rel_style],
    )
    renderer = MermaidRenderOptionsRenderer(render_options=options)
    expected_result = textwrap.dedent(
        """
        UpdateElementStyle(api, $fontColor="#000000", $bgColor="#ffffff", $borderColor="#cccccc")
        UpdateRelStyle(user, system, $textColor="#000000", $lineColor="#333333")
        """
    )

    result = renderer.render_footer()

    assert result.strip() == expected_result.strip()


def test_mermaid_render_options_renderer__render_footer__layout() -> None:
    layout_config = UpdateLayoutConfig(
        c4_shape_in_row=3,
        c4_boundary_in_row=2,
    )
    options = MermaidRenderOptions(
        styles=[],
        update_layout_config=layout_config,
    )
    renderer = MermaidRenderOptionsRenderer(render_options=options)
    expected_result = textwrap.dedent(
        """
        UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="2")
        """
    )

    result = renderer.render_footer()

    assert result.strip() == expected_result.strip()


def test_mermaid_render_options_renderer__render_footer__unsupported_style() -> (
    None
):
    class UnsupportedStyle(BaseStyle):
        pass

    options = MermaidRenderOptions(styles=[UnsupportedStyle()])
    renderer = MermaidRenderOptionsRenderer(render_options=options)

    with pytest.raises(
        TypeError,
        match="No macro registered for style type UnsupportedStyle",
    ):
        renderer.render_footer()

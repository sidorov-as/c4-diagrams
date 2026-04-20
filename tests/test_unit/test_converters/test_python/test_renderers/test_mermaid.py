import textwrap
from typing import Any

import pytest

from c4.converters.python.renderers.mermaid import MermaidRenderOptionsCodegen
from c4.renderers.mermaid.options import (
    ElementStyle,
    MermaidRenderOptions,
    RelStyle,
    UpdateLayoutConfig,
)


@pytest.fixture()
def codegen() -> MermaidRenderOptionsCodegen:
    return MermaidRenderOptionsCodegen()


def test_render_options_codegen__generate_single_line_for_single_call(
    codegen: MermaidRenderOptionsCodegen,
):
    config = MermaidRenderOptions(
        update_layout_config=UpdateLayoutConfig(c4_shape_in_row=4)
    )
    expected_result = textwrap.dedent(
        """
        mermaid_render_options = (
            MermaidRenderOptionsBuilder()
            .update_layout_config(
                c4_shape_in_row=4,
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected_result


def test_render_options_codegen__filtered_kwargs_drops_values_unless_keep():
    kwargs = {"a": "", "b": 1, "c": None, "d": False}
    expected = {"b": 1, "d": False}

    result = MermaidRenderOptionsCodegen._filtered_kwargs(
        kwargs,
        drop_values={"", None},
        keep=set(),
    )

    assert result == expected


@pytest.mark.parametrize(
    ("kwargs", "drop_values", "keep", "expected"),
    [
        ({"a": "", "b": 1}, {"", None}, set(), {"b": 1}),
        (
            {"element": "", "b": 1},
            {"", None},
            {"element"},
            {"element": "", "b": 1},
        ),
        ({"a": None, "b": "x"}, {"", None}, set(), {"b": "x"}),
    ],
)
def test_render_options_codegen__filtered_kwargs_parametrized(
    kwargs: dict[str, Any],
    drop_values: set[Any],
    keep: set[str],
    expected: dict[str, Any],
):
    result = MermaidRenderOptionsCodegen._filtered_kwargs(
        kwargs,
        drop_values=drop_values,
        keep=keep,
    )

    assert result == expected


def test_render_options_codegen__style_to_call_raises_type_error(
    codegen: MermaidRenderOptionsCodegen,
):
    obj = object()
    expected_error = rf"Unsupported style type: {type(obj)!r}"

    with pytest.raises(TypeError, match=expected_error):
        codegen._style_to_call(obj)  # type: ignore[arg-type]


def test_render_options_codegen__generate_renders_element_and_rel_styles(
    codegen: MermaidRenderOptionsCodegen,
):
    config = MermaidRenderOptions(
        styles=[
            ElementStyle(
                element="customer",
                font_color="red",
                bg_color="grey",
                border_color="red",
            ),
            RelStyle(
                from_element="customer",
                to_element="backend",
                line_color="blue",
                text_color="black",
            ),
        ]
    )
    expected = textwrap.dedent(
        """
        mermaid_render_options = (
            MermaidRenderOptionsBuilder()
            .update_element_style(
                element='customer',
                bg_color='grey',
                font_color='red',
                border_color='red',
            )
            .update_rel_style(
                from_element='customer',
                to_element='backend',
                text_color='black',
                line_color='blue',
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected


def test_render_options_codegen__generate_renders_styles_and_layout_config(
    codegen: MermaidRenderOptionsCodegen,
):
    config = MermaidRenderOptions(
        styles=[
            ElementStyle(
                element="customer",
                font_color="red",
            )
        ],
        update_layout_config=UpdateLayoutConfig(
            c4_shape_in_row=4,
            c4_boundary_in_row=2,
        ),
    )
    expected = textwrap.dedent(
        """
        mermaid_render_options = (
            MermaidRenderOptionsBuilder()
            .update_element_style(
                element='customer',
                font_color='red',
            )
            .update_layout_config(
                c4_shape_in_row=4,
                c4_boundary_in_row=2,
            )
            .build()
        )
        """
    ).strip()

    result = codegen.generate(config)

    assert result == expected


def test_render_options_codegen__render_update_layout_config_skips_empty_values(
    codegen: MermaidRenderOptionsCodegen,
):
    config = MermaidRenderOptions(
        update_layout_config=UpdateLayoutConfig(
            c4_shape_in_row=4,
            c4_boundary_in_row=None,
        )
    )

    result = codegen._render_update_layout_config(config)

    assert result == [
        ".update_layout_config(c4_shape_in_row=4)",
    ]


def test_render_options_codegen__render_build(
    codegen: MermaidRenderOptionsCodegen,
):
    result = codegen._render_build()

    assert result == [".build()"]

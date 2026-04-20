from c4.converters.json.schemas.renderers.mermaid import (
    MermaidElementStyleSchema,
    MermaidRelStyleSchema,
    MermaidRenderOptionsSchema,
    UpdateLayoutConfigSchema,
)
from c4.renderers import MermaidRenderOptions
from c4.renderers.mermaid.options import (
    ElementStyle,
    RelStyle,
    UpdateLayoutConfig,
)


def test_mermaid_render_options_schema__to_render_options():
    schema = MermaidRenderOptionsSchema(
        update_layout_config=UpdateLayoutConfigSchema(
            c4_shape_in_row=2,
            c4_boundary_in_row=4,
        ),
        styles=[
            MermaidElementStyleSchema(
                type="ElementStyle",
                element="customer",
                bg_color="#e8f5e9",
                border_color="#66bb6a",
                font_color="#1b5e20",
            ),
            MermaidRelStyleSchema(
                type="RelStyle",
                from_element="customer",
                to_element="retail_platform",
                text_color="#e8f5e9",
                line_color="#66bb6a",
                offset_x=10,
                offset_y=20,
            ),
        ],
    )
    expected_result = MermaidRenderOptions(
        update_layout_config=UpdateLayoutConfig(
            c4_shape_in_row=2,
            c4_boundary_in_row=4,
        ),
        styles=[
            ElementStyle(
                element="customer",
                bg_color="#e8f5e9",
                font_color="#1b5e20",
                border_color="#66bb6a",
            ),
            RelStyle(
                from_element="customer",
                to_element="retail_platform",
                text_color="#e8f5e9",
                line_color="#66bb6a",
                offset_x=10,
                offset_y=20,
            ),
        ],
    )

    result = schema.to_render_options()

    assert result == expected_result

# Mermaid Styles and Options

The **Mermaid** backend supports several layout and styling options that control
diagram direction, legend visibility, and overall visual appearance.

See the [Mermaid documentation](https://mermaid.js.org/syntax/c4.html)
for additional information.

## Layout Options

Layout behavior is configured via the [`MermaidRenderOptionsBuilder`][c4.renderers.mermaid.options.MermaidRenderOptionsBuilder]
builder:

```python
from c4.renderers import MermaidRenderOptionsBuilder

render_options = (
    MermaidRenderOptionsBuilder()
    .update_layout_config(
        c4_shape_in_row=4,
        c4_boundary_in_row=2
    )
    .update_element_style(
        "customer",
        font_color="red",
        bg_color="grey",
        border_color="red",
    )
    .build()
)
```

You can pass `render_options` to [`MermaidRenderer`][c4.renderers.mermaid.renderer.MermaidRenderer].

See the [MermaidRenderOptionsBuilder reference][c4.renderers.mermaid.options.MermaidRenderOptionsBuilder] section for the complete list of
available methods and configuration options.

Layout configuration can also be set via [RenderOptions](../render-options.md).

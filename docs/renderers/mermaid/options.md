# Mermaid Options

The Mermaid backend supports layout and style options through
[`MermaidRenderOptionsBuilder`][c4.renderers.mermaid.options.MermaidRenderOptionsBuilder].

```python
from c4.renderers import MermaidRenderOptionsBuilder

render_options = (
    MermaidRenderOptionsBuilder()
    .update_layout_config(
        c4_shape_in_row=4,
        c4_boundary_in_row=2,
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

Pass the result to [`MermaidRenderer`][c4.renderers.mermaid.renderer.MermaidRenderer]
or through the shared [RenderOptions](../render-options.md) envelope.

Mermaid options are renderer options, not element extension data. Use
[`mermaid={...}`](extensions.md) only for Mermaid-specific element metadata.

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

## Unlabeled Relationships

C4-Mermaid rejects `Rel(a, b)` without a label. A relationship whose label is
`None` (for example `a >> b`) is therefore written with the placeholder
`uses`: `Rel(a, b, "uses")`. Change the text with `default_relationship_label`,
or pass `None` to write the relationship as it is stored:

```python
from c4.renderers import MermaidRenderOptionsBuilder

render_options = (
    MermaidRenderOptionsBuilder()
    .default_relationship_label("relates to")  # or None to turn it off
    .build()
)
```

An explicit empty label (`""`) is written as `Rel(a, b, "")`, not replaced.
The placeholder is added at render time; the relationship is not changed.

Mermaid options are renderer options, not element extension data. Use
[`mermaid={...}`](extensions.md) only for Mermaid-specific element metadata.

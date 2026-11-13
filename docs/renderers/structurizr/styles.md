# Structurizr Styles and Options

Structurizr styles are keyed by tag. This page covers workspace styles,
element-local styles, the style presets, the render options and the theme.

## Workspace styles

`workspace.styles` collects style rules that are written to the `styles` block
of the views:

- `styles.element(tag_or_element, **properties)` styles elements with a tag.
  Passing an element instead of a tag styles that element only.
- `styles.tag(tag, **properties)` is an alias of `element` for a tag.
- `styles.relationship(tag="Relationship", **properties)` styles relationships
  with a tag.

Properties are written in `snake_case` (`stroke_width`, `font_size`) and become
the Structurizr names. The allowed properties and values are listed in the
[Reference](reference.md#style-properties). Relationship styles accept the
relationship properties, and `border` is written as the Structurizr line
`style` (`solid`, `dashed`, `dotted`).

<!-- generated:start structurizr-calls-styles -->
| Python call | Generated DSL |
|---|---|
| <pre><code>workspace.styles.element("Staff", background="#455a64", color="#ffffff")</code></pre> | <pre><code>element "Staff" {&#10;  background #455a64&#10;  color #ffffff&#10;}</code></pre> |
| <pre><code>workspace.styles.tag("Storage", shape="Cylinder")</code></pre> | <pre><code>element "Storage" {&#10;  shape Cylinder&#10;}</code></pre> |
| <pre><code>workspace.styles.relationship("Async", border="Dashed", thickness=2)</code></pre> | <pre><code>relationship "Async" {&#10;  thickness 2&#10;  style dashed&#10;}</code></pre> |
<!-- generated:end structurizr-calls-styles -->

Style rules are written after the preset rules, so they override them.

## Element-local styles

An element can carry its own style: pass `style={...}` when creating it, or call
`element.style(**properties)`. The renderer adds a private tag
(`c4diagrams_style_<alias>`) to the element and one style rule for it, so the
rest of the workspace is unaffected. Unknown properties raise an error naming
the allowed ones.

```python
from c4.contrib.structurizr import Workspace

workspace = Workspace("Styles")

with workspace.model as model:
    customer = model.Person("Customer", style={"shape": "Person"})
    shop = model.SoftwareSystem("Shop")
    shop.style(background="#1168bd", color="#ffffff")
```

## Style presets

The renderer writes a default set of styles for the built-in tags. The preset is
chosen with [`StructurizrRenderOptions(style_preset=...)`][c4.contrib.structurizr.renderer.StructurizrRenderOptions]:

| Preset          | CLI value       | Result                                                            |
|-----------------|-----------------|-------------------------------------------------------------------|
| `"classic"`     | `classic`       | The classic blue C4 colors for people, systems, containers, components. Default. |
| `"new-c4-style"` | `new-c4-style` | Rounded boxes outlined in one blue accent color, thicker relationship lines. |
| `None`          | `none`          | No preset styles. Your own styles and element-local styles remain. |

The CLI flag is `c4 render --structurizr-style-preset {classic,new-c4-style,none}`.

## Render options

`StructurizrRenderOptions(auto_layout=AutoLayout(), style_preset="classic")` is
passed to the renderer, or set on a workspace with [`Workspace(render_options=...)`][c4.contrib.structurizr.Workspace]
or `workspace.render_options = ...`. Options on the workspace win over the
renderer's. `auto_layout=None` omits the `autoLayout` line.

<!-- generated:start structurizr-calls-options -->
| Python call | Generated DSL |
|---|---|
| <pre><code>renderer = StructurizrRenderer(&#10;    StructurizrRenderOptions(style_preset=None))</code></pre> | <pre><code>element "Staff" {&#10;  border Dotted&#10;}</code></pre> |
| <pre><code>renderer = StructurizrRenderer(&#10;    StructurizrRenderOptions(style_preset="new-c4-style"))</code></pre> | <pre><code>element "Element" {&#10;  shape RoundedBox&#10;  color #0773af</code></pre> |
| <pre><code>renderer = StructurizrRenderer(&#10;    StructurizrRenderOptions(&#10;        auto_layout=AutoLayout("TopBottom")))</code></pre> | <pre><code>autoLayout tb</code></pre> |
| <pre><code>workspace = Workspace("Demo", theme="https://example.com/theme.json")</code></pre> | <pre><code>theme "https://example.com/theme.json"</code></pre> |
<!-- generated:end structurizr-calls-options -->

```python
from c4.contrib.structurizr import AutoLayout, Workspace
from c4.contrib.structurizr.renderer import (
    StructurizrRenderer,
    StructurizrRenderOptions,
)

workspace = Workspace("Plain")
workspace.views.SystemLandscapeView(key="landscape")

renderer = StructurizrRenderer(
    StructurizrRenderOptions(
        style_preset=None,
        auto_layout=AutoLayout("TopBottom", rank_separation=100),
    )
)
print(renderer.render(workspace))
```

## Theme

`Workspace(theme=...)` takes a theme URL or a path accepted by the Structurizr
CLI and writes one `theme` line. It is optional and unset by default, so the
generated DSL needs no network access.

!!! warning "`theme=\"default\"` is deprecated"

    Earlier versions emitted `theme default`, which pointed at a remote theme
    that no longer exists and made `structurizr export` fail offline. The value
    `"default"` (in Python and in JSON) is now ignored and issues a
    `DeprecationWarning`. Omit the argument, or pass a custom theme.

Upstream: [styles](https://docs.structurizr.com/dsl/language),
[themes](https://docs.structurizr.com/dsl/cookbook/themes/) and
[element style properties](https://docs.structurizr.com/dsl/language).

# D2 Options

The D2 backend supports render options through
[`D2RenderOptions`](../../api_docs/d2/render-options/#c4.renderers.d2.options.D2RenderOptions) and
[`D2RenderOptionsBuilder`](../../api_docs/d2/render-options/#c4.renderers.d2.options.D2RenderOptionsBuilder).

```python
from c4 import SystemContextDiagram
from c4.renderers import D2RenderOptions, RenderOptions

options = D2RenderOptions(
    direction="down",
    layout="elk",
    theme=300,
    title_near="top-center",
    sequence_diagram=True,
    auto_number_relationships=True,
    include_type_label=False,
    include_technology=False,
    include_properties=True,
)

with SystemContextDiagram("Example", render_options=RenderOptions(d2=options)) as diagram:
    ...

diagram.save_as_d2("diagram.d2")
```

You can pass `render_options` directly to
[`D2Renderer`](../../api_docs/d2/renderers/#c4.renderers.d2.renderer.D2Renderer):

```python
from c4.renderers import D2Renderer

renderer = D2Renderer(render_options=options)
```

D2 render options can also be set via [`RenderOptions`](../render-options.md).

You can also use the builder:

```python
from c4.renderers import D2RenderOptionsBuilder

options = (
    D2RenderOptionsBuilder()
    .direction("down")
    .layout("elk")
    .title_near("bottom-center")
    .sequence_diagram()
    .auto_number_relationships()
    .include_properties()
    .bidirectional_relationships("single_edge")
    .build()
)
```

## Option Reference

| Option                          | Default        | Behavior                                                                                                                        |
|---------------------------------|----------------|---------------------------------------------------------------------------------------------------------------------------------|
| `direction`                     | `"right"`      | Emits the D2 `direction` directive. Set `None` to omit it.                                                                      |
| `layout`                        | `"dagre"`      | Selects the D2 CLI layout engine for image export. Use `"dagre"` or `"elk"`.                                                    |
| `theme`                         | `None`         | Emits a D2 theme ID when set.                                                                                                   |
| `title_near`                    | `"top-center"` | Emits diagram titles as Markdown nodes positioned with D2 `near`. Set `None` to render the title node without forced placement. |
| `sequence_diagram`              | `False`        | Emits `shape: sequence_diagram` for `DynamicDiagram` output.                                                                    |
| `auto_number_relationships`     | `False`        | Prefixes relationship labels with their render order, such as `1. Uses`.                                                        |
| `include_type_label`            | `True`         | Includes C4 element type labels, such as `Software System` or `Container`, in Markdown labels.                                  |
| `include_technology`            | `True`         | Includes element technology in visible labels.                                                                                  |
| `include_properties`            | `False`        | Emits element and relationship properties as Markdown tables.                                                                   |
| `bidirectional_relationships`   | `"two_edges"`  | Renders bidirectional relationships as two directed edges or one `<->` edge.                                                    |
| `fully_qualified_relationships` | `True`         | Uses fully qualified D2 paths for relationship endpoints.                                                                       |
| `legend`                        | `None`         | Emits a structured D2 legend under `vars.d2-legend`.                                                                            |

## Direction

`direction` controls the overall D2 layout direction and accepts `"up"`,
`"down"`, `"left"`, `"right"`, or `None`. The default is `"right"`. Use
`None` when you want D2 or the selected layout engine to choose without an
explicit source directive.

D2 element and boundary extensions also accept `d2={"direction": ...}` for a
local container direction. See [D2 extensions](extensions.md).

## Layout Engine

`layout` controls the [D2 layout engine](https://d2lang.com/tour/layouts/) used for image export through the local
D2 CLI. It accepts `"dagre"` or `"elk"` and defaults to D2's default Dagre
layout engine. This option is not emitted into `.d2` source output; it is
applied when rendering bytes or files with a D2 backend.

```python
options = D2RenderOptions(layout="elk")
```

When exporting with the CLI, `--d2-layout` overrides any `layout` set in
`D2RenderOptions`, including render options attached directly to the diagram.

## Theme

`theme` emits a D2 theme ID when set to a non-negative integer. Leave it as
`None` to use D2's default theme selection.

```python
options = D2RenderOptions(theme=300)
```

See the upstream [D2 themes documentation](https://d2lang.com/tour/themes/) for
available theme IDs and behavior.

## Titles

Diagram titles are emitted as generated Markdown text nodes instead of a
top-level `title:` directive. By default, the renderer uses the reserved
identifier `__title` and places it with `near: top-center`.

```d2
__title: ||md
  # Internet Banking Context
|| {
  near: top-center
}
```

`title_near` accepts `top-left`, `top-center`, `top-right`, `center-left`,
`center-right`, `bottom-left`, `bottom-center`, or `bottom-right`. Set
`title_near=None` to keep the generated title node while leaving placement to
D2.

## Dynamic Diagrams

`sequence_diagram=True` emits `shape: sequence_diagram` for
`DynamicDiagram` output. It is intended for dynamic diagrams where relationship
order matters. Other diagram types keep their normal D2 shape.

`auto_number_relationships=True` prefixes relationship labels with their render
order, such as `1. Uses` and `2. Calls`. This can be used with or without
`sequence_diagram`.

## Labels

`include_type_label` controls whether D2 Markdown labels include the C4 element
type, such as `[Software System]` or `[Container: Python]`. It defaults to
`True`. Set it to `False` when the type should remain in the model but not
appear in the rendered diagram.

`include_technology` controls whether element technology appears in visible
labels. It defaults to `True`, so a container created with
`technology="Python"` includes that technology in the D2 label. Set it to
`False` when technology should remain in the model but not appear in the
rendered diagram.

## Properties

`include_properties` controls whether portable C4 properties are rendered in D2
output. When `include_properties=True`, D2 emits element and relationship
properties as Markdown tables in labels. When `include_properties=False`,
property tables are omitted.

Elements with descriptions may still use Markdown labels, but their
`properties` block is not rendered until properties are enabled. See the shared
[Properties](../properties.md) page for the property API.

Boundaries with Markdown labels are emitted with `shape: rectangle` by default
so the container border remains visible in D2 output. Explicit boundary
extensions still win, so `d2={"shape": "cloud"}` keeps `shape: cloud`.

## Bidirectional Relationships

`bidirectional_relationships` controls how bidirectional relationships are
emitted:

| Value | Behavior |
|-------|----------|
| `"two_edges"` | Render the relationship as two directed D2 edges. This is the default. |
| `"single_edge"` | Render one D2 `<->` edge. |

Use `"two_edges"` when downstream tooling expects separate directed edges. Use
`"single_edge"` when the D2 source should show a compact bidirectional edge.

## Relationship Paths

`fully_qualified_relationships=True` makes relationship endpoints use complete
D2 paths, including parent containers. This is the safest default for nested
boundaries and deployment nodes because endpoint names remain unambiguous.

Set `fully_qualified_relationships=False` only when you need shorter D2 source
and your diagram does not rely on nested endpoint disambiguation.

## Legends

D2 legends are represented by `D2RenderOptions.legend`. The renderer emits them
under `vars.d2-legend`, matching D2's structured legend support.

```python
from c4.renderers import (
    D2Legend,
    D2LegendElement,
    D2LegendRel,
    D2RenderOptions,
)

options = D2RenderOptions(
    legend=D2Legend(
        items=[
            D2LegendElement(
                label="External system",
                shape="rectangle",
                style={"stroke_dash": 5},
            ),
            D2LegendRel(
                label="Synchronous call",
                style={"stroke": "#555555"},
                hide_endpoints=True,
            ),
        ],
    ),
)
```

Legend identifiers are generated by default and scoped to `vars.d2-legend`.
You can provide explicit aliases when you need stable legend item identifiers.
For relationship legend items, `hide_endpoints=True` is the structured
equivalent of setting helper endpoint opacity to zero in raw D2.

See the upstream [D2 legend documentation](https://d2lang.com/tour/legend/) for
the raw D2 syntax.

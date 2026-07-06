# D2 Extensions

D2-specific metadata should be passed with the `d2=` constructor kwarg in
Python code. The data is normalized into `element.extensions["d2"]` and is
consumed only by the D2 renderer.

```python
from c4 import Container, ContainerDiagram, Rel

with ContainerDiagram("Orders") as diagram:
    api = Container(
        "API",
        "Handles requests",
        "Python",
        d2={
            "shape": "hexagon",
            "tooltip": "Public HTTP API",
            "link": "https://example.com/api",
            "style": {"fill": "#edf7ff", "stroke": "#2d6f9f"},
        },
    )
    db = Container(
        "Database",
        "Stores orders",
        "PostgreSQL",
        d2={"shape": "cylinder"},
    )

    api >> Rel("Reads and writes", d2={"style": {"stroke_dash": 3}}) >> db
```

`extensions={"d2": {...}}` also works and normalizes to the same structure.
Prefer `d2={...}` for new Python authoring, and keep `extensions=` for
multi-backend payloads or advanced escape hatches.

## Supported Fields

| Target | Fields |
|--------|--------|
| Elements | `shape`, `style`, `icon`, `near`, `tooltip`, `link`, `classes`, `direction` |
| Boundaries and deployment nodes | `shape`, `style`, `icon`, `near`, `tooltip`, `link`, `classes`, `direction` |
| Relationships | `style`, `icon`, `near`, `tooltip`, `link`, `classes` |

`direction` is useful on containers because D2 supports local layout direction
inside container blocks.

These fields map to D2-native concepts:

- `shape` selects a D2 shape. See the upstream
  [D2 shapes documentation](https://d2lang.com/tour/shapes/).
- `style` emits nested D2 `style.*` attributes. See
  [D2 styles](https://d2lang.com/tour/style/).
- `icon` emits a D2 icon reference. See
  [D2 icons](https://d2lang.com/tour/icons/).
- `near` emits a D2 positioning hint. See
  [D2 positions](https://d2lang.com/tour/positions/).
- `tooltip` and `link` emit D2 interactive fields. See
  [D2 interactive diagrams](https://d2lang.com/tour/interactive/).
- `classes` emits D2 class references. See
  [D2 classes](https://d2lang.com/tour/classes/).
- `direction` emits a local D2 direction for element-like containers. See
  [D2 layouts](https://d2lang.com/tour/layouts/).

## Style Fields

The `style` mapping uses Python-friendly keys and renders D2 style attributes:

| Python key | D2 output |
|------------|-----------|
| `opacity` | `style.opacity` |
| `stroke` | `style.stroke` |
| `fill` | `style.fill` |
| `fill_pattern` | `style.fill-pattern` |
| `stroke_width` | `style.stroke-width` |
| `stroke_dash` | `style.stroke-dash` |
| `border_radius` | `style.border-radius` |
| `shadow` | `style.shadow` |
| `three_d` | `style.3d` |
| `multiple` | `style.multiple` |
| `double_border` | `style.double-border` |
| `font` | `style.font` |
| `font_size` | `style.font-size` |
| `font_color` | `style.font-color` |
| `animated` | `style.animated` |
| `bold` | `style.bold` |
| `italic` | `style.italic` |
| `underline` | `style.underline` |
| `text_transform` | `style.text-transform` |

Unknown extension or style keys fail D2 validation by default.

## Properties

Properties are portable C4 model data, not D2 extension data. Add them with the
[Properties](../properties.md) API, then enable D2 property rendering
with [`D2RenderOptions(include_properties=True)`](options.md#properties).

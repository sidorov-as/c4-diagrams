# LikeC4 Styles

LikeC4 styles live in three places: the defaults of a kind in the
specification, the style of one element, and `style` rules in a view. A more
specific place overrides a less specific one.

<!-- generated:start likec4-calls-styles -->
| Python call | Generated DSL |
|---|---|
| <pre><code>project.specification.color("brand", "#ff6600")&#10;project.specification.tag("promo", color="brand")</code></pre> | <pre><code>tag promo { color brand }</code></pre> |
| <pre><code>project.specification.element("service", shape="component", color="indigo", border="dashed")</code></pre> | <pre><code>element service {&#10;  style {&#10;    color indigo&#10;    shape component&#10;    border dashed&#10;  }&#10;}</code></pre> |
| <pre><code>project.specification.element("service", size="lg", padding="sm", text_size="xs")</code></pre> | <pre><code>style {&#10;  size lg&#10;  textSize xs&#10;  padding sm&#10;}</code></pre> |
| <pre><code>project.model.element("system", "Shop", iconPosition="bottom", icon_size="lg")</code></pre> | <pre><code>style {&#10;  iconSize lg&#10;  iconPosition bottom&#10;}</code></pre> |
| <pre><code>project.specification.relationship("sync", line="solid", head="vee", tail="none")</code></pre> | <pre><code>relationship sync {&#10;  line solid&#10;  head vee&#10;  tail none&#10;}</code></pre> |
| <pre><code>view = project.views.element_view("index")&#10;view.style(shop, shape="queue", size="lg", multiple=True)</code></pre> | <pre><code>style shop {&#10;  shape queue&#10;  size lg&#10;  multiple true&#10;}</code></pre> |
<!-- generated:end likec4-calls-styles -->

## Colors

`color` and `iconColor` take a theme color or the name of a custom color:

- Theme colors (`blue`, `green`, `indigo`, `primary`, ...) need no declaration.
  The full list is in the [Reference](reference.md#allowed-values).
- A custom color is declared once with `specification.color(name, value)`, from
  a hex or `rgb()`/`rgba()` value, and then used by name. Using an undeclared
  color is a validation error that names it.
- `specification.tag(name, color=...)` colors a tag.

## Shapes, borders and sizes

| Property                                | Values                                                      |
|-----------------------------------------|-------------------------------------------------------------|
| `shape`                                 | Element shapes (`rectangle`, `person`, `cylinder`, ...).    |
| `border`                                | `solid`, `dashed`, `dotted`, `none`.                        |
| `opacity`                               | Integer percentage from 0 to 100; written as `50%`.         |
| `size`, `text_size`, `padding`, `icon_size` | `xs`, `sm`, `md`, `lg`, `xl`.                           |
| `multiple`                              | `True` draws a stacked box.                                 |

Style keywords use snake_case in Python (`text_size`, `icon_size`) and are
written in camelCase in the source. camelCase also works. An unknown property
or value raises `ValueError` listing the allowed ones.

## Icons

`icon="tech:python"` sets the element icon. The renderer does not check the
reference; LikeC4 resolves names such as `tech:*`, `aws:*`, `gcp:*` and
`bootstrap:*`, and URLs. `icon_color`, `icon_size` and `icon_position`
(`left`, `right`, `top`, `bottom`) fine-tune it.

## Lines and arrows

Relationship styles take `color`, `line` (`solid`, `dashed`, `dotted`) and the
arrow heads `head` and `tail`. Set them on a relationship, or as defaults in
`specification.relationship(...)`.

## View style rules

`view.style(target, **properties)` styles elements inside one view only.
Targets are the same items as in `include`. It takes element style properties
and cannot target relationship predicates.

Upstream: [styling](https://likec4.dev/dsl/styling/),
[custom colors](https://likec4.dev/dsl/styling/) and
[relationships](https://likec4.dev/dsl/relationships/).

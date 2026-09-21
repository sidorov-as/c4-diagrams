# LikeC4 Reference

<!-- Generated tables: see CONTRIBUTING.md, "Regenerate documentation artifacts". -->

Lookup tables for the LikeC4 backend. For how to use these values see [Authoring](authoring.md), [Views](views.md) and
[Styles](styles.md).

## Allowed values

<!-- generated:start likec4-values -->
### Element shapes

`browser`, `bucket`, `component`, `cylinder`, `document`, `mobile`, `person`, `queue`, `rectangle`, `storage`

### Borders

`dashed`, `dotted`, `none`, `solid`

### Sizes (`size`, `text_size`, `padding`, `icon_size`)

`lg`, `md`, `sm`, `xl`, `xs`

### Icon positions

`bottom`, `left`, `right`, `top`

### Line types

`dashed`, `dotted`, `solid`

### Arrow types (`head`, `tail`)

`crow`, `diamond`, `dot`, `none`, `normal`, `odiamond`, `odot`, `onormal`, `open`, `vee`

### Theme colors

`amber`, `blue`, `gray`, `green`, `indigo`, `muted`, `primary`, `red`, `secondary`, `sky`, `slate`

### Auto-layout directions

`BottomTop`, `LeftRight`, `RightLeft`, `TopBottom`
<!-- generated:end likec4-values -->

## Style properties

Keyword arguments for element, deployment node and instance styles, and for
relationship styles. Python also accepts the camelCase spelling.

<!-- generated:start likec4-style-properties -->
### Element style properties

| Python keyword | LikeC4 property |
|---|---|
| `color` | `color` |
| `shape` | `shape` |
| `icon` | `icon` |
| `icon_color` | `iconColor` |
| `icon_size` | `iconSize` |
| `icon_position` | `iconPosition` |
| `opacity` | `opacity` |
| `border` | `border` |
| `size` | `size` |
| `text_size` | `textSize` |
| `padding` | `padding` |
| `multiple` | `multiple` |

### Relationship style properties

| Python keyword | LikeC4 property |
|---|---|
| `color` | `color` |
| `line` | `line` |
| `head` | `head` |
| `tail` | `tail` |
<!-- generated:end likec4-style-properties -->

## Validation rules

Errors raised when the project is rendered. Mistakes caught while authoring (a
bad identifier, an unknown style value, a duplicate declaration) raise
`ValueError` or `TypeError` immediately.

<!-- generated:start likec4-validation -->
| Cause | Error |
|---|---|
| The rendered object is not a `Project`. | `LikeC4ValidationError` |
| An element kind, relationship kind, deployment node kind, tag or custom color is used but not declared in the specification. | `LikeC4ValidationError` |
| A relationship endpoint does not belong to the project. | `LikeC4ValidationError` |
| A relationship connects an element with its own ancestor or descendant. | `LikeC4ValidationError` |
| A link has no scheme, relative prefix or `@alias`, or contains whitespace. | `LikeC4ValidationError` |
| A deployment node holds several unnamed instances of the same element, or an instance points outside the project model. | `LikeC4ValidationError` |
| View keys are not unique across all view types. | `LikeC4ValidationError` |
| A view scope or predicate reference does not resolve to a member of the project. | `LikeC4ValidationError` |
| `navigate_to` does not name a view (a dynamic view for relationships and steps). | `LikeC4ValidationError` |
| A view style rule targets a relationship predicate. | `LikeC4ValidationError` |
| The local `likec4` CLI fails to export a view. | `LikeC4LocalRenderingError` |
<!-- generated:end likec4-validation -->

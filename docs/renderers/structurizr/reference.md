# Structurizr Reference

<!-- Generated tables: see CONTRIBUTING.md, "Regenerate documentation artifacts". -->

Lookup tables for the Structurizr backend. For how to use these values see [Authoring](authoring.md), [Views](views.md)
and [Styles](styles.md).

## Allowed values

<!-- generated:start structurizr-values -->
### Element shapes

| Python value | Structurizr shape |
|---|---|
| `box` | `Box` |
| `roundedbox` | `RoundedBox` |
| `circle` | `Circle` |
| `ellipse` | `Ellipse` |
| `hexagon` | `Hexagon` |
| `cylinder` | `Cylinder` |
| `pipe` | `Pipe` |
| `person` | `Person` |
| `robot` | `Robot` |
| `folder` | `Folder` |
| `webbrowser` | `WebBrowser` |
| `mobiledevicelandscape` | `MobileDeviceLandscape` |
| `mobiledeviceportrait` | `MobileDevicePortrait` |

### Borders

| Python value | Structurizr border |
|---|---|
| `solid` | `Solid` |
| `dashed` | `Dashed` |
| `dotted` | `Dotted` |

### Auto-layout rank directions

`BottomTop`, `LeftRight`, `RightLeft`, `TopBottom`

### Style presets

`classic`, `new-c4-style`, `none`
<!-- generated:end structurizr-values -->

Shapes and borders are matched ignoring case and underscores (`rounded_box` works); the output uses the
Structurizr spelling shown in the right column.

## Style properties

Keyword arguments of `workspace.styles.element(...)`, `styles.relationship(...)`
and the `style` argument of elements. Upstream:
[element styles](https://docs.structurizr.com/dsl/language),
[relationship styles](https://docs.structurizr.com/dsl/language).

<!-- generated:start structurizr-style-properties -->
| Python keyword | Structurizr style property |
|---|---|
| `shape` | `shape` |
| `width` | `width` |
| `height` | `height` |
| `background` | `background` |
| `color` | `color` |
| `stroke` | `stroke` |
| `stroke_width` | `strokeWidth` |
| `border` | `border` |
| `opacity` | `opacity` |
| `font_size` | `fontSize` |
| `metadata` | `metadata` |
| `description` | `description` |
| `thickness` | `thickness` |
| `routing` | `routing` |
| `position` | `position` |
<!-- generated:end structurizr-style-properties -->

## Validation rules

Errors raised before any output is produced. Most are
`StructurizrRenderingError`; mistakes caught while authoring raise `TypeError`
or `ValueError` immediately.

<!-- generated:start structurizr-validation -->
| Cause | Error |
|---|---|
| The rendered object is not a `Workspace`. | `StructurizrRenderingError` |
| A container has no software system parent, or a component has no container parent. | `StructurizrRenderingError` |
| A deployment instance does not reference a model element of the workspace. | `StructurizrRenderingError` |
| A relationship endpoint does not belong to the workspace. | `StructurizrRenderingError` |
| A relationship connects a parent with its own descendant. | `StructurizrRenderingError` |
| A deployment node does not belong to exactly one environment. | `StructurizrRenderingError` |
| A view that needs a scope has none, or its scope is of the wrong type or outside the workspace. | `StructurizrRenderingError` |
| A deployment view names an unknown deployment environment. | `StructurizrRenderingError` |
| An element `style` mapping has an unknown field or a value of the wrong type. | `StructurizrRenderingError` |
| `tags` is not a `list[str]`, or a view scope is passed as an alias string instead of a model object. | `TypeError` |
| An `owner`, `parent`, scope or endpoint belongs to another workspace, or has the wrong type for the factory. | `ValueError` |
| An export backend is misconfigured (for example a missing view key or binary). | `StructurizrBackendConfigurationError` |
<!-- generated:end structurizr-validation -->

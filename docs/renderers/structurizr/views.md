# Structurizr Views

Views are declared on `workspace.views`. Each factory returns the view, and
every view gets its own block in the DSL. All views share the same keyword
arguments:

| Argument      | Meaning                                                                                  |
|---------------|------------------------------------------------------------------------------------------|
| `title`       | Title shown on the view.                                                                 |
| `key`         | Stable view key. It is what `--structurizr-view-key` and Kroki select.                    |
| `description` | View description.                                                                        |
| `include`     | Selectors to include. A non-dynamic view with no `include` and no `exclude` gets `include *`. |
| `exclude`     | Selectors to exclude.                                                                    |
| `animation`   | Ordered groups of elements revealed step by step.                                        |
| `auto_layout` | An [`AutoLayout`][c4.contrib.structurizr.AutoLayout], or `None` to use the render options.                                    |
| `tags`        | View tags (`list[str]`).                                                                 |
| `properties`  | View properties.                                                                         |

## View types and their scope

| Factory                                            | DSL view         | Scope                                                        |
|----------------------------------------------------|------------------|--------------------------------------------------------------|
| [`SystemLandscapeView()`][c4.contrib.structurizr.workspace.SystemLandscapeView]                            | `systemLandscape` | None.                                                        |
| [`SystemContextView(system)`][c4.contrib.structurizr.workspace.SystemContextView]                        | `systemContext`   | A [`SoftwareSystem`][c4.contrib.structurizr.SoftwareSystem]. Required.                                |
| [`ContainerView(system)`][c4.contrib.structurizr.workspace.ContainerView]                            | `container`       | A `SoftwareSystem`. Required.                                |
| [`ComponentView(container)`][c4.contrib.structurizr.workspace.ComponentView]                         | `component`       | A [`Container`][c4.contrib.structurizr.Container]. Required.                                     |
| [`DynamicView(scope=None)`][c4.contrib.structurizr.DynamicView]                          | `dynamic`         | Optional `SoftwareSystem` or `Container`.                    |
| [`DeploymentView(scope=None, environment=...)`][c4.contrib.structurizr.workspace.DeploymentView]      | `deployment`      | Optional element. `environment` is required.                 |

A scope must be a model object of the same workspace, never an alias string
(that raises `TypeError` immediately). A missing or wrong scope is reported
when the workspace is rendered, for example `ContainerView requires a scope
reference.` or `ComponentView has an invalid scope reference.` A deployment
view whose `environment` has no deployment nodes is rejected too. See
[Limitations](limitations.md#rules-checked-by-the-renderer).

<!-- generated:start structurizr-calls-views -->
| Python call | Generated DSL |
|---|---|
| <pre><code>workspace.views.SystemLandscapeView(key="landscape")</code></pre> | <pre><code>systemLandscape "landscape" {&#10;  include *&#10;  autoLayout lr&#10;}</code></pre> |
| <pre><code>workspace.views.SystemContextView(shop, key="context")</code></pre> | <pre><code>systemContext shop "context" {&#10;  include *&#10;  autoLayout lr&#10;}</code></pre> |
| <pre><code>workspace.views.ContainerView(shop, key="containers")</code></pre> | <pre><code>container shop "containers" {</code></pre> |
| <pre><code>workspace.views.ComponentView(api, key="components")</code></pre> | <pre><code>component api "components" {</code></pre> |
| <pre><code>workspace.views.DeploymentView(shop, environment="Live", key="live")</code></pre> | <pre><code>deployment shop "Live" "live" {</code></pre> |
| <pre><code>flow = workspace.views.DynamicView(shop, key="checkout")&#10;flow.step(customer, api, "Pays", technology="HTTPS")</code></pre> | <pre><code>dynamic shop "checkout" {&#10;  customer -&gt; api "Pays" "HTTPS"&#10;  autoLayout lr&#10;}</code></pre> |
| <pre><code>workspace.views.SystemContextView(shop, key="context",&#10;    include=["*", ViewTag("Critical")],&#10;    exclude=[customer])</code></pre> | <pre><code>include *&#10;include element.tag==Critical&#10;exclude customer</code></pre> |
| <pre><code>workspace.views.ContainerView(shop, key="containers",&#10;    exclude=RawSelector("relationship.tag==Async"))</code></pre> | <pre><code>exclude relationship.tag==Async</code></pre> |
| <pre><code>workspace.views.ContainerView(shop, key="containers",&#10;    animation=[[customer], [api]])</code></pre> | <pre><code>animation {&#10;  customer&#10;  api&#10;}</code></pre> |
| <pre><code>workspace.views.SystemLandscapeView(key="landscape",&#10;    auto_layout=AutoLayout("TopBottom", rank_separation=100))</code></pre> | <pre><code>autoLayout tb 100</code></pre> |
| <pre><code>workspace.views.SystemLandscapeView(key="landscape",&#10;    tags=["Overview"], properties={"audience": "all"})</code></pre> | <pre><code>tags "Overview"&#10;properties {&#10;  "audience" "all"&#10;}</code></pre> |
| <pre><code>flow = workspace.views.DynamicView(shop, key="checkout")&#10;flow.step(customer, api, "Pays", create_relationship=True)</code></pre> | <pre><code>customer -&gt; api "Pays" {</code></pre> |
<!-- generated:end structurizr-calls-views -->

## Selectors

`include`, `exclude` and `animation` accept an element (written as its alias),
a string, a selector object or an iterable of those:

- An element becomes its alias; `"*"` and any other string are written as is.
- [`ViewTag("Critical")`][c4.contrib.structurizr.ViewTag] becomes `element.tag==Critical` and quotes the tag when
  needed.
- [`RawSelector("relationship.tag==Async")`][c4.contrib.structurizr.RawSelector] is written verbatim. The renderer
  cannot check it; the Structurizr CLI does.

A view can also be extended after creation with `view.include(...)` and
`view.exclude(...)`, which return the view.

## Auto layout

`AutoLayout(rank_direction="LeftRight", implementation=None,
rank_separation=None, node_separation=None)` becomes `autoLayout lr` (and the
optional separations). Valid rank directions are listed in the
[Reference](reference.md#auto-layout-rank-directions). A view without
`auto_layout` uses the one from the [render options](styles.md#render-options),
which is left to right by default.

## Dynamic views

A dynamic view is an ordered list of interactions. Add them with
`view.step(source, destination, description, technology=...)`.

- By default a step is **view-local**: it appears in the dynamic view and does
  not add a relationship to the model. This is what you want for sequences
  that reuse elements.
- `create_relationship=True` also registers the interaction as a model
  relationship, so it shows up in other views.
- `relationship=rel` binds the step to an existing model relationship. Passing
  both `relationship=` and `create_relationship=True` raises `ValueError`.
- `steps=[...]` on the factory takes relationships or [`DynamicStep`][c4.contrib.structurizr.DynamicStep] values.

```python
from c4.contrib.structurizr import Rel, Workspace

workspace = Workspace("Checkout")

with workspace.model as model:
    customer = model.Person("Customer")
    shop = model.SoftwareSystem("Shop")
    web = model.Container("Web App", owner=shop)
    api = model.Container("API", owner=shop)
    customer >> Rel("Uses") >> web

flow = workspace.views.DynamicView(shop, key="checkout")
flow.step(customer, web, "Starts checkout")
flow.step(web, api, "Submits the order", technology="JSON/HTTPS")
```

Upstream: [views](https://docs.structurizr.com/dsl/language),
[dynamic views](https://docs.structurizr.com/dsl/language),
[view expressions](https://docs.structurizr.com/dsl/expressions).

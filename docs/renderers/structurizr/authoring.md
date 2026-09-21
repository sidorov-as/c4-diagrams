# Structurizr Authoring

A Structurizr [`Workspace`][c4.contrib.structurizr.Workspace] owns one persistent `model`, `views` and `styles`.
They are properties, not factories. This page covers the workspace, the model,
relationships and deployment; [Views](views.md) and [Styles](styles.md) cover
the rest.

```python
from c4.contrib.structurizr import Rel, Workspace

workspace = Workspace("Payments", description="Payments architecture")

with workspace.model as model:
    customer = model.Person("Customer", tags=["External"])
    payments = model.SoftwareSystem("Payments")
    api = model.Container("API", technology="FastAPI", owner=payments)

    customer >> Rel("Uses", technology="HTTPS") >> api
```

Use the Structurizr names for factories ([`Person`][c4.contrib.structurizr.Person], [`SoftwareSystem`][c4.contrib.structurizr.SoftwareSystem],
[`Container`][c4.contrib.structurizr.Container], [`Component`][c4.contrib.structurizr.Component], ...). Lowercase aliases are not supported. Tags must
be `list[str]` (or tuple) values, never a bare string.

## Workspace

`Workspace(name, description=None, theme=None, default_renderer=None,
render_options=None)` is also a context manager. `workspace.set_property(key,
value)` sets a workspace property. `workspace.render()` returns the DSL and
`workspace.save(path)` writes it. See [Styles](styles.md#theme) for `theme` and
`render_options`.

## Elements

Every element factory is a method of `workspace.model` and returns the element.
Containers and components also have shortcuts on their parent:
`system.Container(...)` and `container.Component(...)`.

Elements nest in two ways: pass `owner=` (or `parent=` for deployment nodes), or
use the parent as a context manager:

```python
from c4.contrib.structurizr import Workspace

workspace = Workspace("Nested")

with workspace.model as model:
    shop = model.SoftwareSystem("Shop")
    with shop:
        api = model.Container("API")  # owner is the active context
        with api:
            model.Component("Controller")
```

<!-- generated:start structurizr-calls-elements -->
| Python call | Generated DSL |
|---|---|
| <pre><code>customer = model.Person("Customer", description="Buys goods", tags=["External"])</code></pre> | <pre><code>customer = person "Customer" "Buys goods" {&#10;  tags "Person,External"&#10;}</code></pre> |
| <pre><code>shop = model.SoftwareSystem("Shop", description="Online shop")</code></pre> | <pre><code>shop = softwareSystem "Shop" "Online shop" {&#10;  tags "Software System"&#10;}</code></pre> |
| <pre><code>api = model.Container("API", description="HTTP API", technology="FastAPI", owner=shop)</code></pre> | <pre><code>api = container "API" "HTTP API" "FastAPI" {&#10;  tags "Container"&#10;}</code></pre> |
| <pre><code>model.Component("Login", description="Checks passwords", technology="Python", owner=api)</code></pre> | <pre><code>login = component "Login" "Checks passwords" "Python" {&#10;  tags "Component"&#10;}</code></pre> |
| <pre><code>live = model.DeploymentEnvironment("Live")&#10;server = live.DeploymentNode("Server", technology="Ubuntu 24.04")</code></pre> | <pre><code>deploymentEnvironment "Live" {&#10;  server = deploymentNode "Server" "" "Ubuntu 24.04" {</code></pre> |
| <pre><code>docker = server.DeploymentNode("Docker")</code></pre> | <pre><code>docker = deploymentNode "Docker" {&#10;  tags "Boundary"</code></pre> |
| <pre><code>lb = server.InfrastructureNode("Load balancer", technology="nginx")</code></pre> | <pre><code>load_balancer = infrastructureNode "Load balancer" "" "nginx" {</code></pre> |
| <pre><code>server.SoftwareSystemInstance(shop)</code></pre> | <pre><code>shop_instance = softwareSystemInstance shop {&#10;  tags "Software System"&#10;}</code></pre> |
| <pre><code>server.ContainerInstance(api)</code></pre> | <pre><code>api_instance = containerInstance api {&#10;  tags "Container"&#10;}</code></pre> |
<!-- generated:end structurizr-calls-elements -->

`technology` is rendered for containers, components, deployment nodes and
infrastructure nodes. Structurizr DSL has no technology slot on people and
software systems, so it is ignored there. When only `technology` is set, the
description slot is written as an empty string.

### Common keyword arguments

All elements accept `description`, `technology`, `alias`, `tags`, `properties`,
`url` and `style`. Containers and components also take `owner`; deployment and
infrastructure nodes take `parent`; instances take `parent`.

<!-- generated:start structurizr-calls-metadata -->
| Python call | Generated DSL |
|---|---|
| <pre><code>model.SoftwareSystem("Shop", alias="web_shop")</code></pre> | <pre><code>web_shop = softwareSystem "Shop" {</code></pre> |
| <pre><code>model.SoftwareSystem("Shop", tags=["Critical"]).tag("Legacy")</code></pre> | <pre><code>tags "Software System,Critical,Legacy"</code></pre> |
| <pre><code>model.SoftwareSystem("Shop", properties={"owner": "team-a"})</code></pre> | <pre><code>properties {&#10;  "owner" "team-a"&#10;}</code></pre> |
| <pre><code>model.SoftwareSystem("Shop", url="https://example.com/shop")</code></pre> | <pre><code>url "https://example.com/shop"</code></pre> |
| <pre><code>model.Person("Customer", style={"shape": "Person"})</code></pre> | <pre><code>element "c4diagrams_style_customer" {&#10;  shape Person&#10;}</code></pre> |
<!-- generated:end structurizr-calls-metadata -->

- **`alias`** is the Python-side identity and the DSL identifier. When omitted
  it is derived from the name (`"Web App"` becomes `web_app`), and a repeated
  alias gets a `_2`, `_3` suffix. An explicit alias must be a valid Python
  identifier. Words reserved by Structurizr DSL (such as `model` or `views`)
  are renamed in the output.
- **`tags`** are added to the built-in tag of the element kind (`Person`,
  `Software System`, `Container`, ...). `element.tag("Critical")` adds more and
  returns the element.
- **`properties`** become a `properties { ... }` block; `element.property(key,
  value)` sets one.
- **`style`** is an element-local style. It generates a private tag and one
  style rule, so it is equivalent to `workspace.styles.element(element, ...)`.
  See [Styles](styles.md#element-local-styles).

## Relationships

`uses`, `used_by` and the `>>` operator create model relationships between
elements of the same workspace. They accept `technology`, `tags`,
`properties`, `url` and `style`.

- `a.uses(b, "label")` creates `a -> b`.
- `b.used_by(a, "label")` creates the same `a -> b`.
- `a >> Rel("label", technology=...) >> b` is the concise form, with the
  [Structurizr `Rel`][c4.contrib.structurizr.Rel] builder. `a >> "label" >> b`
  works without options. `b << Rel("label") << a` and `b << "label" << a` write
  the same relationship in the other direction.
- A list on one side fans out: `a >> Rel("label") >> [b, c]` and
  `[a, b] >> Rel("label") >> c`, and the `<<` forms of both. Each list item
  gives one relationship, in list order, and the expression returns the list.
  A list on both sides raises `ValueError("Either source or destination must be
  a single element")` and creates nothing.
  A list can stand on the left only together with `Rel(...)`: Python has no
  `>>` between a `list` and a `str`, so `[a, b] >> "label" >> c` raises
  `TypeError`. Use `[a, b] >> Rel("label") >> c`. With one element on the left,
  a string works: `a >> "label" >> [b, c]`.
- `a >> b` creates a relationship with no description, and the DSL has no
  description string for it. `a >> b | "label"` sets the description; the pipe
  fills only an empty description and raises `ValueError` if one exists.

`Rel` takes only the description as a positional argument:
`Rel("Calls", technology="HTTPS")`. `Rel("Calls", "HTTPS")` raises `TypeError`,
and there is no `label=` alias. A `Rel` is immutable, so one value can be used
for any number of relationships.

<!-- generated:start structurizr-calls-relationships -->
| Python call | Generated DSL |
|---|---|
| <pre><code>customer.uses(api, "Calls", technology="HTTPS")</code></pre> | <pre><code>customer -&gt; api "Calls" "HTTPS" {&#10;  tags "Relationship"&#10;}</code></pre> |
| <pre><code>api.used_by(customer, "Calls", technology="HTTPS")</code></pre> | <pre><code>customer -&gt; api "Calls" "HTTPS" {</code></pre> |
| <pre><code>customer &gt;&gt; Rel("Calls", technology="HTTPS") &gt;&gt; api</code></pre> | <pre><code>customer -&gt; api "Calls" "HTTPS" {</code></pre> |
| <pre><code>customer &gt;&gt; "Uses" &gt;&gt; shop</code></pre> | <pre><code>customer -&gt; shop "Uses" {</code></pre> |
| <pre><code>customer &gt;&gt; Rel("Calls") &gt;&gt; [api, shop]</code></pre> | <pre><code>customer -&gt; api "Calls" {&#10;  tags "Relationship"&#10;}&#10;customer -&gt; shop "Calls" {&#10;  tags "Relationship"&#10;}</code></pre> |
| <pre><code>api &lt;&lt; Rel("Calls") &lt;&lt; customer</code></pre> | <pre><code>customer -&gt; api "Calls" {</code></pre> |
| <pre><code>[customer, other] &gt;&gt; Rel("Calls") &gt;&gt; api</code></pre> | <pre><code>customer -&gt; api "Calls" {&#10;  tags "Relationship"&#10;}&#10;other -&gt; api "Calls" {&#10;  tags "Relationship"&#10;}</code></pre> |
| <pre><code>customer &gt;&gt; shop</code></pre> | <pre><code>customer -&gt; shop {&#10;  tags "Relationship"&#10;}</code></pre> |
| <pre><code>customer &gt;&gt; shop &#124; "Uses"</code></pre> | <pre><code>customer -&gt; shop "Uses" {</code></pre> |
| <pre><code>customer.uses(api, "Calls", tags=["Async"], properties={"sla": "99.9"})</code></pre> | <pre><code>customer -&gt; api "Calls" {&#10;  tags "Relationship,Async"&#10;  properties {&#10;    "sla" "99.9"&#10;  }&#10;}</code></pre> |
<!-- generated:end structurizr-calls-relationships -->

A relationship between a parent and one of its own descendants is rejected
when rendering, because Structurizr does not allow it. See
[Limitations](limitations.md#rules-checked-by-the-renderer).

Relationships created with `uses` or `>>` are model relationships. A dynamic
view step is view-local unless you ask otherwise; see
[Views](views.md#dynamic-views).

## Deployment

A deployment model has environments, nested deployment nodes, optional
infrastructure nodes and instances of model elements.

```python
from c4.contrib.structurizr import Workspace

workspace = Workspace("Deployment")

with workspace.model as model:
    shop = model.SoftwareSystem("Shop")
    api = model.Container("API", owner=shop)

    with model.DeploymentEnvironment("Live") as live:
        server = live.DeploymentNode("Server", technology="Ubuntu 24.04")
        docker = server.DeploymentNode("Docker")
        docker.InfrastructureNode("Load balancer", technology="nginx")
        docker.ContainerInstance(api)

workspace.views.DeploymentView(shop, environment="Live", key="live")
```

- `model.DeploymentEnvironment(name)` returns the existing environment of that
  name or creates it. Inside `with env:` new deployment nodes join it.
- `env.DeploymentNode(...)` and `node.DeploymentNode(...)` create root and
  nested nodes. Every node belongs to exactly one environment.
- [`InfrastructureNode`][c4.contrib.structurizr.InfrastructureNode] and the two instance factories need a deployment node
  parent. An instance copies the name, description and technology of its
  target and gets the alias `<target>_instance` unless you pass `alias=`.
- [`SoftwareSystemInstance`][c4.contrib.structurizr.SoftwareSystemInstance] takes a `SoftwareSystem`, [`ContainerInstance`][c4.contrib.structurizr.ContainerInstance] takes a
  `Container`, both from the same workspace.

## Validation

The rules checked before rendering are listed in
[Limitations](limitations.md#rules-checked-by-the-renderer), and the full list
with the error that reports each is in the [Reference](reference.md#validation-rules).

Upstream: [model](https://docs.structurizr.com/dsl/language),
[deployment model](https://docs.structurizr.com/dsl/language).

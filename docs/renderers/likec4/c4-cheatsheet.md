# LikeC4 C4 Cheat-sheet

LikeC4 has **no built-in C4 kinds**. There is no `person`, `container` or
`database` until you declare it in [`project.specification`][c4.contrib.likec4.Specification].
This page gives a ready-to-copy specification, the call that creates each C4
concept and the view that shows it. The [`C4` preset](#c4-preset) and the helper
methods are a shorter form of the same calls. Details are in [Authoring](authoring.md),
[Views](views.md) and [Styles](styles.md).

## C4 specification

Copy this block at the top of a project. Every kind has to be declared before
it is used.

```python
from c4.contrib.likec4 import Project, RawPredicate, Where, Wildcard

project = Project("Shop")

spec = project.specification
spec.element("person", title="Person", shape="person", color="blue")
spec.element("system", title="Software System", color="primary")
spec.element("container", title="Container", color="secondary")
spec.element("component", title="Component", shape="component", color="muted")
spec.element("database", title="Database", shape="storage", color="secondary")
spec.element("external", title="External System", color="gray", border="dashed")
spec.deployment_node("environment", title="Environment")
spec.deployment_node("node", title="Node")
```

The shapes and colors are a choice, not a rule: `cylinder` instead of
`storage` for databases, or other theme colors, work the same. See
[Styles](styles.md) for the allowed values.

| C4 concept                       | LikeC4 kind  | Shape and color                  |
|----------------------------------|--------------|----------------------------------|
| [Person](#person)                | `person`     | `person`, blue                   |
| [Software system](#software-system) | `system`  | primary                          |
| [Container](#container)          | `container`  | secondary                        |
| [Component](#component)          | `component`  | `component`, muted               |
| [Database](#database)            | `database`   | `storage`, secondary             |
| [External](#external)            | `external`   | grey, dashed border              |

The snippets below continue this script, in order, and run together as one
script.

### C4 preset

[`C4`][c4.contrib.likec4.C4] declares the same six kinds in one call. It is a
shortcut for the block above and renders the same specification.

```python
from c4.contrib.likec4 import C4, Project

project = Project("Shop")
project.specification.use(C4)
```

The preset is never applied on its own: `Project(...)` starts with an empty
specification. `use` raises `ValueError` if a kind is already declared, so
apply it instead of the explicit block, not after it. Derive a variant with
`C4.with_(elements=[...])`, or define your own
[`Preset`][c4.contrib.likec4.Preset]. See
[Authoring](authoring.md#presets-and-helpers).

The `Model` and `Element` helpers `person`, `system`, `container`, `component`,
`database` and `external` are wrappers over `element(kind, ...)`. They exist
whether or not a preset was applied, and raise an error naming the kind when
that kind is not declared in the specification.

## Model

The model snippets continue the script above, in order.

### Person

`project.model.element("person", title)` with the `person` kind from the
specification. Each snippet shows the helper form as a comment; the helpers
need the kind declared (by hand or with `use(C4)`).

```python
customer = project.model.element("person", "Customer", alias="customer")
# With helpers: customer = project.model.person("Customer", alias="customer")
```

### Software system

```python
shop = project.model.element("system", "Shop", alias="shop")
# With helpers: shop = project.model.system("Shop", alias="shop")
```

### Container

A container is an element of the `container` kind nested in a system, with
`parent=` or `system.element(...)`.

```python
web = shop.element("container", "Web App", alias="web", technology="Django")
# With helpers: web = shop.container("Web App", alias="web", technology="Django")
```

### Component

```python
auth = web.element("component", "Auth", alias="auth")
# With helpers: auth = web.component("Auth", alias="auth")
```

### Database

A database is an element of the `database` kind. The shape in the
specification draws it as storage.

```python
db = shop.element("database", "Database", alias="db", technology="PostgreSQL")
# With helpers: db = shop.database("Database", alias="db", technology="PostgreSQL")
```

### External

An external system is a top-level element of the `external` kind. The dashed
border comes from the specification.

```python
payments = project.model.element("external", "Payment Gateway", alias="payments")
# With helpers: payments = project.model.external("Payment Gateway", alias="payments")
```

### Boundary

LikeC4 has no boundary kind. Nesting is the boundary: the children of `shop`
are drawn inside it when a view includes both, and `shop` is shown as a
single box when a view includes only `shop`.

```python
with project.model.element("system", "Billing", alias="billing"):
    project.model.element("container", "Invoices", alias="invoices")
```

### Relationship

[`element.uses(target, title)`][c4.contrib.likec4.Element] creates a
relationship, and so do `a >> "title" >> b` and
`a >> Rel("title", technology="HTTPS") >> b`
([`Rel`][c4.contrib.likec4.Rel]). A declared relationship kind, a technology and
a direction are keywords:

```python
customer.uses(web, "uses", technology="HTTPS")
web >> Rel("reads and writes") >> db
web >> "charges" >> payments
```

!!! note "Undeclared kinds"

    `project.model.person("Customer")` on a project that does not declare
    `person` raises `ValueError` naming the kind and creates no element. With
    `element("person", ...)` the same mistake surfaces when the project is
    rendered, as a `LikeC4ValidationError`. The helpers do not check nesting: a
    `container` outside a system is allowed.

## Deployment

Deployment nodes need declared kinds (`environment` and `node` above). Nested
nodes are the boundary; `instance` places a model element on a node.

```python
live = project.deployment.node("environment", "Live", alias="live")
region = live.node("node", "EU region", alias="eu")
server = region.node("node", "Server", alias="server")
server.instance(web, "web_1")

project.views.deployment_view("live", "Live").include(Wildcard())
```

## C4 views

LikeC4 has no fixed C4 view types. An element view with the right `of` scope
and predicates gives each of them. [`Wildcard`][c4.contrib.likec4.Wildcard],
[`Children`][c4.contrib.likec4.Children],
[`Descendants`][c4.contrib.likec4.Descendants],
[`Between`][c4.contrib.likec4.Between] and the other relationship predicates,
[`Where`][c4.contrib.likec4.Where] come from `c4.contrib.likec4`.

```python
# System landscape: every top-level element.
project.views.element_view("landscape", "System landscape").include(Wildcard())

# System context: the system and the elements connected to it.
project.views.element_view("context", "System context").include(
    RawPredicate("-> shop ->")
)

# Container view: the system, its containers and their neighbours.
project.views.element_view("containers", "Containers", of=shop).include(Wildcard())

# Component view: the container and its components.
project.views.element_view("components", "Components", of=web).include(Wildcard())

# Only external systems.
project.views.element_view("external", "External systems").include(
    Where(Wildcard(), kind="external")
)

print(project.render())
```

| C4 view                | Call                                                                   | Why                                                            |
|------------------------|------------------------------------------------------------------------|----------------------------------------------------------------|
| System landscape       | `element_view(key).include(Wildcard())`                                | No scope, so `*` is every top-level element.                   |
| System context         | `element_view(key).include(RawPredicate("-> system ->"))`              | The system and its neighbours, without the containers. `of=system` and `*` would show the containers. |
| Container              | `element_view(key, of=system).include(Wildcard())`                     | `*` is the system, its children and what they connect to.      |
| Component              | `element_view(key, of=container).include(Wildcard())`                  | The same rule one level down.                                  |
| Filtered by kind or tag | `include(Where(Wildcard(), kind="external"))`                         | `Where` filters by `kind` or `tag`.                            |
| Deployment             | `deployment_view(key).include(Wildcard())`                             | Nodes and instances.                                           |
| Dynamic                | `dynamic_view(key).step(a, b, "label")`                                | See [Views](views.md#dynamic-views).                           |

The `-> system ->` predicate is written with `RawPredicate`, which
`likec4 validate` checks and this project does not. The alias in the text must
be the alias of the element.

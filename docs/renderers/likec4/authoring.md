# LikeC4 Authoring

A LikeC4 [`Project`][c4.contrib.likec4.Project] has four parts, each a property of the project:
`project.specification` (the vocabulary), `project.model` (elements and
relationships), `project.deployment` (nodes and instances) and `project.views`
([Views](views.md)).

```python
from c4.contrib.likec4 import Project, Rel, Wildcard

project = Project("Shop")

project.specification.element("actor", shape="person").element("system")

customer = project.model.element("actor", "Customer", alias="customer")
shop = project.model.element("system", "Online Shop", alias="shop")
customer >> Rel("buys goods") >> shop

project.views.element_view("index", "Landscape").include(Wildcard())
print(project.render())
```

`Project(name=None, default_renderer=None, view_key=None)` takes an optional
title and the view exported as an image by default. `project.render()` returns
the source and `project.save(path)` writes it.

## Specification

Every kind, tag and custom color has to be declared before it is used, once per
category. Declaring a name twice raises `ValueError`. Methods return the
specification, so they chain.

- `element(name, title=, technology=, description=, notation=, tags=, **style)`
  declares an element kind. The title, technology and tags are defaults for
  every element of the kind.
- `deployment_node(...)` declares a deployment node kind with the same arguments.
- `relationship(name, technology=, description=, **style)` declares a
  relationship kind.
- `tag(name, color=None)` declares a tag, written without `#`.
- `color(name, value)` declares a custom color from a hex or `rgb()`/`rgba()`
  value.

<!-- generated:start likec4-calls-specification -->
| Python call | Generated DSL |
|---|---|
| <pre><code>project.specification.element(&#10;    "actor", title="Actor", shape="person", color="blue")</code></pre> | <pre><code>element actor {&#10;  title "Actor"&#10;  style {&#10;    color blue&#10;    shape person&#10;  }&#10;}</code></pre> |
| <pre><code>project.specification.relationship(&#10;    "async", technology="AMQP", line="dotted", head="open")</code></pre> | <pre><code>relationship async {&#10;  technology "AMQP"&#10;  line dotted&#10;  head open&#10;}</code></pre> |
| <pre><code>project.specification.tag("internal", color="green")</code></pre> | <pre><code>tag internal { color green }</code></pre> |
| <pre><code>project.specification.color("brand", "#ff6600")</code></pre> | <pre><code>color brand #ff6600</code></pre> |
| <pre><code>project.specification.deployment_node("server", title="Server")</code></pre> | <pre><code>deploymentNode server { title "Server" }</code></pre> |
<!-- generated:end likec4-calls-specification -->

Names (kinds, tags, colors, aliases and keys) must contain only letters, digits,
hyphens and underscores, must not start with a digit and must not end with a
hyphen.

## Model elements

`project.model.element(kind, title, **kwargs)` creates an element of a declared
kind. Elements nest without limit in three ways: pass `parent=`, call
`parent.element(kind, title)`, or use the parent as a context manager.

<!-- generated:start likec4-calls-elements -->
| Python call | Generated DSL |
|---|---|
| <pre><code>customer = project.model.element(&#10;    "actor", "Customer", alias="customer")</code></pre> | <pre><code>customer = actor "Customer"</code></pre> |
| <pre><code>shop = project.model.element("system", "Shop", alias="shop")&#10;api = shop.element("container", "API", alias="api")</code></pre> | <pre><code>shop = system "Shop" {&#10;  api = container "API"&#10;}</code></pre> |
| <pre><code>with project.model.element("system", "Shop", alias="shop"):&#10;    project.model.element("container", "API", alias="api")</code></pre> | <pre><code>shop = system "Shop" {&#10;  api = container "API"&#10;}</code></pre> |
| <pre><code>project.model.element("system", "Shop",&#10;    summary="Online shop", technology="Django",&#10;    description="Takes **orders**.")</code></pre> | <pre><code>summary "Online shop"&#10;description '''Takes **orders**.'''&#10;technology "Django"</code></pre> |
| <pre><code>project.model.element("system", "Shop",&#10;    tags=["internal"], icon="tech:python")</code></pre> | <pre><code>#internal&#10;icon tech:python</code></pre> |
| <pre><code>project.model.element("system", "Shop",&#10;    metadata={"owner": "team-a", "env": ["dev", "prod"]},&#10;    links=["https://example.com", ("https://example.com/docs", "Docs")])</code></pre> | <pre><code>metadata {&#10;  owner "team-a"&#10;  env ["dev", "prod"]&#10;}&#10;link https://example.com&#10;link https://example.com/docs "Docs"</code></pre> |
| <pre><code>project.model.element("actor", "Customer",&#10;    color="brand", shape="person", opacity=50)</code></pre> | <pre><code>style {&#10;  color brand&#10;  shape person&#10;  opacity 50%&#10;}</code></pre> |
<!-- generated:end likec4-calls-elements -->

| Argument      | Meaning                                                                                    |
|---------------|--------------------------------------------------------------------------------------------|
| `alias`       | Identifier in the source. Derived from the title when omitted.                             |
| `summary`     | Short text, at most 150 characters.                                                        |
| `description` | Markdown description.                                                                      |
| `technology`  | Implementation technology.                                                                 |
| `tags`        | `list[str]` of declared tags, without `#`.                                                 |
| `icon`        | An icon reference such as `tech:python`. See [Styles](styles.md#icons).                    |
| `metadata`    | Mapping of identifier keys to a string or a list of strings.                               |
| `links`       | [`Link`][c4.contrib.likec4.Link] objects, URL strings or `(url, title)` pairs.                                       |
| style keywords | `color`, `shape`, `border`, `opacity`, `size`, ... See [Styles](styles.md).                |

An element needs a title or an alias. Identifiers come from `alias`, or are
derived from the title; collisions among siblings get `_2`, `_3` suffixes and
reserved words are avoided.

## Relationships

A relationship is created with `uses`, `used_by`, `>>` or `<<` on an element.
Both ends must belong to the same model. The first argument after the target is
the relationship `title`, passed positionally; every other option is a keyword.

- [`a.uses(b, title, **kwargs)`][c4.contrib.likec4.Element] and
  `b.used_by(a, title, **kwargs)` create the relationship from `a` to `b`.
- `a >> "title" >> b` and `b << "title" << a` do the same.
- [`Rel(title, **kwargs)`][c4.contrib.likec4.Rel] carries the options:
  `a >> Rel("title", technology="HTTPS") >> b`. A `Rel` is immutable, so one
  value can be used for any number of relationships.
- `a >> b` creates a relationship with no title; `a >> b | "title"` sets it.
  The pipe fills only an empty title and raises `ValueError` if one exists.

`project.model.relate(source, target, title, **kwargs)` is the lower-level call
that the forms above use.

<!-- generated:start likec4-calls-relationships -->
| Python call | Generated DSL |
|---|---|
| <pre><code>customer.uses(shop, "buys")</code></pre> | <pre><code>customer -&gt; shop "buys"</code></pre> |
| <pre><code>customer.uses(shop, "buys", kind="async", technology="HTTPS")</code></pre> | <pre><code>customer -[async]-&gt; shop "buys" { technology "HTTPS" }</code></pre> |
| <pre><code>customer.uses(shop, "talks", bidirectional=True)</code></pre> | <pre><code>customer &lt;-&gt; shop "talks"</code></pre> |
| <pre><code>customer.uses(shop, "buys", tags=["legacy"], line="dashed")</code></pre> | <pre><code>customer -&gt; shop "buys" {&#10;  #legacy&#10;  style { line dashed }&#10;}</code></pre> |
<!-- generated:end likec4-calls-relationships -->

The same relationships in the operator forms:

<!-- generated:start likec4-calls-relationship-forms -->
<!-- generated:end likec4-calls-relationship-forms -->

One element can be connected to several, in either direction, with a list on
one side: `a >> Rel("title") >> [b, c]`, `[a, b] >> Rel("title") >> c` and their
`<<` forms. Each list item gives one relationship, in list order, and the
expression returns the list. A list on both sides raises `ValueError("Either
source or destination must be a single element")` and creates nothing.

A list can stand on the left only together with `Rel(...)`: Python has no `>>`
between a `list` and a `str`, so `[a, b] >> "title" >> c` raises `TypeError`.
Use `[a, b] >> Rel("title") >> c`. With one element on the left, a string works:
`a >> "title" >> [b, c]`.

The `Rel` keywords are `description`, `technology`, `kind` (a declared relationship
kind), `bidirectional`, `tags`, `metadata`, `links`, `navigate_to` (the key of a
dynamic view, opened on click) and relationship style properties (`color`,
`line`, `head`, `tail`). LikeC4 forbids a relationship between an element and
its own ancestor or descendant; the renderer rejects it.

!!! note "`navigateTo` placement"

    LikeC4 does not allow `navigateTo` inside an element body, so elements have
    no `navigate_to`. It is available in relationships, in view predicates and
    in dynamic-view steps.

## Presets and helpers

`specification.element(...)` and `model.element(kind, ...)` are the primary API
and work with any kinds. Presets and helpers are an optional layer on top for
the C4 vocabulary.

A [`Preset`][c4.contrib.likec4.Preset] is plain data: element kinds,
relationship kinds and tags. `specification.use(preset)` declares them in order
through the same checks as manual declarations, so a name that is already
declared raises `ValueError`. Nothing is applied implicitly and `Project(...)`
starts with an empty specification.

```python
from c4.contrib.likec4 import C4, ElementKind, Project

project = Project("Shop")
project.specification.use(
    C4.with_(elements=[ElementKind("database", title="DB", style={"shape": "cylinder"})])
)

customer = project.model.person("Customer", alias="customer")
shop = project.model.system("Shop", alias="shop")
api = shop.container("API", alias="api", technology="Go")
```

- `C4` declares `person`, `system`, `container`, `component`, `database` and
  `external` with the shapes and colors of the [C4 cheat-sheet](c4-cheatsheet.md).
- `preset.with_(elements=, relationships=, tags=)` returns a copy where an entry
  replaces the one with the same name and new names are appended.
- You can build your own `Preset` from `ElementKind`, `RelationshipKind` and
  `Tag`.
- `Model` and `Element` have `person`, `system`, `container`, `component`,
  `database` and `external`. Each is `element(kind, title, **kwargs)` for the
  kind of the same name; on an element the result is a child of it. They check
  that the kind is declared in the specification, by a preset or by hand, and
  raise `ValueError` naming the kind otherwise. They do not check nesting.

The JSON and Python converters ignore presets and always write explicit kinds.

## Deployment

`project.deployment.node(kind, title, **kwargs)` creates deployment nodes of a
kind declared with `specification.deployment_node(...)`. Nodes nest (`parent=`,
`node.node(...)` or `with node:`) and have their own identifier namespace,
independent of the model. `node.instance(element, name=None, **kwargs)` places an
instance of a model element on a node. Nodes and instances take the same
relationship forms as elements (`uses`, `used_by`, `>>`, `<<`, `Rel`) and create
deployment relationships.

<!-- generated:start likec4-calls-deployment -->
| Python call | Generated DSL |
|---|---|
| <pre><code>prod = project.deployment.node(&#10;    "server", "Production", alias="prod")</code></pre> | <pre><code>prod = server "Production"</code></pre> |
| <pre><code>prod.instance(api, "api_1")&#10;prod.instance(api)</code></pre> | <pre><code>api_1 = instanceOf shop.api&#10;instanceOf shop.api</code></pre> |
| <pre><code>replica = prod.node("server", "Replica")</code></pre> | <pre><code>prod = server "Production" {&#10;  Replica = server "Replica"&#10;}</code></pre> |
| <pre><code>primary.uses(replica, "replicates to")</code></pre> | <pre><code>prod.primary -&gt; prod.replica "replicates to"</code></pre> |
| <pre><code>primary &gt;&gt; Rel("replicates to") &gt;&gt; replica</code></pre> | <pre><code>prod.primary -&gt; prod.replica "replicates to"</code></pre> |
<!-- generated:end likec4-calls-deployment -->

Instances accept `title`, `description`, `technology`, `tags`, `metadata`,
`links` and style properties. A node cannot hold several unnamed instances of
the same element; give each a name.

## Validation

The checks run when the project is rendered and raise [`LikeC4ValidationError`][c4.contrib.likec4.renderer.LikeC4ValidationError]
naming the element, step or view. They are listed in the
[Reference](reference.md#validation-rules) and
[Limitations](limitations.md#rules-checked-by-the-renderer).

Upstream: [specification](https://likec4.dev/dsl/specification/),
[model](https://likec4.dev/dsl/model/),
[deployment](https://likec4.dev/dsl/deployment/model/).

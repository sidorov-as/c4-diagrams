# LikeC4 Views

Views are created on `project.views`. LikeC4 has no fixed C4 view types: an
element view shows any part of the model, a deployment view shows the
deployment, and a dynamic view shows an ordered sequence of interactions. Keys
are unique across all view types.

| Factory                                            | Source                  | Takes                                          |
|----------------------------------------------------|-------------------------|------------------------------------------------|
| `element_view(key, title=None, of=None, ...)`      | `view key of scope`     | `include`, `exclude`, `style`, `auto_layout`   |
| `deployment_view(key, title=None, ...)`            | `deployment view key`   | `include`, `exclude`, `style`, `auto_layout`   |
| `dynamic_view(key, title=None, variant=, ...)`     | `dynamic view key`      | `step`, `back`, `auto_layout`                  |

All three also take `description`, `tags` and `links`. Rules are written in the
order they are added.

<!-- generated:start likec4-calls-views -->
| Python call | Generated DSL |
|---|---|
| <pre><code>project.views.element_view("index", "Landscape", of=shop).include(Wildcard())</code></pre> | <pre><code>view index of shop {&#10;  title "Landscape"&#10;  include *&#10;}</code></pre> |
| <pre><code>view = project.views.element_view("index")&#10;view.include(Children(shop), Descendants(shop))</code></pre> | <pre><code>include shop.*, shop.**</code></pre> |
| <pre><code>view = project.views.element_view("index")&#10;view.include(Between(customer, shop))&#10;view.include(Between(customer, shop, both=True))&#10;view.include(Incoming(shop), Outgoing(shop), InOut(shop))</code></pre> | <pre><code>include customer -&gt; shop&#10;include customer &lt;-&gt; shop&#10;include -&gt; shop&#10;include shop -&gt;&#10;include -&gt; shop -&gt;</code></pre> |
| <pre><code>view = project.views.element_view("index")&#10;view.include(Where(shop, tag="legacy"))&#10;view.include(RawPredicate("shop.api"))</code></pre> | <pre><code>include shop where tag is #legacy&#10;include shop.api</code></pre> |
| <pre><code>view = project.views.element_view("index")&#10;view.include(Wildcard()).exclude(customer)</code></pre> | <pre><code>exclude customer</code></pre> |
| <pre><code>view = project.views.element_view("index")&#10;view.style(shop, color="brand", opacity=40)</code></pre> | <pre><code>style shop {&#10;  color brand&#10;  opacity 40%&#10;}</code></pre> |
| <pre><code>view = project.views.element_view("index")&#10;view.auto_layout("LeftRight", rank_sep=80, node_sep=60)</code></pre> | <pre><code>autoLayout LeftRight 80 60</code></pre> |
| <pre><code>view = project.views.element_view("index")&#10;view.include(shop, navigate_to="flow")</code></pre> | <pre><code>include shop with { navigateTo flow }</code></pre> |
| <pre><code>view = project.views.deployment_view("live", "Live")&#10;view.include(Wildcard())</code></pre> | <pre><code>deployment view live {&#10;  title "Live"&#10;  include *&#10;}</code></pre> |
| <pre><code>flow = project.views.dynamic_view(&#10;    "flow", "Checkout", variant="sequence")&#10;flow.step(customer, shop, "pays", technology="HTTPS")&#10;flow.back(customer, shop, "confirms")</code></pre> | <pre><code>dynamic view flow {&#10;  title "Checkout"&#10;  variant sequence&#10;  customer -&gt; shop "pays" { technology "HTTPS" }&#10;  customer &lt;- shop "confirms"&#10;}</code></pre> |
<!-- generated:end likec4-calls-views -->

## Predicates

`include`, `exclude` and `style` take elements (or deployment nodes and
instances) and these predicate objects:

| Object                       | Written as                | Meaning                                       |
|------------------------------|---------------------------|-----------------------------------------------|
| [`Wildcard()`][c4.contrib.likec4.Wildcard]                 | `*`                       | The view scope, or all top-level elements.    |
| [`Children(x)`][c4.contrib.likec4.Children]                | `x.*`                     | Direct children of `x`.                       |
| [`Descendants(x)`][c4.contrib.likec4.Descendants]             | `x.**`                    | All nested elements of `x`.                   |
| [`Between(a, b)`][c4.contrib.likec4.Between]               | `a -> b`                  | Relationships from `a` to `b`; `both=True` writes `<->`. |
| [`Incoming(x)`][c4.contrib.likec4.Incoming]                | `-> x`                    | Relationships that enter `x`.                 |
| [`Outgoing(x)`][c4.contrib.likec4.Outgoing]                | `x ->`                    | Relationships that leave `x`.                 |
| [`InOut(x)`][c4.contrib.likec4.InOut]                      | `-> x ->`                 | Relationships that enter or leave `x`.        |
| [`Where(x, tag=, kind=)`][c4.contrib.likec4.Where]      | `x where tag is #t ...`   | A filter over another item.                   |
| [`RawPredicate(text)`][c4.contrib.likec4.RawPredicate]         | text as is                | Anything else; checked only by `likec4 validate`. |

!!! note "`Rel` is not a view predicate"

    [`Rel`][c4.contrib.likec4.Rel] is the relationship expression
    (`a >> Rel("title") >> b`) used in the model. In a view, a relationship
    predicate is `Between`, `Incoming`, `Outgoing` or `InOut`.

`include(..., navigate_to="view-key")` writes `with { navigateTo ... }`. A style
rule needs at least one property and cannot target a relationship predicate.
`Where` cannot wrap a `Where` or a `RawPredicate`, and the relationship
predicates cannot connect them either; write a `RawPredicate` instead.

An element view `of X` may only include elements inside `X`. The renderer cannot
check this statically.

## Auto layout

`view.auto_layout(direction="TopBottom", rank_sep=None, node_sep=None)` adds an
`autoLayout` rule. The directions are listed in the
[Reference](reference.md#allowed-values). `node_sep` needs `rank_sep`.

## Deployment views

`deployment_view` works over deployment nodes and instances. Its `include`
takes no `navigate_to`: `with { ... }` overrides are not generated in
deployment views.

## Dynamic views

`dynamic_view(key, title, variant="diagram")` takes a flat list of steps.
`variant` is `"diagram"` or `"sequence"`.

- `view.step(source, target, title, **properties)` writes `source -> target`.
- `view.back(receiver, sender, title, **properties)` writes `receiver <- sender`.
- Step properties are `description`, `technology`, `notes`, `navigate_to`
  (a dynamic view key) and `color`.

Steps connect model elements. Parallel and alternative blocks are not supported.

```python
from c4.contrib.likec4 import Project

project = Project("Checkout")
project.specification.element("actor").element("system")

customer = project.model.element("actor", "Customer", alias="customer")
shop = project.model.element("system", "Shop", alias="shop")

flow = project.views.dynamic_view("checkout", "Checkout", variant="sequence")
flow.step(customer, shop, "pays", technology="HTTPS")
flow.back(customer, shop, "receives a receipt")
print(project.render())
```

Upstream: [views](https://likec4.dev/dsl/views/),
[dynamic views](https://likec4.dev/dsl/views/dynamic/),
[predicates](https://likec4.dev/dsl/views/predicates/).

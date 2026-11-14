# LikeC4 → `Project`

Best-effort. Output is a `c4.contrib.likec4.Project`. APIs: `../../c4-diagrams/references/whole-architecture.md`.
Imitate the examples; do not look for a rule table.

Order in the file: specification, model, views. Set `alias` to the LikeC4 identifier on every element.

## C4 kinds, nesting, relationships, a view

```
specification {
  element person
  element system
  element container
}
model {
  customer = person "Customer"
  shop = system "Shop" {
    web = container "Web App" { technology "Django" }
    db = container "Database" { technology "PostgreSQL" }
  }
  customer -> shop.web "Uses" { technology "HTTPS" }
  shop.web -> shop.db "Reads and writes"
}
views {
  view containers of shop {
    title "Containers"
    include *
  }
}
```

```python
from c4.contrib.likec4 import C4, Project, Rel, Wildcard

project = Project("Shop")
project.specification.use(C4)
customer = project.model.person("Customer", alias="customer")
shop = project.model.system("Shop", alias="shop")
web = shop.container("Web App", alias="web", technology="Django")
db = shop.container("Database", alias="db", technology="PostgreSQL")
customer >> Rel("Uses", technology="HTTPS") >> web
web >> Rel("Reads and writes") >> db
project.views.element_view("containers", "Containers", of=shop).include(Wildcard())
```

`specification.use(C4)` is only right when the kinds are exactly `person`, `system`, `container`, `component`, `database`,
`external`. For any other kinds, declare them (next example).

## Own kinds, tags, colors, two views

```
specification {
  color grey #999999
  element actor { style { shape person } }
  element service
  tag legacy { color grey }
}
model {
  client = actor "Client"
  api = service "API" {
    #legacy
    cache = service "Cache"
  }
  worker = service "Worker"
  client -> api "Calls"
  api -> worker "Queues jobs"
}
views {
  view index { title "Landscape"  include * }
  view api-view of api { title "API"  include * }
}
```

```python
from c4.contrib.likec4 import Project, Rel, Wildcard

project = Project("Shop")
project.specification.element("actor", shape="person")
project.specification.element("service")
project.specification.color("grey", "#999999")
project.specification.tag("legacy", "grey")
client = project.model.element("actor", "Client", alias="client")
api = project.model.element("service", "API", alias="api", tags=["legacy"])
cache = api.element("service", "Cache", alias="cache")
worker = project.model.element("service", "Worker", alias="worker")
client >> Rel("Calls") >> api
api >> Rel("Queues jobs") >> worker
project.views.element_view("index", "Landscape").include(Wildcard())
project.views.element_view("api-view", "API", of=api).include(Wildcard())
```

Mapping: `view x of y` is `element_view("x", title, of=y)`; a view without `of` omits it. `include` and `exclude`
predicates go to `.include(...)` and `.exclude(...)`; plain `*` is `Wildcard()`. Tag colors are names declared with
`specification.color`, not hex.

LikeC4 rejects a relationship between an element and its own ancestor or descendant. If the source has one, report it
as dropped.

## Report as dropped

- `import`, `global`, `style` blocks with no `**style` or tag equivalent, `autoLayout` directions, `navigateTo`
- `dynamic view` variants the example above does not cover (report; do not guess)
- `link`, `icon` values the helper does not take
- `deployment` models, unless you can write them with `project.deployment` from the reference without guessing
- a relationship whose endpoint is not in the file (report it; do not create it)

Anything else you cannot place with an example above is dropped too, not invented.

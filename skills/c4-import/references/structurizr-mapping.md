# Structurizr DSL → `Workspace`

Best-effort. Output is a `c4.contrib.structurizr.Workspace`. APIs: `../../c4-diagrams/references/whole-architecture.md`.
Imitate the examples; do not look for a rule table.

Set `alias` to the DSL identifier on every element. Declare elements in source order; nest with `owner=`.

## Model, nesting, relationships, one view, tags and styles

```
workspace "Shop" {
  model {
    customer = person "Customer"
    shop = softwareSystem "Shop" {
      web = container "Web App" "" "Django"
      db = container "Database" "" "PostgreSQL" "Database"
    }
    payments = softwareSystem "Payment Gateway" "" "External"
    customer -> web "Uses" "HTTPS"
    web -> db "Reads and writes"
    web -> payments "Charges cards"
  }
  views {
    container shop "containers" {
      include *
      autoLayout lr
    }
    styles {
      element "Database" { shape Cylinder }
      element "External" { background #999999 }
    }
  }
}
```

```python
from c4.contrib.structurizr import AutoLayout, Rel, Workspace

workspace = Workspace("Shop")
with workspace.model as model:
    customer = model.Person("Customer", alias="customer")
    shop = model.SoftwareSystem("Shop", alias="shop")
    payments = model.SoftwareSystem("Payment Gateway", alias="payments", tags=["External"])
    web = model.Container("Web App", technology="Django", owner=shop, alias="web")
    db = model.Container("Database", technology="PostgreSQL", owner=shop, alias="db", tags=["Database"])
    customer >> Rel("Uses", technology="HTTPS") >> web
    web >> "Reads and writes" >> db
    web >> "Charges cards" >> payments

workspace.views.ContainerView(shop, key="containers", auto_layout=AutoLayout())
workspace.styles.tag("Database", shape="Cylinder")
workspace.styles.tag("External", background="#999999")
```

Mapping: after the name, `container` takes description, `technology`, then tags (`tags=[...]`). `include *` is the
default and needs no argument. `autoLayout lr` is `AutoLayout()`; other directions go in `AutoLayout(...)`.

## Components and several views

```
workspace "Shop" {
  model {
    shop = softwareSystem "Shop" {
      web = container "Web App" {
        cart = component "Cart"
        prices = component "Prices"
      }
    }
    cart -> prices "Looks up"
  }
  views {
    systemLandscape "landscape" { include * }
    systemContext shop "context" { include * }
    component web "components" "Web components" { include * }
  }
}
```

```python
from c4.contrib.structurizr import Workspace

workspace = Workspace("Shop")
with workspace.model as model:
    shop = model.SoftwareSystem("Shop", alias="shop")
    web = model.Container("Web App", owner=shop, alias="web")
    cart = model.Component("Cart", owner=web, alias="cart")
    prices = model.Component("Prices", owner=web, alias="prices")
    cart >> "Looks up" >> prices

workspace.views.SystemLandscapeView(key="landscape")
workspace.views.SystemContextView(shop, key="context")
workspace.views.ComponentView(web, key="components", title="Web components")
```

Mapping: `systemLandscape`, `systemContext`, `container`, `component`, `dynamic`, `deployment` views are the matching
`workspace.views.*View` methods. The view key is the quoted key, the next string is the title.

Explicit `include` and `exclude` expressions other than `*` are reported as approximated; do not invent selectors.

## Report as dropped

- `!script`, `!plugin`, `!include` (local or remote), `!identifiers`, `!impliedRelationships`, `!docs`, `!adrs`
- `themes`, `branding`, `configuration`, `animation` steps, `autoLayout` separations that `AutoLayout` cannot hold
- `group` blocks (children keep their owner; the group name goes to the report)
- `perspectives`, `properties` with no `properties=` home, `url` on views
- a relationship whose endpoint identifier is not declared in the file (report it; do not create it)

Anything else you cannot place with an example above is dropped too, not invented.

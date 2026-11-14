# D2 → `Diagram`

Best-effort. Output is a portable `Diagram`. D2 has shapes and classes but no C4 kinds, so every kind is proposed and
shown to the user. Never assign kinds silently.

Set `alias` to the D2 key on every element. A D2 container with children becomes a boundary.

## Propose a kind

| D2 shape or class                | Proposed kind                       |
|----------------------------------|-------------------------------------|
| `shape: person`, `c4-person`     | `Person`                            |
| `shape: cylinder`                | `ContainerDb`                       |
| `shape: queue`                   | `ContainerQueue`                    |
| container with children          | `SystemBoundary` (or `Boundary`)    |
| rectangle, no class              | undecided: ask                      |

The diagram class follows the proposed kinds: a mix of `Person`, systems and containers is `ContainerDiagram`; only
people and systems is `SystemContextDiagram`. If unclear, ask.

## Ask about undecided nodes

List every proposed kind in one message, then ask in the same message about each undecided node:

```
Proposed kinds: customer → Person, db → ContainerDb, shop → SystemBoundary.
Which kind is "worker" (plain rectangle, no class)? System, Container, Component, or something else?
```

If the user has no preference, make it a `Container` and say so in the report.

## Nested nodes, shapes, relationships

```
customer: Customer { shape: person }
shop: Shop {
  web: Web App
  db: Database { shape: cylinder }
}
customer -> shop.web: Uses
shop.web -> shop.db: Reads and writes
```

```python
from c4 import Container, ContainerDb, ContainerDiagram, Person, Rel, SystemBoundary

with ContainerDiagram("Shop") as diagram:
    customer = Person("Customer", alias="customer")
    with SystemBoundary("Shop", alias="shop"):
        web = Container("Web App", alias="web")
        db = ContainerDb("Database", alias="db")
    customer >> Rel("Uses") >> web
    web >> Rel("Reads and writes") >> db
```

`web` here is the plain rectangle the user confirmed as a container.

## Queue and title

```
direction: right
title: Jobs
api: API
queue: Jobs { shape: queue }
api -> queue: Publishes
```

```python
from c4 import Container, ContainerDiagram, ContainerQueue, Rel

with ContainerDiagram("Jobs") as diagram:
    api = Container("API", alias="api")
    queue = ContainerQueue("Jobs", alias="queue")
    api >> Rel("Publishes") >> queue
```

## Report as dropped

- layout: `direction`, `grid-*`, `near`, `width`, `height`, `top`, `left`
- icons, images, `style.*` values that no render option holds, themes, `vars`, `...@import`
- animation, `sql_table` and `class` shapes, `layers`, `scenarios`, `steps`
- a connection whose endpoint is not declared in the file (report it; do not create it)

Anything else you cannot place with an example above is dropped too, not invented.

# Portable Core and Backend Extensions

`c4-diagrams` separates portable C4 model data from backend-specific rendering
hints.

The portable core includes C4 elements, boundaries, concrete diagram types, and
the generic [`Rel`](../api_docs/relationships/#c4.diagrams.core.Rel) relationship. Code that stays within
that subset can be rendered by different backends, subject to each backend's
supported C4 syntax.

Backend-specific features are passed with explicit backend kwargs, such as
`plantuml=`, `mermaid=`, or `d2=`. Use those kwargs for data that only one
renderer understands, while keeping the portable core free of
renderer-specific hints.

!!! example "Example: PlantUML-specific features"

    PlantUML directional relationships, bidirectional relationships, layout
    helpers, dynamic indexes, sprites, links, tags, and similar hints are
    convenience DSL for PlantUML rendering. They are not portable C4 model data.

Renderers validate extension data before rendering. By default, foreign
extension data is ignored: PlantUML consumes `plantuml={...}` data and Mermaid
consumes `mermaid={...}` data, while D2 consumes `d2={...}` data. Enable strict
extension validation when a diagram must fail fast if it contains extension
data owned by another backend.

## Portable core example

This diagram uses only portable C4 elements and [`Rel`](../api_docs/relationships/#c4.diagrams.core.Rel),
so it can be rendered to PlantUML, Mermaid, or D2 source:

```python
from c4 import Person, Rel, System, SystemContextDiagram


with SystemContextDiagram("Order Processing") as diagram:
    customer = Person("Customer", "Places orders")
    order_system = System("Order System", "Processes customer orders")

    customer >> Rel("Places orders using") >> order_system


plantuml_source = diagram.as_plantuml()
mermaid_source = diagram.as_mermaid()
d2_source = diagram.as_d2()
```

## PlantUML-specific DSL

Directional relationship shortcuts and layout helpers live in
`c4.contrib.plantuml` because they map to PlantUML/C4-PlantUML behavior:

```python
from c4 import Container, ContainerDiagram, Person, System
from c4.contrib.plantuml import LayRight, RelRight


with ContainerDiagram("Order Processing") as diagram:
    customer = Person("Customer")
    order_system = System("Order System")
    api = Container("API", "Accepts order requests", technology="FastAPI")
    database = Container("Database", "Stores orders", technology="PostgreSQL")

    customer >> RelRight("Uses") >> api
    api >> RelRight("Reads and writes") >> database

    LayRight(api, database)
```

## Backend extension kwargs

Use backend kwargs for renderer-specific element and relationship metadata. The
data is stored in the element's `extensions` mapping under the backend name:

```python
from c4 import ContainerDb, ContainerDiagram


with ContainerDiagram("Order Processing") as diagram:
    orders = ContainerDb(
        "Orders Database",
        "Stores order state",
        technology="PostgreSQL",
        plantuml={"tags": ["storage"]},
    )


assert orders.extensions == {"plantuml": {"tags": ["storage"]}}
```

## Compatibility envelope

The same extension data can be provided through `extensions=`:

```python
from c4 import ContainerDb, ContainerDiagram


with ContainerDiagram("Order Processing") as diagram:
    orders = ContainerDb(
        "Orders Database",
        "Stores order state",
        technology="PostgreSQL",
        extensions={"plantuml": {"tags": ["storage"]}},
    )


assert orders.extensions == {"plantuml": {"tags": ["storage"]}}
```

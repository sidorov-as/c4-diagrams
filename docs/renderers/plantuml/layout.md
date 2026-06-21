# PlantUML Relationship and Layout Helpers

Directional relationships, bidirectional relationships, and relative layout
helpers are PlantUML-only convenience DSL. Import them from
`c4.contrib.plantuml`; they are not portable C4 model data.

## Relationship helpers

```python
from c4 import Container, ContainerDiagram, Person
from c4.contrib.plantuml import BiRelRight, RelDown, RelRight


with ContainerDiagram("Orders") as diagram:
    customer = Person("Customer")
    web = Container("Web App", "Accepts customer traffic", technology="React")
    api = Container("Orders API", "Handles order requests", technology="Python")
    worker = Container("Worker", "Processes async jobs", technology="Python")

    customer >> RelRight("Uses") >> web
    web >> BiRelRight("Calls") >> api
    api >> RelDown("Publishes jobs") >> worker
```

Available relationship helpers:

| Direction or behavior | Helpers                                    |
|-----------------------|--------------------------------------------|
| Backward              | `RelBack`                                  |
| Neighbor              | `RelNeighbor`, `RelBackNeighbor`           |
| Down                  | `RelD`, `RelDown`, `BiRelD`, `BiRelDown`   |
| Up                    | `RelU`, `RelUp`, `BiRelU`, `BiRelUp`       |
| Left                  | `RelL`, `RelLeft`, `BiRelL`, `BiRelLeft`   |
| Right                 | `RelR`, `RelRight`, `BiRelR`, `BiRelRight` |
| Bidirectional generic | `BiRel`, `BiRelNeighbor`                   |

## Relative layout helpers

Layout helpers map to C4-PlantUML `Lay_*` macros and constrain where one
element is placed relative to another.

```python
from c4 import Container, ContainerDiagram
from c4.contrib.plantuml import LayRight


with ContainerDiagram("Orders") as diagram:
    api = Container("Orders API")
    database = Container("Orders DB")

    LayRight(database, api)
```

Available layout helpers:

| Position | Helpers            |
|----------|--------------------|
| Down     | `LayD`, `LayDown`  |
| Up       | `LayU`, `LayUp`    |
| Right    | `LayR`, `LayRight` |
| Left     | `LayL`, `LayLeft`  |

Use diagram-level render options such as `layout_top_down()` or
`layout_left_right()` for the broad direction of the diagram, and use `Lay*`
helpers only when a specific relative placement matters.

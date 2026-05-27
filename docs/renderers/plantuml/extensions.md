# PlantUML Extensions

PlantUML-specific element and relationship metadata should be passed with the
`plantuml=` constructor kwarg in Python code. The data is normalized into
`element.extensions["plantuml"]` and is consumed only by the PlantUML renderer.

```python
from c4 import ContainerDb, ContainerDiagram, Person, Rel


with ContainerDiagram("Orders") as diagram:
    user = Person("Customer", plantuml={"tags": ["external"]})
    database = ContainerDb(
        "Orders DB",
        "Stores order state",
        technology="PostgreSQL",
        plantuml={
            "tags": ["storage"],
            "sprite": "database",
            "link": "https://example.com/runbooks/orders-db",
        },
    )

    user >> Rel("Reads orders", plantuml={"tags": ["audit"]}) >> database
```

## Supported fields

| Target | Fields |
|--------|--------|
| Relationships | `sprite`, `tags`, `link`, `index` |
| People | `sprite`, `tags`, `link`, `type` |
| Software systems | `sprite`, `tags`, `link`, `type`, `base_shape` |
| Storage systems | `sprite`, `tags`, `link`, `type` |
| Containers | `sprite`, `tags`, `link`, `base_shape` |
| Storage containers | `sprite`, `tags`, `link` |
| Components | `sprite`, `tags`, `link`, `base_shape` |
| Storage components | `sprite`, `tags`, `link` |
| Boundaries | `tags`, `link`, `type` |
| Deployment nodes | `sprite`, `tags`, `link`, `type` |

`index` is primarily used by [dynamic diagrams](dynamic-indexes.md). Tags and
style definitions are rendered by C4-PlantUML and are configured through
[PlantUML render options](styles-and-options.md).

!!! note "Compatibility"

    `extensions={"plantuml": {...}}` still works and normalizes to the same
    `element.extensions` structure. Prefer `plantuml={...}` for new Python
    authoring, and keep `extensions=` for Python multi-backend payloads or
    advanced escape hatches.

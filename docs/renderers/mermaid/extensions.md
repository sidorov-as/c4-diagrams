# Mermaid Extensions

Mermaid-specific metadata should be passed with the `mermaid=` constructor kwarg
in Python code. The data is normalized into `element.extensions["mermaid"]` and
is consumed only by the Mermaid renderer.

```python
from c4 import ContainerBoundary, ContainerDiagram


with ContainerDiagram("Orders") as diagram:
    with ContainerBoundary(
        "Order System",
        mermaid={"type": "System_Boundary"},
    ):
        pass
```

## Supported fields

| Target | Fields |
|--------|--------|
| Boundaries | `tags`, `link`, `type` |

Mermaid extension support is intentionally small because Mermaid C4 has a
smaller syntax surface than C4-PlantUML. PlantUML fields such as `sprite`,
`base_shape`, and relationship `index` are not Mermaid features.

## Deployment node variants

Mermaid supports the C4 deployment node macros `Node_L` and `Node_R`. In Python,
use `NodeLeft` and `NodeRight` from `c4.contrib.mermaid`:

```python
from c4 import DeploymentDiagram
from c4.contrib.mermaid import NodeLeft, NodeRight


with DeploymentDiagram("Network") as diagram:
    with NodeLeft("Public Subnet"):
        pass

    with NodeRight("Private Subnet"):
        pass
```

These classes are shared C4 macro helpers. They are not portable core deployment
model classes, but they are supported by the Mermaid renderer and Mermaid JSON
schema.

!!! note "Compatibility"

    `extensions={"mermaid": {...}}` still works and normalizes to the same
    `element.extensions` structure. Prefer `mermaid={...}` for new Python
    authoring, and keep `extensions=` for Python multi-backend payloads or
    advanced escape hatches.

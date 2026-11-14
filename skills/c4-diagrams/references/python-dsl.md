# Portable Python DSL

Everything below imports from `c4`. Docs: https://sidorov-as.github.io/c4-diagrams/concepts/diagrams/
and https://sidorov-as.github.io/c4-diagrams/api_docs/core/

## Diagrams

Open one in a `with` block; elements and relationships created inside belong to it.

| Class                    | Shows                                | Typical contents                                                             |
|--------------------------|--------------------------------------|------------------------------------------------------------------------------|
| `SystemContextDiagram`   | systems and people around one system | `Person`, `System*`, `SystemBoundary`, `EnterpriseBoundary`                  |
| `SystemLandscapeDiagram` | all systems of an enterprise         | same, usually in `EnterpriseBoundary`                                        |
| `ContainerDiagram`       | containers inside a system           | `Container*`, `SystemBoundary`, `ContainerBoundary`, plus people and systems |
| `ComponentDiagram`       | components inside a container        | `Component*`, `ContainerBoundary`, plus containers, systems                  |
| `DynamicDiagram`         | runtime interaction order            | any elements; number labels (`"1. Places order"`)                            |
| `DeploymentDiagram`      | infrastructure topology              | `Node`, `DeploymentNode`, `Container*`                                       |

Constructor: `Diagram(title=None, default_renderer=None, render_options=None)`.

Output methods: `as_plantuml()`, `as_mermaid()`, `as_d2()`, `render(renderer=None)`, `save(...)`,
`save_as_plantuml(path)`, `save_as_mermaid(path)`, `save_as_d2(path)`. Attributes: `elements`, `relationships`.

## Elements

All take `(label, description=None, ..., alias=None)`. Kinds with a `technology` take it as the third positional
argument. `*Ext` marks an external element; `*Db` and `*Queue` change the shape.

| Level     | Classes                                                                                             |
|-----------|-----------------------------------------------------------------------------------------------------|
| Person    | `Person`, `PersonExt`                                                                               |
| System    | `System`, `SystemExt`, `SystemDb`, `SystemDbExt`, `SystemQueue`, `SystemQueueExt`                   |
| Container | `Container`, `ContainerExt`, `ContainerDb`, `ContainerDbExt`, `ContainerQueue`, `ContainerQueueExt` |
| Component | `Component`, `ComponentExt`, `ComponentDb`, `ComponentDbExt`, `ComponentQueue`, `ComponentQueueExt` |

`alias` is the identifier in generated source. It is derived from the label when omitted; set it when labels are
non-ASCII, duplicated, or must stay stable.

## Boundaries and nesting

Boundaries are context managers; elements created inside belong to them. Boundaries can nest.

| Class                    | Use                                                            |
|--------------------------|----------------------------------------------------------------|
| `SystemBoundary`         | the system whose containers or sub-systems are shown           |
| `EnterpriseBoundary`     | the enterprise around systems and people                       |
| `ContainerBoundary`      | the container whose components are shown                       |
| `Boundary`               | generic base boundary                                          |
| `Node`, `DeploymentNode` | deployment infrastructure; nest them (cloud, cluster, runtime) |

A container is not a boundary: group with `ContainerBoundary`. Mermaid rejects relationships that end on a boundary.

## Relationships

```python
a >> Rel("Uses", "HTTPS") >> b  # label, technology
a >> "Uses" >> b  # label only
a >> b | "Uses"  # pipe sets an empty label once
a << Rel("Uses") << b  # reversed: b uses a
a >> Rel("Uses") >> [b, c]  # one-to-many
[b, c] >> Rel("Uses") >> a  # many-to-one; a list needs Rel(...), not a string
a.uses(b, label="Uses");
a.used_by(b, label="Uses")
```

`Rel(label=None, description=None, technology=None, ...)`. `Relationship` is the base class. A relationship made with
`a >> b` has no label; PlantUML and Mermaid then write `uses`.

## Properties

- `element.add_property("Key", "Value")` adds a row (PlantUML table; D2 with `include_properties=True`; Mermaid
  ignores).
- `element.with_properties(("Runtime", "Python 3.12"), ("Team", "Platform"))` returns the element.
- `with_properties(factory_or_element, ("Key", "Value"))` (module function) also wraps a `partial` factory.
- `relationship.set_property_header("Key", "Value", "Notes")`, then `add_property(...)`.

## Backend kwargs

Renderer-specific data goes in `plantuml={...}`, `mermaid={...}` or `d2={...}` (stored under `.extensions`; also
`extensions={...}`). A renderer ignores the other backends' data. Helpers live in `c4.contrib.plantuml` (`RelRight`,
`LayRight`, `Index`, `DeploymentNodeLeft`), `c4.contrib.mermaid`, `c4.contrib.d2`, `c4.contrib.c4_macros` (`NodeLeft`,
`NodeRight`). They are not portable; see [backends.md](backends.md).

## Enums

`DiagramFormat` and its members `PNG`, `SVG`, `EPS`, `LATEX`, `TXT`, `UTXT` name export formats.

## Example

```python
from c4 import Container, ContainerDb, ContainerDiagram, Person, Rel, SystemBoundary, SystemExt

with ContainerDiagram("Shop") as diagram:
    customer = Person("Customer")
    payments = SystemExt("Payment Gateway")

    with SystemBoundary("Shop"):
        web = Container("Web App", technology="Django")
        db = ContainerDb("Database", technology="PostgreSQL")

    customer >> Rel("Uses", technology="HTTPS") >> web
    web >> "Reads and writes" >> db
    web >> "Charges" >> payments
```

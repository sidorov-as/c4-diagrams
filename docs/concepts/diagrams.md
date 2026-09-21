# Diagrams and Components

!!! note

    You can find a detailed description of the different C4 diagram types and components in the
    corresponding sections of the [documentation](portable/system-context.md).

    For the boundary between backend-neutral model data and renderer-specific hints, see
    [Portable core and backend extensions](portable-core-and-extensions.md).

## Diagrams

A diagram is built inside a `with` block. Elements declared in the block are added to the diagram,
and `>> Rel(...) >>` connects them:

```python
from c4 import Person, Rel, System, SystemContextDiagram

with SystemContextDiagram("Example system context") as diagram:
    user = Person(label="User", description="System user")
    backend = System(label="Backend API", description="Main application backend")

    user >> Rel("Uses HTTP API") >> backend

print(diagram.as_plantuml())
```

Each C4 diagram type is implemented as a subclass of [`Diagram`][c4.diagrams.core.Diagram]:

```python
from c4 import (
    SystemContextDiagram,
    SystemLandscapeDiagram,
    ContainerDiagram,
    ComponentDiagram,
    DynamicDiagram,
    DeploymentDiagram,
)
```

A diagram is turned into text by a renderer. [`Diagram.render()`][c4.diagrams.core.Diagram.render]
uses the diagram's `default_renderer` or one you pass, the `as_plantuml()`,
`as_mermaid()` and `as_d2()` shortcuts use a ready-made renderer, and
[`Diagram.save()`][c4.diagrams.core.Diagram.save] writes the result to a file:

```python
print(diagram.as_plantuml())
diagram.save_as_plantuml("output.puml")
```

The renderers, their options and the image export backends are described in
[Rendering backends](../renderers/comparison.md).

## Elements

Elements such as **Person**, **System**, **Container** or **Component** are created inside a diagram context.

### Low-level `Diagram` and `Element`

[`Diagram`][c4.diagrams.core.Diagram] and [`Element`][c4.diagrams.core.Element] are the base classes behind
the concrete diagram and element types. Application code uses the concrete classes above; the base classes are
shown here because the examples on this page use them to keep the code short:

```python
from c4.diagrams.core import Diagram, Element

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")


assert diagram.elements == [element1, element2]
```

Each C4 element type is implemented as a subclass of  [`Element`][c4.diagrams.core.Element]:

```python
from c4 import (
    Person,
    PersonExt,
    System,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemQueue,
    SystemQueueExt,
    Component,
    ComponentDb,
    ComponentDbExt,
    ComponentExt,
    ComponentQueue,
    ComponentQueueExt,
    Container,
    ContainerDb,
    ContainerDbExt,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
    DeploymentNode,
    Node,
)
from c4.contrib.c4_macros import NodeLeft, NodeRight
from c4.contrib.plantuml import DeploymentNodeLeft, DeploymentNodeRight
```

<br/>

## Relationships

[`Relationship`][c4.diagrams.core.Relationship] represents a connection between elements and may include additional
properties such as direction and label.

A relationship object contains four primary attributes: **label**, **relationship_type**,
**from_element**, and **to_element**.

The portable core relationship shortcut is [`Rel`][c4.diagrams.core.Rel]:

```python
from c4.diagrams.core import Rel
```


??? abstract "PlantUML-specific relationship"

    PlantUML-specific relationship shortcuts for direction, bidirectional
    relationships, back relationships, and neighbor relationships are available
    from `c4.contrib.plantuml`:

    ```python
    from c4.contrib.plantuml import (
        BiRel,
        BiRelD,
        BiRelDown,
        BiRelL,
        BiRelLeft,
        BiRelNeighbor,
        BiRelR,
        BiRelRight,
        BiRelU,
        BiRelUp,
        RelBack,
        RelBackNeighbor,
        RelD,
        RelDown,
        RelL,
        RelLeft,
        RelNeighbor,
        RelR,
        RelRight,
        RelU,
        RelUp,
    )
    ```

Relationships must be declared within a diagram context:

```python
from c4.diagrams.core import Diagram, Element, Rel

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")

    element1 >> Rel("Uses") >> element2


assert diagram.relationships[0].label == "Uses"
assert diagram.relationships[0].from_element == element1
assert diagram.relationships[0].to_element == element2
```

<br/>

There are several ways to declare relationships:

#### Simple cases

A relationship can be declared using its **label**:

```python
from c4.diagrams.core import Diagram, Element

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")

    element1 >> "Uses" >> element2
```

Alternatively, a relationship can be declared using an explicit relationship object:

```python
from c4.diagrams.core import Diagram, Element, Rel

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")

    element1 >> Rel("Uses") >> element2
```

??? note "Rel attributes"

    [`Rel`][c4.diagrams.core.Rel] lets you specify portable relationship attributes
    such as `technology` and `description`.

    PlantUML-specific attributes such as links, tags, and dynamic indexes belong
    under the `plantuml={...}` kwarg. PlantUML relationship shortcuts such as
    [`RelUp`][c4.contrib.plantuml.RelUp] and [`RelLeft`][c4.contrib.plantuml.RelLeft]
    are available from `c4.contrib.plantuml`.

    In most cases, a plain string label (`"Uses"`) is enough.

Using the pipe syntax:

```python
from c4.diagrams.core import Diagram, Element

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")

    element1 >> element2 | "Uses"
```

Or by calling the method:

```python
from c4.diagrams.core import Diagram, Element

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")

    element1.uses(element2, label="Uses")
```

All syntaxes above produce the same [`Relationship`][c4.diagrams.core.Relationship] in the diagram.

#### Relationship without a label

`element1 >> element2` creates the relationship at once, with no label
(`label` is `None`). The pipe then sets the label:

```python
from c4.diagrams.core import Diagram, Element

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")

    element1 >> element2

assert diagram.relationships[0].label is None
```

`element1 >> element2 | "Uses"` is the same relationship with the label
`Uses`. The pipe only fills an empty label: it raises `ValueError` if the
relationship already has one, including an empty string, so
`element1 >> "Uses" >> element2 | "Reads"` fails instead of replacing `Uses`.

C4-PlantUML and C4-Mermaid reject a relationship without a label, so the
PlantUML and Mermaid renderers write the placeholder `uses` for it. Change the
text, or turn it off with `None`, through the
`default_relationship_label` render option
([PlantUML](../renderers/plantuml/styles-and-options.md#unlabeled-relationships),
[Mermaid](../renderers/mermaid/options.md#unlabeled-relationships),
[all options](../renderers/render-options.md#unlabeled-relationships)). An explicit empty label (`""`)
is written as it is. The other renderers do not write a placeholder.

<br/>

#### Reversed direction

```python
from c4.diagrams.core import Diagram, Element, Rel

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")

    element2 << Rel("Uses") << element1
```

Or by calling the method:

```python
from c4.diagrams.core import Diagram, Element

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")

    element2.used_by(element1, label="Uses")
```

<br/>

#### One-to-many relationships

```python
from c4.diagrams.core import Diagram, Element, Rel

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")
    element3 = Element(label="Element 3")

    element1 >> Rel("Uses") >> [element2, element3]

assert diagram.relationships[0].label == "Uses"
assert diagram.relationships[0].from_element == element1
assert diagram.relationships[0].to_element == element2
assert diagram.relationships[1].label == "Uses"
assert diagram.relationships[1].from_element == element1
assert diagram.relationships[1].to_element == element3
```

or reversed:

```python
from c4.diagrams.core import Diagram, Element, Rel

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")
    element3 = Element(label="Element 3")

    [element2, element3] << Rel("Uses") << element1
```

<br/>

#### Many-to-one relationships

```python
from c4.diagrams.core import Diagram, Element, Rel

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")
    element3 = Element(label="Element 3")

    [element2, element3] >> Rel("Uses") >> element1
```

or reversed:

```python
from c4.diagrams.core import Diagram, Element, Rel

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")
    element2 = Element(label="Element 2")
    element3 = Element(label="Element 3")

    element1 << Rel("Uses") << [element2, element3]
```

!!! note

    A list can only stand on the left of `>>` or `<<` together with `Rel(...)`.
    Python has no `>>` between a `list` and a `str`, so `[element2, element3] >> "Uses" >> element1`
    raises `TypeError`. Write `[element2, element3] >> Rel("Uses") >> element1` instead.
    A string works when a single element is on the left: `element1 >> "Uses" >> [element2, element3]`.

<br/>

## Boundaries

[`Boundary`][c4.diagrams.core.Boundary] allows grouping (or clustering) elements into an isolated logical container.

Elements that belong to a boundary must be created within a boundary context:

```python
from c4.diagrams.core import Diagram, Element, Boundary, Rel

with Diagram("Simple Diagram") as diagram:
    element1 = Element(label="Element 1")

    with Boundary(label="Boundary") as boundary:
       element2 = Element(label="Element 2")
       element3 = Element(label="Element 3")

    element1 >> Rel("Uses") >> [element2, element3]

assert diagram.elements == [element1]
assert boundary.elements == [element2, element3]
```

There are several types of boundaries:

```python
from c4 import (
    SystemBoundary,
    ContainerBoundary,
    EnterpriseBoundary,
    Node,
    DeploymentNode,
)
from c4.contrib.c4_macros import NodeLeft, NodeRight
from c4.contrib.plantuml import DeploymentNodeLeft, DeploymentNodeRight
```

## Diagram types

Each C4 diagram type has its own page with supported DSL classes, examples and
generated output:

- [System context](portable/system-context.md)
- [Containers](portable/containers.md)
- [Components](portable/components.md)
- [System landscape](portable/system-landscape.md)
- [Dynamic](portable/dynamic.md)
- [Deployment](portable/deployment.md)

More runnable snippets are on the [examples](../examples/plantuml/plantuml.md) page.

# Renderers

Renderers are responsible for converting a `Diagram` object into a textual representation
(for example, PlantUML source code).

!!! note

    You can find a detailed description of the different rendering backends in the
    corresponding sections of the [documentation](../renderers/plantuml/renderers.md).


## Basic rendering

Diagram can be rendered to a string using the `Diagram.render()` method.

By default, a diagram uses its `default_renderer`, if one is configured.

```python
from c4 import Person, Rel, System, SystemContextDiagram
from c4.renderers.plantuml import PlantUMLRenderer

renderer = PlantUMLRenderer()

with SystemContextDiagram(
    "Example system context",
    default_renderer=renderer,
) as diagram:
    user = Person(label="User", description="System user")
    backend = System(label="Backend API", description="Main application backend")

    user >> Rel("Uses HTTP API") >> backend

# Generate PlantUML source code
print(diagram.render())
```

### What happens here?

- `PlantUMLRenderer` is assigned as the diagram’s default renderer
- `diagram.render()` uses this renderer implicitly
- The result is a **string** containing PlantUML source code

<br/>

## Rendering with an explicit renderer

You can also provide a renderer explicitly when calling `render()`.

This is useful when:

- the diagram has no default renderer
- you want to render the same diagram using different formats

```python
from c4 import Person, Rel, System, SystemContextDiagram
from c4.renderers.plantuml import PlantUMLRenderer

renderer = PlantUMLRenderer()

with SystemContextDiagram("Example system context") as diagram:
    user = Person(label="User", description="System user")
    backend = System(label="Backend API", description="Main application backend")

    user >> Rel("Uses HTTP API") >> backend

# Explicit renderer
print(diagram.render(renderer))
```

<br/>

## Renderer shortcuts

For common formats, diagrams provide convenience methods that
wrap `render()` with a predefined renderer.

Example: rendering to PlantUML.

```python
from c4 import Person, Rel, System, SystemContextDiagram

with SystemContextDiagram("Example system context") as diagram:
    user = Person(label="User", description="System user")
    backend = System(label="Backend API", description="Main application backend")

    user >> Rel("Uses HTTP API") >> backend

# Uses PlantUMLRenderer internally
print(diagram.as_plantuml())
```

<br/>

## Saving rendered diagrams to a file

Rendered output can be written directly to a file using `Diagram.save()`.

```python
from c4 import Person, Rel, System, SystemContextDiagram
from c4.renderers.plantuml import PlantUMLRenderer

with SystemContextDiagram("Example system context") as diagram:
    user = Person(label="User", description="System user")
    backend = System(label="Backend API", description="Main application backend")

    user >> Rel("Uses HTTP API") >> backend

diagram.save(
    path="output.puml",
    renderer=PlantUMLRenderer(),
)
```

### Format-specific save shortcuts

Just like rendering, saving also supports format-specific helpers:

```python
diagram.save_as_plantuml("output.puml")
```

This is equivalent to:

```python
diagram.save("output.puml", renderer=PlantUMLRenderer())
```

# Properties

Properties are portable C4 model data. They can be added to diagram elements
and relationships independently of the renderer.

Renderers decide whether and how those properties appear in generated output:

| Renderer | Behavior |
|----------|----------|
| PlantUML | Renders properties as C4-PlantUML property tables. |
| Mermaid | Does not render properties. |
| D2 | Renders properties as Markdown tables when `include_properties=True`. |

## Example

```python
from c4 import Container, ContainerDiagram, Rel


with ContainerDiagram(title="Properties") as diagram:
    api = Container("API", "Handles requests", technology="Python")
    api.add_property("Runtime", "Python 3.12")
    api.add_property("Team", "Orders Team")

    worker = Container("Worker", "Processes jobs", technology="Python")

    relationship = api >> Rel("Publishes jobs") >> worker
    relationship.set_property_header("Key", "Value", "Notes")
    relationship.add_property("Mode", "Async", "Fire-and-forget")
    relationship.add_property("Retry", "Enabled", "Max 3 attempts")
```

## API

- `add_property(*args: str)`

    Adds a row to the property table. The number of values must match the
    number of columns in the header. This is the step-by-step alternative when
    properties are added conditionally or built one row at a time:

    ```python
    app = Container("App Service", "Handles business logic")
    app.add_property("Runtime", "Python 3.12")
    app.add_property("Team", "Platform")
    ```

- `with_properties(*properties, header=None, show_header=True)`

    Adds one or more rows to the property table and returns the element.
    This is available as
    [`BaseDiagramElement.with_properties`](../api_docs/core/#c4.diagrams.core.BaseDiagramElement.with_properties).
    For one row, pass values directly; for multiple rows, pass row sequences.
    Use this form when the element is already being created in-place and you
    want to keep its properties next to the constructor:

    ```python
    app = Container("App Service", "Handles business logic").with_properties(
        ("Runtime", "Python 3.12"),
        ("Team", "Platform"),
    )
    ```

    The top-level [`with_properties`](../api_docs/core/#c4.diagrams.core.with_properties)
    function can add the same rows to an existing element:

    ```python
    from c4 import Container, with_properties


    app = with_properties(
        Container("App Service", "Handles business logic"),
        ("Runtime", "Python 3.12"),
        ("Team", "Platform"),
    )
    ```

    It can also wrap a reusable element factory. Every element created by the
    wrapped factory receives the same property rows:

    ```python
    from functools import partial

    from c4 import Container, with_properties


    PlatformContainer = with_properties(
        partial(Container, description="Owned by the platform team."),
        ("Team", "Platform"),
        ("Support", "24/7"),
    )

    app = PlatformContainer(label="App Service")
    worker = PlatformContainer(label="Worker Service")
    ```

- `set_property_header(*args: str)`

    Sets the column headers for the property table. This must be called before
    adding any property rows, unless the new header has the same number of
    columns as the existing rows. The default header is `("Property", "Value")`.

- `without_property_header()`

    Disables rendering of the header row for the property table.

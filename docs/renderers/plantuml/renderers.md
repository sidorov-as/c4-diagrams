# PlantUML Renderers

The **PlantUML renderer** is responsible for converting a [`Diagram`][c4.diagrams.core.Diagram] object into PlantUML
source code
and exporting it into an image (PNG, SVG, etc.).

It integrates with the [`Diagram`][c4.diagrams.core.Diagram] and delegates image generation
to a configurable backend.

## PlantUMLRenderer

[`PlantUMLRenderer`][c4.renderers.plantuml.PlantUMLRenderer] converts a C4 Diagram into PlantUML syntax.

```python
from c4 import Person, Rel, System, SystemContextDiagram
from c4.renderers.plantuml import PlantUMLRenderer

renderer = PlantUMLRenderer()

with SystemContextDiagram(
    default_renderer=renderer,
) as diagram:
    user = Person("User", "System user")
    backend = System("Backend API", "Main application backend")

    user >> Rel("Uses HTTP API") >> backend

# Generate PlantUML source code
print(diagram.render())
```

**Responsibilities:**

- Select the correct internal renderer for the specific diagram type
- Generate PlantUML source code
- Delegate image generation to a configured backend
- Support layout configuration and `!include` directives

### Diagram Rendering Flow

There are rwo rendering levels:

#### Rendering to PlantUML Source

```python
diagram.render()
```

or explicitly:

```python
renderer.render(diagram)
```

Flow:

```
Diagram.render()
    → PlantUMLRenderer.render()
        → Type-specific renderer
            → PlantUML source string
```

#### Rendering to an Image (PNG, SVG, etc.)

To generate image bytes:

```python
from c4 import PNG

renderer.render_bytes(diagram, format=PNG)
```

To write directly to a file:

```python
from c4 import PNG

renderer.render_file(
    diagram,
    output_path="diagram.png",
    format=PNG,
)
```

Flow:

```
PlantUMLRenderer.render_bytes()
    → generate PlantUML source
    → delegate to backend.to_bytes()
```

The backend performs the actual image generation.

### Using Diagram Convenience Methods

You can also render without manually creating a renderer:

```python
diagram.as_plantuml()
```

Or save directly:

```python
diagram.save_as_plantuml("diagram.puml")
```

These methods internally instantiate `PlantUMLRenderer`.


## PlantUML Backends

Backends are responsible for converting PlantUML source text into rendered images.

### LocalPlantUMLBackend

[`LocalPlantUMLBackend`][c4.renderers.plantuml.LocalPlantUMLBackend] generates diagrams
using a **locally installed** PlantUML binary or JAR file.

**When to use:**

- You have `plantuml` installed locally
- You need offline rendering
- You want maximum performance
- You want full control over execution

**Configuration Sources:**

The backend can be configured via:

- Constructor arguments
- Environment variables

**Environment Variables:**

| Variable                    | Description                         | Default    |
|-----------------------------|-------------------------------------|------------|
| `PLANTUML_BIN`              | Path or name of PlantUML executable | `plantuml` |
| `PLANTUML_JAR`              | Path to `plantuml.jar`              | —          |
| `JAVA_BIN`                  | Java executable                     | `java`     |
| `RENDERING_TIMEOUT_SECONDS` | Rendering timeout (seconds)         | `30`       |

#### Usage

=== "Using system binary"

    ```python
    from c4.renderers.plantuml import PlantUMLRenderer, LocalPlantUMLBackend

    backend = LocalPlantUMLBackend()

    renderer = PlantUMLRenderer(backend=backend)
    ```

    This will try:

    1. `plantuml` binary in PATH
    2. `PLANTUML_JAR`
    3. Otherwise raises `PlantUMLBackendConfigurationError`

=== "Using a specific binary"

    ```python
    backend = LocalPlantUMLBackend(
        plantuml_bin="/usr/local/bin/plantuml",
    )
    ```

=== "Using a JAR file"

    ```python
    from pathlib import Path

    backend = LocalPlantUMLBackend(
        plantuml_jar=Path("/opt/plantuml/plantuml.jar"),
        java_bin="java",
    )
    ```

=== "Passing custom arguments"

    ```python
    backend = LocalPlantUMLBackend(
        plantuml_args=["-DPLANTUML_LIMIT_SIZE=8192"],
        java_args=["-Xmx1024m"],
    )
    ```

---

### RemotePlantUMLBackend

[`RemotePlantUMLBackend`][c4.renderers.plantuml.RemotePlantUMLBackend] generates diagrams using a **PlantUML server** over HTTP.

**When to use:**

- You don't want to install PlantUML locally
- You run inside CI without Java
- You prefer server-based rendering
- You use a central rendering service (e.g. [kroki.io](https://kroki.io/))

---

**Configuration Sources:**

The backend can be configured via:

- Constructor arguments
- Environment variables

**Environment Variables:**

| Variable                    | Description                 | Default                             |
|-----------------------------|-----------------------------|-------------------------------------|
| `PLANTUML_SERVER_URL`       | PlantUML server base URL    | `https://www.plantuml.com/plantuml` |
| `RENDERING_TIMEOUT_SECONDS` | Rendering timeout (seconds) | `30`                                |

#### Usage

=== "Basic Usage"

    ```python
    from c4.renderers.plantuml import (
        PlantUMLRenderer,
        RemotePlantUMLBackend,
    )

    backend = RemotePlantUMLBackend()

    renderer = PlantUMLRenderer(backend=backend)
    ```

=== "Custom Server"

    ```python
    backend = RemotePlantUMLBackend(
        server_url="https://kroki.io/plantuml",
        timeout_seconds=10,
    )
    ```


How it works:

1. Diagram text is compressed
2. Encoded using PlantUML encoding
3. Sent to:

    ```
    {server_url}/{format}/{encoded}
    ```

4. Server returns rendered image bytes


### Choosing a Backend

| Scenario              | Recommended Backend     |
|-----------------------|-------------------------|
| Local development     | `LocalPlantUMLBackend`  |
| CI/CD without Java    | `RemotePlantUMLBackend` |
| Offline environments  | `LocalPlantUMLBackend`  |
| Centralized rendering | `RemotePlantUMLBackend` |

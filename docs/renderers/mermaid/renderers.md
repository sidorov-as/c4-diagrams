# Mermaid Renderers

???+ warning "Mermaid C4 diagram status"

    Mermaid’s C4 diagram support is currently **experimental**.

    According to the official [Mermaid documentation](https://mermaid.js.org/syntax/c4.html):

    >C4 Diagram: This is an experimental diagram for now. The syntax and properties can change in future releases.
    >Proper documentation will be provided when the syntax is stable.


The **Mermaid renderer** is responsible for converting a [`Diagram`][c4.diagrams.core.Diagram] object into Mermaid
source code
and exporting it into an image (PNG, SVG, etc.).

It integrates with the [`Diagram`][c4.diagrams.core.Diagram] and delegates image generation
to a configurable backend.

## MermaidRenderer

[`MermaidRenderer`][c4.renderers.mermaid.MermaidRenderer] converts a C4 Diagram into Mermaid syntax.

```python
from c4 import Person, Rel, System, SystemContextDiagram
from c4.renderers import MermaidRenderer

renderer = MermaidRenderer()

with SystemContextDiagram(
    default_renderer=renderer,
) as diagram:
    user = Person("User", "System user")
    backend = System("Backend API", "Main application backend")

    user >> Rel("Uses HTTP API") >> backend

# Generate Mermaid source code
print(diagram.render())
```

**Responsibilities:**

- Generate Mermaid source code
- Delegate image generation to a configured backend
- Support layout configuration

### Diagram Rendering Flow

There are rwo rendering levels:

#### Rendering to Mermaid Source

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
    → MermaidRenderer.render()
        → Type-specific renderer
            → Mermaid source string
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
MermaidRenderer.render_bytes()
    → generate Mermaid source
    → delegate to backend.to_bytes()
```

The backend performs the actual image generation.

### Using Diagram Convenience Methods

You can also render without manually creating a renderer:

```python
diagram.as_mermaid()
```

Or save directly:

```python
diagram.save_as_mermaid("diagram.mmd")
```

These methods internally instantiate `MermaidRenderer`.


## Mermaid Backends

Backends are responsible for converting Mermaid source text into rendered images.

### LocalMermaidBackend

[`LocalMermaidBackend`][c4.renderers.mermaid.LocalMermaidBackend] generates diagrams
using a **locally installed** [Mermaid cli](https://github.com/mermaid-js/mermaid-cli).

**When to use:**

- You have `mmdc` installed locally
- You need offline rendering
- You want maximum performance
- You want full control over execution

**Configuration Sources:**

The backend can be configured via:

- Constructor arguments
- Environment variables

**Environment Variables:**

| Variable                    | Description                        | Default |
|-----------------------------|------------------------------------|---------|
| `MERMAID_BIN`               | Path or name of Mermaid executable | `mmdc`  |
| `RENDERING_TIMEOUT_SECONDS` | Rendering timeout (seconds)        | `30`    |

#### Usage

=== "Using system binary"

    ```python
    from c4.renderers import MermaidRenderer, LocalMermaidBackend

    backend = LocalMermaidBackend()

    renderer = MermaidRenderer(backend=backend)
    ```

    This will try:

    1. `mmdc` binary in PATH
    2. Otherwise raises `MermaidBackendConfigurationError`

=== "Using a specific binary"

    ```python
    backend = LocalMermaidBackend(
        mermaid_bin="/usr/local/bin/mmdc",
    )
    ```

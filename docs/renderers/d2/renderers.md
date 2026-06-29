# D2 Renderers

The **D2 renderer** converts a [`Diagram`](../../api_docs/core/#c4.diagrams.core.Diagram) object
into D2 source code. Image export is optional and uses a configured D2 backend
after source text has been generated.

D2-specific hints are rendering backend extensions, separate from the portable
C4 core. See [Portable core and backend extensions](../../concepts/portable-core-and-extensions.md)
for how `d2={...}` data is stored and how unsupported foreign extensions are
validated.

## D2Renderer

[`D2Renderer`](../../api_docs/d2/renderers/#c4.renderers.d2.renderer.D2Renderer) converts a C4 diagram into D2 syntax.

```python
from c4 import Person, Rel, System, SystemContextDiagram
from c4.renderers import D2Renderer

renderer = D2Renderer()

with SystemContextDiagram("Example", default_renderer=renderer) as diagram:
    user = Person("User", "System user")
    backend = System("Backend API", "Main application backend")

    user >> Rel("Uses") >> backend

# Generate D2 source code
print(diagram.render())
```

**Responsibilities:**

- Select the correct internal renderer for the specific diagram type
- Generate D2 source code
- Delegate image generation to a configured execution backend
- Apply diagram-level and explicit D2 render options

### Diagram Rendering Flow

There are two rendering levels:

#### Rendering to D2 Source

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
    → D2Renderer.render()
        → Type-specific renderer
            → D2 source string
```

Diagram-level D2 render options are applied automatically. You can also
configure render options when creating the renderer:

```python
from c4.renderers import D2RenderOptions

renderer = D2Renderer(
    render_options=D2RenderOptions(direction="down", theme=300),
)

source = renderer.render(diagram)
```

#### Rendering to an Image (PNG, SVG, PDF)

To generate image bytes:

```python
from c4 import SVG
from c4.renderers import D2Renderer, LocalD2Backend

renderer = D2Renderer(backend=LocalD2Backend())
svg_bytes = renderer.render_bytes(diagram, format=SVG)
```

To write directly to a file:

```python
from c4 import PNG
from c4.renderers import D2Renderer, LocalD2Backend

renderer = D2Renderer(backend=LocalD2Backend())
renderer.render_file(diagram, "diagram.png", format=PNG)
```

Flow:

```
D2Renderer.render_bytes()
    → generate D2 source
    → delegate to backend.to_bytes()
```

The backend performs the actual image generation.

### Using Diagram Convenience Methods

You can also render without manually creating a renderer:

```python
diagram.as_d2()
```

Or save directly:

```python
diagram.save_as_d2("diagram.d2")
```

Both `as_d2()` and `save_as_d2()` accept keyword arguments passed to
`D2Renderer`.

```python
from c4.renderers import D2RenderOptions

source = diagram.as_d2(
    render_options=D2RenderOptions(direction="down", theme=300),
)
```

## LocalD2Backend

[`LocalD2Backend`](../../api_docs/d2/renderers/#c4.renderers.d2.backends.LocalD2Backend) generates rendered artifacts
using a locally installed [D2 CLI](https://d2lang.com/tour/install/).
D2 `v0.7.1` or newer is required for local export.

The backend supports SVG, PNG, and PDF. `.d2` is source output and is handled by
the render path, not by `DiagramFormat`.

Verify the local executable before using image export:

```bash
d2 version
```

If the executable is not available as `d2`, pass `d2_bin` or set `D2_BIN`.

## Environment Variables

| Variable                    | Description                       | Default |
|-----------------------------|-----------------------------------|---------|
| `D2_BIN`                    | Path or name of the D2 executable | `d2`    |
| `RENDERING_TIMEOUT_SECONDS` | Rendering timeout in seconds      | `30`    |

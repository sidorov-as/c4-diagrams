# Structurizr Renderers

The **Structurizr renderer** converts a Structurizr [`Workspace`][c4.contrib.structurizr.Workspace] into
Structurizr DSL. Text rendering does not need external tools. To write a
workspace, start with the [overview](index.md).

```python
from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import StructurizrRenderer

workspace = Workspace("Demo")
print(StructurizrRenderer().render(workspace))
```

## KrokiStructurizrBackend

[`KrokiStructurizrBackend`][c4.contrib.structurizr.renderer.KrokiStructurizrBackend] exports generated Structurizr DSL through a Kroki
server using Kroki diagram type `structurizr`.

Use this backend when you want rendered SVG, PNG, or PDF output from
Structurizr DSL. If a workspace contains multiple views, pass a view key so
Kroki knows which view to render.

```python
from c4.contrib.structurizr.renderer import (
    KrokiStructurizrBackend,
    StructurizrRenderer,
)

renderer = StructurizrRenderer(
    backend=KrokiStructurizrBackend(
        server_url="https://kroki.io",
        view_key="container-view",
    ),
)
```

CLI example:

```bash
c4 export diagram.py --structurizr --structurizr-backend kroki \
  --structurizr-view-key container-view \
  -f svg -o diagram.svg
```

Kroki is the default Structurizr export backend.

## LocalStructurizrBackend

[`LocalStructurizrBackend`][c4.contrib.structurizr.renderer.LocalStructurizrBackend] exports generated Structurizr DSL with the local
[Structurizr CLI](https://docs.structurizr.com/cli) (`structurizr export`).
It renders the official Structurizr diagrams offline, but only supports **PNG**
and **SVG** (use Kroki for PDF) and needs Playwright Chromium, see
[installation](../../installation.md#structurizr-requirements).

`structurizr export` always renders every view of a workspace (one
`<view-key>.png` file per view, plus a `<view-key>-key.png` legend). The backend
runs it once in a temporary directory and returns the view you asked for, so
the workspace does not have to be trimmed to one view. `view_key` can be
omitted only if the workspace has exactly one view.

```python
from c4.contrib.structurizr.renderer import (
    LocalStructurizrBackend,
    StructurizrRenderer,
)

renderer = StructurizrRenderer(
    backend=LocalStructurizrBackend(view_key="container-view"),
)
```

The command can be set with `structurizr_bin` (a name, a path or a command
prefix such as `["npx", "structurizr"]`) or the `STRUCTURIZR_BIN` environment
variable. `timeout_seconds` defaults to `RENDERING_TIMEOUT_SECONDS`.

CLI example:

```bash
c4 export diagram.py --structurizr --structurizr-backend local \
  --structurizr-view-key container-view \
  -f png -o diagram.png
```

The Structurizr CLI exits with `0` even if the DSL is invalid, so the backend
raises [`StructurizrRenderingError`][c4.contrib.structurizr.renderer.StructurizrRenderingError] with the CLI's error lines when the
requested view was not produced.

## Authoring

The renderer consumes a `Workspace`. See [Authoring](authoring.md) for the
model, [Views](views.md) for the views and [Styles](styles.md) for styles,
presets and render options.

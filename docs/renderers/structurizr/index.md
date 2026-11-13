# Structurizr Rendering Backend

The Structurizr backend turns a [`Workspace`][c4.contrib.structurizr.Workspace] into
[Structurizr DSL](https://docs.structurizr.com/dsl/language). Structurizr
models a whole architecture (a model, a set of views and their styles) rather
than a single diagram, so the backend has its own authoring API in
`c4.contrib.structurizr`. It does not accept the portable `Diagram` classes.

Rendering to DSL needs no external tools. Image export goes through
[Kroki](https://kroki.io/) or the local
[Structurizr CLI](https://docs.structurizr.com/cli). See
[Renderers](renderers.md) and
[Installation](../../installation.md#structurizr-requirements).

!!! info "Supported version"

    The backend is tested against **Structurizr CLI 2026.06.28**
    (`structurizr-*` 6.2.2). Other versions may work, but the generated DSL is
    only validated against this one. Anything this project does not check is
    left to the [Structurizr CLI](https://docs.structurizr.com/cli) and the
    [language reference](https://docs.structurizr.com/dsl/language).

## When to use it

Use Structurizr when the artifact you want is Structurizr DSL, for example to
open it in Structurizr Lite, to export it with the Structurizr CLI, or to keep
one model with several views (landscape, context, container, component,
dynamic, deployment). Use the portable diagrams with PlantUML, Mermaid or D2
when you only need one C4 diagram.

## Capability table

| Capability                 | Status                                                                                              |
|----------------------------|-----------------------------------------------------------------------------------------------------|
| DSL rendering              | Supported, deterministic, no external tools                                                         |
| Image export               | Kroki (SVG, PNG, PDF) or the local Structurizr CLI (SVG, PNG)                                        |
| Model                      | People, software systems, containers, components, relationships, tags, properties, URLs             |
| Deployment                 | Environments, nested deployment nodes, infrastructure nodes, system and container instances         |
| Views                      | System landscape, system context, container, component, dynamic and deployment views                |
| View options               | `include`, `exclude`, `animation`, [`AutoLayout`][c4.contrib.structurizr.AutoLayout], tags, properties                                   |
| Styles                     | Element and relationship styles, `classic` and `new-c4-style` presets, element-local styles, theme  |
| JSON and Python conversion | `"backend": "structurizr"` JSON, `c4 convert --json-to-py`                                          |

## Quickstart

Save this as `workspace.py`:

```python
from c4.contrib.structurizr import Rel, Workspace

workspace = Workspace("Online Shop", description="Orders and payments")

with workspace.model as model:
    customer = model.Person("Customer", description="Buys goods")
    shop = model.SoftwareSystem("Shop", description="Takes orders")
    web = model.Container(
        "Web App",
        description="Checkout UI",
        technology="Django",
        owner=shop,
    )
    customer >> Rel("Orders goods", technology="HTTPS") >> web

workspace.views.ContainerView(shop, key="containers", title="Shop containers")
```

Render the DSL, then export a view as an image with the local Structurizr CLI:

```bash
c4 render workspace.py --structurizr -o workspace.dsl

c4 export workspace.py --structurizr --structurizr-backend local \
  --structurizr-view-key containers -f png -o containers.png
```

The rendered DSL (the style block of the default `classic` preset is shortened
here):

<!-- quickstart-output -->
```dsl
workspace "Online Shop" {
  description "Orders and payments"
  model {
    customer = person "Customer" "Buys goods" {
      tags "Person"
    }
    shop = softwareSystem "Shop" "Takes orders" {
      tags "Software System"
      web_app = container "Web App" "Checkout UI" "Django" {
        tags "Container"
      }
    }
    customer -> web_app "Orders goods" "HTTPS" {
      tags "Relationship"
    }
  }
  views {
    container shop "containers" {
      title "Shop containers"
      include *
      autoLayout lr
    }
    styles {
      ...
    }
  }
}
```

## Where to go next

- [Authoring](authoring.md): workspace, model, relationships, deployment.
- [Views](views.md): the six view types, selectors, dynamic views.
- [Styles](styles.md): styles, presets, render options, themes.
- [Reference](reference.md): allowed values and validation rules (generated).
- [Renderers](renderers.md): the renderer, the Kroki and local backends, CLI.
- [Limitations](limitations.md): what is not supported and what is validated.

More complete workspaces are in the [Structurizr examples](../../examples/structurizr/structurizr.md).

Upstream documentation: [Structurizr DSL language reference](https://docs.structurizr.com/dsl/language),
[Structurizr CLI](https://docs.structurizr.com/cli) and
[Structurizr](https://structurizr.com/).

# LikeC4 Rendering Backend

The LikeC4 backend turns a [`Project`][c4.contrib.likec4.Project] into [LikeC4](https://likec4.dev/) `.c4`
source. Like Structurizr, LikeC4 models a whole architecture (a specification
vocabulary, a model, a deployment and a set of views) rather than one diagram,
so the backend has its own authoring API in `c4.contrib.likec4`. It does not
accept the portable `Diagram` classes.

Rendering to `.c4` source needs no external tools. Image export delegates to
the `likec4` CLI, which needs Node.js and Playwright Chromium, and **only the
local backend exists: LikeC4 is not available through Kroki.** See
[Renderers](renderers.md) and [Installation](../../installation.md#likec4-requirements).

!!! info "Supported version"

    The backend is tested against **LikeC4 1.60.0**. Other versions may work,
    but the generated syntax is only validated against this one. Whatever this
    project does not check is left to `likec4 validate` and the
    [LikeC4 documentation](https://likec4.dev/dsl/intro/).

## Capability table

| Capability                  | Status                                                                 |
|-----------------------------|------------------------------------------------------------------------|
| `.c4` source rendering      | Supported, deterministic, no external tools                            |
| Image export                | PNG and JPG through the local `likec4` CLI (no SVG: LikeC4 has none)   |
| Specification               | Element, relationship and deployment node kinds, tags, custom colors   |
| Model                       | Nested elements, relationships (kinds, `<->`), metadata, links, icons  |
| Deployment                  | Nested nodes, instances, deployment relationships                      |
| Views                       | Element, deployment and dynamic views                                  |
| View predicates             | `*`, `.*`, `.**`, `where`, relationship predicates, raw text           |
| Dynamic views               | Flat steps, `back`, `variant`; parallel/alternative blocks not yet     |
| JSON and Python conversion  | `"backend": "likec4"` JSON, `c4 convert --json-to-py`                  |

## Quickstart

Save this as `project.py`:

```python
from c4.contrib.likec4 import Project, Rel, Wildcard

project = Project("Shop")

project.specification.element("actor", shape="person").element("system")

customer = project.model.element("actor", "Customer", alias="customer")
shop = project.model.element("system", "Online Shop", alias="shop")
customer >> Rel("buys goods") >> shop

project.views.element_view("index", "Landscape").include(Wildcard())
```

Render the source, then export the `index` view as an image:

```bash
c4 render project.py --likec4 -o architecture.c4

c4 export project.py --likec4 --likec4-view-key index -f png -o index.png
```

The rendered `.c4`:

<!-- quickstart-output -->
```c4
specification {
  element actor { style { shape person } }
  element system
}

model {
  customer = actor "Customer"
  shop = system "Online Shop"
  customer -> shop "buys goods"
}

views {
  view index {
    title "Landscape"
    include *
  }
}
```

Every kind, tag and custom color must be declared in `project.specification`
before it is used; the renderer reports a missing declaration by name.

??? example "A larger project"

    === "Python"

        ```python
        --8<-- "assets/examples/likec4/project.advanced.py"
        ```

    === "Rendered .c4"

        ```c4
        --8<-- "assets/examples/likec4/project.advanced.c4"
        ```

## Where to go next

- [Authoring](authoring.md): specification, model, relationships, deployment.
- [Views](views.md): element, deployment and dynamic views, predicates.
- [Styles](styles.md): colors, shapes, borders, sizes, icons, line and arrow styles.
- [Reference](reference.md): allowed values and validation rules (generated).
- [Renderers](renderers.md): the renderer, the local backend and the CLI.
- [Limitations](limitations.md): what is not supported and what only `likec4 validate` checks.

Upstream documentation: [LikeC4 DSL](https://likec4.dev/dsl/intro/) and
[LikeC4 CLI](https://likec4.dev/tooling/cli/).

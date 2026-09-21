# Structurizr Limitations

## Unsupported Structurizr DSL features

The Python API covers the model, the six view types and styles. These parts of
the [Structurizr DSL](https://docs.structurizr.com/dsl/language) are not
generated:

- `group` blocks and deployment groups (`deploymentGroup`), and instance counts.
- `perspectives` and `healthCheck` on elements.
- Filtered, custom and image views.
- `branding`, `terminology`, `configuration` (users, scope, visibility) and
  `enterprise`.
- Documentation and decisions (`!docs`, `!adrs`), and the directives `!include`,
  `!script`, `!plugin`, `!identifiers`, `!impliedRelationships` and `!ref`.
- Workspace extension (`workspace extends ...`).
- Element style properties outside the
  [list in the Reference](reference.md#style-properties), such as `icon`.

For any of these, render the workspace and extend the generated DSL by hand, or
use [`RawSelector`](views.md#selectors) for view expressions the API does not
model.

## Rules checked by the renderer

The workspace is validated before any DSL is produced. The checks are listed
with their error class in the [Reference](reference.md#validation-rules). The
most common ones:

| Rule                                                                 | Error                        |
|----------------------------------------------------------------------|------------------------------|
| A relationship connects a parent and its own child or descendant.    | [`StructurizrRenderingError`][c4.contrib.structurizr.renderer.StructurizrRenderingError]  |
| A container has no software system parent, a component no container. | `StructurizrRenderingError`  |
| A relationship endpoint is not in the workspace.                     | `StructurizrRenderingError`  |
| A system context, container or component view has no scope.         | `StructurizrRenderingError`  |
| A view scope has the wrong type or is not in the workspace.          | `StructurizrRenderingError`  |
| A deployment view names an environment with no deployment nodes.     | `StructurizrRenderingError`  |
| A deployment node is not in exactly one environment.                 | `StructurizrRenderingError`  |

For example, `system.uses(container_of_system, "...")` fails with
`Structurizr DSL does not allow relationships between parent and child
elements`.

Mistakes visible while authoring raise earlier: tags that are not a `list[str]`
or a view scope passed as an alias string raise `TypeError`, and an owner or
endpoint from another workspace raises `ValueError`.

Everything else is left to the Structurizr CLI. In particular the renderer does
not parse `RawSelector` text or check that a style property is valid for the
kind of element it is applied to.

## Local backend

`structurizr export` exits with `0` even when the DSL is invalid, so the exit
code is not a reliable signal. [`LocalStructurizrBackend`][c4.contrib.structurizr.renderer.LocalStructurizrBackend] therefore checks that
the requested view file was produced and otherwise raises
`StructurizrRenderingError` with the CLI's error lines. See
[Renderers](renderers.md#localstructurizrbackend).

The local backend exports PNG and SVG only and needs the Playwright Chromium
browser. A workspace with several views needs a view key
(`--structurizr-view-key`, or `view_key=`); a workspace with one view does not.

## Kroki backend

Kroki renders one view per request. Pass `view_key` (`--structurizr-view-key`)
for a workspace with several views so that the view you want is rendered.
Kroki supports SVG, PNG and PDF. The DSL is sent to the Kroki server, so use a
self-managed instance for private architecture.

## Theme

The `theme` is optional. `theme="default"` is deprecated and ignored; see
[Styles](styles.md#theme).

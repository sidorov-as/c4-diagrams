# Rendering Backend Comparison

Rendering-backend pages are the normative source for backend-only behavior.
The portable core docs describe model concepts shared by renderers; backend
docs describe syntax, validation, render options, and extension data owned by
each renderer.

| Capability                           | PlantUML                                                  | Mermaid                                             | D2                                          | Structurizr            | LikeC4                            |
|--------------------------------------|-----------------------------------------------------------|-----------------------------------------------------|---------------------------------------------|------------------------|-----------------------------------|
| System context diagrams              | Supported                                                 | Supported                                           | Supported                                   | [Supported](structurizr/views.md#view-types-and-their-scope) | [Element views (no fixed C4 types)](likec4/views.md) |
| System landscape diagrams            | Supported                                                 | Rendered as Mermaid C4 context syntax               | Supported                                   | [Supported](structurizr/views.md#view-types-and-their-scope) | [Element views (no fixed C4 types)](likec4/views.md) |
| Container diagrams                   | Supported                                                 | Supported                                           | Supported                                   | [Supported](structurizr/views.md#view-types-and-their-scope) | [Element views (no fixed C4 types)](likec4/views.md) |
| Component diagrams                   | Supported                                                 | Supported                                           | Supported                                   | [Supported](structurizr/views.md#view-types-and-their-scope) | [Element views (no fixed C4 types)](likec4/views.md) |
| Dynamic diagrams                     | Supported                                                 | Supported by renderer, limited by Mermaid C4 syntax | Supported                                   | [Supported](structurizr/views.md#view-types-and-their-scope) | [Supported (flat steps)](likec4/views.md#dynamic-views) |
| Deployment diagrams                  | Supported                                                 | Supported by renderer, limited by Mermaid C4 syntax | Supported                                   | [Supported](structurizr/views.md#view-types-and-their-scope) | [Supported](likec4/views.md) |
| Relationship endpoints               | Elements and boundaries                                   | Concrete elements only; boundaries are rejected     | Elements with deterministic D2 paths        | [Structurizr model](structurizr/authoring.md) | [LikeC4 model](likec4/authoring.md) |
| Properties                           | [Property tables](plantuml/properties.md)                 | Not supported                                       | [Markdown tables](d2/options.md#properties) | [Structurizr properties](structurizr/authoring.md#common-keyword-arguments) | [Metadata](likec4/authoring.md#model-elements) |
| Directional relationship helpers     | [`c4.contrib.plantuml`](plantuml/layout.md)               | Syntax accepted, no layout effect                   | Not supported                               | Not supported          | Not supported                     |
| Bidirectional relationship helpers   | [`c4.contrib.plantuml`](plantuml/layout.md)               | [`c4.contrib.mermaid`](mermaid/limitations.md)      | [`c4.contrib.d2`](d2/options.md)            | Not supported          | [`bidirectional=True`](likec4/authoring.md#relationships) |
| Relative layout helpers              | [`c4.contrib.plantuml`](plantuml/layout.md)               | Not supported                                       | D2 `direction` and extension layout hints   | [Auto-layout options](structurizr/views.md#auto-layout) | [`autoLayout`](likec4/views.md#auto-layout) |
| Dynamic relationship indexes         | [`c4.contrib.plantuml`](plantuml/dynamic-indexes.md)      | Not supported                                       | Not supported                               | [Dynamic view order](structurizr/views.md#dynamic-views) | [Step order](likec4/views.md#dynamic-views) |
| Element tags, sprites, links, shapes | [`plantuml={...}`](plantuml/extensions.md)                | Not supported                                       | [`d2={...}`](d2/extensions.md)              | [Tags and styles](structurizr/styles.md) | [Tags, icons, links, shapes](likec4/styles.md) |
| Boundary type hints                  | [`plantuml={...}`](plantuml/extensions.md)                | [`mermaid={...}`](mermaid/extensions.md)            | [`d2={...}`](d2/extensions.md)              | [Model scopes](structurizr/views.md#view-types-and-their-scope) | [Nested elements](likec4/authoring.md#model-elements) |
| Style options                        | [PlantUML render options](plantuml/styles-and-options.md) | [Mermaid options](mermaid/options.md)               | [D2 options](d2/options.md)                 | [Style presets](structurizr/styles.md#style-presets) | [Kinds, colors, view style rules](likec4/styles.md) |
| Image backend                        | Local CLI/JAR, remote server, or Kroki                    | Local Mermaid CLI or Kroki                          | Local D2 CLI or Kroki                       | Kroki or local CLI     | Local `likec4` CLI (PNG, JPG)     |

## Export backends and formats

| Backend   | Source output                     | Local export                                                           | Remote export          | Kroki                      | Image formats                                  |
|-----------|-----------------------------------|------------------------------------------------------------------------|------------------------|----------------------------|------------------------------------------------|
| PlantUML  | C4-PlantUML                       | `plantuml` CLI or `plantuml.jar`                                       | PlantUML server        | Supported                  | PNG, SVG, EPS, LaTeX, TXT, UTXT                |
| Mermaid   | Mermaid C4                        | [Mermaid CLI](mermaid/renderers.md) (`mmdc`)                           | Not supported          | Supported                  | PNG, SVG, PDF                                  |
| D2        | D2                                | `d2` CLI                                                               | Not supported          | Supported                  | PNG, SVG, PDF                                  |
| [Structurizr](structurizr/renderers.md) | Structurizr DSL | [Structurizr CLI](structurizr/renderers.md#localstructurizrbackend) | Not supported | [Supported](structurizr/renderers.md#krokistructurizrbackend) (default) | PNG, SVG, PDF (local CLI: PNG, SVG) |
| [LikeC4](likec4/renderers.md) | LikeC4 `.c4`        | [`likec4` CLI](likec4/renderers.md)                                    | Not supported          | Not supported              | PNG, JPG                                       |

Use [PlantUML](plantuml/index.md) when C4-PlantUML-specific layout, styling,
tags, dynamic indexes, or remote rendering matter. Use [Mermaid](mermaid/index.md)
when Mermaid source is the target format and the diagram fits Mermaid's smaller
experimental C4 feature set. Use [D2](d2/index.md) when deterministic D2 source
or local D2 image export is the target. Use [Structurizr](structurizr/renderers.md) when Structurizr DSL or
Kroki-backed or local Structurizr CLI export is the target. Use [LikeC4](likec4/index.md)
when LikeC4 source or locally exported LikeC4 views are the target.

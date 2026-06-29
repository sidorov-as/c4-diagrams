# Rendering Backend Comparison

Rendering-backend pages are the normative source for backend-only behavior.
The portable core docs describe model concepts shared by renderers; backend
docs describe syntax, validation, render options, and extension data owned by
each renderer.

| Capability                           | PlantUML                                                  | Mermaid                                             | D2                                        |
|--------------------------------------|-----------------------------------------------------------|-----------------------------------------------------|-------------------------------------------|
| System context diagrams              | Supported                                                 | Supported                                           | Supported                                 |
| System landscape diagrams            | Supported                                                 | Rendered as Mermaid C4 context syntax               | Supported                                 |
| Container diagrams                   | Supported                                                 | Supported                                           | Supported                                 |
| Component diagrams                   | Supported                                                 | Supported                                           | Supported                                 |
| Dynamic diagrams                     | Supported                                                 | Supported by renderer, limited by Mermaid C4 syntax | Supported                                 |
| Deployment diagrams                  | Supported                                                 | Supported by renderer, limited by Mermaid C4 syntax | Supported                                 |
| Relationship endpoints               | Elements and boundaries                                   | Concrete elements only; boundaries are rejected     | Elements with deterministic D2 paths      |
| Properties                           | [Property tables](plantuml/properties.md)                 | Not supported                                       | [Markdown tables](d2/options.md#properties) |
| Directional relationship helpers     | [`c4.contrib.plantuml`](plantuml/layout.md)               | Not supported                                       | Not supported                             |
| Bidirectional relationship helpers   | [`c4.contrib.plantuml`](plantuml/layout.md)               | Not supported                                       | [`c4.contrib.d2`](d2/options.md)          |
| Relative layout helpers              | [`c4.contrib.plantuml`](plantuml/layout.md)               | Not supported                                       | D2 `direction` and extension layout hints |
| Dynamic relationship indexes         | [`c4.contrib.plantuml`](plantuml/dynamic-indexes.md)      | Not supported                                       | Not supported                             |
| Element tags, sprites, links, shapes | [`plantuml={...}`](plantuml/extensions.md)                | Not supported                                       | [`d2={...}`](d2/extensions.md)            |
| Boundary type hints                  | [`plantuml={...}`](plantuml/extensions.md)                | [`mermaid={...}`](mermaid/extensions.md)            | [`d2={...}`](d2/extensions.md)            |
| Style options                        | [PlantUML render options](plantuml/styles-and-options.md) | [Mermaid options](mermaid/options.md)               | [D2 options](d2/options.md)               |
| Image backend                        | Local CLI/JAR or remote server                            | Local Mermaid CLI                                   | Local D2 CLI                              |

Use [PlantUML](plantuml/index.md) when C4-PlantUML-specific layout, styling,
tags, dynamic indexes, or remote rendering matter. Use [Mermaid](mermaid/index.md)
when Mermaid source is the target format and the diagram fits Mermaid's smaller
experimental C4 feature set. Use [D2](d2/index.md) when deterministic D2 source
or local D2 image export is the target.

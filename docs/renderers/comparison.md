# Rendering Backend Comparison

Rendering-backend pages are the normative source for backend-only behavior.
The portable core docs describe model concepts shared by renderers; backend
docs describe syntax, validation, render options, and extension data owned by
each renderer.

| Capability                           | PlantUML                                                  | Mermaid                                             |
|--------------------------------------|-----------------------------------------------------------|-----------------------------------------------------|
| System context diagrams              | Supported                                                 | Supported                                           |
| System landscape diagrams            | Supported                                                 | Rendered as Mermaid C4 context syntax               |
| Container diagrams                   | Supported                                                 | Supported                                           |
| Component diagrams                   | Supported                                                 | Supported                                           |
| Dynamic diagrams                     | Supported                                                 | Supported by renderer, limited by Mermaid C4 syntax |
| Deployment diagrams                  | Supported                                                 | Supported by renderer, limited by Mermaid C4 syntax |
| Relationship endpoints               | Elements and boundaries                                   | Concrete elements only; boundaries are rejected     |
| Properties                           | [Property tables](plantuml/properties.md)                 | Not supported                                       |
| Directional relationship helpers     | [`c4.contrib.plantuml`](plantuml/layout.md)               | Not supported                                       |
| Bidirectional relationship helpers   | [`c4.contrib.plantuml`](plantuml/layout.md)               | Not supported                                       |
| Relative layout helpers              | [`c4.contrib.plantuml`](plantuml/layout.md)               | Not supported                                       |
| Dynamic relationship indexes         | [`c4.contrib.plantuml`](plantuml/dynamic-indexes.md)      | Not supported                                       |
| Element tags, sprites, links, shapes | [`plantuml={...}`](plantuml/extensions.md)                | Not supported                                       |
| Boundary type hints                  | [`plantuml={...}`](plantuml/extensions.md)                | [`mermaid={...}`](mermaid/extensions.md)            |
| Style options                        | [PlantUML render options](plantuml/styles-and-options.md) | [Mermaid options](mermaid/options.md)               |
| Image backend                        | Local CLI/JAR or remote server                            | Local Mermaid CLI                                   |

Use [PlantUML](plantuml/index.md) when C4-PlantUML-specific layout, styling,
tags, dynamic indexes, or remote rendering matter. Use [Mermaid](mermaid/index.md)
when Mermaid source is the target format and the diagram fits Mermaid's smaller
experimental C4 feature set.

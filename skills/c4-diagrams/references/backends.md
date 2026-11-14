# Portable core versus extensions, and the backends

Docs: https://sidorov-as.github.io/c4-diagrams/concepts/portable-core-and-extensions/
and https://sidorov-as.github.io/c4-diagrams/renderers/comparison/

## Portable core

Elements, boundaries, the six diagram types and `Rel` are portable: the same Python renders to PlantUML, Mermaid and D2.
Renderer hints are extensions and stay out of the core:

- Kwargs: `plantuml={...}`, `mermaid={...}`, `d2={...}` (or `extensions={"plantuml": {...}}`).
- Helpers: directional relationships (`RelRight`), bidirectional, layout (`LayRight`), dynamic indexes (`Index`),
  sprites, links, tags live in `c4.contrib.plantuml`; `c4.contrib.mermaid`, `c4.contrib.d2`, `c4.contrib.c4_macros` hold
  theirs.
- A renderer ignores other backends' data by default; strict validation makes it fail instead.

When the user wants a PlantUML-only feature, put it in the PlantUML kwarg or helper and say it is not portable.

## Backends

|               | PlantUML                                          | Mermaid                                                             | D2                                         | Structurizr                           | LikeC4                               |
|---------------|---------------------------------------------------|---------------------------------------------------------------------|--------------------------------------------|---------------------------------------|--------------------------------------|
| Authoring     | `Diagram`                                         | `Diagram`                                                           | `Diagram`                                  | `Workspace`                           | `Project`                            |
| Source        | C4-PlantUML                                       | Mermaid C4                                                          | D2                                         | Structurizr DSL                       | LikeC4 `.c4`                         |
| Image export  | local CLI/JAR, remote server, Kroki               | local `mmdc`, Kroki                                                 | local `d2`, Kroki                          | local CLI (PNG, SVG), Kroki (default) | local `likec4` (PNG, JPG)            |
| Remote option | yes (server, Kroki)                               | Kroki                                                               | Kroki                                      | Kroki                                 | none                                 |
| Strengths     | richest layout, tags, dynamic indexes, deployment | small experimental C4 subset                                        | deterministic output, properties as tables | model with many views                 | model with many views, element views |
| Limits        | needs Java and Graphviz                           | no properties, no boundary endpoints, layout helpers have no effect | no directional helpers                     | no portable diagrams                  | no fixed C4 view types               |

Pick PlantUML when C4-PlantUML layout, tags or dynamic indexes matter; Mermaid when Mermaid source is the target; D2 for
D2 source or local D2 images; Structurizr or LikeC4 for those formats or several views of one model.

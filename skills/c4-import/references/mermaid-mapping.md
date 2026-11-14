# Mermaid C4 mapping

Imports: `from c4 import ...`; `from c4.contrib.mermaid import ...` for the helpers.

## Arguments

Mermaid macros take `(alias, label, [technology,] description, $sprite, $tags, $link)`. The Python classes take
`(label, description, [technology,] alias=...)`: **description and technology swap places** and the alias is a keyword.
`Container(web, "Web", "Django", "Serves pages")` becomes
`Container("Web", "Serves pages", "Django", alias="web")`.

Mermaid ignores `$sprite`, `$tags` and `$link` on elements. When the source has them, report them: only boundaries
accept `mermaid={"tags": [...], "link": "..."}`.

## Elements

| Macro                                                                                                  | Class                                                                                               |
|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `Person`, `Person_Ext`                                                                                 | `Person`, `PersonExt`                                                                               |
| `System`, `SystemDb`, `SystemQueue`, `System_Ext`, `SystemDb_Ext`, `SystemQueue_Ext`                   | `System`, `SystemDb`, `SystemQueue`, `SystemExt`, `SystemDbExt`, `SystemQueueExt`                   |
| `Container`, `ContainerDb`, `ContainerQueue`, `Container_Ext`, `ContainerDb_Ext`, `ContainerQueue_Ext` | `Container`, `ContainerDb`, `ContainerQueue`, `ContainerExt`, `ContainerDbExt`, `ContainerQueueExt` |
| `Component`, `ComponentDb`, `ComponentQueue`, `Component_Ext`, `ComponentDb_Ext`, `ComponentQueue_Ext` | `Component`, `ComponentDb`, `ComponentQueue`, `ComponentExt`, `ComponentDbExt`, `ComponentQueueExt` |

## Boundaries and nodes

| Macro                                                          | Class                                                       |
|----------------------------------------------------------------|-------------------------------------------------------------|
| `Boundary(alias, "label", "type")`                             | `Boundary("label", mermaid={"type": "type"}, alias=...)`    |
| `Enterprise_Boundary`, `System_Boundary`, `Container_Boundary` | `EnterpriseBoundary`, `SystemBoundary`, `ContainerBoundary` |
| `Deployment_Node`, `Node`                                      | `DeploymentNode`, `Node`                                    |
| `Node_L`, `Node_R`                                             | `NodeLeft`, `NodeRight` (`c4.contrib.mermaid`)              |

The `type` argument of a boundary goes in `mermaid={"type": "..."}`. A node's technology has no portable field: put it
in the description and report it.

## Relationships

`Rel(from, to, "label", "technology", "description")` becomes
`from_ >> Rel("label", "description", technology="technology") >> to`. Pass `technology` by keyword.

| Macro                                                 | Class (`c4.contrib.mermaid`)                                  |
|-------------------------------------------------------|---------------------------------------------------------------|
| `Rel`                                                 | `Rel` (portable)                                              |
| `Rel_U/Up`, `Rel_D/Down`, `Rel_L/Left`, `Rel_R/Right` | `RelU/RelUp`, `RelD/RelDown`, `RelL/RelLeft`, `RelR/RelRight` |
| `Rel_Back`                                            | `RelBack`                                                     |
| `BiRel`                                               | `BiRel`                                                       |

Mermaid rejects relationships that end on a boundary: keep them as the source has them and note a boundary endpoint
in the report.

## Not mapped (report, do not guess)

`UpdateElementStyle`, `UpdateRelStyle`, `UpdateLayoutConfig`, `%%` comments, `title` beyond the diagram title, any macro
not in this file. A `title` goes to `Diagram("Title")`.

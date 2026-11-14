# C4-PlantUML mapping

Imports: `from c4 import ...` for portable classes; `from c4.contrib.plantuml import ...` for helpers.

## Arguments

Native macros take `(alias, label, [technology,] description, $sprite, $tags, $link, $type)`. The Python classes take
`(label, description, [technology,] alias=...)`: **description and technology swap places**, and the alias becomes a
keyword. Check each macro: `Container(web, "Web", "Django", "Serves pages")` becomes
`Container("Web", "Serves pages", "Django", alias="web")`.

| Native argument                                                  | Python                                                       |
|------------------------------------------------------------------|--------------------------------------------------------------|
| `$sprite="x"`                                                    | `plantuml={"sprite": "x"}`                                   |
| `$tags="a+b"`                                                    | `plantuml={"tags": ["a", "b"]}`                              |
| `$link="https://..."`                                            | `plantuml={"link": "https://..."}`                           |
| `$type="x"` (not on containers)                                  | `plantuml={"type": "x"}`                                     |
| `$descr="x"` (boundaries)                                        | the second argument, `description`                           |
| `SetPropertyHeader(...)` + `AddProperty(k, v)` before an element | `.with_properties((k, v), ...)` on that element              |
| `$baseShape="x"`                                                 | `plantuml={"base_shape": "x"}` (not on Db/Queue, boundaries) |

## Elements

| Macro                                                                                                  | Class                                                                                               |
|--------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `Person`, `Person_Ext`                                                                                 | `Person`, `PersonExt`                                                                               |
| `System`, `System_Ext`, `SystemDb`, `SystemDb_Ext`, `SystemQueue`, `SystemQueue_Ext`                   | `System`, `SystemExt`, `SystemDb`, `SystemDbExt`, `SystemQueue`, `SystemQueueExt`                   |
| `Container`, `Container_Ext`, `ContainerDb`, `ContainerDb_Ext`, `ContainerQueue`, `ContainerQueue_Ext` | `Container`, `ContainerExt`, `ContainerDb`, `ContainerDbExt`, `ContainerQueue`, `ContainerQueueExt` |
| `Component`, `Component_Ext`, `ComponentDb`, `ComponentDb_Ext`, `ComponentQueue`, `ComponentQueue_Ext` | `Component`, `ComponentExt`, `ComponentDb`, `ComponentDbExt`, `ComponentQueue`, `ComponentQueueExt` |

## Boundaries and nodes

Boundaries are `with` blocks; children are the elements inside the braces.

| Macro                         | Class                              |
|-------------------------------|------------------------------------|
| `Boundary`                    | `Boundary`                         |
| `Enterprise_Boundary`         | `EnterpriseBoundary`               |
| `System_Boundary`             | `SystemBoundary`                   |
| `Container_Boundary`          | `ContainerBoundary`                |
| `Deployment_Node`, `Node`     | `DeploymentNode`, `Node`           |
| `Deployment_Node_L`, `Node_L` | `DeploymentNodeLeft`, `NodeLeft`   |
| `Deployment_Node_R`, `Node_R` | `DeploymentNodeRight`, `NodeRight` |

A node's technology argument has no portable field: put it in the description and say so in the report.

## Relationships

`Rel(from, to, "label", "technology", "description", $sprite, $tags, $link)` becomes
`from_ >> Rel("label", "description", technology="technology") >> to`. Pass `technology` by keyword.

| Macro                                                         | Python (`c4.contrib.plantuml`)                                |
|---------------------------------------------------------------|---------------------------------------------------------------|
| `Rel`                                                         | `Rel` (portable)                                              |
| `Rel_U/Up`, `Rel_D/Down`, `Rel_L/Left`, `Rel_R/Right`         | `RelU/RelUp`, `RelD/RelDown`, `RelL/RelLeft`, `RelR/RelRight` |
| `Rel_Back`, `Rel_Neighbor`, `Rel_Back_Neighbor`               | `RelBack`, `RelNeighbor`, `RelBackNeighbor`                   |
| `BiRel`, `BiRel_U/Up/D/Down/L/Left/R/Right`, `BiRel_Neighbor` | `BiRel`, `BiRelU/...`, `BiRelNeighbor`                        |

Relationship `$tags`, `$sprite`, `$link` go in `plantuml={...}` on the `Rel`.

## Layout and dynamic helpers

| Macro                                                                                   | Python                                                                                 |
|-----------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------|
| `Lay_U/Up`, `Lay_D/Down`, `Lay_L/Left`, `Lay_R/Right`                                   | `LayU/LayUp`, `LayD/LayDown`, `LayL/LayLeft`, `LayR/LayRight`, called `LayRight(a, b)` |
| `Index()`, `Index(n)`, `LastIndex()`, `SetIndex(n)` as a relationship label or argument | `plantuml={"index": Index()}`                                                          |
| `increment()`, `increment(n)`                                                           | `increment(n)`                                                                         |
| `setIndex(n)`                                                                           | `set_index(n)`                                                                         |

Dynamic diagrams: a number label such as `"1. Places order"` stays a label.

## Not mapped (report, do not guess)

`Update*Style`, `Add*Tag` (tag definitions: the `$tags` on elements are kept, their styling is not), `LAYOUT_*`,
`SHOW_LEGEND`, `SHOW_FLOATING_LEGEND`, `SHOW_PERSON_*`, `UpdateLegendTitle`, `SET_SKETCH_STYLE`, `HIDE_STEREOTYPE`,
`!include` other than the C4 library files, any macro not in this file. A `render_options` equivalent, if one exists
(check `c4 render --help` and the docs), is allowed; otherwise report the macro as dropped.

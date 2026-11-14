# Round-trip check

Render the Python back to the source's own format and compare. It needs no network and no external tool.

```shell
c4 render diagram.py --plantuml -o /tmp/roundtrip.puml    # PlantUML source
c4 render diagram.py --mermaid -o /tmp/roundtrip.mmd      # Mermaid source
```

Use a scratch directory for `-o`, not the project. For a file with several diagrams, use `file.py:name` per diagram.

Count boundaries separately: `Container` also prefixes `Container_Boundary`. Per diagram, count in both the original and
the rendered text:

| Item          | PlantUML original and rendered                        | Mermaid                  |
|---------------|-------------------------------------------------------|--------------------------|
| Elements      | element macros (`Person`, `System`, `Container`, ...) | element macros           |
| Boundaries    | `*_Boundary`, `Boundary`, `Node`, `Deployment_Node`   | same                     |
| Relationships | `Rel*`, `BiRel*`                                      | `Rel*`, `BiRel`          |
| Labels        | the set of quoted labels                              | the set of quoted labels |

The rendered file may differ in order, includes, styling and layout lines: ignore those. It adds `!include` lines and a
default label for an unlabeled relationship: ignore those too.

## Best-effort formats

Structurizr DSL, LikeC4 and D2 compare counts only, no labels:

```shell
c4 render workspace.py --structurizr -o /tmp/roundtrip.dsl
c4 render project.py --likec4 -o /tmp/roundtrip.c4
c4 render diagram.py --d2 -o /tmp/roundtrip.d2
```

| Format        | Count in original and rendered                                                       |
|---------------|--------------------------------------------------------------------------------------|
| Structurizr   | elements (`person`, `softwareSystem`, `container`, `component`), `->` lines, per view |
| LikeC4        | elements (`name = kind "..."`), `->` lines, per view                                  |
| D2            | nodes (keys with a label or shape), `->` lines, per diagram                           |

Count elements and relationships in the model section, not in the `views` lines (`container shop "x"` is a view, not an
element). Per view means: the elements the view includes; for `include *`, the elements in its scope. Dropped
constructs are not counted. State in the report that only counts were compared.

## Outcome

- Counts and label sets equal: the report states "counts match" with the numbers.
- Different: find the missing or extra item. Fix the Python and render again. If it cannot be fixed (for example Mermaid
  drops a construct), list it in the report with the numbers. Never write "counts match" over a mismatch.

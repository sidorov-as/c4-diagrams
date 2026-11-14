---
name: c4-migrate-backend
description: Rewrite c4-diagrams Python between the portable `Diagram` model (PlantUML, Mermaid, D2) and a Structurizr `Workspace` or LikeC4 `Project`, or between renderers. Native source goes to c4-import. Use when asked to migrate, convert or port a c4-diagrams diagram to another backend.
---

# c4-migrate-backend

Migrates `c4-diagrams` Python to `c4-diagrams` Python. Native PlantUML, Mermaid, D2, Structurizr or LikeC4 source is out
of scope: say so and stop.

Load the `c4-diagrams` skill first. Its rules apply here: source before images, explicit backend flags, consent before
any remote service, warning before network access. Verify a migrated model with `c4 render`; export an image only under
those rules.

## Pick the path

| From → to                          | Path                                                                               |
|------------------------------------|------------------------------------------------------------------------------------|
| PlantUML, Mermaid, D2 → each other | renderer change, below                                                             |
| Portable → Structurizr or LikeC4   | [references/mapping.md](references/mapping.md), then duplicates, then report       |
| Structurizr or LikeC4 → portable   | mapping (reverse table), then report                                               |
| Structurizr ↔ LikeC4               | go through the model: read one, rewrite the other with the mapping's element rules |

## Same family: renderer change

PlantUML, Mermaid and D2 share the portable `Diagram`. Keep the Python. Change only the renderer: `c4 render --mermaid`,
`--d2`, `--plantuml`, or `as_mermaid()`. Warn about extension data the new renderer ignores (`plantuml={...}` under D2,
directional helpers under Mermaid, properties under Mermaid). Name each ignored item.

## Steps

1. Read every diagram in scope. List the elements, relationships and the diagram types.
2. Several diagrams going into one model: follow [references/duplicates.md](references/duplicates.md) before writing
   code.
3. Write the target following [references/mapping.md](references/mapping.md).
4. Render the source and confirm it builds.
5. Present the report from [references/report.md](references/report.md). Migration is done when the report lists every
   dropped construct, merge and chosen view type; never skip it.

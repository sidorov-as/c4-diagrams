---
name: c4-import
description: Rewrite an existing diagram file as c4-diagrams Python. Use when the user has C4-PlantUML (.puml), Mermaid C4, Structurizr DSL (.dsl), LikeC4 (.c4, .likec4) or D2 (.d2) source and asks to import, convert or port it to Python.
---

# c4-import

Rewrites diagram source as `c4-diagrams` Python. Markdown only: no parser, no scripts.

- **Strict:** C4-PlantUML and Mermaid C4 become a portable `Diagram`.
- **Best-effort:** Structurizr DSL becomes a `Workspace`, LikeC4 a `Project`, D2 a portable `Diagram`.
- **Not covered:** anything else (Terraform, PlantUML without C4 macros). Say so and stop. Python to Python is
  `c4-migrate-backend`.

Load the `c4-diagrams` skill first. Its rules apply here: source before images, explicit backend flags, consent before
any remote service, warning before network access, `--help` for unknown flags.

## Rules

1. **Never guess.** An unknown macro, an unclear diagram type or an unresolved `!include` is reported or asked about,
   not invented.
2. **Preserve, then report.** Data with a portable field goes there. Data only the source backend understands goes in
   `plantuml={...}`, `mermaid={...}` or a `c4.contrib` helper. Data with no home is listed in the report.
3. **Verify every import** with the round-trip check. Do not call an import done on a mismatch.
4. **Never skip the report.**

Best-effort formats (Structurizr DSL, LikeC4, D2) replace rules 2 and 3 with one rule: carry over elements,
relationships, nesting and the styles and tags `c4-diagrams` supports, and list everything else as dropped. Do not
reproduce the source language. A relationship with an unresolved endpoint is reported, never created. Verification
compares counts only.
5. **Do not restructure.** Keep the source's order and nesting; no factories or renames.

## Detect the type

| Source                                                                                | Class                                                                                               |
|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| PlantUML `!include` of `C4_Context.puml`                                              | `SystemContextDiagram`; `SystemLandscapeDiagram` only when the source says landscape (same include) |
| `C4_Container.puml`, `C4_Component.puml`                                              | `ContainerDiagram`, `ComponentDiagram`                                                              |
| `C4_Dynamic.puml`, `C4_Deployment.puml`                                               | `DynamicDiagram`, `DeploymentDiagram`                                                               |
| Mermaid header `C4Context`, `C4Container`, `C4Component`, `C4Dynamic`, `C4Deployment` | the matching class; `C4Context` is `SystemContextDiagram`                                           |

No include and no header: decide from the macros (`Container` means container, `Component` means component,
`Deployment_Node` means deployment). Still unclear: ask the user.

A `title` becomes `Diagram("Title")`. One diagram per `@startuml` block or Mermaid fence.

Best-effort sources are detected by extension and content: `workspace { model {` is Structurizr, `specification {` and
`model {` without `workspace` is LikeC4, anything else `.d2` is D2.

## Steps

1. Read the whole source. Note the type, every element, boundary, relationship and extension argument.
2. Translate with the mapping for the source: [references/plantuml-mapping.md](references/plantuml-mapping.md),
   [references/mermaid-mapping.md](references/mermaid-mapping.md),
   [references/structurizr-mapping.md](references/structurizr-mapping.md),
   [references/likec4-mapping.md](references/likec4-mapping.md) or [references/d2-mapping.md](references/d2-mapping.md).
   For D2, propose kinds and ask about undecided nodes before writing the Python.
3. Set an explicit `alias` equal to the source alias or identifier on every element, so relationships stay stable.
4. Write the Python next to the source (same name, `.py`) unless the user names a path.
5. Run the round-trip check: [references/verification.md](references/verification.md).
6. Present the report: [references/report.md](references/report.md).

# Assumptions and losses report

Present after every migration, even when empty ("nothing dropped"). Fill every heading.

```markdown
## Migration report

**From → to:** <portable ContainerDiagram ×2 → Structurizr Workspace>

### Views
- <diagram title> → <view type and key>; scope: <element> (<given | assumed>)

### Merged duplicates
- <label>: merged from <diagrams>; kept <attribute> from <diagram>
### Kept separate
- <label> in <diagram A> and <diagram B>: <reason>

### Assumptions
- <e.g. system X is the scope; EnterpriseBoundary dropped>

### Lost or approximated
- <construct>: <where it was> → <what happened>
```

Constructs with no equivalent in the target, always report when present:

- `plantuml={...}`, `mermaid={...}`, `d2={...}` extension data
- directional relationships (`RelRight`, ...), bidirectional helpers, layout helpers (`LayRight`, ...)
- PlantUML dynamic indexes (`Index`, `SetIndex`)
- sprites, links, tags carried only as extension data
- `render_options`, styles
- `EnterpriseBoundary` (Structurizr)
- properties (when the target is Mermaid)
- view type chosen by approximation (LikeC4 element view for a C4 diagram)

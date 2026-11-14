# Import report

Present after every import, even when empty ("nothing dropped"). Fill every heading.

```markdown
## Import report

**Source → output:** <diagram.puml (C4-PlantUML) → diagram.py (ContainerDiagram)>

### Diagram type

- <class chosen>: <header, include or macros that decided it>; <asked the user | detected>

### Preserved extension data

- <element or relationship>: <sprite, tags, link, direction, layout, index> → <plantuml={...} | mermaid={...} | helper>

### Approximated

- <construct>: <what the source had> → <what the Python has>

### Dropped

- <construct>: <where it was; why it has no home>

### Proposed types

- <D2 element>: <kind proposed> from <shape or class>; <confirmed by the user | assumed Container, user had no preference>

### Round trip

- <diagram>: elements <n>/<n>, relationships <n>/<n>, labels <match | differences | not compared (best-effort)>
```

Always list when present:

- `UpdateElementStyle`, `UpdateRelStyle`, `AddElementTag` and other styling macros
- `LAYOUT_*`, `SHOW_LEGEND`, legends
- unresolved or remote `!include` files
- unknown macros, left out of the Python
- sprites, tags and links on Mermaid elements (Mermaid ignores them)
- node technology folded into the description
- properties

Best-effort imports (Structurizr DSL, LikeC4, D2) also always list, when present:

- `!script`, `!include`, themes, animation, layout and unsupported styles
- unresolved relationship endpoints
- every D2 kind under "Proposed types" (omit the heading for other formats)
- that only counts were compared

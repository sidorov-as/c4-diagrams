# User settings

Look for a `## c4-diagrams` section in `AGENTS.md`, else `CLAUDE.md`, at the repository root. Use its values without
asking again.

## Template

```markdown
## c4-diagrams

- plantuml: plantuml # command, or `jar: /path/plantuml.jar` with `java: /path/java`
- mermaid: mmdc
- d2: d2
- structurizr: structurizr
- likec4: npx likec4@1.60.0 # command may include npx
- kroki: https://kroki.internal.example   # self-hosted
- kroki-allowed: true # true only for a self-hosted server the user trusts
- plantuml-server: none
- preferred-backend: plantuml # plantuml | mermaid | d2 | structurizr | likec4
```

Every field is optional. Map them to flags (`--plantuml-bin`, `--plantuml-jar`, `--java-bin`, `--mermaid-bin`,
`--d2-bin`, `--structurizr-bin`, `--likec4-bin`, `--kroki-url`) or the matching environment variables.

`kroki-allowed: true` exempts that URL from the per-use consent in [consent.md](consent.md). Public `kroki.io` and
`plantuml.com` are never exempt.

## Writing the block

Never edit `AGENTS.md` or `CLAUDE.md` unprompted. When the user supplies a binary path or server during a session, show
the block text and offer to save it; write the file only after a yes.

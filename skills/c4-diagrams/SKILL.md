---
name: c4-diagrams
description: Write or export C4 architecture diagrams with the c4-diagrams Python library. Use when asked for a C4 diagram (any C4 level), a Structurizr workspace or LikeC4 project in Python, a diagram of a codebase, PlantUML/Mermaid/D2 output, or an image export via `c4 export`. Existing PlantUML/Mermaid/Structurizr/LikeC4/D2 source goes to c4-import.
---

# c4-diagrams

Docs: https://sidorov-as.github.io/c4-diagrams/

## Rules

1. **Source first.** Produce Python and `c4 render` text. Run `c4 export` only when the user wants an image or document.
   Rendering needs no external tools.
2. **Name the backend on every export.** Never rely on a default: `--plantuml-backend local`, `--mermaid-backend local`,
   `--d2-backend local`, `--structurizr-backend local`, `--likec4-backend local`. Structurizr defaults to Kroki, a
   remote server.
3. **Remote means consent.** Kroki and PlantUML servers receive the diagram source. Say so and wait for a yes, every
   time. A local failure never falls back to remote on its own. Details: [references/consent.md](references/consent.md).
4. **Network means warning.** `npx`, installs and remote `!include` fetch over the network. Warn first; ask before
   installing.
5. **Settings first.** Read the `## c4-diagrams` block in the user's `AGENTS.md` or `CLAUDE.md` before choosing binaries
   or servers. Never edit those files without a yes. Template: [references/settings.md](references/settings.md).

## Choose the authoring model

The two models do not mix.

| Need                                                    | Write                                     |
|---------------------------------------------------------|-------------------------------------------|
| One diagram, or one diagram in PlantUML, Mermaid and D2 | portable `Diagram` (`from c4 import ...`) |
| One model with several views, or Structurizr DSL output | `Workspace` (`c4.contrib.structurizr`)    |
| One model with several views, or LikeC4 output          | `Project` (`c4.contrib.likec4`)           |

Catalogs, so you need not fetch docs:

- Portable classes, relationships, nesting, properties: [references/python-dsl.md](references/python-dsl.md)
- Structurizr and LikeC4 API: [references/whole-architecture.md](references/whole-architecture.md)
- Portable core versus backend extensions, backend comparison: [references/backends.md](references/backends.md)

Backend-only features (`plantuml={...}`, `mermaid={...}`, `d2={...}`, `c4.contrib.plantuml`) are not portable. Use them
only on request and say so.

## Render and export

```shell
c4 render diagram.py --mermaid -o diagram.mmd      # source, no tools
c4 export diagram.py --d2 --d2-backend local -f svg -o diagram.svg
c4 export workspace.py --structurizr --structurizr-backend local --structurizr-view-key containers -f png -o out.png
```

Always pass `-o` on export: without it, binary bytes go to the terminal. Target syntax: `file.py`, `file.py:name`,
`module.path:name`. Without `:name` the file needs exactly one diagram.

For a flag not listed here (`--timeout`, `--kroki-url`, `--d2-layout`, `--mermaid-puppeteer-config`, ...), run
`c4 export --help` or `c4 render --help`. The help output is current and sends nothing over the network.

## When an export fails or looks wrong

Run the export first, with the user's settings. Do not pre-check dependencies.

Read the error message first. If the export timed out (default 30 s), retry with `--timeout <seconds>` or
`RENDERING_TIMEOUT_SECONDS`; a version check is for other errors.

On a non-zero exit, or when the user reports odd output (Mermaid ignoring layout in headless mode, old distro PlantUML
packages):

1. Run `<bin> --version` for the tool in use. The binary may be overridden by a flag or by `PLANTUML_JAR`,
   `PLANTUML_BIN`, `JAVA_BIN`, `MERMAID_BIN`, `D2_BIN`, `STRUCTURIZR_BIN`, `LIKEC4_BIN`.
2. Compare with [references/tested-versions.md](references/tested-versions.md).
3. Propose a working version and its install command. Run it only after a yes.

If `import c4.contrib.structurizr` or `c4.contrib.likec4` fails, the installed `c4-diagrams` is older than 0.8.0:
propose `pip install -U c4-diagrams` and ask first.

## Diagram from a codebase

When the user asks to diagram a repository,
follow [references/codebase-to-diagram.md](references/codebase-to-diagram.md).

## Reusable elements

When the same element is declared identically in several diagrams, move it to a shared `elements.py` of factories built
with `functools.partial` and `with_properties`, and import them in each diagram. Keep relationships in the diagram
files. Guide: https://sidorov-as.github.io/c4-diagrams/guides/reusable-diagram-elements/

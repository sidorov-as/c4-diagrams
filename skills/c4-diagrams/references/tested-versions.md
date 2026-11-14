# Tested versions

"Tested with" means the version CI runs, not a proven minimum. Source: `.github/workflows/main.yml` and
`.github/actions/*/action.yml`. Update this file whenever a CI tool version changes.

| Tool                 | Tested with                          | Notes                                                                |
|----------------------|--------------------------------------|----------------------------------------------------------------------|
| Python               | 3.10, 3.11, 3.12, 3.13, 3.14         | package requires `>=3.10`                                            |
| c4-diagrams          | `>=0.8.0` for Structurizr and LikeC4 | older releases lack `c4.contrib.structurizr` and `c4.contrib.likec4` |
| PlantUML             | 1.2025.10                            | needs Java and Graphviz (`dot`)                                      |
| Mermaid CLI (`mmdc`) | 11.4.0                               | Node 20, Chromium                                                    |
| D2                   | v0.9.0                               |                                                                      |
| LikeC4               | 1.60.0                               | Node 22, Playwright Chromium                                         |
| Structurizr CLI      | 2026.06.28                           | Java 21, Playwright Chromium (PNG and SVG export)                    |

Check an installed tool: `plantuml -version`, `mmdc --version`, `d2 --version`, `likec4 --version`,
`structurizr version`.

# Installation

**c4-diagrams** is available on
[PyPI](https://pypi.org/project/c4-diagrams/):

=== "pip"

    ```bash
    pip install c4-diagrams
    ```

=== "uv"

    ```bash
    uv add c4-diagrams
    ```

## Optional Dependencies

The base package includes the Python DSL, PlantUML/Mermaid/D2 source
generation, and CLI entry point. Some features need optional Python
dependencies.

### Python Extras

#### Converters

Install the `converters` extra when you use
[JSON conversion](converters/json/json.md), including `c4 convert` and loading
JSON diagrams through the CLI:

=== "pip"

    ```bash
    pip install c4-diagrams[converters]
    ```

=== "uv"

    ```bash
    uv add c4-diagrams[converters]
    ```

#### Watch

Install the `watch` extra when you use
[CLI watch mode](cli.md#watch-mode) with `c4 render --watch` or
`c4 export --watch`:

=== "pip"

    ```bash
    pip install "c4-diagrams[watch]"
    ```

=== "uv"

    ```bash
    uv add "c4-diagrams[watch]"
    ```

## System Dependencies

Rendering source text does not require external system tools:

```bash
c4 render diagram.py --plantuml
c4 render diagram.py --mermaid
c4 render diagram.py --d2
c4 render project.py --likec4
```

Exporting images or documents with `c4 export` does require backend-specific
tools unless you use a remote PlantUML server or Kroki.

### Kroki Remote Rendering

Kroki can export PlantUML, Mermaid, D2, and Structurizr diagrams without local
Java, Graphviz, D2, Mermaid CLI, or a Structurizr CLI. The generated source text
is sent to the configured Kroki server, so use a self-managed Kroki instance for
private diagrams.

Set `KROKI_SERVER_URL` to change the default server root URL:

```bash
export KROKI_SERVER_URL=https://kroki.example.com
```

Examples:

```bash
c4 export diagram.py --plantuml --plantuml-backend kroki \
  --plantuml-use-bundled-c4-plantuml false \
  -f svg -o diagram.svg

c4 export diagram.py --d2 --d2-backend kroki \
  --kroki-method post -f png -o diagram.png

c4 export diagram.py --mermaid --mermaid-backend kroki \
  -f svg -o diagram.svg

c4 export diagram.py --structurizr --structurizr-backend kroki \
  --structurizr-view-key container-view -f svg -o diagram.svg
```

### Structurizr Requirements

The backend is tested with Structurizr CLI `2026.06.28` (`structurizr-*`
`6.2.2`).

Rendering Structurizr DSL does not need any tools. To export images locally
(instead of through Kroki), install the
[Structurizr CLI](https://docs.structurizr.com/cli) (the `structurizr` command,
with `export` support for PNG and SVG) and the Playwright Chromium browser it
uses for rasterization:

```bash
structurizr version
```

Export a view (the local backend exports PNG and SVG only, use Kroki for PDF):

```bash
c4 export workspace.py --structurizr --structurizr-backend local \
  --structurizr-view-key containers \
  -f png \
  -o containers.png
```

A workspace with a single view does not need `--structurizr-view-key`. If the
CLI is not on `PATH`, pass `--structurizr-bin` or set `STRUCTURIZR_BIN`.

### PlantUML Requirements

Use PlantUML when you need the full [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) feature set.
The minimum required version is PlantUML `1.2025.10`.

To export diagrams using the **PlantUML renderer**, choose one execution mode:

- a local `plantuml` executable available in `PATH`;
- a local `plantuml.jar` plus Java;
- a remote PlantUML server.

Graphviz is commonly required by PlantUML for layout. Some package managers
install it with PlantUML, but JAR-based installs usually need a separate
Graphviz installation.

#### Local `plantuml` executable

=== "macOS (Homebrew)"

    ```bash
    brew install plantuml graphviz
    ```

=== "Ubuntu / Debian"

    ```bash
    sudo apt install plantuml graphviz
    ```

Verify the executable:

```bash
plantuml -version
dot -V
```

!!! warning "Ubuntu / Debian package versions"

    Distribution packages can lag behind the version tested by this project.
    Check `plantuml -version`; if it is older than `1.2025.10`, use a newer
    package source or the JAR option below.

#### Local `plantuml.jar` plus Java

Install Java and Graphviz, download a PlantUML JAR, then point the CLI at it:

```bash
c4 export diagram.py --plantuml \
  --plantuml-jar /opt/plantuml/plantuml.jar \
  --java-bin java \
  -f svg \
  -o diagram.svg
```

The same values can be provided with environment variables:

```bash
export PLANTUML_JAR=/opt/plantuml/plantuml.jar
export JAVA_BIN=java
```

#### Remote PlantUML server

Remote rendering does not need local Java, PlantUML, or Graphviz:

```bash
c4 export diagram.py --plantuml \
  --plantuml-backend remote \
  --plantuml-server-url https://www.plantuml.com/plantuml \
  -f svg \
  -o diagram.svg
```

#### Bundled C4-PlantUML files

`c4-diagrams` bundles [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) include files. Use the bundled files for
offline or reproducible local PlantUML exports:

```bash
c4 export diagram.py --plantuml \
  --plantuml-use-bundled-c4-plantuml true \
  -f svg \
  -o diagram.svg
```

### Mermaid Requirements

Use Mermaid when you want Mermaid C4 source or Mermaid CLI rendered artifacts.
Mermaid C4 syntax is [experimental](https://mermaid.ai/open-source/syntax/c4.html).
The minimum required version is Mermaid CLI `11.4.0`.

To export diagrams using the **Mermaid renderer**, install a local
[`mmdc`](https://github.com/mermaid-js/mermaid-cli) executable. Mermaid CLI
runs through Puppeteer, so it also needs a working Chrome/Chromium environment.
The default Mermaid CLI package may download a compatible browser during
installation; locked-down CI or container environments may need an explicit
Chrome/Chromium install and a Puppeteer config.

#### Local Mermaid CLI

```bash
npm install -g @mermaid-js/mermaid-cli@11.4.0
```

Verify the executable:

```bash
mmdc --version
```

!!! note "Mermaid CLI layout configuration"

    Mermaid CLI has a known issue where `mmdc` can ignore Mermaid layout
    configuration in headless mode
    ([mermaid-js/mermaid-cli#440](https://github.com/mermaid-js/mermaid-cli/issues/440)).
    If diagram layout options are not applied, run Mermaid CLI with a Puppeteer
    config that disables headless mode:

    ```json
    {
      "headless": false
    }
    ```

    Pass the file through `c4 export` with `--mermaid-puppeteer-config`, or
    use `--mermaid-puppeteer-headless false`.

If Mermaid CLI cannot launch Chrome in your environment, pass a Puppeteer config
through the CLI:

```bash
c4 export diagram.py --mermaid \
  --mermaid-puppeteer-config puppeteer-config.json \
  -f svg \
  -o diagram.svg
```

For simple headless configuration, use:

```bash
c4 export diagram.py --mermaid \
  --mermaid-puppeteer-headless true \
  -f svg \
  -o diagram.svg
```

### D2 Requirements

Use D2 when you want D2 source or locally rendered D2 artifacts.
Tested with D2 `v0.9.0`.

Rendering D2 source with `c4 render` does not require the D2 CLI:

```bash
c4 render diagram.py --d2 -o diagram.d2
```

To export diagrams using the **D2 renderer**, install a local
[`d2`](https://d2lang.com/tour/install/) executable. D2 supports multiple
installation methods; after installation, verify that the executable is
available and new enough:

```bash
d2 version
```

#### Local D2 CLI

=== "macOS (Homebrew)"

    ```bash
    brew install d2
    ```

=== "Install script"

    ```bash
    curl -fsSL https://d2lang.com/install.sh | sh -s --
    ```

Export with the local D2 backend:

```bash
c4 export diagram.py --d2 \
  -f svg \
  -o diagram.svg
```

If the executable is not named `d2` or is not in `PATH`, pass it explicitly or
set `D2_BIN`:

```bash
c4 export diagram.py --d2 \
  --d2-bin /opt/d2/bin/d2 \
  -f svg \
  -o diagram.svg
```

### LikeC4 Requirements

Use LikeC4 when you want LikeC4 `.c4` source or locally exported views. The
backend is tested with LikeC4 `1.60.0`.

Rendering LikeC4 source with `c4 render` does not require any tool:

```bash
c4 render project.py --likec4 -o architecture.c4
```

To export images with the **LikeC4 renderer**, install Node.js, the `likec4`
CLI and the Playwright Chromium browser it uses for rasterization:

```bash
npm install -g likec4@1.60.0
npx playwright install chromium
likec4 --version
```

Export a view (LikeC4 exports PNG and JPG only, there is no SVG):

```bash
c4 export project.py --likec4 \
  --likec4-view-key index \
  -f png \
  -o index.png
```

A project with a single view does not need `--likec4-view-key`. If the CLI is
not installed globally, pass a command or set `LIKEC4_BIN`:

```bash
c4 export project.py --likec4 \
  --likec4-bin "npx likec4@1.60.0" \
  --likec4-view-key index \
  -o index.png
```

If Chromium is missing, the command fails with a message that suggests
installing it.

## Agent skills

The repository ships four skills for AI coding agents, installed with the
[`skills`](https://www.npmjs.com/package/skills) CLI:

```bash
npx skills add sidorov-as/c4-diagrams
```

- `c4-diagrams` writes, renders and exports diagrams, picks the right authoring
  model, asks before sending diagram source to a remote service (Kroki, a
  PlantUML server), and warns before network downloads.
- `c4-migrate-backend` rewrites a diagram between the portable `Diagram`
  (PlantUML, Mermaid, D2) and a Structurizr `Workspace` or LikeC4 `Project`,
  and reports what was lost.
- `c4-import` rewrites C4-PlantUML, Mermaid C4, Structurizr DSL, LikeC4 and D2
  source as `c4-diagrams` Python (the last three best-effort), checks the result
  by rendering it back, and reports what was kept, approximated or dropped.
- `c4-pipeline` first assesses whether Docker Compose or Kubernetes manifests
  can feed an automatic diagram, gives a verdict with evidence, and only then
  helps write a generator and a CI drift check in your repository.

The skills are Markdown only. They read optional tool settings from a
`## c4-diagrams` section in your `AGENTS.md` or `CLAUDE.md`.

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

The base package includes the Python DSL, PlantUML/Mermaid source generation,
and CLI entry point. Some features need optional Python dependencies.

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

## System Dependencies

Rendering source text does not require external system tools:

```bash
c4 render diagram.py --plantuml
c4 render diagram.py --mermaid
```

Exporting images or documents with `c4 export` does require backend-specific
tools unless you use a remote PlantUML server.

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

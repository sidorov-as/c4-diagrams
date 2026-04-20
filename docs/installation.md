# Installation

**c4-diagrams** is available on [PyPI](https://pypi.org/project/c4-diagrams/) so installation
is straightforward:

=== "pip"

    ```bash
    pip install c4-diagrams
    ```

=== "uv"

    ```bash
    uv add c4-diagrams
    ```

## Optional Dependencies

Some features of `c4-diagrams` require additional optional dependencies.

**Converters**

If you plan to use **diagram conversion functionality** (e.g. [generating diagrams from JSON](converters/json/json.md)),
install the `converters` extra:

=== "pip"

    ```bash
    pip install c4-diagrams[converters]
    ```

=== "uv"

    ```bash
    uv add c4-diagrams[converters]
    ```

## System Dependencies

While `c4-diagrams` itself is installed via PyPI, exporting diagrams may require additional
third-party tools depending on the selected renderer.

Some renderers rely on external system binaries that must be installed separately.

### PlantUML

To export diagrams using the **PlantUML renderer**, you need **one** of the following:

- A local `plantuml` binary available in your `PATH`
- A local `plantuml.jar` (requires Java)
- Access to a remote PlantUML server

**Install locally**

=== "macOS (Homebrew)"

    ```bash
    brew install plantuml
    ```

=== "Ubuntu / Debian"

    ```bash
    sudo apt install plantuml
    ```

**Verify installation**

```bash
plantuml -version
```

### Mermaid

To export diagrams using the **Mermaid renderer**, you need a local [`mmdc`](https://github.com/mermaid-js/mermaid-cli)
binary available in your `PATH`.

**Install locally**

```bash
npm install -g @mermaid-js/mermaid-cli
```

**Verify installation**

```bash
mmdc --version
```

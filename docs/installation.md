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

## System Dependencies

The `c4-diagrams` package itself is installed via PyPI, but exporting diagrams
may require additional third-party tools depending on the selected renderer.

Some renderers rely on external system binaries that must be installed separately.

### PlantUML

To export diagrams using the PlantUML renderer, you need **one** of the following:

- A local `plantuml` binary available in your `PATH`
- A local `plantuml.jar` with Java installed
- A remote PlantUML server

=== "macOS (Homebrew)"

    ```bash
    brew install plantuml
    ```

=== "Ubuntu / Debian"

    ```bash
    sudo apt install plantuml
    ```

After installation, verify that PlantUML is available:

```bash
plantuml -version
```

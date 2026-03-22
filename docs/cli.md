## Getting Started

Diagrams can be defined using the [Python DSL](concepts/diagrams.md) or a [JSON representation](converters/json/json.md).

### Python Example

Create a diagram using the Python DSL:

```python
# diagram.py
from c4 import Person, Rel, System, SystemContextDiagram


with SystemContextDiagram() as diagram:
    user = Person("User", "System user")
    backend = System("Backend API", "Main application backend")

    user >> Rel("Uses HTTP API") >> backend
```

<br/>

To render the diagram to text (by default, PlantUML source), run:

```shell
c4 render diagram.py > diagram.puml
```

<details>
<summary>Generated PlantUML source</summary>

```puml
@startuml
' convert it with additional command line argument -DRELATIVE_INCLUDE="relative/absolute" to use locally
!if %variable_exists("RELATIVE_INCLUDE")
    !include %get_variable_value("RELATIVE_INCLUDE")/C4_Context.puml
!else
    !include https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master/C4_Context.puml
!endif

Person(user_a467, "User", "System user")

System(backend_api_8c20, "Backend API", "Main application backend")

Rel(user_a467, backend_api_8c20, "Uses HTTP API")

@enduml
```

</details>

<br/>

To export the diagram to a rendered artifact (by default, PNG format), run:

```shell
c4 export diagram.py > diagram.png
```

This generates the diagram below:

<figure markdown="span">
  ![cli-diagram](assets/cli-diagram.png){ width="300" }
  <figcaption>diagram.png</figcaption>
</figure>

### JSON Support

Diagrams can also be defined in [JSON format](converters/json/json.md).

The same diagram expressed in JSON:

```json
{
    "type": "SystemContextDiagram",
    "elements": [
        {
          "type": "Person",
          "alias": "user",
          "label": "User",
          "description": "System user"
        },
        {
          "type": "System",
          "alias": "app",
          "label": "Backend API",
          "description": "Main application backend"
        }
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "user",
            "to": "app",
            "label": "Uses HTTP API"
        }
    ]
}
```

JSON diagrams are treated the same way as Python diagrams:

- `c4 render diagram.json` — generate textual output (e.g. PlantUML)
- `c4 export diagram.json` — generate rendered artifacts (e.g. PNG)
- `c4 convert diagram.json` — convert to another representation (e.g. Python)


<br/>

To convert a JSON diagram into the Python DSL, run:

```shell
c4 convert diagram.json --json-to-py > diagram.py
```

This generates:

```python
# diagram.py
from c4 import (
    Person,
    Rel,
    System,
    SystemContextDiagram,
)


with SystemContextDiagram():
    user = Person('User', 'System user', alias='user')
    app = System('Backend API', 'Main application backend', alias='app')
    user >> Rel('Uses HTTP API') >> app
```

<br/>

## CLI Reference

### c4 render

Render a diagram to text output (by default, PlantUML source).

**Usage:**

```shell
c4 render [-h] [-o OUTPUT] \
          [--renderer {plantuml} | --plantuml] \
          [--plantuml-use-new-c4-style] \
          target
```

**Arguments:**

| Name     | Type   | Description                                                                                                                                                         |
|----------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `target` | string | Diagram target: Python file or module (`file.py`, `file.py:diagram`, `module.path`, `module.path:diagram`) or a [JSON file](converters/json/json.md) (`file.json`). |

**Options**:

| Name                                                       | Type                | Description                                                                                             | Default    |
|------------------------------------------------------------|---------------------|---------------------------------------------------------------------------------------------------------|------------|
| `--renderer`                                               | choice (`plantuml`) | Renderer to use (overrides the diagram's default renderer).                                             | `plantuml` |
| `--plantuml`                                               | boolean             | Use PlantUML renderer <br/> (alias for <span style="white-space: nowrap;">`--renderer plantuml`</span>) | False      |
| <span style="white-space: nowrap;">`-o`, `--output`</span> | path                | Redirect output to a file.                                                                              | stdout     |
| `-h`, `--help`                                             | boolean             | Show this help message and exit.                                                                        | False      |

**PlantUML Options**:

These options apply when using the plantuml renderer.

| Name                                                                    | Type    | Description                          | Default |
|-------------------------------------------------------------------------|---------|--------------------------------------|---------|
| <span style="white-space: nowrap;">`--plantuml-use-new-c4-style`</span> | boolean | Activates the new C4-PlantUML style. | False   |

<br/>

### c4 export

Export a diagram to a rendered artifact (e.g., PNG or SVG).

The available formats depend on the selected `renderer`.

!!! note

    Requires [system dependencies](installation.md#system-dependencies).

**Usage:**

```shell
c4 export [-h] [-o OUTPUT] [-f {eps,latex,png,svg,txt,utxt}] \
          [--timeout TIMEOUT] \
          [--renderer {plantuml} | --plantuml] \
          [--plantuml-backend {local,remote}] \
          [--plantuml-server-url PLANTUML_SERVER_URL] \
          [--plantuml-bin PLANTUML_BIN | --plantuml-jar PLANTUML_JAR] \
          [--java-bin JAVA_BIN] \
          [--plantuml-skinparam-dpi PLANTUML_SKINPARAM_DPI] \
          [--plantuml-use-new-c4-style] \
          target
```

**Arguments:**

| Name     | Type   | Description                                                                                                                                                         |
|----------|--------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `target` | string | Diagram target: Python file or module (`file.py`, `file.py:diagram`, `module.path`, `module.path:diagram`) or a [JSON file](converters/json/json.md) (`file.json`). |

**Options**:

| Name                                                       | Type                                                 | Description                                                                                                          | Default    |
|------------------------------------------------------------|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------|------------|
| <span style="white-space: nowrap;">`-f`, `--format`</span> | choice (`eps`, `latex`, `png`, `svg`, `txt`, `utxt`) | Output format (render-specific).<br/>Supported formats:<br/>`plantuml`: `eps`, `latex`, `png`, `svg`, `txt`, `utxt`. | `png`      |
| `--timeout`                                                | integer                                              | Render timeout in seconds.<br/>Can also be set via the `RENDERING_TIMEOUT_SECONDS` environment variable.             | 30         |
| `--renderer`                                               | choice (`plantuml`)                                  | Renderer to use (overrides the diagram's default renderer).                                                          | `plantuml` |
| `--plantuml`                                               | boolean                                              | Use PlantUML renderer <br/> (alias for <span style="white-space: nowrap;">`--renderer plantuml`</span>).             | False      |
| <span style="white-space: nowrap;">`-o`, `--output`</span> | path                                                 | Redirect output to a file.                                                                                           | `stdout`   |
| `-h`, `--help`                                             | boolean                                              | Show this help message and exit.                                                                                     | False      |

**PlantUML Options**:

These options apply when using the plantuml renderer.

| Name                                                                    | Type                       | Description                                                                                                                                                                                                           | Default                                           |
|-------------------------------------------------------------------------|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| <span style="white-space: nowrap;">`--plantuml-backend`</span>          | choice (`local`, `remote`) | How to run PlantUML: local execution or remote server.                                                                                                                                                                | `local`                                           |
| <span style="white-space: nowrap;">`--plantuml-server-url`</span>       | string                     | PlantUML server URL.<br/>If not provided, the `PLANTUML_SERVER_URL` environment variable will be used.                                                                                                                | [plantuml.com](https://www.plantuml.com/plantuml) |
| <span style="white-space: nowrap;">`--plantuml-bin`</span>              | string (path or command)   | PlantUML executable (command name or full path).<br/>If not provided, the `PLANTUML_BIN` environment variable will be used.                                                                                           | `plantuml`                                        |
| <span style="white-space: nowrap;">`--plantuml-jar`</span>              | path                       | Path to the PlantUML JAR file (runs via Java).<br/>If provided, the `PLANTUML_BIN` environment variable is ignored.<br/>Can also be set via the `PLANTUML_JAR` environment variable.                                  | None                                              |
| <span style="white-space: nowrap;">`--java-bin`</span>                  | string (path or command)   | Java executable to use when running PlantUML via JAR.<br/>If not provided, the `JAVA_BIN` environment variable will be used.                                                                                          | `java`                                            |
| <span style="white-space: nowrap;">`--plantuml-skinparam-dpi`</span>    | integer                    | Set PlantUML `skinparam dpi` value to control raster (PNG) resolution.<br/>This modifies diagram rendering and affects all output formats.<br/>Can also be set via the `PLANTUML_SKINPARAM_DPI` environment variable. | None                                              |
| <span style="white-space: nowrap;">`--plantuml-use-new-c4-style`</span> | boolean                    | Activates the new C4-PlantUML style.                                                                                                                                                                                  | False                                             |


### c4 convert

Convert a diagram from one representation to another.

!!! note

    Requires [additional dependencies](installation.md#optional-dependencies).

**Usage:**

```shell
c4 convert [-h] \
           [--json-to-py] \
           [--from {json} | --from-json] \
           [--to {py} | --to-py] \
           [-o OUTPUT] \
           target
```

**Arguments:**

| Name     | Type   | Description     |
|----------|--------|-----------------|
| `target` | string | Diagram target. |

**Options:**

| Name             | Type            | Description                                                                     | Default  |
|------------------|-----------------|---------------------------------------------------------------------------------|----------|
| `--from`         | choice (`json`) | Input format.                                                                   | —        |
| `--to`           | choice (`py`)   | Output format.                                                                  | —        |
| `--from-json`    | flag            | Convert from [JSON diagram](converters/json/json.md) (alias for `--from json`). | False    |
| `--to-py`        | flag            | Convert to Python DSL (alias for `--to py`).                                    | False    |
| `--json-to-py`   | flag            | Shortcut for `--from json --to py`.                                             | False    |
| `-o`, `--output` | path            | Redirect output to a file.                                                      | `stdout` |
| `-h`, `--help`   | flag            | Show this help message and exit.                                                | False    |

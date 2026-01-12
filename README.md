<!-- begin logo -->
<p align="center">
  <a href="https://github.com/sidorov-as/c4-diagrams/">
    <img src="https://sidorov-as.github.io/c4-diagrams/assets/c4-diagrams-logo.png" alt="c4-diagrams logo" />
  </a>
</p>

<p align="center">
  <em>A Python DSL for C4 model diagrams.</em>
</p>

<!-- end logo -->

# c4-diagrams

[![Release](https://img.shields.io/pypi/v/c4-diagrams.svg)](https://pypi.org/project/c4-diagrams/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/c4-diagrams)](https://pypi.org/project/c4-diagrams/)
[![Build status](https://img.shields.io/github/actions/workflow/status/sidorov-as/c4-diagrams/main.yml?branch=main)](https://github.com/sidorov-as/c4-diagrams/actions/workflows/main.yml?query=branch%3Amain)
[![Maintainability](https://qlty.sh/gh/sidorov-as/projects/c4-diagrams/maintainability.svg)](https://qlty.sh/gh/sidorov-as/projects/c4-diagrams)
[![Code Coverage](https://qlty.sh/gh/sidorov-as/projects/c4-diagrams/coverage.svg)](https://qlty.sh/gh/sidorov-as/projects/c4-diagrams)
[![License](https://img.shields.io/github/license/sidorov-as/c4-diagrams)](https://img.shields.io/github/license/sidorov-as/c4-diagrams)

**c4-diagrams** is a Python DSL for defining **[C4 model](https://c4model.com/) architecture diagrams as code**.

The package provides first-class abstractions for C4 entities — people, systems, containers, components, boundaries,
and relationships — allowing you to describe software architecture in Python and render it into multiple diagram formats.

## Features

- Declarative Python DSL for C4 modeling
- First-class C4 entities and relationships
- Multiple rendering backends
- Suitable for documentation, ADRs, and architecture reviews
- Renderer-agnostic DSL (same code → different outputs)

## Rendering backends

Currently supported and planned backends:

- [**PlantUML**](https://github.com/plantuml-stdlib/C4-PlantUML)
  - local rendering via `plantuml` CLI or `plantuml.jar`
  - remote rendering via PlantUML server
- [**Mermaid**](https://mermaid.js.org/syntax/c4.html) — WIP
- [**Structurizr**](https://structurizr.com/) — WIP

## Getting started

**c4-diagrams** requires **Python 3.10** or higher.

```shell
# using pip (pip3)
$ pip install c4-diagrams

# using pipenv
$ pipenv install c4-diagrams

# using poetry
$ poetry add c4-diagrams

# using uv
$ uv add c4-diagrams
```

## Minimal example

A minimal system context diagram defined in Python:

```python
from c4 import Person, Rel, System, SystemContextDiagram

with SystemContextDiagram("Example system context") as diagram:
    user = Person(label="User", description="System user")
    backend = System(label="Backend API", description="Main application backend")

    user >> Rel("Uses HTTP API") >> backend

print(diagram.as_plantuml())
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

title Example system context

Person(user_91e7, "User", "System user")

System(backend_api_610a, "Backend API", "Main application backend")

Rel(user_91e7, backend_api_610a, "Uses HTTP API")

@enduml
```

</details>

## Examples

| System context diagram                                    | Container Diagram                                       | Component Diagram                                       |
|-----------------------------------------------------------|---------------------------------------------------------|---------------------------------------------------------|
| ![system context](https://sidorov-as.github.io/c4-diagrams/assets/system-context-diagram.png) | ![container diagram](https://sidorov-as.github.io/c4-diagrams/assets/container-diagram.png) | ![component diagram](https://sidorov-as.github.io/c4-diagrams/assets/component-diagram.png) |

## Project Links

- [**PyPI**](https://pypi.org/project/c4-diagrams/)
- [**GitHub**](https://github.com/sidorov-as/c4-diagrams/)
- [**Documentation**](https://sidorov-as.github.io/c4-diagrams/)
- [**Changelog**](https://github.com/sidorov-as/c4-diagrams/tree/main/CHANGELOG.md)

## License

* [MIT LICENSE](https://github.com/sidorov-as/c4-diagrams/blob/main/LICENSE)

## Contribution

[Contribution guidelines for this project](https://github.com/sidorov-as/c4-diagrams/blob/main/CONTRIBUTING.md)

---

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).

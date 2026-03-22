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

The following backends are being explored but are not currently planned:

- [**Structurizr**](https://structurizr.com/)
- [**D2**](https://d2lang.com/)

## Getting started

**c4-diagrams** requires **Python 3.10** or higher.

```console
pip install c4-diagrams
```

## Example

Here’s an example of **System Context** diagram defined in Python:

```python3
# diagram.py
from c4 import *


with SystemContextDiagram("Acme Shop Platform") as diagram:
    user = Person(
        "Customer",
        "A registered customer who browses products and places orders.",
    )

    with EnterpriseBoundary("Acme Corp"):
        web_app = System(
            "Web Application",
            "Customer-facing website for browsing products and placing orders.",
        )

        api_backend = System(
            "Backend API",
            "Handles authentication, order processing, and business logic.",
        )

    email_provider = SystemExt(
        "Email Provider",
        "Delivers transactional emails.",
    )

    user >> RelRight("Uses") >> web_app
    web_app >> RelRight("Calls API") >> api_backend
    api_backend >> RelDown("Sends emails via") >> email_provider
```

To export the diagram to a rendered artifact, run:

```console
c4 export diagram.py > diagram.png
```

This generates the diagram below:

<p align="center">
  <img src="https://sidorov-as.github.io/c4-diagrams/assets/readme-diagram.png" alt="readme-diagram" />
</p>

<p align="center">
  <em>diagram.png</em>
</p>

For details (renderers, diagram types, API), see the [documentation](https://sidorov-as.github.io/c4-diagrams/).

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

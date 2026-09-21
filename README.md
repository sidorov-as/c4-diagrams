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
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/sidorov-as/c4-diagrams)

**c4-diagrams** is a Python DSL for defining **[C4 model](https://c4model.com/) architecture diagrams as code**.

The package provides first-class abstractions for C4 entities — people, systems, containers, components, boundaries,
and relationships — allowing you to describe software architecture in Python and render it into multiple diagram formats.

## Features

- Declarative Python DSL for C4 modeling
- First-class C4 entities and relationships
- Multiple rendering backends
- Suitable for documentation, ADRs, and architecture reviews
- Portable core DSL for the common C4 subset, with backend-specific features
  available through contrib extensions

## Rendering backends

| Backend                                                    | What you describe                                       | Formats                         | Docs                                                                                   |
|------------------------------------------------------------|---------------------------------------------------------|---------------------------------|----------------------------------------------------------------------------------------|
| [PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) | Portable diagram, rendered as C4-PlantUML               | PNG, SVG, EPS, LaTeX, TXT, UTXT | [PlantUML backend](https://sidorov-as.github.io/c4-diagrams/renderers/plantuml/)       |
| [Mermaid](https://mermaid.ai/open-source/syntax/c4.html)   | Portable diagram, rendered as Mermaid C4 (experimental) | PNG, SVG, PDF                   | [Mermaid backend](https://sidorov-as.github.io/c4-diagrams/renderers/mermaid/)         |
| [D2](https://d2lang.com/)                                  | Portable diagram, rendered as D2                        | PNG, SVG, PDF                   | [D2 backend](https://sidorov-as.github.io/c4-diagrams/renderers/d2/)                   |
| [Structurizr](https://structurizr.com/)                    | Structurizr `Workspace` (model, views, styles)          | PNG, SVG, PDF                   | [Structurizr backend](https://sidorov-as.github.io/c4-diagrams/renderers/structurizr/) |
| [LikeC4](https://likec4.dev/)                              | LikeC4 `Project` (specification, model, views)          | PNG, JPG                        | [LikeC4 backend](https://sidorov-as.github.io/c4-diagrams/renderers/likec4/)           |

## Getting started

**c4-diagrams** requires **Python 3.10** or higher.

```console
pip install c4-diagrams
```

## Example

Here’s an example of a **system context diagram** defined in Python:

```python
# diagram.py
from c4 import Person, Rel, System, SystemContextDiagram

with SystemContextDiagram("Online Shop") as diagram:
    customer = Person("Customer", "Buys goods online.")
    shop = System("Online Shop", "Takes orders from customers.")
    payments = System("Payment Provider", "Processes card payments.")

    customer >> Rel("Buys goods") >> shop
    shop >> Rel("Takes payments") >> payments
```

To export the diagram to a rendered artifact (PlantUML by default), run:

```console
c4 export diagram.py > diagram.png
```

This generates the diagram below:

<p align="center">
  <img src="https://sidorov-as.github.io/c4-diagrams/assets/overview/overview.plantuml.png" alt="overview-diagram" />
</p>

<p align="center">
  <em>diagram.png</em>
</p>

The same diagram renders with Mermaid and D2, and Structurizr and LikeC4 have their own
authoring models. See the [documentation](https://sidorov-as.github.io/c4-diagrams/) for all backends,
and the [Examples](https://sidorov-as.github.io/c4-diagrams/examples/) page for more diagram types.

## Project Links

- [**PyPI**](https://pypi.org/project/c4-diagrams/)
- [**GitHub**](https://github.com/sidorov-as/c4-diagrams/)
- [**Documentation**](https://sidorov-as.github.io/c4-diagrams/)
- [**Changelog**](https://github.com/sidorov-as/c4-diagrams/tree/main/CHANGELOG.md)

## License

* [MIT LICENSE](https://github.com/sidorov-as/c4-diagrams/blob/main/LICENSE)

This project bundles files from the [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) project.
C4-PlantUML is licensed under the [MIT License](https://github.com/plantuml-stdlib/C4-PlantUML/blob/master/LICENSE).


## Contribution

[Contribution guidelines for this project](https://github.com/sidorov-as/c4-diagrams/blob/main/CONTRIBUTING.md)

## Acknowledgements

- [C4 model](https://c4model.com/)
- [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML)
- [Structurizr](https://structurizr.com/)
- [LikeC4](https://likec4.dev/)
- [Mermaid](https://mermaid.js.org/)
- [D2](https://d2lang.com/)
- [Kroki](https://kroki.io/)
- [diagrams](https://github.com/mingrammer/diagrams)
- [buildzr](https://github.com/amirulmenjeni/buildzr)
- [pystructurizr](https://github.com/nielsvanspauwen/pystructurizr)


---

Repository initiated with [fpgmaas/cookiecutter-uv](https://github.com/fpgmaas/cookiecutter-uv).

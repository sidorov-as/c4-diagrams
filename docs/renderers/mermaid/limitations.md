# Mermaid Limitations

Mermaid C4 syntax is experimental and smaller than the C4-PlantUML macro
surface. Diagrams that use only the portable core are the best fit for Mermaid.

## Relationship endpoints

Mermaid relationships must connect concrete elements. They cannot target
boundaries such as `Boundary`, `EnterpriseBoundary`, `SystemBoundary`,
`ContainerBoundary`, `Node`, `NodeLeft`, `NodeRight`, or `DeploymentNode`.

The Mermaid renderer and Mermaid JSON converter reject relationships whose
`from` or `to` endpoint resolves to a boundary alias. Point the relationship at
a concrete nested element instead.

```python
with SystemContextDiagram() as diagram:
    customer = Person("Customer", alias="customer")
    with SystemBoundary("Platform", alias="platform") as platform:
        web_app = System("Web App", alias="web_app")

    # Invalid for Mermaid: platform is a boundary.
    customer >> Rel("Uses") >> platform

    # Valid for Mermaid: web_app is a concrete element.
    customer >> Rel("Uses") >> web_app
```

## Unsupported PlantUML behavior

| PlantUML feature                                                                 | Mermaid behavior                                                |
|----------------------------------------------------------------------------------|-----------------------------------------------------------------|
| Directional relationship helpers such as `RelRight`                              | Not supported                                                   |
| Bidirectional relationship helpers such as `BiRel`                               | Not supported                                                   |
| Relative layout helpers such as `LayRight`                                       | Not supported                                                   |
| Dynamic index helpers such as `Index` and `set_index`                            | Not supported                                                   |
| Deployment node variants `NodeLeft` and `NodeRight`                              | Supported as `Node_L` and `Node_R` through `c4.contrib.mermaid` |
| Deployment node variants `DeploymentNodeLeft` and `DeploymentNodeRight`          | Not supported                                                   |
| PlantUML element fields such as `sprite`, `base_shape`, and relationship `index` | Not supported                                                   |
| Remote rendering backend                                                         | Not supported                                                   |

By default, Mermaid ignores foreign extension data. A diagram with
`plantuml={...}` data can still be rendered with Mermaid, but PlantUML-only
hints are not emitted. Enable strict extension validation when Mermaid rendering
must fail if a diagram contains PlantUML-owned extension data.

## Local CLI requirements

Image rendering requires the Mermaid CLI (`mmdc`) to be available locally. Source
rendering with `diagram.as_mermaid()` does not require the CLI.

Configure the local backend with constructor arguments or the `MERMAID_BIN`
environment variable when `mmdc` is not on `PATH`.

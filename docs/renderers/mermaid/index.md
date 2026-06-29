# Mermaid Rendering Backend

The Mermaid rendering backend renders C4 diagrams as Mermaid C4 syntax. Mermaid
C4 support is experimental, so this backend deliberately has a smaller feature
surface than the PlantUML rendering backend.

???+ warning "Mermaid C4 diagram status"

    Mermaid’s C4 diagram support is currently **experimental**.

    According to the official [Mermaid documentation](https://mermaid.ai/open-source/syntax/c4.html):

    >C4 Diagram: This is an experimental diagram for now. The syntax and properties can change in future releases.
    >Proper documentation will be provided when the syntax is stable.

## Capability table

| Capability                                     | Status                                                        |
|------------------------------------------------|---------------------------------------------------------------|
| System context diagrams                        | Supported as `C4Context`                                      |
| System landscape diagrams                      | Rendered as `C4Context`                                       |
| Container diagrams                             | Supported as `C4Container`                                    |
| Component diagrams                             | Supported as `C4Component`                                    |
| Dynamic diagrams                               | Supported as `C4Dynamic`, subject to Mermaid syntax limits    |
| Deployment diagrams                            | Supported as `C4Deployment`, subject to Mermaid syntax limits |
| Deployment `NodeLeft` and `NodeRight` variants | Supported through `c4.contrib.mermaid`                        |
| Boundary extension data                        | Supported with `mermaid={...}`                                |
| Element and relationship style options         | Supported through `MermaidRenderOptionsBuilder`               |
| Layout row configuration                       | Supported through `UpdateLayoutConfig` options                |
| Image rendering                                | Local Mermaid CLI only                                        |

## Pages

- [Renderers](renderers.md): `MermaidRenderer` and local Mermaid CLI backend.
- [Extensions](extensions.md): preferred `mermaid={...}` authoring syntax.
- [Options](options.md): layout and style options.
- [Limitations](limitations.md): Mermaid C4 syntax limits and unsupported PlantUML helpers.

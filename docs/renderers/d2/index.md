# D2 Rendering Backend

The D2 rendering backend maps diagrams to [D2](https://d2lang.com/) source.
It is a text-first backend: rendering to `.d2` source does not require a local
D2 binary, while image export delegates to an optional local D2 installation.

For portable model code, start with
[Portable core and backend extensions](../../concepts/portable-core-and-extensions.md).
For D2-specific behavior, use the pages in this section.

## Capability table

| Capability                                                      | Status                                                                              | Where to configure                                                           |
|-----------------------------------------------------------------|-------------------------------------------------------------------------------------|------------------------------------------------------------------------------|
| D2 source rendering                                             | Supported for all current C4 diagram types                                          | [`Diagram.as_d2()`](renderers.md) and [`Diagram.save_as_d2()`](renderers.md) |
| D2 image export                                                 | Supported through local D2 for SVG, PNG, and PDF                                    | [Renderers](renderers.md)                                                    |
| Element and boundary mapping                                    | Supported for core elements, boundaries, and deployment nodes                       | Core diagram classes plus [`d2={...}`](extensions.md)                        |
| Nested boundaries                                               | Preserved as D2 containers                                                          | Core boundary and deployment node classes                                    |
| Element and relationship properties                             | Rendered as Markdown tables when enabled                                            | [Options](options.md)                                                        |
| Layout direction, theme, sequence shape, relationship numbering | Supported as render options                                                         | [Options](options.md)                                                        |
| Structured legends                                              | Supported through `D2RenderOptions.legend`                                          | [Options](options.md)                                                        |
| D2 extension fields                                             | Supported for shapes, styles, links, tooltips, icons, classes, and local directions | [Extensions](extensions.md)                                                  |
| Bidirectional relationships                                     | Rendered as two directed edges by default, or one `<->` edge                        | [Options](options.md)                                                        |

## Pages

- [Renderers](renderers.md): `D2Renderer`, local D2 backend, `as_d2()`, and `save_as_d2()`.
- [Options](options.md): direction, theme, sequence diagrams, relationship numbering, properties, bidirectional edges, and legends.
- [Extensions](extensions.md): preferred `d2={...}` authoring syntax.
- [Limitations](limitations.md): validation behavior and degraded backend-only helpers.

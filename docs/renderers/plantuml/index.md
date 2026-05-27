# PlantUML Rendering Backend

The PlantUML rendering backend maps diagrams to [C4-PlantUML](https://github.com/plantuml-stdlib/C4-PlantUML) output.
It is the richest rendering backend in this project and owns PlantUML-only DSL helpers,
extension data, render options, local/remote image backends, and C4-PlantUML
include behavior.

For portable model code, start with
[Portable core and backend extensions](../../concepts/portable-core-and-extensions.md).
For PlantUML-specific behavior, use the pages in this section.

## Capability table

| Capability                       | Status                                                                   | Where to configure                                                       |
|----------------------------------|--------------------------------------------------------------------------|--------------------------------------------------------------------------|
| C4-PlantUML element mapping      | Supported for core C4 elements, boundaries, and deployment nodes         | Core diagram classes plus [`plantuml={...}`](extensions.md)              |
| C4-PlantUML relationship mapping | Portable `Rel` plus PlantUML directional and bidirectional helpers       | [`c4.contrib.plantuml`](layout.md)                                       |
| Layout direction                 | Supported as render options                                              | [Styles and options](styles-and-options.md)                              |
| Relative positioning             | Supported with `Lay*` helpers                                            | [Layout helpers](layout.md)                                              |
| Dynamic indexes                  | Supported for dynamic diagrams                                           | [Dynamic indexes](dynamic-indexes.md)                                    |
| Properties                       | Supported on most elements and relationships                             | [Properties](properties.md)                                              |
| Tags, styles, and legend         | Supported through extension data and render options                      | [Extensions](extensions.md), [styles and options](styles-and-options.md) |
| Local backend                    | Supported with `plantuml` binary or `plantuml.jar`                       | [Renderers](renderers.md)                                                |
| Remote backend                   | Supported with PlantUML-compatible HTTP servers                          | [Renderers](renderers.md)                                                |
| Bundled C4-PlantUML includes     | Uses remote C4-PlantUML includes by default, with local include override | [Limitations](limitations.md)                                            |
| Sequence diagrams                | Not exposed by the Python DSL                                            | [Limitations](limitations.md)                                            |

## Pages

- [Renderers](renderers.md): `PlantUMLRenderer`, local backend, and remote backend.
- [Extensions](extensions.md): preferred `plantuml={...}` authoring syntax.
- [Layout helpers](layout.md): directional relationships, bidirectional relationships, and relative layouts.
- [Dynamic indexes](dynamic-indexes.md): `Index`, `LastIndex`, `SetIndex`, `increment`, and `set_index`.
- [Styles and options](styles-and-options.md): diagram layout direction, legend, sketch style, and C4 visual style.
- [Properties](properties.md): PlantUML property tables.
- [Limitations](limitations.md): unsupported C4-PlantUML features and include behavior.

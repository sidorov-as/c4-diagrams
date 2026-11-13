# Render Options

Different backends support various layout and styling options that control
diagram direction, legend visibility, and overall visual appearance.


Backend-specific render options can be configured via [`RenderOptions`][c4.renderers.common.RenderOptions]
in the constructor, or patched after creation with `diagram.set_render_options(...)`:


```python
from c4 import SystemContextDiagram
from c4.renderers.plantuml.options import PlantUMLRenderOptionsBuilder


plantuml_render_options = (
    PlantUMLRenderOptionsBuilder()
    .layout_top_down(with_legend=True)  # Vertical layout with legend enabled
    .build()
)

with SystemContextDiagram() as diagram:
    ...

diagram.set_render_options(plantuml=plantuml_render_options)

diagram.save_as_plantuml("output.puml")
```

In this example, `plantuml_render_options` is passed
to [`PlantUMLRenderer`][c4.renderers.plantuml.renderer.PlantUMLRenderer].

## Unlabeled Relationships

A relationship created with `a >> b` has no label. C4-PlantUML and C4-Mermaid
reject such a relationship, so the PlantUML and Mermaid renderers write the
placeholder `uses` for it. Set `default_relationship_label` on
[`PlantUMLRenderOptionsBuilder`](plantuml/styles-and-options.md#unlabeled-relationships)
or [`MermaidRenderOptionsBuilder`](mermaid/options.md#unlabeled-relationships)
to change the text, or to `None` to write the relationship as it is stored. D2,
Structurizr and LikeC4 do not use the option and write no placeholder.

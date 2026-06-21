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

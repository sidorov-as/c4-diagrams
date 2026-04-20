# Render Options

Different backends support various layout and styling options that control
diagram direction, legend visibility, and overall visual appearance.


Backend-specific render options can be configured via [`RenderOptions`][c4.renderers.common.RenderOptions]:


```python
from c4 import SystemContextDiagram
from c4.renderers.plantuml.options import PlantUMLRenderOptionsBuilder
from c4.renderers import RenderOptions


plantuml_render_options = (
    PlantUMLRenderOptionsBuilder()
    .layout_top_down(with_legend=True)  # Vertical layout with legend enabled
    .build()
)

render_options = RenderOptions(plantuml=plantuml_render_options)

with SystemContextDiagram(render_options=render_options) as diagram:
    ...

# You can also set render options after diagram creation:
# diagram.render_options = render_options

diagram.save_as_plantuml("output.puml")
```

In this example, `plantuml_render_options` is passed
to [`PlantUMLRenderer`][c4.renderers.plantuml.renderer.PlantUMLRenderer].

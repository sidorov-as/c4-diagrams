from dataclasses import dataclass

from c4.renderers.d2.options import D2RenderOptions
from c4.renderers.mermaid.options import MermaidRenderOptions
from c4.renderers.plantuml.options import PlantUMLRenderOptions


@dataclass
class RenderOptions:
    """
    Rendering options grouped by renderer/backend.

    Attributes:
        plantuml: Optional PlantUML-specific render options.
        mermaid: Optional Mermaid-specific render options.
        d2: Optional D2-specific render options.
    """

    plantuml: PlantUMLRenderOptions | None = None
    mermaid: MermaidRenderOptions | None = None
    d2: D2RenderOptions | None = None

    @property
    def is_empty(self) -> bool:
        """Return whether no render options are configured."""
        return all(
            [
                self.plantuml is None,
                self.mermaid is None,
                self.d2 is None,
            ],
        )

    def __bool__(self) -> bool:
        return not self.is_empty

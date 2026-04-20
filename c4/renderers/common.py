from dataclasses import dataclass

from c4.renderers.mermaid.options import MermaidRenderOptions
from c4.renderers.plantuml.options import PlantUMLRenderOptions


@dataclass
class RenderOptions:
    """
    Rendering options grouped by renderer/backend.

    Attributes:
        plantuml: Optional PlantUML-specific render options.
        mermaid: Optional Mermaid-specific render options.
    """

    plantuml: PlantUMLRenderOptions | None = None
    mermaid: MermaidRenderOptions | None = None

    @property
    def is_empty(self) -> bool:
        """Return whether no render options are configured."""
        return all(
            [
                self.plantuml is None,
                self.mermaid is None,
            ],
        )

from dataclasses import dataclass

from c4.renderers.plantuml.layout_options import (
    LayoutConfig as PlantUMLLayoutConfig,
)


@dataclass
class RenderOptions:
    """
    Rendering options grouped by renderer/backend.

    Attributes:
        plantuml: Optional PlantUML-specific layout configuration.
    """

    plantuml: PlantUMLLayoutConfig | None = None

    @property
    def is_empty(self) -> bool:
        """Return whether no render options are configured."""
        return all([self.plantuml is None])

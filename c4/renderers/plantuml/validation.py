from __future__ import annotations

from typing import Generic

from c4.diagrams.core import (
    Diagram,
    DiagramValidator,
    TDiagram,
)
from c4.enums import (
    IGNORE_FOREIGN,
    ExtensionValidationModeType,
    RendererEnum,
)


class PlantUMLDiagramValidator(
    DiagramValidator[TDiagram],
    Generic[TDiagram],
):
    """Validate PlantUML-specific rendering constraints."""

    def __init__(
        self,
        *,
        renderer_name: str = "PlantUMLRenderer",
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        super().__init__(
            renderer_type=RendererEnum.PLANTUML,
            renderer_name=renderer_name,
            extension_validation_mode=extension_validation_mode,
        )


def validate_plantuml_diagram(
    diagram: Diagram,
    *,
    renderer_name: str = "PlantUMLRenderer",
    extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
) -> None:
    """Validate that a diagram can be rendered as PlantUML."""
    validator: PlantUMLDiagramValidator[Diagram] = PlantUMLDiagramValidator(
        renderer_name=renderer_name,
        extension_validation_mode=extension_validation_mode,
    )
    validator.validate(diagram)

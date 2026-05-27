from __future__ import annotations

from typing import Generic

from c4.diagrams.core import (
    BaseDiagramElement,
    Boundary,
    Diagram,
    DiagramValidator,
    ExtensionValidationModeType,
    Relationship,
    TDiagram,
)
from c4.diagrams.core.traversal import IGNORE_FOREIGN
from c4.enums import RendererEnum


class MermaidDiagramValidator(DiagramValidator[TDiagram], Generic[TDiagram]):
    """Validate Mermaid-specific rendering constraints."""

    def __init__(
        self,
        *,
        renderer_name: str = "MermaidRenderer",
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        super().__init__(
            renderer_type=RendererEnum.MERMAID,
            renderer_name=renderer_name,
            extension_validation_mode=extension_validation_mode,
        )

    def _check_relationship_participants(
        self,
        relationship: Relationship,
    ) -> None:
        """Validate Mermaid relationship endpoints."""
        from_element, to_element = relationship.get_participants()  # type: ignore[var-annotated]
        from_alias = from_element.alias
        to_alias = to_element.alias

        for participant in (from_element, to_element):
            if isinstance(participant, Boundary):
                participant_type = participant.__class__.__name__
                raise ValueError(  # noqa: TRY004
                    "Mermaid relationships cannot target boundaries: "
                    f"{from_alias} -> {to_alias} targets "
                    f"{participant_type}({participant.alias}). "
                    "Use a concrete nested element instead."
                )

    def _check_element(self, element: BaseDiagramElement) -> None:
        """Validate one Mermaid diagram declaration item."""
        super()._check_element(element)

        if isinstance(element, Relationship):
            self._check_relationship_participants(element)


def validate_mermaid_diagram(
    diagram: Diagram,
    *,
    renderer_name: str = "MermaidRenderer",
    extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
) -> None:
    """Validate that a diagram can be rendered as Mermaid."""
    validator: MermaidDiagramValidator[Diagram] = MermaidDiagramValidator(
        renderer_name=renderer_name,
        extension_validation_mode=extension_validation_mode,
    )
    validator.validate(diagram)

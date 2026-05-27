from __future__ import annotations

from collections.abc import Iterator
from typing import Generic

from c4.diagrams.core.components import BaseDiagramElement, Boundary
from c4.diagrams.core.diagram import TDiagram
from c4.enums import (
    IGNORE_FOREIGN,
    ExtensionValidationMode,
    ExtensionValidationModeType,
    RendererEnum,
)


def iter_validation_items(
    scope: TDiagram | Boundary,
) -> Iterator[BaseDiagramElement]:
    """Return a flat recursive stream of all declaration items."""
    for item in scope.ordered_elements:
        yield item

        if isinstance(item, Boundary):
            yield from iter_validation_items(item)


class DiagramValidator(Generic[TDiagram]):
    """Validate renderer-owned constraints against a diagram."""

    def __init__(
        self,
        *,
        renderer_type: RendererEnum,
        renderer_name: str,
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        self.renderer_type = renderer_type
        self.renderer_name = renderer_name
        self._extension_validation_mode = ExtensionValidationMode(
            extension_validation_mode
        )

    def _check_allowed_renderers(
        self,
        element: BaseDiagramElement,
    ) -> None:
        """Validate that the element can be rendered by this renderer."""
        if not element.allowed_renderers:
            return None

        if self.renderer_type not in element.allowed_renderers:
            element_name = element.__class__.__name__
            renderer_type = self.renderer_type.value
            allowed = ", ".join([rt.value for rt in element.allowed_renderers])

            raise ValueError(
                f"{element_name} is not supported by {self.renderer_name} "
                f"({renderer_type}). Allowed renderer types: {allowed}."
            )

        return None

    def _check_supported_extensions(
        self,
        element: BaseDiagramElement,
    ) -> None:
        """Validate backend-specific extension data for this renderer."""
        if self._extension_validation_mode is IGNORE_FOREIGN:
            return None

        if not element.extensions:  # pragma: no cover
            return None

        renderer_key = self.renderer_type.value

        foreign_extensions = {
            key: value
            for key, value in element.extensions.items()
            if key != renderer_key and value is not None
        }
        if not foreign_extensions:  # pragma: no cover
            return None

        element_name = element.__class__.__name__
        extension_names = ", ".join(sorted(foreign_extensions))

        raise ValueError(
            f"{element_name} has unsupported backend extensions for "
            f"{self.renderer_name}: {extension_names}. "
            f"Render with a matching renderer or remove those extensions."
        )

    def _check_supported_nesting(self, diagram: TDiagram) -> None:
        """
        Validate renderer-specific nesting semantics.

        Validators should override this when their target model cannot
        preserve some parent-child relationships represented by the core
        diagram.
        """
        return None

    def _check_element(self, element: BaseDiagramElement) -> None:
        """Validate one diagram declaration item."""
        self._check_allowed_renderers(element)
        self._check_supported_extensions(element)

    def validate(self, diagram: TDiagram) -> None:
        """Validate that this renderer can faithfully render the diagram."""
        for element in iter_validation_items(diagram):
            self._check_element(element)

        self._check_supported_nesting(diagram)

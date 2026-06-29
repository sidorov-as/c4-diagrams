from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any, Generic

from c4.diagrams.core import (
    BaseDiagramElement,
    Boundary,
    Diagram,
    DiagramValidator,
    Element,
    ExtensionValidationModeType,
    Relationship,
    TDiagram,
)
from c4.diagrams.core.enums import RelationshipType
from c4.enums import IGNORE_FOREIGN, RendererEnum
from c4.renderers.d2.constants import (
    _D2_STYLE_BOOLEAN_KEYS,
    _D2_STYLE_INTEGER_KEYS,
    _D2_STYLE_KEYS,
    _D2_STYLE_STRING_KEYS,
)
from c4.renderers.d2.identifiers import D2Identifier, D2IdentifierPolicy


class D2UnresolvedRelationshipEndpointError(ValueError):
    """Raised when D2 validation cannot resolve a relationship endpoint."""


class D2UnsupportedDeclarationError(ValueError):
    """Raised when D2 validation encounters unsupported declarations."""


class D2ExtensionValidationError(ValueError):
    """Raised when D2 extension data is malformed or unsupported."""


_SUPPORTED_RELATIONSHIP_TYPES = {
    RelationshipType.REL,
    RelationshipType.BI_REL,
}

_D2_EXTENSION_KEY = "d2"
_D2_DIRECTIONS = {"up", "down", "left", "right"}
_D2_ELEMENT_EXTENSION_KEYS = {
    "shape",
    "style",
    "icon",
    "near",
    "tooltip",
    "link",
    "classes",
    "direction",
}
_D2_RELATIONSHIP_EXTENSION_KEYS = {
    "style",
    "icon",
    "near",
    "tooltip",
    "link",
    "classes",
}
_D2_STRING_EXTENSION_KEYS = {
    "shape",
    "icon",
    "near",
    "tooltip",
    "link",
}


class D2DiagramValidator(
    DiagramValidator[TDiagram],
    Generic[TDiagram],
):
    """Validate D2-specific rendering constraints."""

    def __init__(
        self,
        *,
        renderer_name: str = "D2Renderer",
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        super().__init__(
            renderer_type=RendererEnum.D2,
            renderer_name=renderer_name,
            extension_validation_mode=extension_validation_mode,
        )
        self._identifiers: dict[str, D2Identifier] = {}

    def iter_render_items(
        self,
        diagram: TDiagram,
    ) -> Iterator[BaseDiagramElement]:
        """Return the top-level declaration validation stream."""
        yield from diagram.ordered_elements

    def iter_boundary_render_items(
        self,
        boundary: Boundary,
    ) -> Iterator[BaseDiagramElement]:
        """Return the declaration validation stream inside a boundary."""
        yield from boundary.ordered_elements

    def validate(self, diagram: TDiagram) -> None:
        """Validate that the diagram can be rendered as D2."""
        self._identifiers = D2IdentifierPolicy(strict=True).build(
            diagram,
            self,
        )
        super().validate(diagram)

    def _check_element(self, element: BaseDiagramElement) -> None:
        """Validate one D2 diagram declaration item."""
        super()._check_element(element)
        self._check_d2_extensions(element)

        if isinstance(element, Relationship):
            self._check_relationship_type(element)
            self._check_relationship_endpoints(element)

    def _check_d2_extensions(self, element: BaseDiagramElement) -> None:
        if not element.extensions:
            return

        extension = element.extensions.get(_D2_EXTENSION_KEY)
        if extension is None:
            return

        if not isinstance(extension, Mapping):
            raise D2ExtensionValidationError(
                self._extension_error_prefix(element)
                + "must be a mapping or None."
            )

        allowed_keys = (
            _D2_RELATIONSHIP_EXTENSION_KEYS
            if isinstance(element, Relationship)
            else _D2_ELEMENT_EXTENSION_KEYS
        )
        unknown_keys = set(extension) - allowed_keys
        if unknown_keys:
            keys = ", ".join(sorted(str(key) for key in unknown_keys))
            raise D2ExtensionValidationError(
                self._extension_error_prefix(element)
                + f"contains unsupported keys: {keys}."
            )

        for key, value in extension.items():
            self._check_d2_extension_value(element, str(key), value)

    def _check_d2_extension_value(
        self,
        element: BaseDiagramElement,
        key: str,
        value: Any,
    ) -> None:
        if value is None:
            return

        if key in _D2_STRING_EXTENSION_KEYS:
            self._check_string_value(element, key, value)
            return

        if key == "direction":
            if value not in _D2_DIRECTIONS:
                allowed = ", ".join(sorted(_D2_DIRECTIONS))
                raise D2ExtensionValidationError(
                    self._extension_error_prefix(element)
                    + f"direction must be one of: {allowed}."
                )
            return

        if key == "classes":
            if not isinstance(value, list) or any(
                not isinstance(item, str) for item in value
            ):
                raise D2ExtensionValidationError(
                    self._extension_error_prefix(element)
                    + "classes must be a list of strings or None."
                )
            return

        if key == "style":  # pragma: no brancj
            self._check_style_extension(element, value)
            return

    def _check_style_extension(
        self,
        element: BaseDiagramElement,
        style: Any,
    ) -> None:
        if not isinstance(style, Mapping):
            raise D2ExtensionValidationError(
                self._extension_error_prefix(element)
                + "style must be a mapping or None."
            )

        unknown_keys = set(style) - _D2_STYLE_KEYS
        if unknown_keys:
            keys = ", ".join(sorted(str(key) for key in unknown_keys))
            raise D2ExtensionValidationError(
                self._extension_error_prefix(element)
                + f"style contains unsupported keys: {keys}."
            )

        for key, value in style.items():
            self._check_style_value(element, str(key), value)

    def _check_style_value(
        self,
        element: BaseDiagramElement,
        key: str,
        value: Any,
    ) -> None:
        if value is None:
            return

        if key in _D2_STYLE_STRING_KEYS:
            self._check_string_value(element, f"style.{key}", value)
            return

        if key in _D2_STYLE_INTEGER_KEYS:
            if not isinstance(value, int) or isinstance(value, bool):
                raise D2ExtensionValidationError(
                    self._extension_error_prefix(element)
                    + f"style.{key} must be an integer or None."
                )
            return

        if key in _D2_STYLE_BOOLEAN_KEYS:
            if not isinstance(value, bool):
                raise D2ExtensionValidationError(
                    self._extension_error_prefix(element)
                    + f"style.{key} must be a boolean or None."
                )
            return

        if key == "opacity":  # pragma: no branch
            if (
                not isinstance(value, (int, float))
                or isinstance(value, bool)
                or not 0 <= value <= 1
            ):
                raise D2ExtensionValidationError(
                    self._extension_error_prefix(element)
                    + "style.opacity must be a number between 0 and 1 "
                    "or None."
                )
            return

    def _check_string_value(
        self,
        element: BaseDiagramElement,
        key: str,
        value: Any,
    ) -> None:
        if not isinstance(value, str):
            raise D2ExtensionValidationError(
                self._extension_error_prefix(element)
                + f"{key} must be a string or None."
            )

    def _extension_error_prefix(self, element: BaseDiagramElement) -> str:
        return f"{element.__class__.__name__} D2 extension data "

    def _check_relationship_type(self, relationship: Relationship) -> None:
        if relationship.relationship_type in _SUPPORTED_RELATIONSHIP_TYPES:
            return

        raise D2UnsupportedDeclarationError(
            f"{relationship.relationship_type.value} is a layout-only "
            "relationship variant and cannot be represented faithfully by D2."
        )

    def _check_relationship_endpoints(
        self,
        relationship: Relationship,
    ) -> None:
        source: Element
        destination: Element
        source, destination = relationship.get_participants()

        for endpoint in (source, destination):
            if endpoint.alias not in self._identifiers:
                raise D2UnresolvedRelationshipEndpointError(
                    "D2 relationship endpoint is not declared in the "
                    f"diagram: {endpoint.alias!r}."
                )


def validate_d2_diagram(
    diagram: Diagram,
    *,
    renderer_name: str = "D2Renderer",
    extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
) -> None:
    """Validate that a diagram can be rendered as D2."""
    validator: D2DiagramValidator[Diagram] = D2DiagramValidator(
        renderer_name=renderer_name,
        extension_validation_mode=extension_validation_mode,
    )
    validator.validate(diagram)

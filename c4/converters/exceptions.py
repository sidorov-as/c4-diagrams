from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from c4.diagrams.core import Element


class ConversionError(Exception):
    """Base exception for all diagram conversion errors."""

    def __init__(self, message: str) -> None:
        """
        Initialize the conversion error.

        Args:
            message: Human-readable error message.
        """
        self.message = message

        super().__init__(message)


class DiagramJSONSchemaParsingError(ConversionError):
    """Raised when a JSON diagram cannot be parsed."""

    def __init__(self, details: str) -> None:
        """
        Initialize the parsing error.

        Args:
            details: Additional parsing error details.
        """
        super().__init__(f"Failed to parse JSON diagram: {details}.")


class DiagramJSONSchemaValidationError(ConversionError):
    """Raised when a JSON diagram does not match the expected schema."""

    def __init__(self, details: str) -> None:
        """
        Initialize the validation error.

        Args:
            details: Additional validation error details.
        """
        super().__init__(f"JSON diagram schema validation failed:\n{details}.")


class ElementResolutionError(ConversionError):
    """Raised when an element cannot be resolved by alias or label."""

    def __init__(self, alias_or_label: str) -> None:
        """
        Initialize the element resolution error.

        Args:
            alias_or_label: Alias or label that could not be resolved.
        """
        super().__init__(
            f"Could not resolve an element with alias or label: "
            f"{alias_or_label!r}."
        )


class ElementResolutionConflictError(ConversionError):
    """
    Raised when a label matches multiple elements and resolution is ambiguous.
    """

    def __init__(self, label: str, conflicted_elements: list[Element]) -> None:
        """
        Initialize the element resolution conflict error.

        Args:
            label: Label that matched multiple elements.
            conflicted_elements: Elements that conflict with each other.
        """
        elements = ", ".join(str(element) for element in conflicted_elements)
        super().__init__(
            f"Could not resolve element by label {label!r}: "
            f"multiple matches found ({elements})."
        )

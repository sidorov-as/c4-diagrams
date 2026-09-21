from __future__ import annotations

from c4.exceptions import C4Exception


class StructurizrError(C4Exception):
    """Base exception class for Structurizr's contrib integration."""


class StructurizrRenderingError(StructurizrError):
    """Raised when rendering a Structurizr workspace fails."""


class StructurizrBackendConfigurationError(StructurizrError):
    """Raised when a Structurizr export backend is misconfigured."""


def relationship_missing_endpoint_error(
    *,
    source_alias: str,
    destination_alias: str,
    missing_side: str,
    missing_alias: str,
) -> StructurizrRenderingError:
    """Report a relationship endpoint omitted from the native model."""
    return StructurizrRenderingError(
        f'Cannot render relationship "{source_alias} -> {destination_alias}": '
        f'{missing_side} alias "{missing_alias}" was not emitted into the '
        "Structurizr model. Check that both endpoints belong to the workspace."
    )


def parent_child_relationship_error(
    *,
    source_alias: str,
    destination_alias: str,
    relationship_text: str,
) -> StructurizrRenderingError:
    """Report the Structurizr restriction on parent-child relationships."""
    return StructurizrRenderingError(
        "Structurizr DSL does not allow relationships between parent and "
        f'child elements: "{relationship_text}" '
        f"({source_alias} -> {destination_alias})."
    )


__all__ = (
    "StructurizrBackendConfigurationError",
    "StructurizrError",
    "StructurizrRenderingError",
    "parent_child_relationship_error",
    "relationship_missing_endpoint_error",
)

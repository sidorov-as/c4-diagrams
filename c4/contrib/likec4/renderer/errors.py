from __future__ import annotations

from c4.exceptions import C4Exception


class LikeC4Error(C4Exception):
    """Base exception class for LikeC4's contrib integration."""


class LikeC4RenderingError(LikeC4Error):
    """Raised when rendering a LikeC4 project fails."""


class LikeC4ValidationError(LikeC4RenderingError):
    """Raised when a project cannot be rendered to valid LikeC4 DSL."""


class LikeC4BackendConfigurationError(LikeC4Error):
    """Raised when a LikeC4 export backend is misconfigured."""


class LikeC4LocalRenderingError(LikeC4RenderingError):
    """Raised when the local ``likec4`` CLI fails to export a view."""


def undeclared_error(
    *, owner: str, what: str, name: str
) -> LikeC4ValidationError:
    """Report a kind, tag or color missing from the specification."""
    return LikeC4ValidationError(
        f'{owner}: {what} "{name}" is not declared in the specification.'
    )


def parent_child_relationship_error(
    *, source: str, target: str
) -> LikeC4ValidationError:
    """Report the LikeC4 restriction on parent-child relationships."""
    return LikeC4ValidationError(
        "LikeC4 does not allow relationships between an element and its own "
        f'ancestor or descendant: "{source}" -> "{target}".'
    )


def missing_endpoint_error(
    *, owner: str, side: str, endpoint: str
) -> LikeC4ValidationError:
    """Report a relationship endpoint that is not part of the project."""
    return LikeC4ValidationError(
        f'{owner}: {side} "{endpoint}" does not belong to this project.'
    )


__all__ = (
    "LikeC4BackendConfigurationError",
    "LikeC4Error",
    "LikeC4LocalRenderingError",
    "LikeC4RenderingError",
    "LikeC4ValidationError",
    "missing_endpoint_error",
    "parent_child_relationship_error",
    "undeclared_error",
)

from __future__ import annotations

import warnings
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from c4.contrib.structurizr._options import (
    StructurizrRenderOptions,
)
from c4.contrib.structurizr._styles import (
    StructurizrStyleModel,
)
from c4.contrib.structurizr.workspace.model import (
    Model,
)
from c4.contrib.structurizr.workspace.styles import (
    Styles,
)
from c4.contrib.structurizr.workspace.views import (
    Views,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.renderers import BaseRenderer


class Workspace:
    """
    A native Structurizr workspace ready to render as DSL.

    Attributes:
        properties: Custom workspace properties.
        _model: Elements, relationships, and deployment topology.
        _views: Ordered collection of declared views.
        _styles: Workspace-level style declarations.
    """

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        theme: str | None = None,
        default_renderer: BaseRenderer[Workspace] | None = None,
        render_options: StructurizrRenderOptions | None = None,
    ) -> None:
        """
        Initialize a Structurizr workspace.

        Args:
            name: Optional workspace title.
            description: Optional workspace description.
            theme: Optional custom theme URL or path accepted by the
                Structurizr CLI. No theme is emitted by default. The former
                default value ``"default"`` is deprecated: it is ignored
                and a ``DeprecationWarning`` is issued.
            default_renderer: Renderer used when ``render`` receives none.
            render_options: Optional Structurizr renderer configuration.
        """
        self.properties: dict[str, Any] = {}

        self._title = name
        self._description = description
        if theme == "default":
            warnings.warn(
                'Structurizr theme="default" is deprecated and ignored; '
                "omit the theme or pass a custom theme URL.",
                DeprecationWarning,
                stacklevel=2,
            )
            theme = None
        self.theme = theme
        self._default_renderer = default_renderer
        self._render_options = render_options
        self._model = Model(self)
        self._views = Views(self)
        self._styles = Styles(self)
        self._element_styles: list[StructurizrStyleModel] = []
        self._relationship_styles: list[StructurizrStyleModel] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    @property
    def name(self) -> str | None:
        """Return the workspace name used in rendered output."""
        return self._title

    @property
    def description(self) -> str | None:
        """Return the workspace description."""
        return self._description

    @property
    def model(self) -> Model:
        """Return the workspace model."""
        return self._model

    @property
    def views(self) -> Views:
        """Return the workspace view collection."""
        return self._views

    @property
    def styles(self) -> Styles:
        """Return the workspace style declarations."""
        return self._styles

    @property
    def element_styles(self) -> tuple[StructurizrStyleModel, ...]:
        """Return workspace-level element style declarations."""
        return tuple(self._element_styles)

    @property
    def relationship_styles(self) -> tuple[StructurizrStyleModel, ...]:
        """Return workspace-level relationship style declarations."""
        return tuple(self._relationship_styles)

    @property
    def render_options(self) -> StructurizrRenderOptions | None:
        """Return renderer options reserved for Structurizr output."""
        return self._render_options

    @render_options.setter
    def render_options(self, value: StructurizrRenderOptions | None) -> None:
        """Set renderer options reserved for Structurizr output."""
        self._render_options = value

    def set_property(self, key: str, value: Any) -> Self:
        """
        Set a workspace property and return this workspace.

        Args:
            key: Property name.
            value: Property value.
        """
        self.properties[key] = value
        return self

    def render(
        self,
        renderer: BaseRenderer[Workspace] | None = None,
    ) -> str:
        """
        Render this workspace as Structurizr DSL.

        Args:
            renderer: Optional Structurizr renderer to use.
        """
        from c4.contrib.structurizr.renderer import StructurizrRenderer

        active = renderer or self._default_renderer or StructurizrRenderer()
        if not isinstance(active, StructurizrRenderer):
            raise TypeError(
                "Structurizr Workspace requires StructurizrRenderer; got "
                f"{type(active).__name__}."
            )

        return active.render(self)

    def save(
        self,
        path: str | Path,
        renderer: BaseRenderer[Workspace] | None = None,
    ) -> Path:
        """
        Render the workspace and save the DSL to ``path``.

        Args:
            path: Destination file path.
            renderer: Optional Structurizr renderer to use.
        """
        result = Path(path)
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(self.render(renderer), encoding="utf-8")
        return result

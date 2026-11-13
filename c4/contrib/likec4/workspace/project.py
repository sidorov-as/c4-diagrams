from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import Self

from c4.contrib.likec4.workspace.deployment import Deployment
from c4.contrib.likec4.workspace.model import Model
from c4.contrib.likec4.workspace.specification import Specification
from c4.contrib.likec4.workspace.views import Views

if TYPE_CHECKING:  # pragma: no cover
    from c4.renderers import BaseRenderer


class Project:
    """
    A LikeC4 project ready to render as ``.c4`` text.

    Attributes:
        name: Optional project title.
        view_key: View exported as an image when the renderer is not given
            one; the only view is used when neither is set.
    """

    def __init__(
        self,
        name: str | None = None,
        default_renderer: BaseRenderer[Project] | None = None,
        view_key: str | None = None,
    ) -> None:
        """
        Initialize an empty project.

        Args:
            name: Optional project title.
            default_renderer: Renderer used when ``render`` receives none.
            view_key: View exported as an image by default.
        """
        self.name = name
        self.view_key = view_key
        self._default_renderer = default_renderer
        self._specification = Specification(self)
        self._model = Model(self)
        self._deployment = Deployment(self)
        self._views = Views(self)

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    @property
    def specification(self) -> Specification:
        """Return the project's vocabulary."""
        return self._specification

    @property
    def model(self) -> Model:
        """Return the project's model."""
        return self._model

    @property
    def deployment(self) -> Deployment:
        """Return the project's deployment."""
        return self._deployment

    @property
    def views(self) -> Views:
        """Return the project's views."""
        return self._views

    def render(self, renderer: BaseRenderer[Project] | None = None) -> str:
        """
        Render this project as LikeC4 DSL.

        Args:
            renderer: Optional LikeC4 renderer to use.
        """
        from c4.contrib.likec4.renderer import LikeC4Renderer

        active = renderer or self._default_renderer or LikeC4Renderer()
        if not isinstance(active, LikeC4Renderer):
            raise TypeError(
                "LikeC4 Project requires LikeC4Renderer; got "
                f"{type(active).__name__}."
            )

        return active.render(self)

    def save(
        self,
        path: str | Path,
        renderer: BaseRenderer[Project] | None = None,
    ) -> Path:
        """
        Render the project and save the DSL to ``path``.

        Args:
            path: Destination file path.
            renderer: Optional LikeC4 renderer to use.
        """
        result = Path(path)
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(self.render(renderer), encoding="utf-8")
        return result

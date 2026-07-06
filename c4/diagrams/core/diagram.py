from __future__ import annotations

from pathlib import Path
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    TypeVar,
)

from typing_extensions import Self

from c4.diagrams.core.enums import DiagramType
from c4.diagrams.core.utils import (
    AliasGenerator,
    get_boundary,
    is_valid_alias,
    set_diagram,
)
from c4.utils import MISSING, Maybe

if TYPE_CHECKING:  # pragma: no cover
    from c4.diagrams.core.components import (
        BaseDiagramElement,
        Boundary,
        Element,
        Relationship,
        TBoundary,
        TElement,
        TRelationship,
    )
    from c4.renderers import (
        BaseRenderer,
        D2Renderer,
        D2RenderOptions,
        MermaidRenderer,
        MermaidRenderOptions,
        PlantUMLRenderer,
        PlantUMLRenderOptions,
        RenderOptions,
    )

_T = TypeVar("_T")


class Diagram:
    """
    Represents a complete C4 diagram.

    Manages the registration and layout of elements, boundaries,
    relationships, and renderers.
    """

    type: ClassVar[DiagramType] = DiagramType.DIAGRAM

    def __init__(
        self,
        title: str | None = None,
        default_renderer: BaseRenderer[Diagram] | None = None,
        render_options: RenderOptions | None = None,
    ) -> None:
        """
        Initialize a new diagram.

        Args:
            title: Optional title to label the diagram.
            default_renderer: Optional default renderer to use for rendering.
            render_options: Optional renderer-specific options.
        """
        self._title = title
        self._default_renderer = default_renderer
        self._elements: list[Element] = []
        self._boundaries: list[Boundary] = []
        self._relationships: list[Relationship] = []
        self._render_options = render_options

        self.__elements_by_alias: dict[str, Element] = {}
        self.__elements_by_label: dict[str, list[Element]] = {}
        self.__alias_generator = AliasGenerator()
        self.__referenced_elements: list[str] = []
        self.__ordered_elements: list[BaseDiagramElement] = []

    def __enter__(self) -> Self:
        """
        Enter the diagram context.

        Automatically sets this diagram as the current active diagram.

        Returns:
            The current instance.
        """
        set_diagram(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,  # type: ignore[valid-type]
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exit the diagram context and clear the current diagram.
        """
        set_diagram(None)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        attrs = []

        if self._title:
            attrs.append(f"title={self._title!r}")

        args = ", ".join(attrs)
        return f"{cls_name}({args})"

    def _check_alias(self, element: Element) -> None:
        """Validate and register an element alias within this diagram."""
        alias = element.alias

        if existing_element := self.get_element_by_alias(alias):
            raise ValueError(f"Duplicated alias {alias!r}: {existing_element}.")

        if not is_valid_alias(alias):
            raise ValueError(
                f"Alias {alias!r} of {element} must be a valid identifier."
            )

        self.__elements_by_alias[alias] = element

    def _check_label(self, element: Element) -> None:
        """Register an element under its human-readable label."""
        label = element.label

        self.__elements_by_label.setdefault(label, [])
        self.__elements_by_label[label].append(element)

    @property
    def title(self) -> str | None:
        """
        Returns the title of the diagram.
        """
        return self._title

    @property
    def elements(self) -> list[Element]:
        """
        Returns a list of top-level elements in the diagram.
        """
        return self._elements

    @property
    def boundaries(self) -> list[Boundary]:
        """
        Returns all top-level boundaries in the diagram.
        """
        return self._boundaries

    @property
    def ordered_elements(self) -> list[BaseDiagramElement]:
        """
        Return diagram items in their order of definition.

        The sequence can include C4 elements, relationships, boundaries, and
        backend-owned statements that affect declaration-order rendering.
        """
        return self.__ordered_elements

    @property
    def relationships(self) -> list[Relationship]:
        """
        Returns all relationships defined in the diagram.
        """
        return self._relationships

    def get_element_by_alias(self, alias: str) -> Element | None:
        """Return the element with the given alias."""
        return self.__elements_by_alias.get(alias)

    def get_elements_by_label(self, label: str) -> list[Element]:
        """Return all elements that share the given label."""
        return self.__elements_by_label.get(label, [])

    def generate_alias(
        self,
        label: str,
        alias: str | None = None,
        fallback_prefix: str | None = None,
    ) -> str:
        """
        Generate a unique alias.

        Args:
            label: Source label used to derive the alias when `alias` is None.
            alias: Optional explicit alias. If provided, it must be unique.
            fallback_prefix: Prefix to use when the label cannot produce a
                valid alias.

        Returns:
            A unique alias string.

        Raises:
            ValueError: If alias already exists.
        """
        return self.__alias_generator.generate(label, alias, fallback_prefix)

    def add_referenced_element(self, element: Element) -> None:
        """Mark an element as referenced by another diagram object."""
        self.__referenced_elements.append(element.alias)

    def add_ordered_element(
        self, element: BaseDiagramElement
    ) -> BaseDiagramElement:
        """Add a diagram object to the declaration-order sequence."""
        if boundary := get_boundary():
            boundary.add_ordered_element(element)
        else:
            self.__ordered_elements.append(element)

        return element

    def add(self, element: TElement) -> TElement:
        """
        Add an element to the diagram or the currently active boundary.

        Args:
            element: The element to add.

        Returns:
            The added element.
        """
        self._check_alias(element)
        self._check_label(element)

        if boundary := get_boundary():
            boundary.add(element)
        else:
            self._elements.append(element)
            self.__ordered_elements.append(element)

        return element

    def add_boundary(self, boundary: TBoundary) -> TBoundary:
        """
        Add a top-level boundary to the diagram.

        Args:
            boundary: The boundary to add.

        Returns:
            The added boundary.
        """
        self._check_alias(boundary)
        self._check_label(boundary)

        if parent := get_boundary():
            parent.add_boundary(boundary)
        else:
            self._boundaries.append(boundary)
            self.__ordered_elements.append(boundary)

        return boundary

    def add_relationship(self, relationship: TRelationship) -> TRelationship:
        """
        Add a relationship between elements.

        Args:
            relationship: The relationship to add.

        Returns:
            The added relationship.
        """
        from_element, to_element = relationship.get_participants()  # type: ignore[var-annotated]
        self.add_referenced_element(from_element)
        self.add_referenced_element(to_element)

        if boundary := get_boundary():
            boundary.add_relationship(relationship)
        else:
            self._relationships.append(relationship)
            self.__ordered_elements.append(relationship)

        return relationship

    def as_plantuml(self, **kwargs: Any) -> str:
        """
        Render the diagram using the built-in PlantUML renderer.

        Args:
            **kwargs: Optional keyword arguments passed to the
                [PlantUML renderer][c4.renderers.PlantUMLRenderer].

        Returns:
            The rendered PlantUML code.
        """
        renderer = self._build_plantuml_renderer(**kwargs)

        return self.render(renderer)

    def as_mermaid(self, **kwargs: Any) -> str:
        """
        Render the diagram using the built-in Mermaid renderer.

        Args:
            **kwargs: Optional keyword arguments passed to the
                [Mermaid renderer][c4.renderers.MermaidRenderer].

        Returns:
            The rendered Mermaid code.
        """
        renderer = self._build_mermaid_renderer(**kwargs)

        return self.render(renderer)

    def as_d2(self, **kwargs: Any) -> str:
        """
        Render the diagram using the built-in D2 renderer.

        Args:
            **kwargs: Optional keyword arguments passed to the
                [D2 renderer][c4.renderers.D2Renderer].

        Returns:
            The rendered D2 code.
        """
        renderer = self._build_d2_renderer(**kwargs)

        return self.render(renderer)

    def is_element_referenced_by_alias(self, alias: str) -> bool:
        """
        Check whether an element identified by the given alias is referenced.

        An element is considered "referenced" if it participates
        in relationships or layout definitions, and therefore must be
        rendered using its alias.
        """
        return alias in self.__referenced_elements

    def render(self, renderer: BaseRenderer[Diagram] | None = None) -> str:
        """
        Render the diagram to a string using the given or default renderer.

        Args:
            renderer: Optional renderer to override the default.

        Returns:
            The rendered diagram output.

        Raises:
            ValueError: If no renderer is provided and no default
                renderer is set.
        """
        renderer = renderer or self._default_renderer
        if not renderer:
            raise ValueError("No renderer provided and no default_renderer set")

        return renderer.render(self)

    def save(
        self,
        path: str | Path,
        renderer: BaseRenderer[Diagram] | None = None,
    ) -> None:
        """
        Render and save the diagram to a file.

        Args:
            path: Target path to save the rendered output.
            renderer: Optional renderer to override the default.
        """
        path = Path(path)

        path.parent.mkdir(parents=True, exist_ok=True)

        content = self.render(renderer)

        path.write_text(content, encoding="utf-8")

    def save_as_plantuml(self, path: str | Path, **kwargs: Any) -> None:
        """
        Render and save the diagram using the PlantUML renderer.

        Args:
            path: Target file path.
            **kwargs: Optional kwargs passed to the
                [PlantUML renderer][c4.renderers.PlantUMLRenderer].
        """
        renderer = self._build_plantuml_renderer(**kwargs)

        return self.save(path, renderer=renderer)

    def save_as_mermaid(self, path: str | Path, **kwargs: Any) -> None:
        """
        Render and save the diagram using the Mermaid renderer.

        Args:
            path: Target file path.
            **kwargs: Optional kwargs passed to the
                [Mermaid renderer][c4.renderers.MermaidRenderer].
        """
        renderer = self._build_mermaid_renderer(**kwargs)

        return self.save(path, renderer=renderer)

    def save_as_d2(self, path: str | Path, **kwargs: Any) -> None:
        """
        Render and save the diagram using the D2 renderer.

        Args:
            path: Target file path.
            **kwargs: Optional kwargs passed to the
                [D2 renderer][c4.renderers.D2Renderer].
        """
        renderer = self._build_d2_renderer(**kwargs)

        return self.save(path, renderer=renderer)

    @property
    def render_options(self) -> RenderOptions | None:
        """Return rendering options for the diagram."""
        return self._render_options

    @render_options.setter
    def render_options(self, render_options: RenderOptions) -> None:
        """Set rendering options for the diagram."""
        self._render_options = render_options

    def set_render_options(
        self,
        *,
        plantuml: Maybe[PlantUMLRenderOptions] = MISSING,
        mermaid: Maybe[MermaidRenderOptions] = MISSING,
        d2: Maybe[D2RenderOptions] = MISSING,
    ) -> Self:
        """
        Patch renderer-specific options for this diagram.

        Omitted renderer keys are left unchanged. Passing `None` clears that
        renderer's diagram-level defaults.
        """
        if self._render_options is None:
            from c4.renderers import RenderOptions

            self._render_options = RenderOptions()

        if plantuml is not MISSING:
            self._render_options.plantuml = plantuml

        if mermaid is not MISSING:
            self._render_options.mermaid = mermaid

        if d2 is not MISSING:
            self._render_options.d2 = d2

        return self

    def _build_plantuml_renderer(self, **kwargs: Any) -> PlantUMLRenderer:
        """
        Create and configure a `PlantUMLRenderer` instance.

        If diagram render options are set and include PlantUML-specific
        settings, they are applied as default `render_options` unless
        explicitly provided in `kwargs`.

        Args:
            **kwargs: Additional keyword arguments passed directly to
                `PlantUMLRenderer`.

        Returns:
            A configured `PlantUMLRenderer` instance.
        """
        from c4.renderers import PlantUMLRenderer

        if self._render_options and self._render_options.plantuml:
            kwargs.setdefault("render_options", self._render_options.plantuml)

        return PlantUMLRenderer(**kwargs)

    def _build_mermaid_renderer(self, **kwargs: Any) -> MermaidRenderer:
        """
        Create and configure a `MermaidRenderer` instance.

        If diagram render options are set and include Mermaid-specific
        settings, they are applied as default `render_options` unless
        explicitly provided in `kwargs`.

        Args:
            **kwargs: Additional keyword arguments passed directly to
                `MermaidRenderer`.

        Returns:
            A configured `MermaidRenderer` instance.
        """
        from c4.renderers import MermaidRenderer

        if self._render_options and self._render_options.mermaid:
            kwargs.setdefault("render_options", self._render_options.mermaid)

        return MermaidRenderer(**kwargs)

    def _build_d2_renderer(self, **kwargs: Any) -> D2Renderer:
        """
        Create and configure a `D2Renderer` instance.

        If diagram render options are set and include D2-specific settings,
        they are applied as default `render_options` unless explicitly provided
        in `kwargs`.

        Args:
            **kwargs: Additional keyword arguments passed directly to
                `D2Renderer`.

        Returns:
            A configured `D2Renderer` instance.
        """
        from c4.renderers import D2Renderer

        if self._render_options and self._render_options.d2:
            kwargs.setdefault("render_options", self._render_options.d2)

        return D2Renderer(**kwargs)


TDiagram = TypeVar("TDiagram", bound=Diagram)

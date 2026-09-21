from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping
from types import TracebackType
from typing import TYPE_CHECKING, Any, TypeVar

from typing_extensions import Self

from c4.contrib.structurizr._metadata import (
    normalize_structurizr_tags,
)
from c4.contrib.structurizr._options import (
    AutoLayout,
)
from c4.contrib.structurizr._styles import (
    parse_style_metadata,
)
from c4.contrib.structurizr._views import (
    ViewMetadata,
    ViewSelectorInput,
    normalize_view_selectors,
)
from c4.contrib.structurizr.workspace.elements import (
    Container,
    DynamicStep,
    Relationship,
    SoftwareSystem,
    StructurizrElement,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.structurizr.workspace.workspace import Workspace


_ViewT = TypeVar("_ViewT", bound="_WorkspaceView")


class _WorkspaceView:
    """Base class for a declared Structurizr workspace view."""

    type = "view"

    def __init__(
        self,
        workspace: Workspace,
        title: str | None = None,
        scope: StructurizrElement | None = None,
        *,
        key: str | None = None,
        description: str | None = None,
        tags: tuple[str, ...] = (),
        properties: Mapping[str, Any] | None = None,
        include: tuple[str, ...] = (),
        exclude: tuple[str, ...] = (),
        auto_layout: AutoLayout | None = None,
        animation: tuple[tuple[str, ...], ...] = (),
        environment: str | None = None,
    ) -> None:
        """
        Initialize a workspace view.

        Args:
            workspace: Workspace that owns the view.
            title: Optional title shown on the view.
            scope: Optional model element that scopes the view.
            key: Optional stable Structurizr view key.
            description: Optional view description.
            tags: Tags applied to the view.
            properties: Custom view properties.
            include: Initial selectors to include.
            exclude: Initial selectors to exclude.
            auto_layout: Optional automatic-layout configuration.
            animation: Ordered animation selector groups.
            environment: Deployment environment for a deployment view.
        """
        if scope is not None and scope._model is not workspace.model:
            raise ValueError("View scope must belong to this workspace model")

        self._workspace = workspace
        self._title = title
        self.scope_target = scope
        self.key = key
        self.description = description
        self.tags = tags
        self.properties = dict(properties or {})
        self.include_selectors = include
        self.exclude_selectors = exclude
        self.auto_layout = auto_layout
        self.animation = animation
        self.environment = environment

    @property
    def title(self) -> str | None:
        return self._title

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,  # type: ignore[valid-type]
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def include(self, *values: Any) -> Self:
        """
        Add selectors to include in this view.

        Args:
            *values: Elements, selectors, or iterables of either to include.
        """
        self.include_selectors = (
            *self.include_selectors,
            *normalize_view_selectors(values),
        )
        return self

    def exclude(self, *values: Any) -> Self:
        """
        Add selectors to exclude from this view.

        Args:
            *values: Elements, selectors, or iterables of either to exclude.
        """
        self.exclude_selectors = (
            *self.exclude_selectors,
            *normalize_view_selectors(values),
        )
        return self


class SystemLandscapeView(_WorkspaceView):
    """A view showing the software systems in the enterprise landscape."""

    type = "systemLandscape"


class SystemContextView(_WorkspaceView):
    """A view showing a software system and its direct context."""

    type = "systemContext"


class ContainerView(_WorkspaceView):
    """A view showing the containers within a software system."""

    type = "container"


class ComponentView(_WorkspaceView):
    """A view showing the components within a container."""

    type = "component"


class DeploymentView(_WorkspaceView):
    """A view showing a deployment environment and its infrastructure."""

    type = "deployment"


class DynamicView(_WorkspaceView):
    """A view showing an ordered sequence of interactions."""

    type = "dynamic"

    def __init__(
        self,
        *args: Any,
        steps: Iterable[Relationship | DynamicStep] | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize a dynamic view.

        Args:
            *args: Positional arguments accepted by ``_WorkspaceView``.
            steps: Initial relationships or dynamic steps, in display order.
            **kwargs: Keyword arguments accepted by ``_WorkspaceView``.
        """
        super().__init__(*args, **kwargs)
        self._steps: list[DynamicStep] = []
        for item in steps or ():
            self._add(item)

    @property
    def steps(self) -> list[DynamicStep]:
        return self._steps

    def _add(self, value: Relationship | DynamicStep) -> None:
        self._steps.append(
            value
            if isinstance(value, DynamicStep)
            else DynamicStep(
                value.source,
                value.destination,
                value.description,
                value.technology,
                value,
            )
        )

    def step(
        self,
        source: StructurizrElement,
        destination: StructurizrElement,
        description: str | None = None,
        *,
        technology: str | None = None,
        relationship: Relationship | None = None,
        create_relationship: bool = False,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        url: str | None = None,
        style: Mapping[str, Any] | None = None,
    ) -> DynamicStep:
        """
        Append an interaction, optionally creating its model relationship.

        Args:
            source: Element that initiates the interaction.
            destination: Element that receives the interaction.
            description: Optional human-readable interaction label.
            technology: Optional technology used by the interaction.
            relationship: Existing relationship represented by this step.
            create_relationship: Whether to also register this interaction as a
                model relationship. Dynamic steps are view-local by default.
            tags: Tags applied to the dynamic step or created relationship.
            properties: Custom dynamic-step properties.
            url: Optional hyperlink associated with the step.
            style: Step-local style properties.
        """
        if (
            source._model is not self._workspace.model
            or destination._model is not self._workspace.model
        ):
            raise ValueError(
                "Dynamic step endpoints must belong to this workspace model"
            )

        if relationship and create_relationship:
            raise ValueError(
                "Pass either relationship or create_relationship=True, not both"
            )

        bound = relationship or (
            source.uses(
                destination,
                description,
                technology=technology,
                tags=tags,
                properties=properties,
                url=url,
                style=style,
            )
            if create_relationship
            else None
        )

        result = DynamicStep(
            source=source,
            destination=destination,
            description=description,
            technology=technology,
            relationship=bound,
            tags=normalize_structurizr_tags(tags),
            url=url,
            properties=properties,
            style=parse_style_metadata(style),
        )
        self._steps.append(result)

        return result


class Views:
    """The ordered collection of views declared for a workspace."""

    def __init__(self, workspace: Workspace) -> None:
        """
        Initialize the view collection for ``workspace``.

        Args:
            workspace: Workspace that owns the collection.
        """
        self._workspace = workspace
        self._items: list[_WorkspaceView] = []

    def __iter__(self) -> Iterator[_WorkspaceView]:
        return iter(self._items)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    def __len__(self) -> int:
        return len(self._items)

    def __getitem__(self, index: int) -> _WorkspaceView:
        return self._items[index]

    def _add(
        self,
        cls: type[_ViewT],
        scope: StructurizrElement | None = None,
        *,
        title: str | None = None,
        metadata: ViewMetadata,
        **kwargs: Any,
    ) -> _ViewT:
        if isinstance(scope, str):
            raise TypeError(
                "Structurizr view scopes must be model objects, not aliases"
            )

        result = cls(
            self._workspace,
            title=title,
            scope=scope,
            **metadata.as_kwargs(),
            **kwargs,
        )
        self._items.append(result)

        return result

    def SystemLandscapeView(
        self,
        *,
        title: str | None = None,
        key: str | None = None,
        description: str | None = None,
        include: ViewSelectorInput | None = None,
        exclude: ViewSelectorInput | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        auto_layout: AutoLayout | None = None,
        animation: ViewSelectorInput | None = None,
    ) -> SystemLandscapeView:
        """
        Add an enterprise-wide system landscape view.

        Args:
            title: Optional title shown on the view.
            key: Optional stable Structurizr view key.
            description: Optional view description.
            include: Initial selectors to include.
            exclude: Initial selectors to exclude.
            tags: Tags applied to the view.
            properties: Custom view properties.
            auto_layout: Optional automatic-layout configuration.
            animation: Ordered animation selector groups.
        """
        return self._add(
            SystemLandscapeView,
            title=title,
            metadata=ViewMetadata(
                key=key,
                description=description,
                include=include,
                exclude=exclude,
                tags=tags,
                properties=properties,
                auto_layout=auto_layout,
                animation=animation,
            ),
        )

    def SystemContextView(
        self,
        scope: SoftwareSystem,
        *,
        title: str | None = None,
        key: str | None = None,
        description: str | None = None,
        include: ViewSelectorInput | None = None,
        exclude: ViewSelectorInput | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        auto_layout: AutoLayout | None = None,
        animation: ViewSelectorInput | None = None,
    ) -> SystemContextView:
        """
        Add a context view for a software system.

        Args:
            scope: Software system shown as the view's focus.
            title: Optional title shown on the view.
            key: Optional stable Structurizr view key.
            description: Optional view description.
            include: Initial selectors to include.
            exclude: Initial selectors to exclude.
            tags: Tags applied to the view.
            properties: Custom view properties.
            auto_layout: Optional automatic-layout configuration.
            animation: Ordered animation selector groups.
        """
        return self._add(
            SystemContextView,
            scope,
            title=title,
            metadata=ViewMetadata(
                key=key,
                description=description,
                include=include,
                exclude=exclude,
                tags=tags,
                properties=properties,
                auto_layout=auto_layout,
                animation=animation,
            ),
        )

    def ContainerView(
        self,
        scope: SoftwareSystem,
        *,
        title: str | None = None,
        key: str | None = None,
        description: str | None = None,
        include: ViewSelectorInput | None = None,
        exclude: ViewSelectorInput | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        auto_layout: AutoLayout | None = None,
        animation: ViewSelectorInput | None = None,
    ) -> ContainerView:
        """
        Add a container view for a software system.

        Args:
            scope: Software system shown as the view's focus.
            title: Optional title shown on the view.
            key: Optional stable Structurizr view key.
            description: Optional view description.
            include: Initial selectors to include.
            exclude: Initial selectors to exclude.
            tags: Tags applied to the view.
            properties: Custom view properties.
            auto_layout: Optional automatic-layout configuration.
            animation: Ordered animation selector groups.
        """
        return self._add(
            ContainerView,
            scope,
            title=title,
            metadata=ViewMetadata(
                key=key,
                description=description,
                include=include,
                exclude=exclude,
                tags=tags,
                properties=properties,
                auto_layout=auto_layout,
                animation=animation,
            ),
        )

    def ComponentView(
        self,
        scope: Container,
        *,
        title: str | None = None,
        key: str | None = None,
        description: str | None = None,
        include: ViewSelectorInput | None = None,
        exclude: ViewSelectorInput | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        auto_layout: AutoLayout | None = None,
        animation: ViewSelectorInput | None = None,
    ) -> ComponentView:
        """
        Add a component view for a container.

        Args:
            scope: Container shown as the view's focus.
            title: Optional title shown on the view.
            key: Optional stable Structurizr view key.
            description: Optional view description.
            include: Initial selectors to include.
            exclude: Initial selectors to exclude.
            tags: Tags applied to the view.
            properties: Custom view properties.
            auto_layout: Optional automatic-layout configuration.
            animation: Ordered animation selector groups.
        """
        return self._add(
            ComponentView,
            scope,
            title=title,
            metadata=ViewMetadata(
                key=key,
                description=description,
                include=include,
                exclude=exclude,
                tags=tags,
                properties=properties,
                auto_layout=auto_layout,
                animation=animation,
            ),
        )

    def DynamicView(
        self,
        scope: StructurizrElement | None = None,
        *,
        title: str | None = None,
        key: str | None = None,
        description: str | None = None,
        include: ViewSelectorInput | None = None,
        exclude: ViewSelectorInput | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        auto_layout: AutoLayout | None = None,
        animation: ViewSelectorInput | None = None,
        steps: Iterable[Relationship | DynamicStep] | None = None,
    ) -> DynamicView:
        """
        Add a dynamic view, optionally scoped to an element.

        Args:
            scope: Optional model element shown as the view's focus.
            title: Optional title shown on the view.
            key: Optional stable Structurizr view key.
            description: Optional view description.
            include: Initial selectors to include.
            exclude: Initial selectors to exclude.
            tags: Tags applied to the view.
            properties: Custom view properties.
            auto_layout: Optional automatic-layout configuration.
            animation: Ordered animation selector groups.
            steps: Initial relationships or dynamic steps, in display order.
        """
        return self._add(
            DynamicView,
            scope,
            title=title,
            metadata=ViewMetadata(
                key=key,
                description=description,
                include=include,
                exclude=exclude,
                tags=tags,
                properties=properties,
                auto_layout=auto_layout,
                animation=animation,
            ),
            steps=steps,
        )

    def DeploymentView(
        self,
        scope: StructurizrElement | None = None,
        *,
        environment: str,
        title: str | None = None,
        key: str | None = None,
        description: str | None = None,
        include: ViewSelectorInput | None = None,
        exclude: ViewSelectorInput | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        properties: Mapping[str, Any] | None = None,
        auto_layout: AutoLayout | None = None,
        animation: ViewSelectorInput | None = None,
    ) -> DeploymentView:
        """
        Add a deployment view for an environment.

        Args:
            scope: Optional model element shown as the view's focus.
            environment: Deployment environment name to show.
            title: Optional title shown on the view.
            key: Optional stable Structurizr view key.
            description: Optional view description.
            include: Initial selectors to include.
            exclude: Initial selectors to exclude.
            tags: Tags applied to the view.
            properties: Custom view properties.
            auto_layout: Optional automatic-layout configuration.
            animation: Ordered animation selector groups.
        """
        return self._add(
            DeploymentView,
            scope,
            title=title,
            metadata=ViewMetadata(
                key=key,
                description=description,
                include=include,
                exclude=exclude,
                tags=tags,
                properties=properties,
                auto_layout=auto_layout,
                animation=animation,
            ),
            environment=environment,
        )

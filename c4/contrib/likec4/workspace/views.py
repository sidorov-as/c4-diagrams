from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from typing_extensions import Self

from c4.contrib.likec4._identifiers import check_identifier
from c4.contrib.likec4._metadata import (
    Link,
    normalize_likec4_tags,
    normalize_links,
)
from c4.contrib.likec4._styles import parse_element_style
from c4.contrib.likec4._views import (
    AutoLayoutRule,
    ExcludeRule,
    IncludeRule,
    StyleRule,
    validate_auto_layout,
)
from c4.contrib.likec4.workspace.deployment import (
    DeploymentInstance,
    DeploymentNode,
)
from c4.contrib.likec4.workspace.elements import Element

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.likec4.workspace.project import Project

DynamicVariant = Literal["diagram", "sequence"]
DYNAMIC_VARIANTS = ("diagram", "sequence")


class _View:
    """Properties shared by every view type."""

    def __init__(
        self,
        key: str,
        title: str | None = None,
        *,
        description: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        links: list[Any] | tuple[Any, ...] | None = None,
    ) -> None:
        self.key = check_identifier(key, "View key")
        self.title = title
        self.description = description
        self.tags = normalize_likec4_tags(tags)
        self.links: tuple[Link, ...] = normalize_links(links)
        self.rules: list[Any] = []

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.key!r})"

    def auto_layout(
        self,
        direction: str = "TopBottom",
        rank_sep: int | None = None,
        node_sep: int | None = None,
    ) -> Self:
        """
        Add an ``autoLayout`` rule.

        Args:
            direction: ``TopBottom``, ``LeftRight``, ``BottomTop`` or
                ``RightLeft``.
            rank_sep: Optional spacing between ranks.
            node_sep: Optional spacing between nodes; needs ``rank_sep``.
        """
        self.rules.append(validate_auto_layout(direction, rank_sep, node_sep))
        return self

    @property
    def layout(self) -> AutoLayoutRule | None:
        """Return the last ``autoLayout`` rule, if any."""
        layouts = [r for r in self.rules if isinstance(r, AutoLayoutRule)]
        return layouts[-1] if layouts else None


def _items(items: tuple[Any, ...], rule: str) -> tuple[Any, ...]:
    if not items:
        raise ValueError(f"{rule} needs at least one item")
    return items


class _PredicateView(_View):
    """A view whose content comes from ordered include/exclude/style rules."""

    def include(self, *items: Any, navigate_to: str | None = None) -> Self:
        """
        Add an ``include`` rule.

        Args:
            *items: Elements, ``Wildcard``, ``Children``, ``Descendants``,
                ``Between``, ``Incoming``, ``Outgoing``, ``InOut``,
                ``Where`` or ``RawPredicate`` objects.
            navigate_to: Key of the view to open on click.
        """
        if navigate_to is not None:
            check_identifier(navigate_to, "navigate_to view key")

        self.rules.append(IncludeRule(_items(items, "include"), navigate_to))
        return self

    def exclude(self, *items: Any) -> Self:
        """
        Add an ``exclude`` rule.

        Args:
            *items: Same kinds of item as ``include``.
        """
        self.rules.append(ExcludeRule(_items(items, "exclude")))
        return self

    def style(self, *targets: Any, **properties: Any) -> Self:
        """
        Add a ``style`` rule.

        Args:
            *targets: Items to style.
            **properties: Element style properties.
        """
        parsed = parse_element_style(**properties)
        if not parsed:
            raise ValueError("A style rule needs at least one property")

        self.rules.append(
            StyleRule(_items(targets, "style"), tuple(parsed.items()))
        )
        return self


class ElementView(_PredicateView):
    """
    A view over model elements.

    Attributes:
        key: Unique view key.
        title: Optional title.
        description: Optional Markdown description.
        scope: Element the view is ``of``, or ``None``.
        tags: View tags, without ``#``.
        links: Hyperlinks.
        rules: Include, exclude, style and autoLayout rules in the order
            they were added.
    """

    def __init__(
        self,
        key: str,
        title: str | None = None,
        *,
        of: Element | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(key, title, **kwargs)
        if of is not None and not isinstance(of, Element):
            raise TypeError(
                "The 'of' scope of an element view must be an Element"
            )

        self.scope = of


class DeploymentView(_PredicateView):
    """
    A view over deployment nodes and instances.

    ``include`` takes no ``navigate_to``: ``with`` overrides are not emitted
    in deployment views.
    """

    def include(self, *items: Any) -> Self:  # type: ignore[override]
        """
        Add an ``include`` rule.

        Args:
            *items: Deployment nodes or instances, ``Wildcard``,
                ``Children``, ``Descendants`` or ``RawPredicate`` objects.
        """
        return super().include(*items)


@dataclass(frozen=True)
class DynamicStep:
    """
    One interaction of a dynamic view.

    Attributes:
        source: Element that appears on the left of the arrow.
        target: Element that appears on the right of the arrow.
        title: Step label.
        description: Longer Markdown description.
        technology: Technology of the interaction.
        notes: Markdown notes.
        navigate_to: Key of a dynamic view to open on click.
        color: Theme or custom color name.
        backward: ``True`` for ``source <- target``.
    """

    source: Element
    target: Element
    title: str | None = None
    description: str | None = None
    technology: str | None = None
    notes: str | None = None
    navigate_to: str | None = None
    color: str | None = None
    backward: bool = False

    def __post_init__(self) -> None:
        for end in (self.source, self.target):
            if not isinstance(end, Element):
                raise TypeError("A dynamic step connects model Elements")

        if self.navigate_to is not None:
            check_identifier(self.navigate_to, "navigate_to view key")

        if self.color is not None:
            check_identifier(self.color, "Step color")


class DynamicView(_View):
    """
    A dynamic view: an ordered, flat list of steps.

    The steps live in a list of immutable nodes so that block nodes can be
    added later without changing the flat-step API.

    Attributes:
        key: Unique view key.
        title: Optional title.
        description: Optional Markdown description.
        variant: ``diagram`` (default) or ``sequence``.
    """

    def __init__(
        self,
        key: str,
        title: str | None = None,
        *,
        variant: DynamicVariant = "diagram",
        **kwargs: Any,
    ) -> None:
        super().__init__(key, title, **kwargs)
        if variant not in DYNAMIC_VARIANTS:
            raise ValueError(
                f"Invalid dynamic view variant {variant!r}; expected one of "
                f"{', '.join(DYNAMIC_VARIANTS)}."
            )

        self.variant: DynamicVariant = variant
        self._nodes: list[DynamicStep] = []

    @property
    def steps(self) -> tuple[DynamicStep, ...]:
        """Return the steps in order."""
        return tuple(self._nodes)

    def step(
        self,
        source: Element,
        target: Element,
        title: str | None = None,
        **properties: Any,
    ) -> Self:
        """
        Add a ``source -> target`` step.

        Args:
            source: Sending element.
            target: Receiving element.
            title: Step label.
            **properties: ``description``, ``technology``, ``notes``,
                ``navigate_to`` and ``color``.
        """
        self._nodes.append(DynamicStep(source, target, title, **properties))
        return self

    def back(
        self,
        receiver: Element,
        sender: Element,
        title: str | None = None,
        **properties: Any,
    ) -> Self:
        """
        Add a ``receiver <- sender`` step.

        Args:
            receiver: Element on the left of the arrow; it receives.
            sender: Element on the right of the arrow; it sends.
            title: Step label.
            **properties: Same as ``step``.
        """
        self._nodes.append(
            DynamicStep(receiver, sender, title, backward=True, **properties)
        )
        return self


class Views:
    """
    The views of a project in declaration order.

    Attributes:
        all: Every view in creation order, whatever its type.
    """

    def __init__(self, project: Project) -> None:
        """
        Initialize an empty view collection.

        Args:
            project: Project that owns the views.
        """
        self._project = project
        self.all: list[ElementView | DeploymentView | DynamicView] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    def element_view(
        self, key: str, title: str | None = None, **kwargs: Any
    ) -> ElementView:
        """
        Create an element view.

        Args:
            key: View key.
            title: Optional title.
            **kwargs: ``of``, ``description``, ``tags`` and ``links``.
        """
        view = ElementView(key, title, **kwargs)
        self.all.append(view)
        return view

    def deployment_view(
        self, key: str, title: str | None = None, **kwargs: Any
    ) -> DeploymentView:
        """
        Create a deployment view.

        Args:
            key: View key.
            title: Optional title.
            **kwargs: ``description``, ``tags`` and ``links``.
        """
        view = DeploymentView(key, title, **kwargs)
        self.all.append(view)
        return view

    def dynamic_view(
        self, key: str, title: str | None = None, **kwargs: Any
    ) -> DynamicView:
        """
        Create a dynamic view.

        Args:
            key: View key.
            title: Optional title.
            **kwargs: ``variant``, ``description``, ``tags`` and ``links``.
        """
        view = DynamicView(key, title, **kwargs)
        self.all.append(view)
        return view


__all__ = (
    "DeploymentInstance",
    "DeploymentNode",
    "DeploymentView",
    "DynamicStep",
    "DynamicView",
    "ElementView",
    "Views",
)

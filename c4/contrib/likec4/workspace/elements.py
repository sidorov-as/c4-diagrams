from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import TracebackType
from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from c4.contrib.likec4._identifiers import check_identifier
from c4.contrib.likec4._metadata import (
    Link,
    MetadataValue,
    normalize_likec4_tags,
    normalize_links,
    normalize_metadata,
    validate_summary,
)
from c4.contrib.likec4._styles import (
    StyleValue,
    parse_element_style,
    parse_relationship_style,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.likec4.workspace.model import Model


@dataclass
class Relationship:
    """
    A relationship between two model elements.

    ``a >> b`` creates a relationship with no ``title``; ``a >> b | "title"``
    sets it while it is ``None`` and raises ``ValueError`` once a title exists.

    Attributes:
        source: Element that initiates the relationship.
        target: Element that receives the relationship.
        title: Relationship label.
        description: Longer Markdown description.
        technology: Technology used by the relationship.
        kind: Declared relationship kind, if any.
        bidirectional: Whether the relationship is declared with ``<->``.
        tags: Tags applied to the relationship, without ``#``.
        metadata: Custom metadata.
        links: Hyperlinks.
        style: Relationship-local style properties.
        navigate_to: Key of the dynamic view to open on click.
    """

    source: Element
    target: Element
    title: str | None = None
    description: str | None = None
    technology: str | None = None
    kind: str | None = None
    bidirectional: bool = False
    tags: tuple[str, ...] = ()
    metadata: dict[str, MetadataValue] = field(default_factory=dict)
    links: tuple[Link, ...] = ()
    style: dict[str, StyleValue] = field(default_factory=dict)
    navigate_to: str | None = None

    def __or__(self, title: str) -> Relationship:
        """
        Set the title of an unlabeled relationship: ``a >> b | "title"``.

        Raises:
            ValueError: If the relationship already has a title.
        """
        if not isinstance(title, str):
            return NotImplemented

        _set_title(self, title)
        return self

    @classmethod
    def create(
        cls,
        source: Element,
        target: Element,
        title: str | None = None,
        *,
        description: str | None = None,
        technology: str | None = None,
        kind: str | None = None,
        bidirectional: bool = False,
        tags: list[str] | tuple[str, ...] | None = None,
        metadata: Mapping[str, Any] | None = None,
        links: list[Any] | tuple[Any, ...] | None = None,
        navigate_to: str | None = None,
        **style: Any,
    ) -> Relationship:
        """Build a relationship, validating the supplied properties."""
        if kind is not None:
            check_identifier(kind, "Relationship kind")
        if navigate_to is not None:
            check_identifier(navigate_to, "navigate_to view key")
        return cls(
            source=source,
            target=target,
            title=title,
            description=description,
            technology=technology,
            kind=kind,
            bidirectional=bidirectional,
            tags=normalize_likec4_tags(tags),
            metadata=normalize_metadata(metadata),
            links=normalize_links(links),
            style=parse_relationship_style(**style),
            navigate_to=navigate_to,
        )


def _set_title(relationship: Any, title: str) -> None:
    """Set the title of an unlabeled relationship, or fail."""
    if relationship.title is not None:
        raise ValueError(
            f"Relationship already has the title {relationship.title!r}"
        )

    relationship.title = title


@dataclass(frozen=True)
class _RelExpression:
    """
    An immutable relationship expression produced by ``Rel(...)``.

    Binding it to an element with ``>>`` or ``<<`` returns a new
    ``_BoundRel`` and leaves the expression unchanged, so one ``Rel`` can be
    reused for any number of relationships.
    """

    title: str | None = None
    description: str | None = None
    technology: str | None = None
    kind: str | None = None
    bidirectional: bool = False
    tags: tuple[str, ...] | list[str] | None = None
    metadata: Mapping[str, Any] | None = None
    links: tuple[Any, ...] | list[Any] | None = None
    navigate_to: str | None = None
    style: Mapping[str, Any] = field(default_factory=dict)

    def __rrshift__(self, other: Any) -> _BoundRel:
        """Bind left-hand sources: ``a >> Rel()`` or ``[a, b] >> Rel()``."""
        return _BoundRel.bind(self, other, is_source=True)

    def __rlshift__(self, other: Any) -> _BoundRel:
        """Bind left-hand targets: ``c << Rel()`` or ``[a, b] << Rel()``."""
        return _BoundRel.bind(self, other, is_source=False)

    def _arguments(self) -> dict[str, Any]:
        """Return the keyword arguments of ``relate``."""
        arguments: dict[str, Any] = {
            "description": self.description,
            "technology": self.technology,
            "kind": self.kind,
            "bidirectional": self.bidirectional,
            "tags": self.tags,
            "metadata": self.metadata,
            "links": self.links,
            **self.style,
        }

        if self.navigate_to is not None:
            # Deployment relationships have no ``navigate_to``.
            arguments["navigate_to"] = self.navigate_to

        return arguments


@dataclass(frozen=True)
class _BoundRel:
    """
    A relationship expression with one side already chosen.

    Attributes:
        expression: The expression that supplies the relationship properties.
        fixed: Elements already on one side of the relationship.
        fixed_is_list: Whether that side was written as a list.
        fixed_is_source: Whether the fixed side is the source.
    """

    expression: _RelExpression
    fixed: tuple[Any, ...]
    fixed_is_list: bool
    fixed_is_source: bool

    @classmethod
    def bind(
        cls, expression: _RelExpression, other: Any, *, is_source: bool
    ) -> _BoundRel:
        """Bind ``expression`` to one element or a list of elements."""
        return cls(
            expression=expression,
            fixed=tuple(other) if isinstance(other, list) else (other,),
            fixed_is_list=isinstance(other, list),
            fixed_is_source=is_source,
        )

    def __rshift__(self, other: Any) -> Any:
        """Complete ``source >> Rel() >> target``."""
        if not self.fixed_is_source:
            return NotImplemented

        return self._complete(other)

    def __lshift__(self, other: Any) -> Any:
        """Complete ``target << Rel() << source``."""
        if self.fixed_is_source:
            return NotImplemented

        return self._complete(other)

    def _complete(self, other: Any) -> Any:
        """Create one relationship per element on the open side."""
        other_is_list = isinstance(other, list)
        if self.fixed_is_list and other_is_list:
            raise ValueError(
                "Either source or destination must be a single element"
            )

        others = tuple(other) if other_is_list else (other,)
        arguments = self.expression._arguments()

        result = [
            (fixed if self.fixed_is_source else item)._relate(
                item if self.fixed_is_source else fixed,
                self.expression.title,
                **arguments,
            )
            for fixed in self.fixed
            for item in others
        ]

        return result if self.fixed_is_list or other_is_list else result[0]


def Rel(
    title: str | None = None,
    *,
    description: str | None = None,
    technology: str | None = None,
    kind: str | None = None,
    bidirectional: bool = False,
    tags: list[str] | tuple[str, ...] | None = None,
    metadata: Mapping[str, Any] | None = None,
    links: list[Any] | tuple[Any, ...] | None = None,
    navigate_to: str | None = None,
    **style: Any,
) -> _RelExpression:
    """
    Start a relationship expression: ``a >> Rel("calls") >> b``.

    Only ``title`` may be positional; pass the other options by name. The
    expression is immutable and can be reused.

    Args:
        title: Relationship label.
        description: Longer Markdown description.
        technology: Technology used by the relationship.
        kind: Declared relationship kind.
        bidirectional: Declare the relationship with ``<->``.
        tags: Tags applied to the relationship, without ``#``.
        metadata: Custom metadata.
        links: Hyperlinks.
        navigate_to: Key of the dynamic view to open on click.
        **style: Relationship-local style properties.
    """
    return _RelExpression(
        title=title,
        description=description,
        technology=technology,
        kind=kind,
        bidirectional=bidirectional,
        tags=tags,
        metadata=metadata,
        links=links,
        navigate_to=navigate_to,
        style=style,
    )


class _RelationOperators:
    """
    Relationship authoring shared by elements and deployment nodes/instances.

    Subclasses implement ``_relate(target, title, **kwargs)``.
    """

    def _relate(self, target: Any, title: str | None, **kwargs: Any) -> Any:
        raise NotImplementedError  # pragma: no cover

    def uses(self, other: Any, title: str | None = None, **kwargs: Any) -> Any:
        """
        Declare that this element uses ``other``.

        Args:
            other: Receiving element.
            title: Relationship label.
            **kwargs: Any other ``Rel`` option.
        """
        return self._relate(other, title, **kwargs)

    def used_by(
        self, other: Any, title: str | None = None, **kwargs: Any
    ) -> Any:
        """
        Declare that ``other`` uses this element.

        Args:
            other: Initiating element.
            title: Relationship label.
            **kwargs: Any other ``Rel`` option.
        """
        return other._relate(self, title, **kwargs)

    def __rshift__(self, other: Any) -> Any:
        """Build a relationship with ``>>``: ``a >> b``, ``a >> Rel() >> b``."""
        if isinstance(other, str):
            return _BoundRel.bind(_RelExpression(other), self, is_source=True)
        if isinstance(other, _RelExpression):
            return _BoundRel.bind(other, self, is_source=True)
        if isinstance(other, _RelationOperators):
            return self._relate(other, None)
        if isinstance(other, list):
            return _BoundRel.bind(
                _RelExpression(), self, is_source=True
            )._complete(other)

        return NotImplemented

    def __lshift__(self, other: Any) -> Any:
        """Build a relationship with ``<<``: ``b << a``, ``b << Rel() << a``."""
        if isinstance(other, str):
            return _BoundRel.bind(_RelExpression(other), self, is_source=False)
        if isinstance(other, _RelExpression):
            return _BoundRel.bind(other, self, is_source=False)
        if isinstance(other, _RelationOperators):
            return other._relate(self, None)
        if isinstance(other, list):
            return _BoundRel.bind(
                _RelExpression(), self, is_source=False
            )._complete(other)

        return NotImplemented

    def __rrshift__(self, other: Any) -> Any:
        """Support ``[a, b] >> c``."""
        if isinstance(other, list):
            return _BoundRel.bind(
                _RelExpression(), self, is_source=False
            )._complete(other)

        return NotImplemented

    def __rlshift__(self, other: Any) -> Any:
        """Support ``[b, c] << a``."""
        if isinstance(other, list):
            return _BoundRel.bind(
                _RelExpression(), self, is_source=True
            )._complete(other)

        return NotImplemented


class Element(_RelationOperators):
    """
    A model element of a declared kind; elements nest without limit.

    Attributes:
        kind: Declared element kind.
        title: Display title.
        alias: Explicit identifier; derived from the title when omitted.
        parent: Parent element, or ``None`` for a root element.
        children: Child elements in declaration order.
        summary: Short summary, at most 150 characters.
        description: Markdown description.
        technology: Implementation technology.
        tags: Tags applied to the element, without ``#``.
        style: Element-local style properties.
        icon: Icon reference such as ``tech:go``.
        metadata: Custom metadata.
        links: Hyperlinks.
    """

    def __init__(
        self,
        model: Model,
        kind: str,
        title: str | None = None,
        *,
        alias: str | None = None,
        parent: Element | None = None,
        summary: str | None = None,
        description: str | None = None,
        technology: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
        icon: str | None = None,
        metadata: Mapping[str, Any] | None = None,
        links: list[Any] | tuple[Any, ...] | None = None,
        **style: Any,
    ) -> None:
        """
        Initialize an element; prefer ``Model.element`` or ``Element.element``.

        Args:
            model: Model that owns the element.
            kind: Declared element kind.
            title: Display title.
            alias: Explicit identifier.
            parent: Parent element.
            summary: Short summary, at most 150 characters.
            description: Markdown description.
            technology: Implementation technology.
            tags: Tags applied to the element, without ``#``.
            icon: Icon reference such as ``tech:go``.
            metadata: Custom metadata.
            links: Hyperlinks.
            **style: Element-local style properties.
        """
        if title is None and alias is None:
            raise ValueError("An element needs a title or an alias.")

        if alias is not None:
            check_identifier(alias, "Element alias")

        if parent is not None and parent._model is not model:
            raise ValueError("The parent element belongs to another model.")

        self._model: Model = model
        self.kind = check_identifier(kind, "Element kind")
        self.title = title
        self.alias = alias
        self.parent = parent
        self.children: list[Element] = []
        self.summary = validate_summary(summary)
        self.description = description
        self.technology = technology
        self.tags = normalize_likec4_tags(tags)
        self.style: dict[str, StyleValue] = parse_element_style(**style)
        self.icon = icon
        self.metadata = normalize_metadata(metadata)
        self.links = normalize_links(links)

    def __repr__(self) -> str:
        return f"Element({self.kind!r}, {self.title or self.alias!r})"

    def __enter__(self) -> Self:
        self._model._owner_stack.append(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._model._pop_owner(self)

    @property
    def name(self) -> str:
        """Return the title, or the alias when there is no title."""
        return self.title or self.alias or ""

    def element(
        self, kind: str, title: str | None = None, **kwargs: Any
    ) -> Element:
        """
        Create a child element.

        Args:
            kind: Declared element kind.
            title: Display title.
            **kwargs: Any other ``Model.element`` argument.
        """
        return self._model.element(kind, title, parent=self, **kwargs)

    def person(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create a child element of the ``person`` kind.

        Equivalent to ``element("person", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``Model.element`` argument.

        Raises:
            ValueError: If the ``person`` kind is not declared.
        """
        return self._model._c4_element("person", title, parent=self, **kwargs)

    def system(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create a child element of the ``system`` kind.

        Equivalent to ``element("system", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``Model.element`` argument.

        Raises:
            ValueError: If the ``system`` kind is not declared.
        """
        return self._model._c4_element("system", title, parent=self, **kwargs)

    def container(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create a child element of the ``container`` kind.

        Equivalent to ``element("container", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``Model.element`` argument.

        Raises:
            ValueError: If the ``container`` kind is not declared.
        """
        return self._model._c4_element(
            "container", title, parent=self, **kwargs
        )

    def component(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create a child element of the ``component`` kind.

        Equivalent to ``element("component", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``Model.element`` argument.

        Raises:
            ValueError: If the ``component`` kind is not declared.
        """
        return self._model._c4_element(
            "component", title, parent=self, **kwargs
        )

    def database(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create a child element of the ``database`` kind.

        Equivalent to ``element("database", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``Model.element`` argument.

        Raises:
            ValueError: If the ``database`` kind is not declared.
        """
        return self._model._c4_element("database", title, parent=self, **kwargs)

    def external(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create a child element of the ``external`` kind.

        Equivalent to ``element("external", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``Model.element`` argument.

        Raises:
            ValueError: If the ``external`` kind is not declared.
        """
        return self._model._c4_element("external", title, parent=self, **kwargs)

    def _relate(
        self, target: Element, title: str | None, **kwargs: Any
    ) -> Relationship:
        return self._model.relate(self, target, title, **kwargs)

    def set_style(self, **properties: Any) -> Self:
        """
        Merge element-local style properties.

        Args:
            **properties: Element style properties.
        """
        self.style = {**self.style, **parse_element_style(**properties)}
        return self

    def ancestors(self) -> list[Element]:
        """Return the parents from the nearest to the root."""
        result: list[Element] = []
        node = self.parent

        while node is not None:
            result.append(node)
            node = node.parent

        return result

    def descendants(self) -> list[Element]:
        """Return all nested elements in depth-first declaration order."""
        result: list[Element] = []

        for child in self.children:
            result.append(child)
            result.extend(child.descendants())

        return result

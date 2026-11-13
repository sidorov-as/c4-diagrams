from __future__ import annotations

from typing import TYPE_CHECKING, Any

from typing_extensions import Self

from c4.contrib.likec4.workspace.elements import Element, Relationship

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.likec4.workspace.project import Project


class Model:
    """
    The element hierarchy and relationships of a project.

    Attributes:
        elements: Every element in creation order.
        relationships: Every relationship in creation order.
    """

    def __init__(self, project: Project) -> None:
        """
        Initialize an empty model.

        Args:
            project: Project that owns the model.
        """
        self._project = project
        self._owner_stack: list[Element] = []
        self.elements: list[Element] = []
        self.relationships: list[Relationship] = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        return None

    @property
    def roots(self) -> list[Element]:
        """Return the top-level elements in declaration order."""
        return [element for element in self.elements if element.parent is None]

    def _pop_owner(self, element: Element) -> None:
        if not self._owner_stack or self._owner_stack[-1] is not element:
            raise RuntimeError("LikeC4 model ownership context mismatch")
        self._owner_stack.pop()

    def element(
        self,
        kind: str,
        title: str | None = None,
        *,
        parent: Element | None = None,
        **kwargs: Any,
    ) -> Element:
        """
        Create an element of a declared kind.

        Without ``parent`` the element nests into the innermost element whose
        ``with`` block is active, or becomes a root element.

        Args:
            kind: Declared element kind.
            title: Display title.
            parent: Explicit parent element.
            **kwargs: Any other ``Element`` argument.
        """
        if parent is None and self._owner_stack:
            parent = self._owner_stack[-1]

        element = Element(self, kind, title, parent=parent, **kwargs)
        if parent is not None:
            parent.children.append(element)

        self.elements.append(element)
        return element

    def _c4_element(
        self, kind: str, title: str | None, **kwargs: Any
    ) -> Element:
        if kind not in self._project.specification.element_kinds:
            raise ValueError(
                f"Element kind {kind!r} is not declared in the specification. "
                f"Declare it with specification.element({kind!r}) or apply a "
                "preset with specification.use(C4)."
            )

        return self.element(kind, title, **kwargs)

    def person(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create an element of the ``person`` kind.

        Equivalent to ``element("person", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``element`` argument.

        Raises:
            ValueError: If the ``person`` kind is not declared.
        """
        return self._c4_element("person", title, **kwargs)

    def system(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create an element of the ``system`` kind.

        Equivalent to ``element("system", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``element`` argument.

        Raises:
            ValueError: If the ``system`` kind is not declared.
        """
        return self._c4_element("system", title, **kwargs)

    def container(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create an element of the ``container`` kind.

        Equivalent to ``element("container", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``element`` argument.

        Raises:
            ValueError: If the ``container`` kind is not declared.
        """
        return self._c4_element("container", title, **kwargs)

    def component(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create an element of the ``component`` kind.

        Equivalent to ``element("component", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``element`` argument.

        Raises:
            ValueError: If the ``component`` kind is not declared.
        """
        return self._c4_element("component", title, **kwargs)

    def database(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create an element of the ``database`` kind.

        Equivalent to ``element("database", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``element`` argument.

        Raises:
            ValueError: If the ``database`` kind is not declared.
        """
        return self._c4_element("database", title, **kwargs)

    def external(self, title: str | None = None, **kwargs: Any) -> Element:
        """
        Create an element of the ``external`` kind.

        Equivalent to ``element("external", ...)``; the kind must be declared.

        Args:
            title: Display title.
            **kwargs: Any other ``element`` argument.

        Raises:
            ValueError: If the ``external`` kind is not declared.
        """
        return self._c4_element("external", title, **kwargs)

    def relate(
        self,
        source: Element,
        target: Element,
        title: str | None = None,
        **kwargs: Any,
    ) -> Relationship:
        """
        Create a relationship between two elements of this model.

        Args:
            source: Initiating element.
            target: Receiving element.
            title: Relationship label.
            **kwargs: Any other ``Relationship.create`` argument.
        """
        for end in (source, target):
            if not isinstance(end, Element) or end._model is not self:
                raise ValueError(
                    f"Relationship endpoint {end!r} does not belong to this "
                    "model."
                )

        relationship = Relationship.create(source, target, title, **kwargs)
        self.relationships.append(relationship)
        return relationship

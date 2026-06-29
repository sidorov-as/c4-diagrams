from __future__ import annotations

import abc
import copy
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from itertools import repeat
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    NoReturn,
    TypeVar,
    cast,
    overload,
)

from typing_extensions import ParamSpec, Self, TypedDict, override

from c4.diagrams.core.enums import DiagramType, RelationshipType
from c4.diagrams.core.utils import current_diagram, get_boundary, set_boundary
from c4.enums import RendererEnum
from c4.utils import MISSING, REQUIRED, Maybe, Required

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.d2.extensions import (
        BoundaryExtensions as D2BoundaryExtensions,
    )
    from c4.contrib.d2.extensions import (
        ElementExtensions as D2ElementExtensions,
    )
    from c4.contrib.d2.extensions import (
        RelationshipExtensions as D2RelationshipExtensions,
    )
    from c4.contrib.mermaid.extensions import (
        BoundaryExtensions as MermaidBoundaryExtensions,
    )
    from c4.contrib.plantuml.extensions import (
        BoundaryExtensions as PlantUMLBoundaryExtensions,
    )
    from c4.contrib.plantuml.extensions import (
        ElementExtensions as PlantUMLElementExtensions,
    )
    from c4.contrib.plantuml.extensions import (
        RelationshipExtensions as PlantUMLRelationshipExtensions,
    )
    from c4.diagrams.core.diagram import Diagram

P = ParamSpec("P")
TDiagramElement = TypeVar("TDiagramElement", bound="BaseDiagramElement")
PropertyRow = Sequence[str]


class ElementExtensions(TypedDict, total=False):
    """Backend-specific extension data for a diagram element."""

    plantuml: PlantUMLElementExtensions | None
    mermaid: Mapping[str, Any] | None
    d2: D2ElementExtensions | None
    structurizr: Mapping[str, Any] | None


class BoundaryExtensions(TypedDict, total=False):
    """Backend-specific extension data for a boundary element."""

    plantuml: PlantUMLBoundaryExtensions | None
    mermaid: MermaidBoundaryExtensions | None
    d2: D2BoundaryExtensions | None


def merge_extensions(
    extensions: ElementExtensions | None = None,
    **backend_extensions: Any,
) -> ElementExtensions | None:
    """Merge backend-specific kwargs into the canonical extensions mapping."""
    merged: dict[str, Any] = dict(extensions or {})

    for backend, value in backend_extensions.items():
        if value is None:
            continue

        existing = merged.get(backend)
        if existing is not None and existing != value:
            raise ValueError(
                f"Extension data for {backend!r} was provided twice"
            )

        merged[backend] = value

    return cast(ElementExtensions, merged) or None


def _repr_extension_attrs(
    extensions: ElementExtensions | None,
) -> list[str]:
    """Return constructor kwargs for backend-specific extension data."""
    if not extensions:
        return []

    attrs: list[str] = []
    remaining: dict[str, Any] = {}

    for backend, value in extensions.items():
        if value is None:
            continue

        if backend in {"plantuml", "mermaid", "d2"}:
            attrs.append(f"{backend}={value!r}")
        else:
            remaining[backend] = value

    if remaining:
        attrs.append(f"extensions={remaining!r}")

    return attrs


DEFAULT_PROPERTIES_HEADER: tuple[str, str] = ("Property", "Value")


@dataclass
class DiagramElementProperties:
    """
    Holds tabular property metadata for a diagram element.

    Used to annotate elements with additional labeled attributes,
    typically rendered as a table in the diagram.

    Attributes:
        show_header: Whether to display the header row.
        header: Column names for the property table.
        properties: List of rows (each row is a list of string values).
    """

    show_header: bool = True
    header: list[str] = field(
        default_factory=lambda: list(DEFAULT_PROPERTIES_HEADER)
    )
    properties: list[list[str]] = field(default_factory=list)

    def __bool__(self) -> bool:
        return bool(self.properties)

    @staticmethod
    def _normalize_rows(
        *properties: str | PropertyRow,
    ) -> list[tuple[str, ...]]:
        if not properties:
            return []

        if all(isinstance(item, str) for item in properties):
            return [tuple(str(value) for value in properties)]

        if any(isinstance(item, str) for item in properties):
            raise ValueError(
                "Properties must be passed either as string values for one row "
                "or as row sequences"
            )

        return [tuple(str(value) for value in row) for row in properties]

    def set_header(self, *args: str) -> Self:
        if not args:
            raise ValueError("The header cannot be empty")

        if self.properties:
            expected_header_length = self.properties[0]

            if len(args) != len(expected_header_length):
                raise ValueError(
                    "The header length does not match the number of values"
                )

        self.header = list(args)

        return self

    def without_header(self) -> Self:
        self.show_header = False

        return self

    def add_row(self, *args: str) -> Self:
        if len(args) != len(self.header):
            raise ValueError(
                "The number of values does not match the header length"
            )

        self.properties.append(list(args))

        return self

    def add_rows(self, *properties: str | PropertyRow) -> Self:
        for row in self._normalize_rows(*properties):
            self.add_row(*row)

        return self

    def with_rows(
        self,
        *properties: str | PropertyRow,
        header: Sequence[str] | None = None,
        show_header: bool = True,
    ) -> Self:
        if header is not None:
            self.set_header(*header)

        if not show_header:
            self.without_header()

        self.add_rows(*properties)

        return self


@overload
def with_properties(
    element: TDiagramElement,
    *properties: str | PropertyRow,
    header: Sequence[str] | None = None,
    show_header: bool = True,
) -> TDiagramElement: ...  # pragma: no cover


@overload
def with_properties(
    element: Callable[P, TDiagramElement],
    *properties: str | PropertyRow,
    header: Sequence[str] | None = None,
    show_header: bool = True,
) -> Callable[P, TDiagramElement]: ...  # pragma: no cover


def with_properties(
    element: TDiagramElement | Callable[P, TDiagramElement],
    *properties: str | PropertyRow,
    header: Sequence[str] | None = None,
    show_header: bool = True,
) -> TDiagramElement | Callable[P, TDiagramElement]:
    """
    Adds property rows to a diagram element or wraps an element factory.

    For one row, pass values directly:

        with_properties(Person("CRM Operator"), "Role", "Operator")

    For multiple rows, pass row sequences:

        with_properties(
            Person("CRM Operator"),
            ("Role", "Operator"),
            ("Shift", "Daytime"),
        )

    To pre-build a reusable element factory:

        CRMOperator = with_properties(
            partial(Person, label="CRM Operator"),
            ("Role", "Operator"),
            ("Shift", "Daytime"),
        )
    """
    if isinstance(element, BaseDiagramElement):
        element.properties.with_rows(
            *properties,
            header=header,
            show_header=show_header,
        )
        return element

    def wrapped(*args: P.args, **kwargs: P.kwargs) -> TDiagramElement:
        instance = element(*args, **kwargs)
        instance.properties.with_rows(
            *properties,
            header=header,
            show_header=show_header,
        )
        return instance

    return wrapped


class BaseDiagramElement:
    """
    Base class for any object that belongs to a diagram.

    Instances are registered in the current diagram context when created.
    Subclasses may limit the diagram types or renderers that can contain them.
    """

    allowed_diagram_types: tuple[DiagramType, ...] | None = None
    allowed_renderers: tuple[RendererEnum, ...] | None = None
    extensions: ElementExtensions | None = None

    _diagram: Diagram

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the object and add it to the current diagram context.

        Args:
            **kwargs: Reserved for subclasses.
        """
        self._diagram = current_diagram()
        self._contribute_to_diagram()
        self.properties = DiagramElementProperties()

    def _check_diagram_type(self) -> None:
        """Validate that this object is allowed in the current diagram type."""
        if not self.allowed_diagram_types:
            return None

        if self._diagram.type not in self.allowed_diagram_types:
            element_name = self.__class__.__name__
            diagram_type = self._diagram.type.value
            allowed = ", ".join([dt.value for dt in self.allowed_diagram_types])

            raise ValueError(
                f"{element_name} is not allowed in {diagram_type}. "
                f"Allowed diagram types: {allowed}."
            )

        return None

    def _contribute_to_diagram(self) -> None:
        """Register this object in the current diagram declaration stream."""
        self._check_diagram_type()
        self._diagram.add_ordered_element(self)

    def set_property_header(self, *args: str) -> Self:
        """
        Sets the column headers for the element's property table.

        This must be called either before adding any property rows, or
        the header length must match the number of values.

        Args:
            *args: Column names to use as the property header.

        Returns:
            The updated diagram element.

        Raises:
            ValueError: If header length does not match the number of values.
        """
        self.properties.set_header(*args)

        return self

    def without_property_header(self) -> Self:
        """
        Disables the rendering of the header row in the property table.

        Returns:
            The updated diagram element.
        """
        self.properties.without_header()

        return self

    def with_properties(
        self,
        *properties: str | PropertyRow,
        header: Sequence[str] | None = None,
        show_header: bool = True,
    ) -> Self:
        """
        Adds one or more rows to the property table.

        For one row, pass values directly:

            element.with_properties("Role", "Operator")

        For multiple rows, pass row sequences:

            element.with_properties(
                ("Role", "Operator"),
                ("Shift", "Daytime"),
            )

        Args:
            *properties: Values for one row, or row sequences.
            header: Optional property table header override.
            show_header: Whether to render the property table header.

        Returns:
            The updated diagram element.
        """
        self.properties.with_rows(
            *properties,
            header=header,
            show_header=show_header,
        )

        return self

    def add_property(self, *args: str) -> Self:
        """
        Adds a row to the property table.

        The number of arguments must match the number of header columns.

        Args:
            *args: Values for each column in the property row.

        Returns:
            The updated diagram element.

        Raises:
            ValueError: If the number of values does not match the
                header length.
        """
        self.properties.add_row(*args)

        return self

    @property
    def diagram(self) -> Diagram:
        """Returns the current diagram context."""
        return self._diagram


class Element(BaseDiagramElement, abc.ABC):
    """
    Base class for all C4 elements (e.g. Person, System, Container, Component).

    Elements are automatically registered in the current diagram context.
    """

    allowed_diagram_types: tuple[DiagramType, ...] | None = None

    _diagram: Diagram

    alias: str
    label: str
    technology: str | None

    def __init__(
        self,
        label: Required[str] = REQUIRED,
        description: str | None = None,
        extensions: ElementExtensions | None = None,
        plantuml: Mapping[str, Any] | None = None,
        mermaid: Mapping[str, Any] | None = None,
        d2: D2ElementExtensions | None = None,
        alias: Maybe[str] = MISSING,
    ) -> None:
        """
        Initialize a new diagram element. Automatically adds the element to the
        current diagram.

        Args:
            label: Display name for the element. Required.
            description: Optional description text.
            extensions: Backend-specific extension data.
            plantuml: PlantUML-specific extension data.
            mermaid: Mermaid-specific extension data.
            d2: D2-specific extension data.
            alias: Unique identifier for the element. If not provided, it is
                autogenerated from the label.

        Raises:
            ValueError: If `label` is not provided.
        """
        self.label = self._check_label(label)
        self.alias = self._check_alias(alias, self.label)
        self.description = description
        self.extensions = merge_extensions(
            extensions,
            plantuml=plantuml,
            mermaid=mermaid,
            d2=d2,
        )

        self.technology = None

        super().__init__()

    @overload
    def __rshift__(self, other: str) -> Relationship: ...  # pragma: no cover

    @overload
    def __rshift__(self, other: Element) -> _EdgeDraft: ...  # pragma: no cover

    def __rshift__(self, other: str | Element) -> Relationship | _EdgeDraft:
        """
        Start a fluent relationship declaration from this element.

        Args:
            other: A relationship label for `self >> "label" >> element`,
                or the destination element for `self >> element | "label"`.

        Returns:
            A partial relationship or edge draft to complete the declaration.
        """
        if isinstance(other, str):
            # self >> "label" >> element2
            return Relationship(label=other, from_element=self)

        if isinstance(other, Element):
            # Draft for: self >> element2 | "label"
            return _EdgeDraft(source=self, destination=other)

        return NotImplemented

    @overload
    def __lshift__(self, other: str) -> Relationship: ...  # pragma: no cover

    @overload
    def __lshift__(self, other: Element) -> _EdgeDraft: ...  # pragma: no cover

    def __lshift__(self, other: str | Element) -> Relationship | _EdgeDraft:
        """
        Start a fluent relationship declaration toward this element.

        Args:
            other: A relationship label for `element << "label" << self`,
                or the source element for `element << self | "label"`.

        Returns:
            A partial relationship or edge draft to complete the declaration.
        """
        if isinstance(other, str):
            # element1 << "label" << element2
            return Relationship(label=other, to_element=self)

        if isinstance(other, Element):
            # Draft for: element1 >> element2 | "label"
            return _EdgeDraft(source=other, destination=self)

        return NotImplemented

    def __rrshift__(self, other: list[Relationship]) -> list[Relationship]:
        """
        Complete relationships from their stored sources to this element.

        Args:
            other: Partial relationships with source elements already set.

        Returns:
            Completed relationships targeting this element.
        """
        if isinstance(other, list) and all(
            isinstance(r, Relationship) for r in other
        ):
            return [r._connect(r.from_element, destination=self) for r in other]

        return NotImplemented  # pragma: no cover

    def __rlshift__(self, other: list[Relationship]) -> list[Relationship]:
        """
        Complete relationships from this element to their stored destinations.

        Args:
            other: Partial relationships with destination elements already set.

        Returns:
            Completed relationships sourced from this element.
        """
        if isinstance(other, list) and all(
            isinstance(r, Relationship) for r in other
        ):
            return [
                r._connect(source=self, destination=r.to_element) for r in other
            ]

        return NotImplemented  # pragma: no cover

    def _check_label(self, label: str | Required) -> str:
        """Return a valid element label or raise if it is missing."""
        if label is REQUIRED:
            raise ValueError("The 'label' argument is required")

        return cast(str, label)

    def _check_alias(self, alias: Maybe[str], label: str) -> str:
        """Return the provided alias or generate one from the label."""
        if alias is MISSING:
            alias = self._generate_alias(label)

        return cast(str, alias)

    @override
    def _contribute_to_diagram(self) -> None:
        """Register this element in the current diagram or active boundary."""
        self._check_diagram_type()
        self._diagram.add(self)

    def uses(
        self,
        other: TElement,
        label: str,
        relationship_type: RelationshipType = RelationshipType.REL,
        **kwargs: Any,
    ) -> Relationship:
        """
        Declare that this element uses another.

        Args:
            other: The element being used.
            label: Description of the interaction.
            relationship_type: Type of arrow to use.
            kwargs: Optional relationship kwargs.

        Returns:
            The created relationship.
        """
        relationship_class = Relationship.get_relationship_by_type(
            relationship_type
        )
        return relationship_class(
            from_element=self,  # type: ignore[arg-type]
            to_element=other,  # type: ignore[arg-type]
            label=label,
            **kwargs,
        )

    def used_by(
        self,
        other: TElement,
        label: str,
        relationship_type: RelationshipType = RelationshipType.REL,
        **kwargs: Any,
    ) -> Relationship:
        """
        Declare that another element uses this element.

        Args:
            other: The element that uses this element.
            label: Description of the interaction.
            relationship_type: Type of arrow to use.
            kwargs: Optional relationship kwargs.

        Returns:
            The created relationship.
        """
        relationship_class = Relationship.get_relationship_by_type(
            relationship_type
        )
        return relationship_class(
            from_element=other,  # type: ignore[arg-type]
            to_element=self,  # type: ignore[arg-type]
            label=label,
            **kwargs,
        )

    def _generate_alias(self, label: str) -> str:
        """Generate an alias from the label in the current diagram context."""
        return current_diagram().generate_alias(
            label=label,
            fallback_prefix=self.__class__.__name__,
        )

    @override
    def __str__(self) -> str:
        """Returns the string representation of the element."""
        cls_name = self.__class__.__name__
        return f"{cls_name}(alias={self.alias!r}, label={self.label!r})"

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        attrs = [
            f"{self.label!r}",
        ]

        if self.description:
            attrs.append(f"{self.description!r}")

        attrs.extend(_repr_extension_attrs(self.extensions))

        if self.technology:
            attrs.append(f"technology={self.technology!r}")

        attrs.append(f"alias={self.alias!r}")

        args = ", ".join(attrs)
        return f"{cls_name}({args})"


class ElementWithTechnology(Element):
    """
    Base class for elements that define a `technology` field.
    """

    def __init__(
        self,
        label: Required[str] = REQUIRED,
        description: str | None = None,
        technology: str | None = None,
        extensions: ElementExtensions | None = None,
        plantuml: Mapping[str, Any] | None = None,
        mermaid: Mapping[str, Any] | None = None,
        d2: D2ElementExtensions | None = None,
        alias: Maybe[str] = MISSING,
    ) -> None:
        """
        Initialize a new diagram element.

        Args:
            label: Display name for the element. Required.
            description: Optional description text.
            technology: Optional technology.
            extensions: Backend-specific extension data.
            plantuml: PlantUML-specific extension data.
            mermaid: Mermaid-specific extension data.
            d2: D2-specific extension data.
            alias: Unique identifier for the element. If not provided, it is
                autogenerated from the label.
        """
        super().__init__(
            alias=alias,
            label=label,
            description=description,
            extensions=extensions,
            plantuml=plantuml,
            mermaid=mermaid,
            d2=d2,
        )

        self.technology = technology


class Boundary(Element):
    """
    Represents a boundary element that groups other elements.

    Boundaries can be nested, and manage their own child elements.
    """

    def __init__(
        self,
        label: Required[str] = REQUIRED,
        description: str | None = None,
        extensions: ElementExtensions | None = None,
        plantuml: Mapping[str, Any] | None = None,
        mermaid: Mapping[str, Any] | None = None,
        d2: D2BoundaryExtensions | None = None,
        alias: Maybe[str] = MISSING,
    ) -> None:
        """
        Initialize a new boundary element.

        Args:
            label: Human-readable name for the boundary. Required.
            description: Optional description.
            extensions: Backend-specific extension data.
            plantuml: PlantUML-specific extension data.
            mermaid: Mermaid-specific extension data.
            d2: D2-specific extension data.
            alias: Unique identifier for the boundary.
                If not provided, one is autogenerated.

        Notes:
            - If the boundary is created within another boundary context, it is
              added as a nested boundary.
            - Otherwise, it is added directly to the current diagram.
        """
        self._parent = get_boundary()

        super().__init__(
            label=label,
            alias=alias,
            description=description,
            extensions=extensions,
            plantuml=plantuml,
            mermaid=mermaid,
            d2=d2,
        )

        self._elements: list[Element] = []
        self._relationships: list[Relationship] = []
        self._boundaries: list[Boundary] = []

        self.__ordered_elements: list[BaseDiagramElement] = []

    @override
    def _contribute_to_diagram(self) -> None:
        """Register this boundary in the current diagram or parent boundary."""
        self._check_diagram_type()
        self._diagram.add_boundary(self)

    @property
    def elements(self) -> list[Element]:
        """
        Returns the list of diagram elements added to this boundary.

        Returns:
            Child elements grouped under this boundary.
        """
        return self._elements

    @property
    def boundaries(self) -> list[Boundary]:
        """
        Returns the list of nested boundaries inside this boundary.

        Returns:
            Child boundaries nested within this boundary.
        """
        return self._boundaries

    @property
    def ordered_elements(self) -> list[BaseDiagramElement]:
        """
        Return boundary items in their order of definition.

        The sequence can include C4 elements, relationships, boundaries, and
        backend-owned statements that affect declaration-order rendering.
        """
        return self.__ordered_elements

    @property
    def relationships(self) -> list[Relationship]:
        """
        Returns all relationships defined in the boundary.
        """
        return self._relationships

    def __enter__(self) -> Self:
        """
        Enter the boundary context.

        Returns:
            The boundary instance now active as context.
        """
        set_boundary(self)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """
        Exit the boundary context and restore the previous boundary.
        """
        set_boundary(self._parent)

    def add(self, element: TElement) -> TElement:
        """
        Add a diagram element to this boundary.

        Args:
            element: The element to add.

        Returns:
            The added element.
        """
        self._elements.append(element)
        self.__ordered_elements.append(element)

        return element

    def add_boundary(self, boundary: TBoundary) -> TBoundary:
        """
        Add a nested boundary to this boundary.

        Args:
            boundary: The boundary to add.

        Returns:
            The added boundary.
        """
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
        self._relationships.append(relationship)
        self.__ordered_elements.append(relationship)

        return relationship

    def add_ordered_element(
        self, element: BaseDiagramElement
    ) -> BaseDiagramElement:
        """Add a diagram object to this boundary declaration-order sequence."""
        self.__ordered_elements.append(element)

        return element


@dataclass(frozen=True)
class _EdgeDraft:
    """
    Intermediate object for `source >> destination | "label"` syntax.
    """

    source: Element
    destination: Element

    def __or__(self, label: str) -> Relationship:
        """Create the relationship represented by this draft."""
        if not isinstance(label, str):
            return NotImplemented  # pragma: no cover

        return Relationship(
            label=label,
            from_element=self.source,
            to_element=self.destination,
        )


class Relationship(BaseDiagramElement):
    """
    Represents a connection between two elements.

    Supports direct construction and fluent chaining using `>>` and `<<`
    operators. Subclasses are registered by
    [`RelationshipType`][c4.diagrams.core.RelationshipType].
    """

    __relationship_by_type: ClassVar[
        dict[RelationshipType, type[Relationship]]
    ] = {}

    relationship_type: RelationshipType = RelationshipType.REL

    def __init__(
        self,
        label: str | None = None,
        description: str | None = None,
        technology: str | None = None,
        from_element: TElement | None = None,
        to_element: TElement | None = None,
        relationship_type: RelationshipType | None = None,
        extensions: ElementExtensions | None = None,
        plantuml: PlantUMLRelationshipExtensions | None = None,
        mermaid: Mapping[str, Any] | None = None,
        d2: D2RelationshipExtensions | None = None,
    ) -> None:
        """
        Initialize a relationship between two elements.

        Args:
            label: The label shown on the relationship edge.
            description: Additional details about the relationship.
            technology: The technology used in the communication.
            from_element: The source element. Optional.
            to_element: The destination element. Optional.
            relationship_type: Type of the relationship.
                Defaults to the class-level `relationship_type`.
            extensions: Backend-specific extension data.
            plantuml: PlantUML-specific extension data.
            mermaid: Mermaid-specific extension data.
            d2: D2-specific extension data.

        Notes:
            If both `from_element` and `to_element` are provided,
            the relationship will be registered in the current
            diagram immediately.
        """
        self.from_element = from_element
        self.to_element = to_element
        self.label = label
        self.technology = technology
        self.description = description
        self.extensions = merge_extensions(
            extensions,
            plantuml=plantuml,
            mermaid=mermaid,
            d2=d2,
        )

        self.relationship_type = relationship_type or self.relationship_type

        super().__init__()

    @override
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """
        Registers the relationship subclass under its unique
        `relationship_type`.
        """
        super().__init_subclass__(*args, **kwargs)

        relationship_type = getattr(cls, "relationship_type", None)
        if (
            relationship_type is None
            or relationship_type in cls.__relationship_by_type
        ):
            raise TypeError(
                f"Please provide an unique `relationship_type` for this"
                f" class {cls.__name__}"
            )

        cls.__relationship_by_type[relationship_type] = cls

    def get_participants(self) -> tuple[TElement, TElement]:
        """
        Return the source and destination elements for a complete relationship.

        Raises:
            ValueError: If either endpoint has not been provided yet.
        """
        if not self.from_element:
            raise ValueError("from_element not provided")

        if not self.to_element:
            raise ValueError("to_element not provided")

        return self.from_element, self.to_element  # type: ignore[return-value]

    @overload
    def __rshift__(
        self, other: TElement
    ) -> Relationship: ...  # pragma: no cover

    @overload
    def __rshift__(
        self, other: list[TElement]
    ) -> list[Relationship]: ...  # pragma: no cover

    def __rshift__(
        self, other: TElement | list[TElement]
    ) -> Relationship | list[Relationship]:
        """Complete this partial relationship with one or more destinations."""
        self._ensure_not_completed()

        return self._connect(source=self.from_element, destination=other)  # type: ignore[arg-type,type-var]

    @overload
    def __lshift__(
        self, other: TElement
    ) -> Relationship: ...  # pragma: no cover

    @overload
    def __lshift__(
        self, other: list[TElement]
    ) -> list[Relationship]: ...  # pragma: no cover

    def __lshift__(
        self, other: TElement | list[TElement]
    ) -> Relationship | list[Relationship]:
        """Complete this partial relationship with one or more sources."""
        self._ensure_not_completed()

        return self._connect(source=other, destination=self.to_element)  # type: ignore[arg-type,type-var]

    @overload
    def __rrshift__(
        self, other: TElement
    ) -> Relationship: ...  # pragma: no cover

    @overload
    def __rrshift__(
        self, other: list[TElement]
    ) -> list[Relationship]: ...  # pragma: no cover

    def __rrshift__(
        self, other: TElement | list[TElement]
    ) -> Relationship | list[Relationship]:
        """Complete this partial relationship from left-hand sources."""
        self._ensure_not_completed()

        return self._connect(source=other, destination=self.to_element)  # type: ignore[arg-type,type-var]

    @overload
    def __rlshift__(
        self, other: TElement
    ) -> Relationship: ...  # pragma: no cover

    @overload
    def __rlshift__(
        self, other: list[TElement]
    ) -> list[Relationship]: ...  # pragma: no cover

    def __rlshift__(
        self, other: TElement | list[TElement]
    ) -> Relationship | list[Relationship]:
        """Complete this partial relationship to left-hand destinations."""
        self._ensure_not_completed()

        return self._connect(source=self.from_element, destination=other)  # type: ignore[arg-type,type-var]

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        attrs = [
            f"{self.label!r}",
        ]

        if self.description:
            attrs.append(f"{self.description!r}")

        repr_attrs = ["technology"]

        for attr in repr_attrs:
            value = getattr(self, attr)
            if value:
                attrs.append(f"{attr}={value!r}")

        attrs.extend(_repr_extension_attrs(self.extensions))

        args = ", ".join(attrs)
        return f"{cls_name}({args})"

    @overload
    def _connect(
        self, source: None, destination: None
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def _connect(
        self, source: TElement, destination: None
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def _connect(
        self, source: None, destination: TElement
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def _connect(
        self, source: TElement, destination: TElement
    ) -> Relationship: ...  # pragma: no cover

    @overload
    def _connect(
        self, source: list[TElement], destination: None
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def _connect(
        self, source: None, destination: list[TElement]
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def _connect(
        self, source: list[TElement], destination: list[TElement]
    ) -> NoReturn: ...  # pragma: no cover

    @overload
    def _connect(
        self, source: list[TElement], destination: TElement
    ) -> list[Relationship]: ...  # pragma: no cover

    @overload
    def _connect(
        self, source: TElement, destination: list[TElement]
    ) -> list[Relationship]: ...  # pragma: no cover

    def _connect(
        self,
        source: TElement | list[TElement] | None,
        destination: TElement | list[TElement] | None,
    ) -> Relationship | list[Relationship]:
        """
        Create one or more completed relationship copies.

        Args:
            source: Source element, list of sources, or `None` for an
                already-stored source.
            destination: Destination element, list of destinations, or `None`
                for an already-stored destination.

        Returns:
            A completed relationship or a list of completed relationships.

        Raises:
            ValueError: If both endpoints are missing, both endpoints are
                lists, or this relationship is already complete.
        """
        self._ensure_not_completed()

        if not source and not destination:
            raise ValueError("Either source or destination must be provided")

        if isinstance(source, list) and isinstance(destination, list):
            raise ValueError(  # noqa: TRY004
                "Either source or destination must be a single element"
            )

        if isinstance(source, list):
            from_iter = source
            to_iter: Iterable[TElement] = repeat(destination)  # type: ignore[arg-type]
        elif isinstance(destination, list):
            from_iter: Iterable[TElement] = repeat(source)  # type: ignore[no-redef]
            to_iter = destination
        else:
            # Both are single elements
            return self.copy(from_element=source, to_element=destination)

        return [
            self.copy(from_element=src, to_element=dst)
            for src, dst in zip(from_iter, to_iter, strict=False)
        ]

    def _ensure_not_completed(self) -> None:
        """Raise if both relationship endpoints are already set."""
        if self.from_element and self.to_element:
            raise ValueError(
                "Cannot modify relationship with both specified elements"
            )

    @override
    def _contribute_to_diagram(self) -> None:
        """Register complete relationships in the current diagram context."""
        self._check_diagram_type()
        if self.from_element and self.to_element:
            self._diagram.add_relationship(self)

    def get_attrs(self) -> dict[str, Any]:
        """
        Return the constructor attributes for this relationship.
        """
        return {
            "from_element": self.from_element,
            "to_element": self.to_element,
            "label": self.label,
            "technology": self.technology,
            "description": self.description,
            "extensions": self.extensions,
            "relationship_type": self.relationship_type,
        }

    def copy(self, **overrides: Any) -> Relationship:
        """
        Clone this relationship, optionally overriding constructor fields.

        Args:
            **overrides: Field values to override in the cloned relationship.

        Returns:
            A new relationship with copied properties.
        """
        attrs = {**self.get_attrs(), **overrides}

        cls = self.get_relationship_by_type(self.relationship_type)

        relationship_copy = cls(**attrs)

        if self.properties.properties:
            relationship_copy.properties = copy.deepcopy(self.properties)

        return relationship_copy

    @classmethod
    def get_relationship_by_type(
        cls, relationship_type: RelationshipType
    ) -> type[Relationship]:
        """
        Retrieve the relationship class associated with the
        given RelationshipType.

        Args:
            relationship_type: The enum value representing the
                type of relationship.

        Returns:
            The corresponding Relationship subclass.

        Raises:
            KeyError: If no class is registered for the provided
                relationship type.
        """
        return cls.__relationship_by_type[relationship_type]


TRelationship = TypeVar("TRelationship", bound=Relationship)
TBoundary = TypeVar("TBoundary", bound=Boundary)
TElement = TypeVar("TElement", bound=Element)

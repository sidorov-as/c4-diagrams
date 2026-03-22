from __future__ import annotations

import abc
from collections import UserString, defaultdict
from collections.abc import Iterable
from contextvars import ContextVar
from dataclasses import dataclass, field
from enum import unique
from itertools import repeat
from pathlib import Path
from types import TracebackType
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    TypeVar,
    cast,
)

from typing_extensions import Self, override

from c4.compat import StrEnum

if TYPE_CHECKING:  # pragma: no cover
    from c4.renderers import BaseRenderer, PlantUMLRenderer, RenderOptions

__diagram: ContextVar[Diagram | None] = ContextVar("diagram")
__boundary: ContextVar[Boundary | None] = ContextVar("boundary")


class AliasGenerator:
    """
    Generate unique, deterministic aliases based on a label.

    Alias generation rules:

    1. If an explicit `alias` is provided:
       - It is returned as-is.
       - A `ValueError` is raised if it has already been used.

    2. If `alias` is not provided:
       - The label is normalized:
         * lowercased
         * spaces replaced with "_"
         * hyphens replaced with "_"
       - If the normalized value has not been used yet, it is returned as-is.
       - Otherwise, a numeric suffix is appended:
           `<base>_<n>`
         where numbering starts from 1 for the first collision.

    Example:
        >>> gen = AliasGenerator()
        >>> gen.generate("My Service")
        'my_service'
        >>> gen.generate("My Service")
        'my_service_1'
        >>> gen.generate("My Service")
        'my_service_2'

    Notes:
        - Uniqueness is enforced per generator instance.
        - Explicit aliases participate in uniqueness checks.
        - Counters are maintained per normalized base alias.
    """

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._used: set[str] = set()

    @staticmethod
    def _normalize(label: str) -> str:
        return label.lower().replace(" ", "_").replace("-", "_")

    def generate(
        self,
        label: str,
        alias: str | None = None,
    ) -> str:
        """
        Generate a unique alias.

        Args:
            label: Source label used to derive the alias when `alias` is None.
            alias: Optional explicit alias. If provided, it must be unique.

        Returns:
            A unique alias string.

        Raises:
            ValueError: If alias already exists.
        """
        if alias:
            if alias in self._used:
                raise ValueError(f"Alias {alias!r} already exists.")
            self._used.add(alias)
            return alias

        base = self._normalize(label)

        if base not in self._used:
            self._used.add(base)
            self._counters[base] = 1
            return base

        counter = self._counters[base]
        while True:
            candidate = f"{base}_{counter}"
            counter += 1
            if candidate not in self._used:
                self._used.add(candidate)
                self._counters[base] = counter
                return candidate


class EnumDescriptionsMixin:
    @classmethod
    def get_descriptions(cls) -> dict[Self, str]:
        """Return the Enum items description used in documentation."""
        raise NotImplementedError("Must be implemented by subclasses")


@unique
class RelationshipType(EnumDescriptionsMixin, StrEnum):
    """
    Enum representing different types of relationships between
    diagram elements.
    """

    REL = "REL"
    BI_REL = "BI_REL"
    REL_BACK = "REL_BACK"
    REL_NEIGHBOR = "REL_NEIGHBOR"
    BI_REL_NEIGHBOR = "BI_REL_NEIGHBOR"
    REL_BACK_NEIGHBOR = "REL_BACK_NEIGHBOR"
    REL_D = "REL_D"
    REL_DOWN = "REL_DOWN"
    BI_REL_D = "BI_REL_D"
    BI_REL_DOWN = "BI_REL_DOWN"
    REL_U = "REL_U"
    REL_UP = "REL_UP"
    BI_REL_U = "BI_REL_U"
    BI_REL_UP = "BI_REL_UP"
    REL_L = "REL_L"
    REL_LEFT = "REL_LEFT"
    BI_REL_L = "BI_REL_L"
    BI_REL_LEFT = "BI_REL_LEFT"
    REL_R = "REL_R"
    REL_RIGHT = "REL_RIGHT"
    BI_REL_R = "BI_REL_R"
    BI_REL_RIGHT = "BI_REL_RIGHT"

    @classmethod
    def get_descriptions(cls) -> dict[RelationshipType, str]:
        """Return the Enum items description used in documentation."""
        return {
            cls.BI_REL: "A bidirectional relationship between two elements.",
            cls.BI_REL_DOWN: "A bidirectional downward relationship.",
            cls.BI_REL_D: (
                "A bidirectional downward relationship. "
                "Shorthand for `BI_REL_DOWN`."
            ),
            cls.BI_REL_LEFT: "A bidirectional leftward relationship.",
            cls.BI_REL_L: (
                "A bidirectional leftward relationship. "
                "Shorthand for `BI_REL_LEFT`."
            ),
            cls.BI_REL_NEIGHBOR: (
                "A bidirectional neighboring relationship between two elements."
            ),
            cls.BI_REL_RIGHT: "A bidirectional rightward relationship.",
            cls.BI_REL_R: (
                "A bidirectional rightward relationship. "
                "Shorthand for `BI_REL_RIGHT`."
            ),
            cls.BI_REL_UP: "A bidirectional upward relationship.",
            cls.BI_REL_U: (
                "A bidirectional upward relationship. "
                "Shorthand for `BI_REL_UP`."
            ),
            cls.REL: "A unidirectional relationship between two elements.",
            cls.REL_BACK: "A unidirectional relationship pointing backward.",
            cls.REL_BACK_NEIGHBOR: (
                "A unidirectional relationship combining backward "
                "and neighboring semantics."
            ),
            cls.REL_DOWN: "A unidirectional downward relationship.",
            cls.REL_D: (
                "A unidirectional downward relationship. "
                "Shorthand for `REL_DOWN`."
            ),
            cls.REL_LEFT: "A unidirectional leftward relationship.",
            cls.REL_L: (
                "A unidirectional leftward relationship. "
                "Shorthand for `REL_LEFT`."
            ),
            cls.REL_NEIGHBOR: (
                "A unidirectional relationship representing a lateral "
                "or neighboring interaction."
            ),
            cls.REL_RIGHT: "A unidirectional rightward relationship.",
            cls.REL_R: (
                "A unidirectional rightward relationship. "
                "Shorthand for `REL_RIGHT`."
            ),
            cls.REL_UP: "A unidirectional upward relationship.",
            cls.REL_U: (
                "A unidirectional upward relationship. Shorthand for `REL_UP`."
            ),
        }


@unique
class LayoutType(EnumDescriptionsMixin, StrEnum):
    """
    Enum representing layout modifiers for diagram elements.
    """

    LAY_D = "LAY_D"
    LAY_DOWN = "LAY_DOWN"
    LAY_U = "LAY_U"
    LAY_UP = "LAY_UP"
    LAY_R = "LAY_R"
    LAY_RIGHT = "LAY_RIGHT"
    LAY_L = "LAY_L"
    LAY_LEFT = "LAY_LEFT"

    @classmethod
    def get_descriptions(cls) -> dict[LayoutType, str]:
        """Return the Enum items description used in documentation."""
        return {
            cls.LAY_DOWN: "Positions `from` element below `to` element.",
            cls.LAY_D: (
                "Positions `from` element below `to` element. "
                "Shorthand for `LAY_DOWN` layout."
            ),
            cls.LAY_UP: "Positions `from` element above `to` element.",
            cls.LAY_U: (
                "Positions `from` element above `to` element. "
                "Shorthand for `LAY_UP` layout."
            ),
            cls.LAY_RIGHT: (
                "Positions `from` element to the right of `to` element."
            ),
            cls.LAY_R: (
                "Positions `from` element to the right of `to` element. "
                "Shorthand for `LAY_RIGHT` layout."
            ),
            cls.LAY_LEFT: (
                "Positions `from` element to the left of `to` element."
            ),
            cls.LAY_L: (
                "Positions `from` element to the left of `to` element. "
                "Shorthand for `LAY_LEFT` layout."
            ),
        }


@unique
class DiagramType(StrEnum):
    """
    Enum representing diagram types.
    """

    DIAGRAM = "Diagram"
    SYSTEM_CONTEXT_DIAGRAM = "SystemContextDiagram"
    SYSTEM_LANDSCAPE_DIAGRAM = "SystemLandscapeDiagram"
    CONTAINER_DIAGRAM = "ContainerDiagram"
    COMPONENT_DIAGRAM = "ComponentDiagram"
    DYNAMIC_DIAGRAM = "DynamicDiagram"
    DEPLOYMENT_DIAGRAM = "DeploymentDiagram"


def get_diagram() -> Diagram | None:
    """
    Get the current diagram from thread-local context.

    Returns:
        The currently active diagram, or None if not set.
    """
    try:
        return __diagram.get()
    except LookupError:  # pragma: no cover
        return None


def current_diagram() -> Diagram:
    """
    Get the current diagram, or raise if no diagram is active.

    Returns:
        The current diagram.

    Raises:
        ValueError: If no diagram is set in context.
    """
    diagram = get_diagram()
    if not diagram:
        raise ValueError("Element must be created within a diagram context")

    return diagram


def set_diagram(diagram: Diagram | None) -> None:
    """
    Set the current diagram in thread-local context.
    """
    __diagram.set(diagram)


def get_boundary() -> Boundary | None:
    """
    Get the current boundary from thread-local context.

    Returns:
        The currently active boundary, or None if not set.
    """
    try:
        return __boundary.get()
    except LookupError:
        return None


def current_boundary() -> Boundary:
    """
    Get the current boundary, or raise if no boundary is active.

    Returns:
        The current boundary.

    Raises:
        ValueError: If no boundary is set in context.
    """
    boundary = get_boundary()
    if not boundary:
        raise ValueError("Element must be created within a boundary context")

    return boundary


def set_boundary(boundary: Boundary | None) -> None:
    """
    Set the current boundary in thread-local context.
    """
    __boundary.set(boundary)


class EmptyStr(UserString):
    def __init__(self) -> None:
        super().__init__("")

    @override
    def __repr__(self) -> str:
        return "<EmptyStr>"


empty = EmptyStr()


class Required(UserString):
    def __init__(self) -> None:
        super().__init__("")

    @override
    def __repr__(self) -> str:
        return "<Required>"


not_provided = Required()

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


class BaseDiagramElement:
    """
    Base class for any object that belongs to a diagram.

    Provides access to the current diagram context and allows
    attaching structured properties (e.g. key-value tables).
    """

    allowed_diagram_types: tuple[DiagramType, ...] | None = None

    _diagram: Diagram

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the element and adds it to the current diagram context.
        """
        self._diagram = current_diagram()
        self._contribute_to_diagram()
        self.properties = DiagramElementProperties()

    def _check_diagram_type(self) -> None:
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

    def _contribute_to_diagram(self) -> None:
        self._check_diagram_type()
        self._diagram.add_base_element(self)

    def set_property_header(self, *args: str) -> Self:
        """
        Sets the column headers for the element's property table.

        This must be called before adding any property rows.

        Args:
            *args: Column names to use as the property header.

        Returns:
            The updated diagram element.

        Raises:
            ValueError: If properties were already added before setting
                the header.
        """
        if not args:
            raise ValueError("The header cannot be empty")

        if self.properties.properties:
            raise ValueError(
                "Cannot change header after properties have been added. "
                "Set the header before calling add_property()."
            )

        self.properties.header = list(args)

        return self

    def without_property_header(self) -> Self:
        """
        Disables the rendering of the header row in the property table.

        Returns:
            The updated diagram element.
        """
        self.properties.show_header = False

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
        if len(args) != len(self.properties.header):
            raise ValueError(
                "The number of values does not match the header length"
            )

        self.properties.properties.append(list(args))

        return self

    @property
    def diagram(self) -> Diagram:
        """Returns the current diagram context."""
        return self._diagram


class BaseIndex:
    """
    Abstract base class for index-related macros.
    """

    def __init__(self) -> None:
        """
        Initializes an index object.
        """
        self.prefix: str | None = None
        self.suffix: str | None = None
        self._class_name = self.__class__.__name__

        self._operations: list[tuple[str, int]] = []

    def __add__(self, other: Any) -> Self:
        """
        Applies a right-hand operation to the index.

        This method supports two behaviors:

        - If `other` is a non-empty string, it is appended as a suffix.
          This is allowed only once per instance.
        - If `other` is an integer, it is recorded as a `+N` arithmetic
          operation that will be rendered after the base index.

        Examples:
            str(Index() + "-2") -> "Index()-2"
            str(Index() + 1) -> "Index()+1"
            str(Index() - 1) -> "Index()-1"

        Args:
            other: A non-empty string suffix or an integer offset.

        Returns:
            Self, with the suffix applied or the arithmetic operation recorded.

        Raises:
            ValueError: If `other` is not a non-empty string or an int,
                or if a suffix has already been set when adding a string.
        """
        if isinstance(other, str):
            if not other:
                raise TypeError(
                    f"{self._class_name}.__add__() requires non-empty string"
                )

            if self.suffix is not None:
                raise ValueError(
                    f"Operation not allowed. "
                    f"Use a new {self._class_name}() instance instead"
                )

            self.suffix = other
            return self

        if isinstance(other, int):
            self._operations.append(("+", other))
            return self

        raise TypeError(
            f"{self._class_name}.__add__() requires str or int, got {other!r}"
        )

    def __sub__(self, other: Any) -> Self:
        """
        Records a subtraction operation on the index.

        The operation is stored and later rendered after the base index.

        Examples:
            str(Index() - 2) -> "Index()-2"
            str(SetIndex(10) - 3) -> "SetIndex(10)-3"

        Args:
            other: An integer value to subtract.

        Returns:
            Self, with the `-N` arithmetic operation recorded.

        Raises:
            ValueError: If `other` is not an integer.
        """
        if not isinstance(other, int):
            raise TypeError(
                f"{self._class_name}.__sub__() requires int, got {other!r}"
            )

        self._operations.append(("-", other))
        return self

    def __radd__(self, other: Any) -> Self:
        """
        Applies a left-hand string prefix to the index.

        This enables expressions where a string appears on the left side,
        such as `"prefix" + Index()`. The prefix is allowed only once per
        instance.

        Examples:
            str("1+" + Index()) -> "1+Index()"
            str("2-" + Index() + 1) -> "2-Index()+1"

        Args:
            other: A non-empty string to prepend.

        Returns:
            Self, with the prefix applied.

        Raises:
            ValueError: If `other` is not a non-empty string,
                or if a prefix has already been set.
        """
        if not isinstance(other, str) or not other:
            raise TypeError(
                f"{self._class_name}.__add__() requires non-empty string"
            )

        if self.prefix is not None:
            raise ValueError(
                f"Operation not allowed. "
                f"Use a new {self._class_name}() instance instead"
            )

        self.prefix = other

        return self

    def get_signature(self) -> str:
        """
        Returns the core value of the index used in rendering.

        Subclasses should override this method to define meaningful output.

        Returns:
            A string representing the internal value of the index.
        """
        return ""

    @override
    def __str__(self) -> str:
        """
        Returns a string representation of the index with any applied
        prefix or suffix.

        Example:
            "Index(1)-1", "Index(3)", etc.
        """
        prefix = self.prefix or ""
        suffix = self.suffix or ""

        signature = self.get_signature()

        base = f"{self._class_name}({signature})"

        # render arithmetic operations
        ops = "".join(f"{op}{value}" for op, value in self._operations)

        return f"{prefix}{base}{ops}{suffix}"


class Index(BaseIndex):
    """
    Represents an increment operation on the internal diagram index.

    Optionally accepts an offset to increment by.
    """

    def __init__(self, offset: int | None = None):
        """
        Initializes an index object.

        Args:
            offset: Optional offset value to increment the index by.
        """
        super().__init__()
        self.offset = offset

    @override
    def get_signature(self) -> str:
        """
        Returns the offset value as a string, or an empty string
        if no offset is set.
        """
        if self.offset is not None:
            return str(self.offset)

        return ""


class LastIndex(BaseIndex):
    """
    Represents access to the last used diagram index.

    Used to refer to the previously rendered index value.
    """


class SetIndex(BaseIndex):
    """
    Explicitly sets the relationship index to a new value.

    This index operation resets the internal counter and returns a new index.
    It is typically used as an argument to
    [`Relationship`][c4.diagrams.core.Relationship] to control
    relationship ordering explicitly.
    """

    def __init__(self, new_index: int) -> None:
        """
        Initializes a SetIndex object.

        Args:
            new_index: The index value to assign.
        """
        super().__init__()
        self.new_index = new_index

    @override
    def get_signature(self) -> str:
        """
        Returns the new index value as a string.
        """
        return str(self.new_index)


class increment(BaseDiagramElement):
    """
    Diagram element representing an increment macro call.

    Used to increment the internal index counter by a specified offset.
    """

    allowed_diagram_types: tuple[DiagramType, ...] | None = (
        DiagramType.DYNAMIC_DIAGRAM,
    )

    def __init__(self, offset: int = 1):
        """
        Initializes a macro call.

        Args:
            offset: The amount to increment the index by. Defaults to 1.
        """
        self.offset = offset

        super().__init__()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        args = f"{self.offset}" if self.offset else ""

        return f"{cls_name}({args})"


class set_index(BaseDiagramElement):
    """
    Diagram element representing a **setIndex** PlantUML macro call.

    Used to explicitly set the internal index counter to a given value.
    """

    allowed_diagram_types: tuple[DiagramType, ...] | None = (
        DiagramType.DYNAMIC_DIAGRAM,
    )

    def __init__(self, new_index: int) -> None:
        """
        Initializes a macro call.

        Args:
            new_index: The value to assign to the internal index.
        """
        self.new_index = new_index

        super().__init__()

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__

        return f"{cls_name}({self.new_index})"


@dataclass(frozen=True)
class _EdgeDraft:
    """
    Intermediate object for: Element >> Element | 'label'
    """

    source: Element
    destination: Element

    def __or__(self, label: str) -> Relationship:
        if not isinstance(label, str):
            return NotImplemented  # pragma: no cover

        return Relationship(
            label=label,
            from_element=self.source,
            to_element=self.destination,
        )


class Element(BaseDiagramElement, abc.ABC):
    """
    Base class for all C4 elements (e.g. Person, System, Container, Component).

    Elements are automatically registered in the current diagram context.
    """

    allowed_diagram_types: tuple[DiagramType, ...] | None = None

    _diagram: Diagram

    alias: str
    label: str
    tags: list[str]

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        sprite: str = "",
        tags: list[str] | None = None,
        link: str = "",
        type_: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize a new diagram element. Automatically adds the element to the
        current diagram.

        Args:
            label: Display name for the element. Required.
            description: Optional description text.
            sprite: Optional sprite/icon reference for rendering.
            tags: Optional tags for styling or grouping.
            link: Optional URL associated with the element.
            type_: Optional custom type or stereotype label.
            alias: Unique identifier for the element. If not provided, it is
                autogenerated from the label.

        Raises:
            ValueError: If `label` is not provided.
        """
        self.label = self._check_label(label)
        self.alias = self._check_alias(alias, self.label)
        self.sprite = sprite
        self.type = type_
        self.tags = tags or []
        self.link = link

        self.description = description
        self.base_shape = ""
        self.technology = ""

        super().__init__()

    def __rshift__(self, other: Any) -> Any:
        """
        Enables:
          - Self >> "label" >> Element2   (pending relationship)
          - Self >> Element2 | "label"    (draft for later '| "label"')
        """
        if isinstance(other, str):
            # self >> "label" >> element2
            return Relationship(label=other, from_element=self)

        if isinstance(other, Element):
            # Draft for: self >> element2 | "label"
            return _EdgeDraft(source=self, destination=other)

        return NotImplemented

    def __lshift__(self, other: Any) -> Any:
        """
        Enables:
          - Element2 << "label" << Self   (pending relationship)
          - Element2 << self | "label"      (draft for later '| "label"')
        """
        if isinstance(other, str):
            # element1 << "label" << element2
            return Relationship(label=other, to_element=self)

        if isinstance(other, Element):
            # Draft for: element1 >> element2 | "label"
            return _EdgeDraft(source=other, destination=self)

        return NotImplemented

    def __rrshift__(self, other: Any) -> Any:
        """
        Enables: [Relationship(...), ...] >> Element.
        """
        if isinstance(other, list) and all(
            isinstance(r, Relationship) for r in other
        ):
            return [r._connect(r.from_element, destination=self) for r in other]

        return NotImplemented  # pragma: no cover

    def __rlshift__(self, other: Any) -> Any:
        """
        Enables: Element << [Relationship(...), ...].
        """
        if isinstance(other, list) and all(
            isinstance(r, Relationship) for r in other
        ):
            return [
                r._connect(source=self, destination=r.to_element) for r in other
            ]

        return NotImplemented  # pragma: no cover

    def _check_label(self, label: str | Required) -> str:
        if label is not_provided:
            raise ValueError("The 'label' argument is required")

        return cast(str, label)

    def _check_alias(self, alias: str | EmptyStr, label: str) -> str:
        if alias is empty:
            alias = self._generate_alias(label)

        return cast(str, alias)

    @override
    def _contribute_to_diagram(self) -> None:
        self._check_diagram_type()
        self._diagram.add(self)

    def uses(
        self,
        other: Element,
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
            from_element=self,
            to_element=other,
            label=label,
            **kwargs,
        )

    def used_by(
        self,
        other: Element,
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
            from_element=other,
            to_element=self,
            label=label,
            **kwargs,
        )

    def _generate_alias(self, label: str) -> str:
        return current_diagram().generate_alias(label=label)

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

        if self.sprite:
            attrs.append(f"sprite={self.sprite!r}")

        if self.type:
            attrs.append(f"type_={self.type!r}")

        if self.tags:
            attrs.append(f"tags={self.tags!r}")

        if self.link:
            attrs.append(f"link={self.link!r}")

        if self.technology:
            attrs.append(f"technology={self.technology!r}")

        if self.base_shape:
            attrs.append(f"base_shape={self.base_shape!r}")

        attrs.append(f"alias={self.alias!r}")

        args = ", ".join(attrs)
        return f"{cls_name}({args})"


class ElementWithTechnology(Element):
    """
    Base class for elements that define a `technology` field.
    """

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        technology: str = "",
        sprite: str = "",
        tags: list[str] | None = None,
        link: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize a new diagram element.

        Args:
            label: Display name for the element. Required.
            description: Optional description text.
            technology: Optional technology.
            sprite: Optional sprite/icon reference for rendering.
            tags: Optional tags for styling or grouping.
            link: Optional URL associated with the element.
            alias: Unique identifier for the element. If not provided, it is
                autogenerated from the label.
        """
        super().__init__(
            alias=alias,
            label=label,
            description=description,
            sprite=sprite,
            tags=tags,
            link=link,
        )

        self.technology = technology


class Boundary(Element):
    """
    Represents a boundary element that groups other elements.

    Boundaries can be nested, and manage their own child elements.
    """

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        type_: str = "",
        tags: list[str] | None = None,
        link: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize a new boundary element.

        Args:
            label: Human-readable name for the boundary. Required.
            description: Optional description.
            type_: Optional stereotype or visual marker.
            tags: Optional tags for styling or grouping.
            link: Optional hyperlink associated with the boundary.
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
            type_=type_,
            tags=tags,
            link=link,
        )

        self._elements: list[Element] = []
        self._relationships: list[Relationship] = []
        self._boundaries: list[Boundary] = []

    @override
    def _contribute_to_diagram(self) -> None:
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

    def add(self, element: _TElement) -> _TElement:
        """
        Add a diagram element to this boundary.

        Args:
            element: The element to add.

        Returns:
            The added element.
        """
        self._elements.append(element)

        return element

    def add_boundary(self, boundary: _TBoundary) -> _TBoundary:
        """
        Add a nested boundary to this boundary.

        Args:
            boundary: The boundary to add.

        Returns:
            The added boundary.
        """
        self._boundaries.append(boundary)

        return boundary

    def add_relationship(self, relationship: _TRelationship) -> _TRelationship:
        """
        Add a relationship between elements.

        Args:
            relationship: The relationship to add.

        Returns:
            The added relationship.
        """
        self._relationships.append(relationship)

        return relationship


_TBoundary = TypeVar("_TBoundary", bound=Boundary)


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
        self._layouts: list[Layout] = []
        self._base_elements: list[BaseDiagramElement] = []
        self._render_options = render_options

        self.__elements_by_alias: dict[str, Element] = {}
        self.__elements_by_label: dict[str, list[Element]] = {}
        self.__alias_generator = AliasGenerator()
        self.__referenced_elements: list[str] = []

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
        alias = element.alias

        if existing_element := self.get_element_by_alias(alias):
            raise ValueError(f"Duplicated alias {alias!r}: {existing_element}.")

        if not alias.isidentifier():
            raise ValueError(
                f"Alias {alias!r} of {element} must be a valid identifier."
            )

        self.__elements_by_alias[alias] = element

    def _check_label(self, element: Element) -> None:
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
    def base_elements(self) -> list[BaseDiagramElement]:
        """
        Returns a list of base elements of the diagram that should be rendered
        in a strict order.
        """
        return self._base_elements

    @property
    def boundaries(self) -> list[Boundary]:
        """
        Returns all top-level boundaries in the diagram.
        """
        return self._boundaries

    @property
    def layouts(self) -> list[Layout]:
        """
        Returns all layout constraints defined for the diagram.
        """
        return self._layouts

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
    ) -> str:
        """
        Generate a unique alias.

        Args:
            label: Source label used to derive the alias when `alias` is None.
            alias: Optional explicit alias. If provided, it must be unique.

        Returns:
            A unique alias string.

        Raises:
            ValueError: If alias already exists.
        """
        return self.__alias_generator.generate(label, alias)

    def add_base_element(
        self, element: BaseDiagramElement
    ) -> BaseDiagramElement:
        """
        Add a base element to the diagram.

        rgs:
            element: The base element to add.

        Returns:
            The added base element.
        """
        self._base_elements.append(element)

        return element

    def add(self, element: _TElement) -> _TElement:
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

        return element

    def add_boundary(self, boundary: _TBoundary) -> _TBoundary:
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

        return boundary

    def add_relationship(self, relationship: _TRelationship) -> _TRelationship:
        """
        Add a relationship between elements.

        Args:
            relationship: The relationship to add.

        Returns:
            The added relationship.
        """
        self.__referenced_elements.append(relationship.from_element.alias)  # type: ignore[union-attr]
        self.__referenced_elements.append(relationship.to_element.alias)  # type: ignore[union-attr]

        if boundary := get_boundary():
            boundary.add_relationship(relationship)
        else:
            self._relationships.append(relationship)

        return relationship

    def add_layout(self, layout: _TLayout) -> _TLayout:
        """
        Add a layout constraint between elements.

        Args:
            layout: The layout constraint to add.

        Returns:
            The added layout.
        """
        self.__referenced_elements.append(layout.from_element.alias)
        self.__referenced_elements.append(layout.to_element.alias)

        self._layouts.append(layout)

        return layout

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

    @property
    def render_options(self) -> RenderOptions | None:
        """Return rendering options for the diagram."""
        return self._render_options

    @render_options.setter
    def render_options(self, render_options: RenderOptions) -> None:
        """Set rendering options for the diagram."""
        self._render_options = render_options

    def _build_plantuml_renderer(self, **kwargs: Any) -> PlantUMLRenderer:
        """
        Create and configure a `PlantUMLRenderer` instance.

        If diagram render options are set and include PlantUML-specific
        settings, they are applied as default `layout_options` unless
        explicitly provided in `kwargs`.

        Args:
            **kwargs: Additional keyword arguments passed directly to
                ``PlantUMLRenderer``.

        Returns:
            A configured `PlantUMLRenderer` instance.
        """
        from c4.renderers import PlantUMLRenderer

        if self._render_options and self._render_options.plantuml:
            kwargs.setdefault("layout_config", self._render_options.plantuml)

        return PlantUMLRenderer(**kwargs)


class Relationship(BaseDiagramElement):
    """
    Represents a connection between two elements.

    Supports fluent chaining using `>>` and `<<` operators, and
    subclass registration for each `RelationshipType`.
    """

    __relationship_by_type: ClassVar[
        dict[RelationshipType, type[Relationship]]
    ] = {}

    relationship_type: RelationshipType = RelationshipType.REL

    def __init__(
        self,
        label: str,
        description: str = "",
        technology: str = "",
        sprite: str = "",
        tags: list[str] | None = None,
        link: str = "",
        index: str | BaseIndex | None = None,
        from_element: Element | None = None,
        to_element: Element | None = None,
        relationship_type: RelationshipType | None = None,
    ) -> None:
        """
        Initialize a relationship between two elements.

        Args:
            label: The label shown on the relationship edge.
            description: Additional details about the relationship.
            technology: The technology used in the communication.
            sprite: Optional sprite to represent the relationship.
            tags: Optional tags for styling or grouping.
            link: URL link associated with the relationship.
            index: Index associated with the relationship.
            from_element: The source element. Optional.
            to_element: The destination element. Optional.
            relationship_type: Type of the relationship.
                Defaults to the class-level `relationship_type`.

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
        self.sprite = sprite
        self.tags = tags or []
        self.link = link
        self.index = index

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

    def get_participants(self) -> tuple[Element, Element]:
        if not self.from_element:
            raise ValueError("from_element not provided")

        if not self.to_element:
            raise ValueError("to_element not provided")

        return self.from_element, self.to_element

    def __rshift__(
        self, other: Element | list[Element]
    ) -> Relationship | list[Relationship]:
        """Implements Self >> Element and Self >> [Element]."""
        self._ensure_not_completed()

        return self._connect(source=self.from_element, destination=other)

    def __lshift__(
        self, other: Element | list[Element]
    ) -> Relationship | list[Relationship]:
        """Implements Self << Element and Self << [Element]."""
        self._ensure_not_completed()

        return self._connect(source=other, destination=self.to_element)

    def __rrshift__(
        self, other: Element | list[Element]
    ) -> Relationship | list[Relationship]:
        """Called for [Element] >> Self or Element >> Self."""
        self._ensure_not_completed()

        return self._connect(source=other, destination=self.to_element)

    def __rlshift__(
        self, other: Element | list[Element]
    ) -> Relationship | list[Relationship]:
        """Called for [Element] << Self or Element << Self."""
        self._ensure_not_completed()

        return self._connect(source=self.from_element, destination=other)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        attrs = [
            f"{self.label!r}",
        ]

        if self.description:
            attrs.append(f"{self.description!r}")

        repr_attrs = [
            "technology",
            "sprite",
            "tags",
            "link",
            "index",
        ]

        for attr in repr_attrs:
            value = getattr(self, attr)
            if value:
                attrs.append(f"{attr}={value!r}")

        args = ", ".join(attrs)
        return f"{cls_name}({args})"

    def _connect(
        self,
        source: Element | list[Element] | None,
        destination: Element | list[Element] | None,
    ) -> Relationship | list[Relationship]:
        self._ensure_not_completed()

        if not source and not destination:
            raise ValueError("Either source or destination must be provided")

        if isinstance(source, list) and isinstance(destination, list):
            raise ValueError(  # noqa: TRY004
                "Either source or destination must be a single element"
            )

        if isinstance(source, list):
            from_iter = source
            to_iter: Iterable[Element] = repeat(destination)  # type: ignore[arg-type]
        elif isinstance(destination, list):
            from_iter: Iterable[Element] = repeat(source)  # type: ignore[no-redef]
            to_iter = destination
        else:
            # Both are single elements
            return self.copy(from_element=source, to_element=destination)

        return [
            self.copy(from_element=src, to_element=dst)
            for src, dst in zip(from_iter, to_iter, strict=False)
        ]

    def _ensure_not_completed(self) -> None:
        if self.from_element and self.to_element:
            raise ValueError(
                "Cannot modify relationship with both specified elements"
            )

    @override
    def _contribute_to_diagram(self) -> None:
        if self.from_element and self.to_element:
            self._diagram.add_relationship(self)

    def get_attrs(self) -> dict[str, Any]:
        """
        Returns a dictionary of all relationship attributes.
        """
        return {
            "from_element": self.from_element,
            "to_element": self.to_element,
            "label": self.label,
            "technology": self.technology,
            "description": self.description,
            "sprite": self.sprite,
            "tags": self.tags,
            "link": self.link,
            "index": self.index,
            "relationship_type": self.relationship_type,
        }

    def copy(self, **overrides: Any) -> Relationship:
        """
        Clone the relationship, optionally overriding fields.
        """
        attrs = {**self.get_attrs(), **overrides}

        cls = self.get_relationship_by_type(self.relationship_type)

        return cls(**attrs)

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


class Rel(Relationship):
    """A unidirectional relationship between two elements."""

    relationship_type: RelationshipType = RelationshipType.REL


class BiRel(Relationship):
    """A bidirectional relationship between two elements."""

    relationship_type = RelationshipType.BI_REL


class RelBack(Relationship):
    """A unidirectional relationship pointing backward."""

    relationship_type = RelationshipType.REL_BACK


class RelNeighbor(Relationship):
    """
    A unidirectional relationship representing a lateral or
    neighboring interaction.
    """

    relationship_type = RelationshipType.REL_NEIGHBOR


class BiRelNeighbor(Relationship):
    """A bidirectional neighboring relationship between two elements."""

    relationship_type = RelationshipType.BI_REL_NEIGHBOR


class RelBackNeighbor(Relationship):
    """
    A unidirectional relationship combining backward and neighboring semantics.
    """

    relationship_type = RelationshipType.REL_BACK_NEIGHBOR


class RelD(Relationship):
    """A unidirectional downward relationship."""

    relationship_type = RelationshipType.REL_D


class RelDown(Relationship):
    """A unidirectional downward relationship."""

    relationship_type = RelationshipType.REL_DOWN


class BiRelD(Relationship):
    """A bidirectional downward relationship."""

    relationship_type = RelationshipType.BI_REL_D


class BiRelDown(Relationship):
    """A bidirectional downward relationship."""

    relationship_type = RelationshipType.BI_REL_DOWN


class RelU(Relationship):
    """A unidirectional upward relationship."""

    relationship_type = RelationshipType.REL_U


class RelUp(Relationship):
    """A unidirectional upward relationship."""

    relationship_type = RelationshipType.REL_UP


class BiRelU(Relationship):
    """A bidirectional upward relationship."""

    relationship_type = RelationshipType.BI_REL_U


class BiRelUp(Relationship):
    """A bidirectional upward relationship."""

    relationship_type = RelationshipType.BI_REL_UP


class RelL(Relationship):
    """A unidirectional leftward relationship."""

    relationship_type = RelationshipType.REL_L


class RelLeft(Relationship):
    """A unidirectional leftward relationship."""

    relationship_type = RelationshipType.REL_LEFT


class BiRelL(Relationship):
    """A bidirectional leftward relationship."""

    relationship_type = RelationshipType.BI_REL_L


class BiRelLeft(Relationship):
    """A bidirectional leftward relationship."""

    relationship_type = RelationshipType.BI_REL_LEFT


class RelR(Relationship):
    """A unidirectional rightward relationship."""

    relationship_type = RelationshipType.REL_R


class RelRight(Relationship):
    """A unidirectional rightward relationship."""

    relationship_type = RelationshipType.REL_RIGHT


class BiRelR(Relationship):
    """A bidirectional rightward relationship."""

    relationship_type = RelationshipType.BI_REL_R


class BiRelRight(Relationship):
    """A bidirectional rightward relationship."""

    relationship_type = RelationshipType.BI_REL_RIGHT


class Layout(BaseDiagramElement, abc.ABC):
    """
    Represents a relative layout constraint between two elements.
    """

    layout_type: LayoutType

    __layout_by_type: ClassVar[dict[LayoutType, type[Layout]]] = {}

    def __init__(
        self,
        from_element: Element,
        to_element: Element,
    ) -> None:
        """
        Initialize a layout constraint between two elements.

        Args:
            from_element: The element to be positioned.
            to_element: The element to position relative to.

        Raises:
            ValueError: If `layout_type` is not provided and the subclass
                does not define a class-level ``layout_type``.
        """
        self.from_element = from_element
        self.to_element = to_element

        if not hasattr(self, "layout_type"):
            raise ValueError(
                "`layout_type` must be provided explicitly or defined as "
                "a class attribute"
            )

        super().__init__()

    @override
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """
        Registers the layout subclass under its unique
        `layout_type`.
        """
        super().__init_subclass__(*args, **kwargs)

        layout_type = getattr(cls, "layout_type", None)
        if layout_type is None or layout_type in cls.__layout_by_type:
            raise TypeError(
                f"Please provide an unique `layout_type` for this"
                f" class {cls.__name__}"
            )

        cls.__layout_by_type[layout_type] = cls

    @override
    def _contribute_to_diagram(self) -> None:
        self._diagram.add_layout(self)

    def __repr__(self) -> str:
        cls_name = self.__class__.__name__
        from_ = self.from_element.alias
        to_ = self.to_element.alias

        return f"{cls_name}({from_}, {to_})"

    @classmethod
    def get_layout_by_type(cls, layout_type: LayoutType) -> type[Layout]:
        """
        Retrieve the layout class associated with the
        given LayoutType.

        Args:
            layout_type: The enum value representing the
                type of layout.

        Returns:
            The corresponding Layout subclass.

        Raises:
            KeyError: If no class is registered for the provided
                layout type.
        """
        return cls.__layout_by_type[layout_type]


class LayD(Layout):
    """
    Positions `from_element` below `to_element` using shorthand 'Lay_D' layout.
    """

    layout_type = LayoutType.LAY_D


class LayDown(Layout):
    """
    Positions `from_element` explicitly below `to_element`
    using 'Lay_Down' layout.
    """

    layout_type = LayoutType.LAY_DOWN


class LayU(Layout):
    """
    Positions `from_element` above `to_element` using shorthand 'Lay_U' layout.
    """

    layout_type = LayoutType.LAY_U


class LayUp(Layout):
    """
    Positions `from_element` explicitly above `to_element`
    using 'Lay_Up' layout.
    """

    layout_type = LayoutType.LAY_UP


class LayR(Layout):
    """
    Positions `from_element` to the right of `to_element`
    using shorthand 'Lay_R' layout.
    """

    layout_type = LayoutType.LAY_R


class LayRight(Layout):
    """
    Positions `from_element` explicitly to the right of `to_element`
    using 'Lay_Right' layout.
    """

    layout_type = LayoutType.LAY_RIGHT


class LayL(Layout):
    """
    Positions `from_element` to the left of `to_element`
    using shorthand 'Lay_L' layout.
    """

    layout_type = LayoutType.LAY_L


class LayLeft(Layout):
    """
    Positions `from_element` explicitly to the left of `to_element`
    using 'Lay_Left' layout.
    """

    layout_type = LayoutType.LAY_LEFT


_TDiagram = TypeVar("_TDiagram", bound=Diagram)
_TRelationship = TypeVar("_TRelationship", bound=Relationship)
_TElement = TypeVar("_TElement", bound=Element)
_TLayout = TypeVar("_TLayout", bound=Layout)

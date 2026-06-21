from __future__ import annotations

import abc
from typing import Any, ClassVar, Final

from typing_extensions import Self, override

from c4.contrib.plantuml.enums import LayoutType
from c4.diagrams.core.components import BaseDiagramElement, Element
from c4.diagrams.core.enums import DiagramType
from c4.diagrams.deployment import DeploymentNode as _DeploymentNode
from c4.enums import RendererEnum

ALLOWED_RENDERERS: Final = (RendererEnum.PLANTUML,)

AllowedDiagramTypes = tuple[DiagramType, ...] | None


class DeploymentNodeLeft(_DeploymentNode):
    """
    Represents a deployment node aligned to the left in the diagram layout.

    Inherits both deployment semantics and directional positioning.
    """

    allowed_diagram_types: AllowedDiagramTypes = (
        DiagramType.DEPLOYMENT_DIAGRAM,
    )


class DeploymentNodeRight(_DeploymentNode):
    """
    Represents a deployment node aligned to the right in the diagram layout.

    Useful for organizing infrastructure visually with directional context.
    """

    allowed_diagram_types: AllowedDiagramTypes = (
        DiagramType.DEPLOYMENT_DIAGRAM,
    )


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
    allowed_renderers: tuple[RendererEnum, ...] | None = ALLOWED_RENDERERS

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
    allowed_renderers: tuple[RendererEnum, ...] | None = ALLOWED_RENDERERS

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


class Layout(BaseDiagramElement, abc.ABC):
    """
    Represents a relative layout constraint between two elements.
    """

    allowed_renderers: tuple[RendererEnum, ...] | None = ALLOWED_RENDERERS

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
        """Register this layout and mark both elements as referenced."""
        self._check_diagram_type()
        self._diagram.add_referenced_element(self.from_element)
        self._diagram.add_referenced_element(self.to_element)
        self._diagram.add_ordered_element(self)

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

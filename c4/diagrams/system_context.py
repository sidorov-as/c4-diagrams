from typing import ClassVar

from c4.diagrams.core import (
    Boundary,
    Diagram,
    DiagramType,
    Element,
    EmptyStr,
    Required,
    empty,
    not_provided,
)


class SystemContextDiagram(Diagram):
    """
    Represents a [C4 System Context Diagram](https://c4model.com/diagrams/system-context).
    """

    type: ClassVar[DiagramType] = DiagramType.SYSTEM_CONTEXT_DIAGRAM


class SystemLandscapeDiagram(Diagram):
    """
    Represents a [C4 System Landscape Diagram](https://c4model.com/diagrams/system-landscape).
    """

    type: ClassVar[DiagramType] = DiagramType.SYSTEM_LANDSCAPE_DIAGRAM


class Person(Element):
    """
    Represents a person (actor) interacting with the system.
    """


class PersonExt(Person):
    """
    Represents an external person (actor) interacting with the system.
    """


class System(Element):
    """
    Represents a software system in the C4 model.
    """

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        sprite: str = "",
        tags: list[str] | None = None,
        link: str = "",
        type_: str = "",
        base_shape: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize a software system element.

        Args:
            label: Human-readable name.
            description: Optional description for the system.
            sprite: Optional icon or sprite.
            tags: Optional tags for styling or grouping.
            link: Optional hyperlink associated with the element.
            type_: Custom type/stereotype string.
            base_shape: Optional override for visual shape.
            alias: Unique identifier for the system.
        """
        super().__init__(
            alias=alias,
            label=label,
            description=description,
            sprite=sprite,
            tags=tags,
            link=link,
            type_=type_,
        )

        self.base_shape = base_shape


class SystemDb(Element):
    """
    Represents a system database (storage-centric system) in the C4 model.
    """


class SystemQueue(Element):
    """
    Represents a message queue or streaming system in the C4 model.
    """


class SystemExt(System):
    """
    Represents an external system interacting with the system under
    consideration.
    """


class SystemDbExt(Element):
    """
    Represents an external system database.
    """


class SystemQueueExt(Element):
    """
    Represents an external system queue or messaging system.
    """


class EnterpriseBoundary(Boundary):
    """
    Represents an enterprise boundary in a system landscape or context diagram.

    Used to group systems and actors that belong to the same
    organizational unit.
    """

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        tags: list[str] | None = None,
        link: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize the enterprise boundary element.

        Args:
            label: Display name.
            description: Optional description.
            tags: Optional tags for styling or grouping.
            link: Optional hyperlink.
            alias: Unique identifier for the boundary.
        """
        super().__init__(
            label=label,
            alias=alias,
            description=description,
            tags=tags,
            link=link,
        )


class SystemBoundary(Boundary):
    """
    Represents the boundary around a specific system.

    Used to group containers or components that belong to a single system.
    """

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        tags: list[str] | None = None,
        link: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize the system boundary element.

        Args:
            label: Display name.
            description: Optional description.
            tags: Optional tags for styling or grouping.
            link: Optional hyperlink.
            alias: Unique identifier for the boundary.
        """
        super().__init__(
            label=label,
            alias=alias,
            description=description,
            tags=tags,
            link=link,
        )


__all__ = (
    "EnterpriseBoundary",
    "Person",
    "PersonExt",
    "System",
    "SystemBoundary",
    "SystemContextDiagram",
    "SystemDb",
    "SystemDbExt",
    "SystemExt",
    "SystemLandscapeDiagram",
    "SystemQueue",
    "SystemQueueExt",
)

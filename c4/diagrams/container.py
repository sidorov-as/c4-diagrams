from c4.diagrams.core import (
    Boundary,
    Diagram,
    Element,
    ElementWithTechnology,
    EmptyStr,
    Required,
    empty,
    not_provided,
)


class ContainerDiagram(Diagram):
    """
    Represents a [C4 Container diagram](https://c4model.com/diagrams/container).
    """


class Container(Element):
    """
    Represents an application or service container in a C4 Container diagram.

    A container can be a web application, API, worker, or any executable unit
    of deployment. It may optionally include technology and shape hints.
    """

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        technology: str = "",
        sprite: str = "",
        tags: str = "",
        link: str = "",
        base_shape: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize a container element.

        Args:
            label: Human-readable name of the container.
            description: Optional description of the container's purpose.
            technology: The technology stack used by the container.
            sprite: Optional sprite identifier for visual representation.
            tags: Comma-separated tags for filtering or styling.
            link: Optional URL for external documentation or navigation.
            base_shape: Optional base shape override for rendering.
            alias: Unique identifier for the container.
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
        self.base_shape = base_shape


class ContainerDb(ElementWithTechnology):
    """
    Represents a container specifically modeled as a database.
    """


class ContainerQueue(ElementWithTechnology):
    """
    Represents a container modeled as a message queue or event broker.
    """


class ContainerExt(Container):
    """
    Represents an external container (outside the system boundary).
    """


class ContainerDbExt(ContainerDb):
    """
    Represents an external database container.
    """


class ContainerQueueExt(ContainerQueue):
    """
    Represents an external message queue or broker.
    """


class ContainerBoundary(Boundary):
    """
    Represents a boundary grouping containers within a system.
    """

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        tags: str = "",
        link: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize a container-level boundary.

        Args:
            label: Displayed label of the boundary. Defaults to `empty`.
            description: Optional human-readable description of the boundary.
            tags: Optional comma-separated tags for styling or filtering.
            link: URL associated with the boundary for navigation or
                documentation.
            alias: Unique identifier for the boundary.
        """
        super().__init__(
            alias=alias,
            label=label,
            description=description,
            tags=tags,
            link=link,
        )


__all__ = (
    "Container",
    "ContainerBoundary",
    "ContainerDb",
    "ContainerDbExt",
    "ContainerDiagram",
    "ContainerExt",
    "ContainerQueue",
    "ContainerQueueExt",
)

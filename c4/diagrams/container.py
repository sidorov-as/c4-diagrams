from typing import ClassVar

from c4.diagrams.core import (
    Boundary,
    Diagram,
    DiagramType,
    Element,
    ElementWithTechnology,
    EmptyStr,
    Required,
    empty,
    not_provided,
)

AllowedDiagramTypes = tuple[DiagramType, ...] | None


ALLOWED_DIAGRAM_TYPES: tuple[DiagramType, ...] = (
    DiagramType.CONTAINER_DIAGRAM,
    DiagramType.COMPONENT_DIAGRAM,
    DiagramType.DYNAMIC_DIAGRAM,
    DiagramType.DEPLOYMENT_DIAGRAM,
)


class ContainerDiagram(Diagram):
    """
    Represents a [C4 Container diagram](https://c4model.com/diagrams/container).
    """

    type: ClassVar[DiagramType] = DiagramType.CONTAINER_DIAGRAM


class Container(Element):
    """
    Represents an application or service container in a C4 Container diagram.

    A container can be a web application, API, worker, or any executable unit
    of deployment. It may optionally include technology and shape hints.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        technology: str = "",
        sprite: str = "",
        tags: list[str] | None = None,
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
            tags: Optional tags for styling or grouping.
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

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ContainerQueue(ElementWithTechnology):
    """
    Represents a container modeled as a message queue or event broker.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ContainerExt(Container):
    """
    Represents an external container (outside the system boundary).
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ContainerDbExt(ContainerDb):
    """
    Represents an external database container.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ContainerQueueExt(ContainerQueue):
    """
    Represents an external message queue or broker.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ContainerBoundary(Boundary):
    """
    Represents a boundary grouping containers within a system.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES

    def __init__(
        self,
        label: str | Required = not_provided,
        description: str = "",
        tags: list[str] | None = None,
        link: str = "",
        alias: str | EmptyStr = empty,
    ) -> None:
        """
        Initialize a container-level boundary.

        Args:
            label: Displayed label of the boundary. Defaults to `empty`.
            description: Optional human-readable description of the boundary.
            tags: Optional tags for styling or grouping.
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

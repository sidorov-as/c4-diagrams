from typing import ClassVar

from c4.diagrams.core import (
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
    DiagramType.COMPONENT_DIAGRAM,
    DiagramType.DYNAMIC_DIAGRAM,
    DiagramType.DEPLOYMENT_DIAGRAM,
)


class ComponentDiagram(Diagram):
    """
    Represents a [C4 Component diagram](https://c4model.com/diagrams/component).
    """

    type: ClassVar[DiagramType] = DiagramType.COMPONENT_DIAGRAM


class Component(Element):
    """
    Represents a software component within a container.

    A component is a logical unit (such as a class, module, or handler)
    that performs a specific function within a container. Includes metadata
    like technology, visual style, and links.
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
        Initialize a component element.

        Args:
            label: Human-readable name of the component.
            description: Optional description of the component's
                behavior or role.
            technology: Technology used to implement the component.
            sprite: Optional sprite for visual appearance in the diagram.
            tags: Optional tags for styling or grouping.
            link: Optional external link related to the component.
            base_shape: Optional shape override for rendering.
            alias: Unique identifier for the component.
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


class ComponentDb(ElementWithTechnology):
    """
    Represents a component modeled as a database.

    Used to depict data storage components in a component diagram.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ComponentQueue(ElementWithTechnology):
    """
    Represents a component modeled as a message queue.

    Useful for showing message-based or asynchronous communication paths.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ComponentExt(Component):
    """
    Represents an external component outside the container boundary.

    Commonly used to show third-party libraries or external system components.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ComponentDbExt(ComponentDb):
    """
    Represents an external database component.

    Used for visualizing data stores not maintained by the system.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class ComponentQueueExt(ComponentQueue):
    """
    Represents an external message queue or broker.

    Used to show external infrastructure for asynchronous communication.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


__all__ = (
    "Component",
    "ComponentDb",
    "ComponentDbExt",
    "ComponentDiagram",
    "ComponentExt",
    "ComponentQueue",
    "ComponentQueueExt",
)

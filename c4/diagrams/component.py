from c4.diagrams.core import (
    Diagram,
    Element,
    ElementWithTechnology,
    EmptyStr,
    Required,
    empty,
    not_provided,
)


class ComponentDiagram(Diagram):
    """
    Represents a [C4 Component diagram](https://c4model.com/diagrams/component).
    """


class Component(Element):
    """
    Represents a software component within a container.

    A component is a logical unit (such as a class, module, or handler)
    that performs a specific function within a container. Includes metadata
    like technology, visual style, and links.
    """

    def __init__(
        self,
        alias: str | EmptyStr = empty,
        label: str | Required = not_provided,
        technology: str = "",
        description: str = "",
        sprite: str = "",
        tags: str = "",
        link: str = "",
        base_shape: str = "",
    ) -> None:
        """
        Initialize a component element.

        Args:
            alias: Unique identifier for the component.
            label: Human-readable name of the component.
            technology: Technology used to implement the component.
            description: Optional description of the component's
                behavior or role.
            sprite: Optional sprite for visual appearance in the diagram.
            tags: Comma-separated tags for filtering or styling.
            link: Optional external link related to the component.
            base_shape: Optional shape override for rendering.
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


class ComponentQueue(ElementWithTechnology):
    """
    Represents a component modeled as a message queue.

    Useful for showing message-based or asynchronous communication paths.
    """


class ComponentExt(Component):
    """
    Represents an external component outside the container boundary.

    Commonly used to show third-party libraries or external system components.
    """


class ComponentDbExt(ComponentDb):
    """
    Represents an external database component.

    Used for visualizing data stores not maintained by the system.
    """


class ComponentQueueExt(ComponentQueue):
    """
    Represents an external message queue or broker.

    Used to show external infrastructure for asynchronous communication.
    """


__all__ = (
    "Component",
    "ComponentDb",
    "ComponentDbExt",
    "ComponentDiagram",
    "ComponentExt",
    "ComponentQueue",
    "ComponentQueueExt",
)

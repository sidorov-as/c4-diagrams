from __future__ import annotations

from c4.diagrams.core import (
    Boundary,
    Diagram,
    EmptyStr,
    Required,
    empty,
    not_provided,
)


class DeploymentDiagram(Diagram):
    """
    Represents a [C4 Deployment Diagram](https://c4model.com/diagrams/deployment).

    A deployment diagram shows how software systems and containers are
    mapped onto infrastructure nodes, such as servers, devices,
    or cloud services.
    """


class Node(Boundary):
    """
    Represents a deployment node in the C4 model.

    A Node is a container for deployment elements and can optionally include
    a sprite for visual representation (e.g., server icon, cloud logo).

    Nodes can be nested, and manage their own child elements.
    """

    def __init__(
        self,
        alias: str | EmptyStr = empty,
        label: str | Required = not_provided,
        type_: str = "",
        description: str = "",
        sprite: str = "",
        tags: str = "",
        link: str = "",
    ) -> None:
        """
        Initialize a new Node element.

        Args:
            alias: Optional identifier for the node.
            label: Display label shown on the diagram.
            type_: Optional classifier for the node (e.g., "database").
            description: Optional description shown in the rendered diagram.
            sprite: Optional sprite name to visually represent the node.
            tags: Comma-separated list of tags for styling or filtering.
            link: Optional hyperlink associated with the node.
        """
        super().__init__(
            label=label,
            alias=alias,
            description=description,
            type_=type_,
            tags=tags,
            link=link,
        )

        self.sprite = sprite


class NodeLeft(Node):
    """
    Represents a deployment node aligned to the left in the diagram layout.

    Typically used for directional positioning in deployment views.
    """


class NodeRight(Node):
    """
    Represents a deployment node aligned to the right in the diagram layout.

    Useful for controlling horizontal positioning in deployment diagrams.
    """


class DeploymentNode(Node):
    """
    Represents a deployment-specific node in the C4 model.

    Used to group containers or systems that are deployed together on a
    specific machine or environment (e.g., EC2 instance, on-prem server).
    """


class DeploymentNodeLeft(DeploymentNode):
    """
    Represents a deployment node aligned to the left in the diagram layout.

    Inherits both deployment semantics and directional positioning.
    """


class DeploymentNodeRight(DeploymentNode):
    """
    Represents a deployment node aligned to the right in the diagram layout.

    Useful for organizing infrastructure visually with directional context.
    """


__all__ = (
    "DeploymentDiagram",
    "DeploymentNode",
    "DeploymentNodeLeft",
    "DeploymentNodeRight",
    "Node",
    "NodeLeft",
    "NodeRight",
)

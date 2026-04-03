from __future__ import annotations

from typing import ClassVar

from c4.diagrams.core import (
    MISSING,
    REQUIRED,
    Boundary,
    Diagram,
    DiagramType,
    Maybe,
    Required,
)

AllowedDiagramTypes = tuple[DiagramType, ...] | None


ALLOWED_DIAGRAM_TYPES: tuple[DiagramType, ...] = (
    DiagramType.DEPLOYMENT_DIAGRAM,
)


class DeploymentDiagram(Diagram):
    """
    Represents a [C4 Deployment Diagram](https://c4model.com/diagrams/deployment).

    A deployment diagram shows how software systems and containers are
    mapped onto infrastructure nodes, such as servers, devices,
    or cloud services.
    """

    type: ClassVar[DiagramType] = DiagramType.DEPLOYMENT_DIAGRAM


class Node(Boundary):
    """
    Represents a deployment node in the C4 model.

    A Node is a container for deployment elements and can optionally include
    a sprite for visual representation (e.g., server icon, cloud logo).

    Nodes can be nested, and manage their own child elements.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES

    def __init__(
        self,
        label: Required[str] = REQUIRED,
        description: str | None = None,
        type_: str | None = None,
        sprite: str | None = None,
        tags: list[str] | None = None,
        link: str | None = None,
        alias: Maybe[str] = MISSING,
    ) -> None:
        """
        Initialize a new Node element.

        Args:
            label: Display label shown on the diagram.
            description: Optional description shown in the rendered diagram.
            type_: Optional classifier for the node (e.g., "database").
            sprite: Optional sprite name to visually represent the node.
            tags: Optional tags for styling or grouping.
            link: Optional hyperlink associated with the node.
            alias: Optional identifier for the node.
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

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class NodeRight(Node):
    """
    Represents a deployment node aligned to the right in the diagram layout.

    Useful for controlling horizontal positioning in deployment diagrams.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class DeploymentNode(Node):
    """
    Represents a deployment-specific node in the C4 model.

    Used to group containers or systems that are deployed together on a
    specific machine or environment (e.g., EC2 instance, on-prem server).
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class DeploymentNodeLeft(DeploymentNode):
    """
    Represents a deployment node aligned to the left in the diagram layout.

    Inherits both deployment semantics and directional positioning.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


class DeploymentNodeRight(DeploymentNode):
    """
    Represents a deployment node aligned to the right in the diagram layout.

    Useful for organizing infrastructure visually with directional context.
    """

    allowed_diagram_types: AllowedDiagramTypes = ALLOWED_DIAGRAM_TYPES


__all__ = (
    "DeploymentDiagram",
    "DeploymentNode",
    "DeploymentNodeLeft",
    "DeploymentNodeRight",
    "Node",
    "NodeLeft",
    "NodeRight",
)

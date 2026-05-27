from c4.diagrams.core import DiagramType
from c4.diagrams.deployment import Node as _Node

AllowedDiagramTypes = tuple[DiagramType, ...] | None


class NodeLeft(_Node):
    """
    Represents a deployment node aligned to the left in the diagram layout.

    Typically used for directional positioning in deployment views.
    """

    allowed_diagram_types: AllowedDiagramTypes = (
        DiagramType.DEPLOYMENT_DIAGRAM,
    )


class NodeRight(_Node):
    """
    Represents a deployment node aligned to the right in the diagram layout.

    Useful for controlling horizontal positioning in deployment diagrams.
    """

    allowed_diagram_types: AllowedDiagramTypes = (
        DiagramType.DEPLOYMENT_DIAGRAM,
    )


__all__ = (
    "NodeLeft",
    "NodeRight",
)

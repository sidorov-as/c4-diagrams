from __future__ import annotations

from typing import ClassVar

from c4.diagrams.core import (
    Diagram,
    DiagramType,
)


class DynamicDiagram(Diagram):
    """
    Represents a [C4 Dynamic diagram](https://c4model.com/diagrams/dynamic).
    """

    type: ClassVar[DiagramType] = DiagramType.DYNAMIC_DIAGRAM

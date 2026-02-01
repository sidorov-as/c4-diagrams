from __future__ import annotations

from typing_extensions import override

from c4.diagrams.core import (
    Diagram,
    _TRelationship,
)


class DynamicDiagram(Diagram):
    """
    Represents a [C4 Dynamic diagram](https://c4model.com/diagrams/dynamic).
    """

    @override
    def add_relationship(self, relationship: _TRelationship) -> _TRelationship:
        """
        Add a relationship between elements.

        In dynamic diagrams, relationships are added as base elements
        to enforce the required rendering order.

        Args:
            relationship: The relationship to add.

        Returns:
            The added relationship.
        """
        self.add_base_element(relationship)

        return relationship

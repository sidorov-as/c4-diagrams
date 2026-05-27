from c4.diagrams.core.components import Relationship
from c4.diagrams.core.enums import RelationshipType


class Rel(Relationship):
    """A unidirectional relationship between two elements."""

    relationship_type: RelationshipType = RelationshipType.REL


__all__ = (
    "Rel",
    "Relationship",
)

from c4.diagrams.core.components import Relationship
from c4.diagrams.core.enums import RelationshipType


class Rel(Relationship):
    """
    A unidirectional relationship between two elements.

    Use it as `a >> Rel("label", technology="HTTPS") >> b`. The first
    argument is the `label`; the second positional argument is the
    `description`, so pass `technology` and other options by name. A
    relationship written as `a >> b` has no label (`None`); set it with
    `a >> b | "label"`. PlantUML and Mermaid write the
    `default_relationship_label` placeholder for an unlabeled relationship.
    """

    relationship_type: RelationshipType = RelationshipType.REL


__all__ = (
    "Rel",
    "Relationship",
)

from c4.diagrams.core.components import Relationship
from c4.diagrams.core.enums import RelationshipType


class BiRel(Relationship):
    """A bidirectional relationship between two elements."""

    relationship_type = RelationshipType.BI_REL


class RelBack(Relationship):
    """A unidirectional relationship pointing backward."""

    relationship_type = RelationshipType.REL_BACK


class RelNeighbor(Relationship):
    """
    A unidirectional relationship representing a lateral or
    neighboring interaction.
    """

    relationship_type = RelationshipType.REL_NEIGHBOR


class BiRelNeighbor(Relationship):
    """A bidirectional neighboring relationship between two elements."""

    relationship_type = RelationshipType.BI_REL_NEIGHBOR


class RelBackNeighbor(Relationship):
    """
    A unidirectional relationship combining backward and neighboring semantics.
    """

    relationship_type = RelationshipType.REL_BACK_NEIGHBOR


class RelD(Relationship):
    """A unidirectional downward relationship."""

    relationship_type = RelationshipType.REL_D


class RelDown(Relationship):
    """A unidirectional downward relationship."""

    relationship_type = RelationshipType.REL_DOWN


class BiRelD(Relationship):
    """A bidirectional downward relationship."""

    relationship_type = RelationshipType.BI_REL_D


class BiRelDown(Relationship):
    """A bidirectional downward relationship."""

    relationship_type = RelationshipType.BI_REL_DOWN


class RelU(Relationship):
    """A unidirectional upward relationship."""

    relationship_type = RelationshipType.REL_U


class RelUp(Relationship):
    """A unidirectional upward relationship."""

    relationship_type = RelationshipType.REL_UP


class BiRelU(Relationship):
    """A bidirectional upward relationship."""

    relationship_type = RelationshipType.BI_REL_U


class BiRelUp(Relationship):
    """A bidirectional upward relationship."""

    relationship_type = RelationshipType.BI_REL_UP


class RelL(Relationship):
    """A unidirectional leftward relationship."""

    relationship_type = RelationshipType.REL_L


class RelLeft(Relationship):
    """A unidirectional leftward relationship."""

    relationship_type = RelationshipType.REL_LEFT


class BiRelL(Relationship):
    """A bidirectional leftward relationship."""

    relationship_type = RelationshipType.BI_REL_L


class BiRelLeft(Relationship):
    """A bidirectional leftward relationship."""

    relationship_type = RelationshipType.BI_REL_LEFT


class RelR(Relationship):
    """A unidirectional rightward relationship."""

    relationship_type = RelationshipType.REL_R


class RelRight(Relationship):
    """A unidirectional rightward relationship."""

    relationship_type = RelationshipType.REL_RIGHT


class BiRelR(Relationship):
    """A bidirectional rightward relationship."""

    relationship_type = RelationshipType.BI_REL_R


class BiRelRight(Relationship):
    """A bidirectional rightward relationship."""

    relationship_type = RelationshipType.BI_REL_RIGHT


__all__ = (
    "BiRel",
    "BiRelD",
    "BiRelDown",
    "BiRelL",
    "BiRelLeft",
    "BiRelNeighbor",
    "BiRelR",
    "BiRelRight",
    "BiRelU",
    "BiRelUp",
    "RelBack",
    "RelBackNeighbor",
    "RelD",
    "RelDown",
    "RelL",
    "RelLeft",
    "RelNeighbor",
    "RelR",
    "RelRight",
    "RelU",
    "RelUp",
)

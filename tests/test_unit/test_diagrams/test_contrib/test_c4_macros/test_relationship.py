import pytest

from c4.contrib import mermaid, plantuml
from c4.contrib.c4_macros import (
    BiRel,
    BiRelD,
    BiRelDown,
    BiRelL,
    BiRelLeft,
    BiRelNeighbor,
    BiRelR,
    BiRelRight,
    BiRelU,
    BiRelUp,
    RelBack,
    RelBackNeighbor,
    RelD,
    RelDown,
    RelL,
    RelLeft,
    RelNeighbor,
    RelR,
    RelRight,
    RelU,
    RelUp,
)
from c4.diagrams.core import Relationship, RelationshipType


@pytest.mark.parametrize(
    ("relationship_class", "expected_type"),
    [
        (BiRel, RelationshipType.BI_REL),
        (RelBack, RelationshipType.REL_BACK),
        (RelNeighbor, RelationshipType.REL_NEIGHBOR),
        (BiRelNeighbor, RelationshipType.BI_REL_NEIGHBOR),
        (RelBackNeighbor, RelationshipType.REL_BACK_NEIGHBOR),
        (RelD, RelationshipType.REL_D),
        (RelDown, RelationshipType.REL_DOWN),
        (BiRelD, RelationshipType.BI_REL_D),
        (BiRelDown, RelationshipType.BI_REL_DOWN),
        (RelU, RelationshipType.REL_U),
        (RelUp, RelationshipType.REL_UP),
        (BiRelU, RelationshipType.BI_REL_U),
        (BiRelUp, RelationshipType.BI_REL_UP),
        (RelL, RelationshipType.REL_L),
        (RelLeft, RelationshipType.REL_LEFT),
        (BiRelL, RelationshipType.BI_REL_L),
        (BiRelLeft, RelationshipType.BI_REL_LEFT),
        (RelR, RelationshipType.REL_R),
        (RelRight, RelationshipType.REL_RIGHT),
        (BiRelR, RelationshipType.BI_REL_R),
        (BiRelRight, RelationshipType.BI_REL_RIGHT),
    ],
)
def test_c4_macro_relationship_type(
    relationship_class: type[Relationship],
    expected_type: RelationshipType,
):
    assert relationship_class.relationship_type == expected_type


@pytest.mark.parametrize(
    ("expected_class", "relationship_type"),
    [
        (BiRel, RelationshipType.BI_REL),
        (RelBack, RelationshipType.REL_BACK),
        (RelNeighbor, RelationshipType.REL_NEIGHBOR),
        (BiRelNeighbor, RelationshipType.BI_REL_NEIGHBOR),
        (RelBackNeighbor, RelationshipType.REL_BACK_NEIGHBOR),
        (RelD, RelationshipType.REL_D),
        (RelDown, RelationshipType.REL_DOWN),
        (BiRelD, RelationshipType.BI_REL_D),
        (BiRelDown, RelationshipType.BI_REL_DOWN),
        (RelU, RelationshipType.REL_U),
        (RelUp, RelationshipType.REL_UP),
        (BiRelU, RelationshipType.BI_REL_U),
        (BiRelUp, RelationshipType.BI_REL_UP),
        (RelL, RelationshipType.REL_L),
        (RelLeft, RelationshipType.REL_LEFT),
        (BiRelL, RelationshipType.BI_REL_L),
        (BiRelLeft, RelationshipType.BI_REL_LEFT),
        (RelR, RelationshipType.REL_R),
        (RelRight, RelationshipType.REL_RIGHT),
        (BiRelR, RelationshipType.BI_REL_R),
        (BiRelRight, RelationshipType.BI_REL_RIGHT),
    ],
)
def test_c4_macro_relationship_by_type(
    expected_class: type[Relationship],
    relationship_type: RelationshipType,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )

    assert relationship_class == expected_class


@pytest.mark.parametrize(
    "relationship_name",
    [
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
    ],
)
def test_c4_macro_relationships_are_re_exported_by_backend_contribs(
    relationship_name: str,
):
    assert getattr(mermaid, relationship_name) is getattr(
        plantuml, relationship_name
    )

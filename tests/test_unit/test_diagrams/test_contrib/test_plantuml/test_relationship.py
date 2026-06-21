import pytest

from c4.contrib.plantuml import Index
from c4.diagrams.core import Diagram, Element, Relationship, RelationshipType


@pytest.mark.parametrize(
    "index",
    [Index(1), f"{Index()}-2"],
    ids=["index-object", "relative-index"],
)
def test_relationship_attrs_accepts_plantuml_index(index: str):
    attrs = {
        "label": "example",
        "technology": "technology",
        "description": "Description",
        "extensions": {
            "plantuml": {
                "sprite": "$sprite",
                "tags": ["tag1", "tag2"],
                "link": "https://example.com",
                "index": index,
            }
        },
        "relationship_type": RelationshipType.BI_REL,
    }

    with Diagram():
        from_element = Element(label="from")
        to_element = Element(label="to")

        attrs["from_element"] = from_element
        attrs["to_element"] = to_element

        relationship = Relationship(**attrs)

    assert relationship.from_element == attrs["from_element"]
    assert relationship.to_element == attrs["to_element"]
    assert relationship.label == attrs["label"]
    assert relationship.technology == attrs["technology"]
    assert relationship.description == attrs["description"]
    assert relationship.extensions == attrs["extensions"]
    assert relationship.relationship_type == attrs["relationship_type"]
    assert relationship.get_attrs() == attrs

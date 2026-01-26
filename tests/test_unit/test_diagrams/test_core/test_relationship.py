import pytest

from c4.diagrams.core import (
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
    Diagram,
    Element,
    Index,
    Rel,
    Relationship,
    RelationshipType,
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


@pytest.fixture()
def diagram():
    with Diagram() as _diagram:
        yield _diagram


def test_create_relationship_outside_the_diagram_context():
    expected_error = "Element must be created within a diagram context"

    with pytest.raises(ValueError, match=expected_error):
        Relationship(label="example")


def test_create_empty_relationship():
    with Diagram() as diagram:
        Relationship(label="example")

    assert not diagram.relationships


def test_create_relationship_without_to_element():
    with Diagram() as diagram:
        element = Element(label="elem")
        Relationship(label="example", from_element=element)

    assert not diagram.relationships


def test_create_relationship_without_from_element():
    with Diagram() as diagram:
        element = Element(label="elem")
        Relationship(label="example", to_element=element)

    assert not diagram.relationships


def test_create_relationship_with_elements():
    with Diagram() as diagram:
        from_element = Element(label="from")
        to_element = Element(label="to")
        relationship = Relationship(
            label="example",
            from_element=from_element,
            to_element=to_element,
        )

    assert diagram.relationships == [relationship]
    assert relationship.from_element == from_element
    assert relationship.to_element == to_element
    assert relationship.label == "example"
    assert relationship.technology == ""
    assert relationship.description == ""
    assert relationship.sprite == ""
    assert relationship.tags == ""
    assert relationship.link == ""
    assert relationship.index is None
    assert relationship.relationship_type == RelationshipType.REL


@pytest.mark.parametrize(
    "index",
    ["1", Index(1), f"{Index()}-2"],
    ids=["str", "index-object", "relative-index"],
)
def test_relationship_attrs(index: str):
    attrs = {
        "label": "example",
        "technology": "technology",
        "description": "Description",
        "sprite": "$sprite",
        "tags": "tag1,tag2",
        "link": "https://example.com",
        "index": index,
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
    assert relationship.sprite == attrs["sprite"]
    assert relationship.tags == attrs["tags"]
    assert relationship.link == attrs["link"]
    assert relationship.index == attrs["index"]
    assert relationship.relationship_type == attrs["relationship_type"]
    assert relationship.get_attrs() == attrs


def test_copy_relationship(diagram: Diagram):
    attrs = {
        "label": "example",
        "technology": "technology",
        "description": "Description",
        "sprite": "$sprite",
        "tags": "tag1,tag2",
        "link": "https://example.com",
        "index": "1",
        "relationship_type": RelationshipType.BI_REL,
        "from_element": Element(label="from"),
        "to_element": Element(label="to"),
    }
    relationship = Relationship(**attrs)

    relationship_copy = relationship.copy(
        relationship_type=RelationshipType.REL_BACK
    )

    assert relationship_copy.from_element == relationship.from_element
    assert relationship_copy.to_element == relationship.to_element
    assert relationship_copy.label == relationship.label
    assert relationship_copy.technology == relationship.technology
    assert relationship_copy.description == relationship.description
    assert relationship_copy.sprite == relationship.sprite
    assert relationship_copy.tags == relationship.tags
    assert relationship_copy.link == relationship.link
    assert relationship_copy.index == relationship.index
    assert relationship_copy.relationship_type == RelationshipType.REL_BACK


@pytest.mark.parametrize(
    ("relationship_class", "expected_type"),
    [
        (Relationship, RelationshipType.REL),
        (Rel, RelationshipType.REL),
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
def test_relationship_type(
    relationship_class: type[Relationship],
    expected_type: RelationshipType,
):
    assert relationship_class.relationship_type == expected_type


@pytest.mark.parametrize(
    ("expected_class", "relationship_type"),
    [
        (Rel, RelationshipType.REL),
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
def test_relationship_by_type(
    expected_class: type[Relationship],
    relationship_type: RelationshipType,
):
    relationship_class = Relationship.get_relationship_by_type(
        relationship_type
    )

    assert relationship_class == expected_class


def test_relationship_init_subclass_empty_type():
    expected_error = (
        "Please provide an unique `relationship_type` for this"
        " class TestRelationship"
    )

    with pytest.raises(TypeError, match=expected_error):

        class TestRelationship(Relationship): ...


def test_relationship_init_subclass_duplicated_type():
    expected_error = (
        "Please provide an unique `relationship_type` for this"
        " class TestRelationship"
    )

    with pytest.raises(TypeError, match=expected_error):

        class TestRelationship(Relationship):
            relationship_type = RelationshipType.REL


def test_relationship_one_to_one(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = frontend >> Rel("Uses", "JSON/HTTPS") >> backend

    assert len(diagram.relationships) == 1
    assert isinstance(result, Relationship)
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"


def test_relationship_one_to_one_already_completed_error(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")
    relationship = frontend >> Rel("Uses", "JSON/HTTPS") >> backend
    expected_error = "Cannot modify relationship with both specified elements"

    with pytest.raises(ValueError, match=expected_error):
        Element("e1", "Element 1") >> relationship >> Element("e2", "Element 2")


def test_relationship_one_to_one_reversed(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = backend << Rel("Uses", "JSON/HTTPS") << frontend

    assert len(diagram.relationships) == 1
    assert isinstance(result, Relationship)
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"


def test_relationship_one_to_one_reversed_already_completed_error(
    diagram: Diagram,
):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")
    relationship = backend << Rel("Uses", "JSON/HTTPS") << frontend

    expected_error = "Cannot modify relationship with both specified elements"

    with pytest.raises(ValueError, match=expected_error):
        Element("e1", "Element 1") >> relationship >> Element("e2", "Element 2")


def test_relationship_one_to_one_label_only(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = frontend >> "Uses" >> backend

    assert len(diagram.relationships) == 1
    assert isinstance(result, Relationship)
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"


def test_relationship_one_to_one_label_only_already_completed_error(
    diagram: Diagram,
):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")
    relationship = frontend >> "Uses" >> backend

    expected_error = "Cannot modify relationship with both specified elements"

    with pytest.raises(ValueError, match=expected_error):
        Element("e1", "Element 1") >> relationship >> Element("e2", "Element 2")


def test_relationship_one_to_one_reversed_label_only(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = backend << "Uses" << frontend

    assert len(diagram.relationships) == 1
    assert isinstance(result, Relationship)
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"


def test_relationship_one_to_one_reversed_label_only_already_completed_error(
    diagram: Diagram,
):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")
    relationship = backend << "Uses" << frontend

    expected_error = "Cannot modify relationship with both specified elements"

    with pytest.raises(ValueError, match=expected_error):
        Element("e1", "Element 1") << relationship << Element("e2", "Element 2")


def test_relationship_one_to_one_label_only_via_pipe(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = frontend >> backend | "Uses"

    assert len(diagram.relationships) == 1
    assert isinstance(result, Relationship)
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"


def test_relationship_one_to_one_reversed_label_only_via_pipe(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = backend << frontend | "Uses"

    assert len(diagram.relationships) == 1
    assert isinstance(result, Relationship)
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"


def test_relationship_one_to_one_uses(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = frontend.uses(backend, "Uses", technology="JSON/HTTPS")

    assert len(diagram.relationships) == 1
    assert isinstance(result, Relationship)
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"
    assert diagram.relationships[0].relationship_type == RelationshipType.REL


def test_relationship_one_to_one_uses_with_rel(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = frontend.uses(
        backend,
        "Uses",
        RelationshipType.REL_BACK,
        technology="JSON/HTTPS",
    )

    assert len(diagram.relationships) == 1
    assert isinstance(result, Relationship)
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"
    assert (
        diagram.relationships[0].relationship_type == RelationshipType.REL_BACK
    )


def test_relationship_one_to_one_used_by(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = backend.used_by(frontend, "Uses", technology="JSON/HTTPS")

    assert len(diagram.relationships) == 1
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"
    assert diagram.relationships[0].relationship_type == RelationshipType.REL


def test_relationship_one_to_one_used_by_with_rel(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    backend = Element("backend", "API")

    result = backend.used_by(
        frontend,
        "Uses",
        RelationshipType.REL_BACK,
        technology="JSON/HTTPS",
    )

    assert len(diagram.relationships) == 1
    assert diagram.relationships[0] == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == backend
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"
    assert (
        diagram.relationships[0].relationship_type == RelationshipType.REL_BACK
    )


def test_relationship_one_to_many(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    auth_service = Element("auth", "Authorization Service")
    api_service = Element("api", "Backend API Service")

    result = (
        frontend >> Rel("Uses", "JSON/HTTPS") >> [auth_service, api_service]
    )

    assert len(diagram.relationships) == 2
    assert isinstance(result, list)
    assert diagram.relationships == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == auth_service
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"
    assert diagram.relationships[1].from_element == frontend
    assert diagram.relationships[1].to_element == api_service
    assert diagram.relationships[1].label == "Uses"
    assert diagram.relationships[1].technology == "JSON/HTTPS"


def test_relationship_one_to_many_reversed(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    auth_service = Element("auth", "Authorization Service")
    api_service = Element("api", "Backend API Service")

    result = (
        [auth_service, api_service] << Rel("Uses", "JSON/HTTPS") << frontend
    )

    assert len(diagram.relationships) == 2
    assert isinstance(result, list)
    assert diagram.relationships == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == auth_service
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"
    assert diagram.relationships[1].from_element == frontend
    assert diagram.relationships[1].to_element == api_service
    assert diagram.relationships[1].label == "Uses"
    assert diagram.relationships[1].technology == "JSON/HTTPS"


def test_relationship_many_to_one(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    mobile_app = Element("mobile", "Mobile app")
    api_service = Element("api", "Backend API Service")

    result = [frontend, mobile_app] >> Rel("Uses", "JSON/HTTPS") >> api_service

    assert len(diagram.relationships) == 2
    assert isinstance(result, list)
    assert diagram.relationships == result
    assert diagram.relationships[0].from_element == frontend
    assert diagram.relationships[0].to_element == api_service
    assert diagram.relationships[0].label == "Uses"
    assert diagram.relationships[0].technology == "JSON/HTTPS"
    assert diagram.relationships[1].from_element == mobile_app
    assert diagram.relationships[1].to_element == api_service
    assert diagram.relationships[1].label == "Uses"
    assert diagram.relationships[1].technology == "JSON/HTTPS"


def test_relationship_connect_many_to_many_error(diagram: Diagram):
    frontend = Element("frontend", "Web app")
    mobile_app = Element("mobile", "Mobile app")
    auth_service = Element("auth", "Authorization Service")
    api_service = Element("api", "Backend API Service")
    relationship = Rel("Uses", "JSON/HTTPS")
    expected_error = "Either source or destination must be a single element"

    with pytest.raises(ValueError, match=expected_error):
        relationship._connect(
            source=[frontend, mobile_app],
            destination=[api_service, auth_service],
        )

    assert not diagram.relationships


def test_relationship_connect_empty_source_error(diagram: Diagram):
    relationship = Rel("Uses", "JSON/HTTPS")
    expected_error = "Either source or destination must be provided"

    with pytest.raises(ValueError, match=expected_error):
        relationship._connect(
            source=None,
            destination=None,
        )

    assert not diagram.relationships

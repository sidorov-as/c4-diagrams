import uuid

import pytest
from pytest_mock import MockerFixture

from c4 import (
    EnterpriseBoundary,
    Person,
    PersonExt,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemLandscapeDiagram,
    SystemQueue,
    SystemQueueExt,
)
from c4.diagrams import core
from c4.diagrams.core import Boundary, Diagram, Element


@pytest.mark.parametrize(
    "diagram_class",
    [SystemContextDiagram, SystemLandscapeDiagram],
)
@pytest.mark.parametrize(
    "system_class",
    [System, SystemExt],
)
def test_system_check_label_valid(
    diagram_class: type[Diagram],
    system_class: type[Element],
):
    with diagram_class() as diagram:
        system = system_class(label="example")

    assert system.label == "example"
    assert diagram.elements == [system]


@pytest.mark.parametrize(
    "diagram_class",
    [SystemContextDiagram, SystemLandscapeDiagram],
)
@pytest.mark.parametrize(
    "system_class",
    [System, SystemExt],
)
def test_system_label_not_provided(
    diagram_class: type[Diagram],
    system_class: type[Element],
):
    expected_error = "The 'label' argument is required"

    with diagram_class(), pytest.raises(ValueError, match=expected_error):
        system_class()


@pytest.mark.parametrize(
    "diagram_class",
    [SystemContextDiagram, SystemLandscapeDiagram],
)
@pytest.mark.parametrize(
    "system_class",
    [System, SystemExt],
)
def test_system_check_alias(
    diagram_class: type[Diagram],
    system_class: type[Element],
):
    with diagram_class():
        system = system_class(alias="example", label="...")

    assert system.alias == "example"


@pytest.mark.parametrize(
    "diagram_class",
    [SystemContextDiagram, SystemLandscapeDiagram],
)
@pytest.mark.parametrize(
    "system_class",
    [System, SystemExt],
)
def test_system_generate_alias(
    mocker: MockerFixture,
    diagram_class: type[Diagram],
    system_class: type[Element],
):
    expected_uuid = uuid.UUID("12340000-0000-0000-0000-000000000000")
    mocker.patch.object(core, "uuid4", return_value=expected_uuid)
    with diagram_class():
        system = system_class(label="example")

    assert system.alias == "example_1234"


@pytest.mark.parametrize(
    "diagram_class",
    [SystemContextDiagram, SystemLandscapeDiagram],
)
@pytest.mark.parametrize(
    "system_class",
    [System, SystemExt],
)
def test_system_attrs(
    diagram_class: type[Diagram],
    system_class: type[System] | type[SystemExt],
):
    alias = "system1"
    label = "System"
    description = "A system"
    sprite = "$foo1"
    tags = "foo,bar"
    link = "https://example.com"
    type_ = "stereotype"
    base_shape = "rectangle"

    with diagram_class() as diagram:
        system = system_class(
            alias=alias,
            label=label,
            description=description,
            sprite=sprite,
            tags=tags,
            link=link,
            type_=type_,
            base_shape=base_shape,
        )

    assert diagram.elements == [system]
    assert system.alias == alias
    assert system.label == label
    assert system.description == description
    assert system.sprite == sprite
    assert system.tags == tags
    assert system.link == link
    assert system.type == type_
    assert system.base_shape == base_shape
    # reserved for other elements
    assert system.technology == ""


@pytest.mark.parametrize("boundary_class", [EnterpriseBoundary, SystemBoundary])
@pytest.mark.parametrize(
    "diagram_class",
    [SystemContextDiagram, SystemLandscapeDiagram],
)
def test_enterprise_boundary_attrs(
    boundary_class: type[Boundary],
    diagram_class: type[Diagram],
):
    alias = "boundary1"
    label = "Enterprise Boundary"
    description = "An enterprise boundary"
    tags = "foo,bar"
    link = "https://example.com"

    with diagram_class() as diagram:
        boundary = boundary_class(
            alias=alias,
            label=label,
            description=description,
            tags=tags,
            link=link,
        )

    assert diagram.boundaries == [boundary]
    assert boundary.alias == alias
    assert boundary.label == label
    assert boundary.description == description
    assert boundary.tags == tags
    assert boundary.link == link
    # reserved for other elements
    assert boundary.type == ""
    assert boundary.base_shape == ""
    assert boundary.technology == ""
    assert boundary.sprite == ""


@pytest.mark.parametrize(
    "diagram_class",
    [SystemContextDiagram, SystemLandscapeDiagram],
)
@pytest.mark.parametrize(
    "element_class",
    [
        Person,
        PersonExt,
        SystemDb,
        SystemQueue,
        SystemDbExt,
        SystemQueueExt,
    ],
)
def test_element_adds_itself_to_diagram(
    diagram_class: type[Diagram], element_class: type[Element]
):
    with diagram_class() as diagram:
        element = element_class(label="example")

    assert element.label == "example"
    assert diagram.elements == [element]

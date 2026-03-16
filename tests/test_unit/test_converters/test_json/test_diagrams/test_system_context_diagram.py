from typing import Any

import pytest

from c4.converters.json.schemas.diagrams.system_context import (
    PersonExtSchema,
    PersonSchema,
    SystemBoundarySchema,
    SystemDbExtSchema,
    SystemDbSchema,
    SystemExtSchema,
    SystemQueueExtSchema,
    SystemQueueSchema,
    SystemSchema,
)
from tests.fixtures.converters.json import (
    PersonExtSchemaFactory,
    PersonSchemaFactory,
    SystemBoundarySchemaFactory,
    SystemDbExtSchemaFactory,
    SystemDbSchemaFactory,
    SystemExtSchemaFactory,
    SystemQueueExtSchemaFactory,
    SystemQueueSchemaFactory,
    SystemSchemaFactory,
)
from tests.test_unit.test_converters.test_json.test_diagrams.conftest import (
    GetDiagramSchema,
)


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"stereotype": None},
        {"description": None},
        {"sprite": None},
        {"tags": []},
        {"link": None},
        {"properties": None},
    ],
)
def test_person_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = PersonSchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "elements": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    element = diagram_schema.elements[0]

    assert isinstance(element, PersonSchema)
    assert element == schema


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"stereotype": None},
        {"description": None},
        {"sprite": None},
        {"tags": []},
        {"link": None},
        {"properties": None},
    ],
)
def test_person_ext_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = PersonExtSchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "elements": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    element = diagram_schema.elements[0]

    assert isinstance(element, PersonExtSchema)
    assert element == schema


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"stereotype": None},
        {"description": None},
        {"base_shape": None},
        {"tags": []},
        {"sprite": None},
        {"link": None},
        {"properties": None},
    ],
)
def test_system_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = SystemSchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "elements": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    element = diagram_schema.elements[0]

    assert isinstance(element, SystemSchema)
    assert element == schema


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"stereotype": None},
        {"description": None},
        {"base_shape": None},
        {"tags": []},
        {"sprite": None},
        {"link": None},
        {"properties": None},
    ],
)
def test_system_ext_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = SystemExtSchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "elements": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    element = diagram_schema.elements[0]

    assert isinstance(element, SystemExtSchema)
    assert element == schema


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"stereotype": None},
        {"description": None},
        {"tags": []},
        {"sprite": None},
        {"link": None},
        {"properties": None},
    ],
)
def test_system_db_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = SystemDbSchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "elements": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    element = diagram_schema.elements[0]

    assert isinstance(element, SystemDbSchema)
    assert element == schema


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"stereotype": None},
        {"description": None},
        {"tags": []},
        {"sprite": None},
        {"link": None},
        {"properties": None},
    ],
)
def test_system_db_ext_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = SystemDbExtSchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "elements": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    element = diagram_schema.elements[0]

    assert isinstance(element, SystemDbExtSchema)
    assert element == schema


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"stereotype": None},
        {"description": None},
        {"tags": []},
        {"sprite": None},
        {"link": None},
        {"properties": None},
    ],
)
def test_system_queue_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = SystemQueueSchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "elements": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    element = diagram_schema.elements[0]

    assert isinstance(element, SystemQueueSchema)
    assert element == schema


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"stereotype": None},
        {"description": None},
        {"tags": []},
        {"sprite": None},
        {"link": None},
        {"properties": None},
    ],
)
def test_system_queue_ext_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = SystemQueueExtSchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "elements": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    element = diagram_schema.elements[0]

    assert isinstance(element, SystemQueueExtSchema)
    assert element == schema


@pytest.mark.parametrize(
    "overrides",
    [
        {},
        {"alias": None},
        {"description": None},
        {"stereotype": None},
        {"tags": []},
        {"link": None},
        {"properties": None},
        {"elements": []},
        {"boundaries": []},
        {"relationships": []},
    ],
)
def test_system_boundary_schema(
    get_diagram_schema: GetDiagramSchema,
    overrides: dict[str, Any],
):
    schema = SystemBoundarySchemaFactory.build(**overrides)
    data = {
        "type": "SystemContextDiagram",
        "boundaries": [schema.model_dump(exclude_none=False, by_alias=True)],
    }
    diagram_schema = get_diagram_schema(data)

    boundary = diagram_schema.boundaries[0]

    assert isinstance(boundary, SystemBoundarySchema)
    assert boundary == schema

from __future__ import annotations

from typing import Any

import pytest

from c4 import (
    Component,
    ComponentDb,
    ComponentDbExt,
    ComponentExt,
    ComponentQueue,
    ComponentQueueExt,
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDbExt,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
    DeploymentNode,
    DynamicDiagram,
    Node,
)
from c4.contrib.c4_macros import NodeLeft, NodeRight
from c4.contrib.mermaid.converters.json.schemas import (
    MermaidNodeLeftSchema,
    MermaidNodeRightSchema,
)
from c4.contrib.plantuml import DeploymentNodeLeft, DeploymentNodeRight
from c4.contrib.plantuml.converters.json.schemas import (
    PlantUMLDeploymentNodeLeftSchema,
    PlantUMLDeploymentNodeRightSchema,
    PlantUMLNodeLeftSchema,
    PlantUMLNodeRightSchema,
)
from c4.converters.json.converter import JSONToDiagramConverter
from c4.converters.json.schemas.diagrams.component import (
    ComponentDbExtSchema,
    ComponentDbSchema,
    ComponentExtSchema,
    ComponentQueueExtSchema,
    ComponentQueueSchema,
    ComponentSchema,
)
from c4.converters.json.schemas.diagrams.container import (
    ContainerBoundarySchema,
    ContainerDbExtSchema,
    ContainerDbSchema,
    ContainerExtSchema,
    ContainerQueueExtSchema,
    ContainerQueueSchema,
    ContainerSchema,
)
from c4.converters.json.schemas.diagrams.deployment import (
    DeploymentNodeSchema,
    NodeSchema,
)
from c4.converters.json.schemas.diagrams.dynamic import DynamicBoundarySchema
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
from c4.diagrams.core import Boundary, Relationship
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
        {"description": None},
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
        {"description": None},
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
        {"description": None},
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
        {"description": None},
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
        {"description": None},
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
        {"description": None},
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
        {"description": None},
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
        {"description": None},
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


@pytest.mark.parametrize(
    ("diagram_type", "payload", "schema_class", "element_class"),
    [
        (
            "ContainerDiagram",
            {"type": "Container", "technology": "Python"},
            ContainerSchema,
            Container,
        ),
        (
            "ContainerDiagram",
            {"type": "ContainerExt", "technology": "REST"},
            ContainerExtSchema,
            ContainerExt,
        ),
        (
            "ContainerDiagram",
            {"type": "ContainerDb", "technology": "PostgreSQL"},
            ContainerDbSchema,
            ContainerDb,
        ),
        (
            "ContainerDiagram",
            {"type": "ContainerDbExt", "technology": "Vendor DB"},
            ContainerDbExtSchema,
            ContainerDbExt,
        ),
        (
            "ContainerDiagram",
            {"type": "ContainerQueue", "technology": "Kafka"},
            ContainerQueueSchema,
            ContainerQueue,
        ),
        (
            "ContainerDiagram",
            {"type": "ContainerQueueExt", "technology": "Vendor MQ"},
            ContainerQueueExtSchema,
            ContainerQueueExt,
        ),
        (
            "ComponentDiagram",
            {"type": "Component", "technology": "Python"},
            ComponentSchema,
            Component,
        ),
        (
            "ComponentDiagram",
            {"type": "ComponentExt", "technology": "REST"},
            ComponentExtSchema,
            ComponentExt,
        ),
        (
            "ComponentDiagram",
            {"type": "ComponentDb", "technology": "SQLite"},
            ComponentDbSchema,
            ComponentDb,
        ),
        (
            "ComponentDiagram",
            {"type": "ComponentDbExt", "technology": "Vendor DB"},
            ComponentDbExtSchema,
            ComponentDbExt,
        ),
        (
            "ComponentDiagram",
            {"type": "ComponentQueue", "technology": "RabbitMQ"},
            ComponentQueueSchema,
            ComponentQueue,
        ),
        (
            "ComponentDiagram",
            {"type": "ComponentQueueExt", "technology": "Vendor MQ"},
            ComponentQueueExtSchema,
            ComponentQueueExt,
        ),
    ],
)
def test_element_schemas_map_to_dsl_classes(
    diagram_type: str,
    payload: dict[str, Any],
    schema_class: type[Any],
    element_class: type[Any],
) -> None:
    data = {
        "type": diagram_type,
        "elements": [
            {
                **payload,
                "label": "Element",
                "alias": "element",
                "description": "Element description",
            }
        ],
    }

    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()

    assert isinstance(converter._diagram_schema.elements[0], schema_class)
    assert isinstance(diagram.elements[0], element_class)
    assert diagram.elements[0].technology == payload["technology"]


@pytest.mark.parametrize(
    ("payload", "schema_class", "boundary_class"),
    [
        (
            {"type": "ContainerBoundary"},
            ContainerBoundarySchema,
            ContainerBoundary,
        ),
        (
            {"type": "Boundary"},
            DynamicBoundarySchema,
            Boundary,
        ),
    ],
)
def test_boundary_schemas_map_to_dsl_classes(
    payload: dict[str, Any],
    schema_class: type[Any],
    boundary_class: type[Any],
) -> None:
    diagram_type = (
        "DynamicDiagram"
        if payload["type"] == "Boundary"
        else "ContainerDiagram"
    )
    data = {
        "type": diagram_type,
        "boundaries": [
            {
                **payload,
                "label": "Boundary",
                "alias": "boundary",
                "description": "Boundary description",
                "elements": [],
                "boundaries": [],
                "relationships": [],
            }
        ],
    }

    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()

    assert isinstance(converter._diagram_schema.boundaries[0], schema_class)
    assert isinstance(diagram.boundaries[0], boundary_class)


@pytest.mark.parametrize(
    ("node_type", "schema_class", "node_class"),
    [
        ("Node", NodeSchema, Node),
        ("DeploymentNode", DeploymentNodeSchema, DeploymentNode),
    ],
)
def test_deployment_node_schemas_map_to_dsl_classes(
    node_type: str,
    schema_class: type[Any],
    node_class: type[Any],
) -> None:
    data = {
        "type": "DeploymentDiagram",
        "boundaries": [
            {
                "type": node_type,
                "label": "Runtime",
                "alias": "runtime",
                "description": "Runtime node",
                "elements": [
                    {
                        "type": "Container",
                        "label": "API",
                        "alias": "api",
                        "technology": "Python",
                    }
                ],
                "boundaries": [],
                "relationships": [],
            }
        ],
    }

    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()
    node = diagram.boundaries[0]

    assert isinstance(converter._diagram_schema.boundaries[0], schema_class)
    assert isinstance(node, node_class)
    assert isinstance(node.elements[0], Container)


@pytest.mark.parametrize(
    ("node_type", "schema_class", "node_class"),
    [
        ("NodeLeft", PlantUMLNodeLeftSchema, NodeLeft),
        ("NodeRight", PlantUMLNodeRightSchema, NodeRight),
        (
            "DeploymentNodeLeft",
            PlantUMLDeploymentNodeLeftSchema,
            DeploymentNodeLeft,
        ),
        (
            "DeploymentNodeRight",
            PlantUMLDeploymentNodeRightSchema,
            DeploymentNodeRight,
        ),
    ],
)
def test_plantuml_deployment_node_schemas_map_to_dsl_classes(
    node_type: str,
    schema_class: type[Any],
    node_class: type[Any],
) -> None:
    data = {
        "type": "DeploymentDiagram",
        "backend": "plantuml",
        "boundaries": [
            {
                "type": node_type,
                "label": "Runtime",
                "alias": "runtime",
                "description": "Runtime node",
                "elements": [
                    {
                        "type": "Container",
                        "label": "API",
                        "alias": "api",
                        "technology": "Python",
                    }
                ],
                "boundaries": [],
                "relationships": [],
            }
        ],
    }

    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()
    node = diagram.boundaries[0]

    assert isinstance(converter._diagram_schema.boundaries[0], schema_class)
    assert isinstance(node, node_class)
    assert isinstance(node.elements[0], Container)


@pytest.mark.parametrize(
    ("node_type", "schema_class", "node_class"),
    [
        ("NodeLeft", MermaidNodeLeftSchema, NodeLeft),
        ("NodeRight", MermaidNodeRightSchema, NodeRight),
    ],
)
def test_mermaid_deployment_node_schemas_map_to_dsl_classes(
    node_type: str,
    schema_class: type[Any],
    node_class: type[Any],
) -> None:
    data = {
        "type": "DeploymentDiagram",
        "backend": "mermaid",
        "boundaries": [
            {
                "type": node_type,
                "label": "Runtime",
                "alias": "runtime",
                "description": "Runtime node",
                "elements": [
                    {
                        "type": "Container",
                        "label": "API",
                        "alias": "api",
                        "technology": "Python",
                    }
                ],
                "boundaries": [],
                "relationships": [],
            }
        ],
    }

    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()
    node = diagram.boundaries[0]

    assert isinstance(converter._diagram_schema.boundaries[0], schema_class)
    assert isinstance(node, node_class)
    assert isinstance(node.elements[0], Container)


def test_dynamic_diagram_schema_maps_relationships_and_diagram_class() -> None:
    data = {
        "type": "DynamicDiagram",
        "elements": [
            {"type": "Person", "label": "Customer", "alias": "customer"},
            {"type": "System", "label": "Shop", "alias": "shop"},
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "shop",
                "label": "Uses",
            }
        ],
    }

    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()

    assert isinstance(diagram, DynamicDiagram)
    assert isinstance(diagram.relationships[0], Relationship)

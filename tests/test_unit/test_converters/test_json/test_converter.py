from __future__ import annotations

import re
import textwrap
from io import BytesIO, StringIO
from pathlib import Path
from typing import IO, Any

import pytest
from pytest_mock import MockerFixture

from c4 import (
    Person,
    Rel,
    Relationship,
    RelDown,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemDb,
    increment,
    set_index,
)
from c4.converters.exceptions import (
    ConversionError,
    DiagramJSONSchemaParsingError,
    DiagramJSONSchemaValidationError,
    ElementResolutionConflictError,
    ElementResolutionError,
)
from c4.converters.json import converter as converter_module
from c4.converters.json.converter import (
    JSONToDiagramConverter,
    diagram_from_dict,
    diagram_from_json,
)
from c4.diagrams.core import LayoutType
from c4.renderers import MermaidRenderOptions
from c4.renderers.mermaid.options import (
    ElementStyle,
    RelStyle,
    UpdateLayoutConfig,
)
from c4.renderers.plantuml.options import (
    DiagramLayout,
    ElementTag,
    PlantUMLRenderOptions,
    ShowLegend,
)


@pytest.fixture()
def system_context_diagram_dict() -> dict[str, Any]:
    return {
        "type": "SystemContextDiagram",
        "title": "Online Shop",
        "elements": [
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer",
            },
            {
                "type": "System",
                "alias": "shop",
                "label": "Online Shop",
            },
            {
                "type": "SystemDb",
                "alias": "orders_db",
                "label": "Orders DB",
            },
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "shop",
                "label": "Uses",
                "technology": "HTTPS",
            },
            {
                "type": "REL",
                "from": "shop",
                "to": "orders_db",
                "label": "Reads/Writes",
                "technology": "SQL",
            },
        ],
        "layouts": [
            {
                "type": "LAY_R",
                "from": "customer",
                "to": "shop",
            },
            {
                "type": "LAY_D",
                "from": "shop",
                "to": "orders_db",
            },
        ],
    }


@pytest.fixture()
def nested_system_context_diagram_dict() -> dict[str, Any]:
    return {
        "type": "SystemContextDiagram",
        "title": "Nested Shop",
        "elements": [
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer",
            }
        ],
        "boundaries": [
            {
                "type": "SystemBoundary",
                "alias": "shop_boundary",
                "label": "Online Shop Platform",
                "elements": [
                    {
                        "type": "System",
                        "alias": "shop",
                        "label": "Online Shop",
                        "technology": "Python / Django",
                    }
                ],
                "boundaries": [
                    {
                        "type": "SystemBoundary",
                        "alias": "storage_boundary",
                        "label": "Storage",
                        "elements": [
                            {
                                "type": "SystemDb",
                                "alias": "orders_db",
                                "label": "Orders DB",
                                "technology": "PostgreSQL",
                            }
                        ],
                    }
                ],
                "relationships": [
                    {
                        "type": "REL_DOWN",
                        "from": "shop",
                        "to": "orders_db",
                        "label": "Reads/Writes",
                        "technology": "SQL",
                    }
                ],
            }
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "shop",
                "label": "Uses",
                "technology": "HTTPS",
            }
        ],
        "layouts": [
            {
                "type": "LAY_R",
                "from": "customer",
                "to": "shop",
            },
            {
                "type": "LAY_D",
                "from": "shop",
                "to": "orders_db",
            },
        ],
    }


@pytest.fixture()
def dynamic_diagram_dict() -> dict[str, Any]:
    return {
        "type": "DynamicDiagram",
        "title": "Online Shop",
        "elements": [
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer",
            },
            {
                "type": "System",
                "alias": "shop",
                "label": "Online Shop",
            },
            {
                "type": "SystemDb",
                "alias": "orders_db",
                "label": "Orders DB",
            },
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "shop",
                "label": "Uses",
                "technology": "HTTPS",
            },
            {
                "type": "increment",
                "offset": "2",
            },
            {
                "type": "REL",
                "from": "shop",
                "to": "orders_db",
                "label": "Reads/Writes",
                "technology": "SQL",
            },
            {
                "type": "set_index",
                "new_index": "10",
            },
        ],
        "layouts": [
            {
                "type": "LAY_R",
                "from": "customer",
                "to": "shop",
            },
            {
                "type": "LAY_D",
                "from": "shop",
                "to": "orders_db",
            },
        ],
    }


@pytest.fixture()
def diagram_with_plantuml_render_options():
    return {
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "elements": [
            {
                "type": "Person",
                "label": "Customer",
                "alias": "customer",
                "description": "Places orders through the storefront.",
                "tags": ["person", "primary"],
            },
            {
                "type": "PersonExt",
                "label": "Support Agent",
                "alias": "support_agent",
                "description": "Handles issues in an external CRM.",
                "tags": ["person", "external"],
            },
            {
                "type": "System",
                "label": "Retail Platform",
                "alias": "retail_platform",
                "description": (
                    "Core platform for catalog, checkout, and order management."
                ),
                "tags": ["system", "core"],
                "link": "https://retail.example.com",
            },
            {
                "type": "SystemExt",
                "label": "Payment Gateway",
                "alias": "payment_gateway",
                "description": "Processes card payments.",
                "tags": ["system", "external"],
                "base_shape": "RoundedBox",
            },
        ],
        "boundaries": [
            {
                "type": "EnterpriseBoundary",
                "label": "Acme Corp",
                "alias": "acme_enterprise",
                "description": "Internal systems owned by Acme.",
                "tags": ["enterprise"],
                "elements": [
                    {
                        "type": "System",
                        "label": "Retail Platform",
                        "alias": "retail_platform",
                        "description": "Core commerce system.",
                    }
                ],
                "boundaries": [],
            }
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "retail_platform",
                "label": "Browses and places orders",
                "technology": "HTTPS",
            },
            {
                "type": "REL",
                "from": "retail_platform",
                "to": "payment_gateway",
                "label": "Charges card",
                "technology": "REST API",
            },
        ],
        "layouts": [
            {"type": "LAY_R", "from": "customer", "to": "retail_platform"},
            {
                "type": "LAY_R",
                "from": "retail_platform",
                "to": "payment_gateway",
            },
        ],
        "render_options": {
            "plantuml": {
                "layout": "LAYOUT_LEFT_RIGHT",
                "layout_with_legend": True,
                "show_legend": {"details": "Normal", "hide_stereotype": False},
                "legend_title": "System",
                "hide_stereotype": False,
                "tags": [
                    {
                        "type": "ElementTag",
                        "tag_stereo": "external",
                        "legend_text": "External dependency",
                        "sprite": "cloud",
                    }
                ],
            }
        },
    }


@pytest.fixture()
def diagram_with_render_options():
    return {
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "elements": [
            {
                "type": "Person",
                "label": "Customer",
                "alias": "customer",
                "description": "Places orders through the storefront.",
                "tags": ["person", "primary"],
            },
            {
                "type": "PersonExt",
                "label": "Support Agent",
                "alias": "support_agent",
                "description": "Handles issues in an external CRM.",
                "tags": ["person", "external"],
            },
            {
                "type": "System",
                "label": "Retail Platform",
                "alias": "retail_platform",
                "description": (
                    "Core platform for catalog, checkout, and order management."
                ),
                "tags": ["system", "core"],
                "link": "https://retail.example.com",
            },
            {
                "type": "SystemExt",
                "label": "Payment Gateway",
                "alias": "payment_gateway",
                "description": "Processes card payments.",
                "tags": ["system", "external"],
                "base_shape": "RoundedBox",
            },
        ],
        "boundaries": [
            {
                "type": "EnterpriseBoundary",
                "label": "Acme Corp",
                "alias": "acme_enterprise",
                "description": "Internal systems owned by Acme.",
                "tags": ["enterprise"],
                "elements": [
                    {
                        "type": "System",
                        "label": "Retail Platform",
                        "alias": "retail_platform",
                        "description": "Core commerce system.",
                    }
                ],
                "boundaries": [],
            }
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "retail_platform",
                "label": "Browses and places orders",
                "technology": "HTTPS",
            },
            {
                "type": "REL",
                "from": "retail_platform",
                "to": "payment_gateway",
                "label": "Charges card",
                "technology": "REST API",
            },
        ],
        "layouts": [
            {"type": "LAY_R", "from": "customer", "to": "retail_platform"},
            {
                "type": "LAY_R",
                "from": "retail_platform",
                "to": "payment_gateway",
            },
        ],
        "render_options": {
            "plantuml": {
                "layout": "LAYOUT_LEFT_RIGHT",
                "layout_with_legend": True,
                "show_legend": {"details": "Normal", "hide_stereotype": False},
                "legend_title": "System",
                "hide_stereotype": False,
                "tags": [
                    {
                        "type": "ElementTag",
                        "tag_stereo": "external",
                        "legend_text": "External dependency",
                        "sprite": "cloud",
                    }
                ],
            },
            "mermaid": {
                "update_layout_config": {
                    "c4_shape_in_row": 2,
                    "c4_boundary_in_row": 4,
                },
            },
        },
    }


@pytest.fixture()
def diagram_with_mermaid_render_options():
    return {
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "elements": [
            {
                "type": "Person",
                "label": "Customer",
                "alias": "customer",
                "description": "Places orders through the storefront.",
                "tags": ["person", "primary"],
            },
            {
                "type": "PersonExt",
                "label": "Support Agent",
                "alias": "support_agent",
                "description": "Handles issues in an external CRM.",
                "tags": ["person", "external"],
            },
            {
                "type": "System",
                "label": "Retail Platform",
                "alias": "retail_platform",
                "description": (
                    "Core platform for catalog, checkout, and order management."
                ),
                "tags": ["system", "core"],
                "link": "https://retail.example.com",
            },
            {
                "type": "SystemExt",
                "label": "Payment Gateway",
                "alias": "payment_gateway",
                "description": "Processes card payments.",
                "tags": ["system", "external"],
                "base_shape": "RoundedBox",
            },
        ],
        "boundaries": [
            {
                "type": "EnterpriseBoundary",
                "label": "Acme Corp",
                "alias": "acme_enterprise",
                "description": "Internal systems owned by Acme.",
                "tags": ["enterprise"],
                "elements": [
                    {
                        "type": "System",
                        "label": "Retail Platform",
                        "alias": "retail_platform",
                        "description": "Core commerce system.",
                    }
                ],
                "boundaries": [],
            }
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "retail_platform",
                "label": "Browses and places orders",
                "technology": "HTTPS",
            },
            {
                "type": "REL",
                "from": "retail_platform",
                "to": "payment_gateway",
                "label": "Charges card",
                "technology": "REST API",
            },
        ],
        "layouts": [
            {"type": "LAY_R", "from": "customer", "to": "retail_platform"},
            {
                "type": "LAY_R",
                "from": "retail_platform",
                "to": "payment_gateway",
            },
        ],
        "render_options": {
            "mermaid": {
                "update_layout_config": {
                    "c4_shape_in_row": 2,
                    "c4_boundary_in_row": 4,
                },
                "styles": [
                    {
                        "type": "ElementStyle",
                        "element": "customer",
                        "bg_color": "#e8f5e9",
                        "border_color": "#66bb6a",
                        "font_color": "#1b5e20",
                    },
                    {
                        "type": "RelStyle",
                        "from_element": "customer",
                        "to_element": "retail_platform",
                        "text_color": "#e8f5e9",
                        "line_color": "#66bb6a",
                        "offset_x": 10,
                        "offset_y": 20,
                    },
                ],
            }
        },
    }


@pytest.fixture()
def duplicate_label_system_context_diagram_dict() -> dict[str, Any]:
    return {
        "type": "SystemContextDiagram",
        "title": "Duplicate Labels",
        "elements": [
            {
                "type": "System",
                "alias": "shop_api",
                "label": "Shared Label",
            },
            {
                "type": "System",
                "alias": "shop_admin",
                "label": "Shared Label",
            },
        ],
    }


@pytest.fixture()
def missing_target_system_context_diagram_dict() -> dict[str, Any]:
    return {
        "type": "SystemContextDiagram",
        "title": "Broken Diagram",
        "elements": [
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer",
            }
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "missing_system",
                "label": "Uses",
                "technology": "HTTPS",
            }
        ],
        "layouts": [
            {
                "type": "LAY_D",
                "from": "missing_system",
                "to": "customer",
            },
        ],
    }


def test_json_to_diagram_converter__init(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)

    assert converter._diagram_schema.title == "Online Shop"
    assert converter._diagram.title == "Online Shop"


def test_json_to_diagram_converter__check_empty(
    system_context_diagram_dict: dict[str, Any],
):
    diagram_dict = {
        "type": "SystemContextDiagram",
        "title": "Online Shop",
        "elements": [
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer",
            }
        ],
        "render_options": {
            "plantuml": {
                "tags": [
                    {
                        "type": "PersonTag",
                        "tag_stereo": "Customer",
                        "bg_color": "#e8f5e9",
                        "border_color": "#66bb6a",
                        "border_style": "SolidLine",
                        "border_thickness": "1",
                        "font_color": "#1b5e20",
                        "legend_sprite": "user",
                        "legend_text": "Primary customer actor",
                        "shadowing": False,
                    }
                ],
            }
        },
    }

    diagram = JSONToDiagramConverter(diagram_dict).convert()

    assert diagram.title == "Online Shop"


def test_json_to_diagram_converter__validation_error():
    diagram_dict = {
        "type": "UnknownDiagramType",
        "title": "Online Shop",
    }
    expected_error = (
        "Input tag 'UnknownDiagramType' found using 'type' does not match any "
        "of the expected tags: "
        "'SystemContextDiagram', "
        "'SystemLandscapeDiagram', "
        "'ContainerDiagram', "
        "'ComponentDiagram', "
        "'DeploymentDiagram', "
        "'DynamicDiagram'"
    )

    with pytest.raises(DiagramJSONSchemaValidationError, match=expected_error):
        JSONToDiagramConverter(diagram_dict)


def test_json_to_diagram_converter__validation_error__invalid_nested_items():
    diagram_dict = {
        "type": "SystemContextDiagram",
        "title": "Online Shop",
        "elements": ["foo"],
    }
    expected_error = textwrap.dedent("""\
        JSON diagram schema validation failed:
        root->SystemContextDiagram->elements[0]->PersonSchema: Input should be a valid dictionary or instance of PersonSchema
        root->SystemContextDiagram->elements[0]->PersonExtSchema: Input should be a valid dictionary or instance of PersonExtSchema
        root->SystemContextDiagram->elements[0]->SystemSchema: Input should be a valid dictionary or instance of SystemSchema
        root->SystemContextDiagram->elements[0]->SystemExtSchema: Input should be a valid dictionary or instance of SystemExtSchema
        root->SystemContextDiagram->elements[0]->SystemDbSchema: Input should be a valid dictionary or instance of SystemDbSchema
        root->SystemContextDiagram->elements[0]->SystemDbExtSchema: Input should be a valid dictionary or instance of SystemDbExtSchema
        root->SystemContextDiagram->elements[0]->SystemQueueSchema: Input should be a valid dictionary or instance of SystemQueueSchema
        root->SystemContextDiagram->elements[0]->SystemQueueExtSchema: Input should be a valid dictionary or instance of SystemQueueExtSchema
    """).strip()

    with pytest.raises(
        DiagramJSONSchemaValidationError, match=re.escape(expected_error)
    ):
        JSONToDiagramConverter(diagram_dict)


def test_json_to_diagram_converter__add_elements(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    diagram = converter._diagram

    with diagram:
        converter._add_elements(converter._diagram_schema)

    customer = converter._diagram.get_element_by_alias("customer")
    shop = converter._diagram.get_element_by_alias("shop")
    orders_db = converter._diagram.get_element_by_alias("orders_db")
    assert diagram.elements == [customer, shop, orders_db]
    assert isinstance(customer, Person)
    assert customer.alias == "customer"
    assert customer.label == "Customer"
    assert isinstance(shop, System)
    assert shop.alias == "shop"
    assert shop.label == "Online Shop"
    assert isinstance(orders_db, SystemDb)
    assert orders_db.alias == "orders_db"
    assert orders_db.label == "Orders DB"


def test_json_to_diagram_converter__add_elements__no_elements(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    diagram = converter._diagram
    parent = object()

    with diagram:
        converter._add_elements(parent)

    assert not diagram.elements


def test_json_to_diagram_converter__add_boundary__nested_elements(
    nested_system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(nested_system_context_diagram_dict)
    diagram = converter._diagram
    with diagram:
        converter._add_elements(converter._diagram_schema)
    boundary_schema = converter._diagram_schema.boundaries[0]

    with diagram:
        converter._add_boundary(boundary_schema)

    customer = converter._diagram.get_element_by_alias("customer")
    shop = converter._diagram.get_element_by_alias("shop")
    orders_db = converter._diagram.get_element_by_alias("orders_db")
    assert len(diagram.boundaries) == 1
    assert len(diagram.boundaries[0].boundaries) == 1
    shop_boundary = diagram.boundaries[0]
    storage_boundary = diagram.boundaries[0].boundaries[0]
    assert diagram.elements == [customer]
    assert shop_boundary.elements == [shop]
    assert shop_boundary.boundaries == [storage_boundary]
    assert storage_boundary.elements == [orders_db]
    assert len(shop_boundary.relationships) == 1
    assert shop_boundary.relationships[0].get_participants() == (
        shop,
        orders_db,
    )


def test_json_to_diagram_converter__add_boundaries__no_boundaries(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    diagram = converter._diagram
    parent = object()

    with diagram:
        converter._add_boundaries(parent)

    assert not diagram.boundaries


def test_json_to_diagram_converter__get_relationships(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)

    relationships = converter._get_relationships(converter._diagram_schema)

    assert len(relationships) == 2
    assert relationships[0].from_ == "customer"
    assert relationships[0].to == "shop"
    assert relationships[1].from_ == "shop"
    assert relationships[1].to == "orders_db"


def test_json_to_diagram_converter__get_relationships__no_relationships(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    parent = object()

    relationships = converter._get_relationships(parent)

    assert relationships == []


def test_json_to_diagram_converter__get_relationships__dynamic_diagram(
    dynamic_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(dynamic_diagram_dict)

    relationships = converter._get_relationships(converter._diagram_schema)

    assert relationships == []
    assert dynamic_diagram_dict["relationships"]


def test_json_to_diagram_converter__resolve_element__by_alias(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    diagram = converter.convert()
    customer, *_ = diagram.elements

    element = converter._resolve_element("customer")

    assert element is customer
    assert customer.label == "Customer"


def test_json_to_diagram_converter__resolve_element__by_label(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    diagram = converter.convert()
    _, shop, *_ = diagram.elements

    element = converter._resolve_element("Online Shop")

    assert element is shop
    assert shop.label == "Online Shop"
    assert shop.alias == "shop"


def test_json_to_diagram_converter__resolve_element__resolution_error(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    converter.convert()
    expected_error = re.escape(
        "Could not resolve an element with alias or label: 'missing'"
    )

    with pytest.raises(ElementResolutionError, match=expected_error):
        converter._resolve_element("missing")


def test_json_to_diagram_converter__resolve_element__resolution_conflict(
    duplicate_label_system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(
        duplicate_label_system_context_diagram_dict
    )
    with converter._diagram:
        converter._add_elements(converter._diagram_schema)
    expected_error = re.escape(
        "Could not resolve element by label 'Shared Label': "
        "multiple matches found ("
        "System(alias='shop_api', label='Shared Label'), "
        "System(alias='shop_admin', label='Shared Label')"
        ")."
    )

    with pytest.raises(ElementResolutionConflictError, match=expected_error):
        converter._resolve_element("Shared Label")


def test_json_to_diagram_converter__add_relationships(
    system_context_diagram_dict: dict[str, Any],
    mocker: MockerFixture,
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    spied_add_relationship = mocker.spy(converter, "_add_relationship")
    diagram = converter._diagram
    with diagram:
        converter._add_elements(converter._diagram_schema)

    with diagram:
        converter._add_relationships(converter._diagram_schema)

    customer = diagram.get_element_by_alias("customer")
    shop = diagram.get_element_by_alias("shop")
    orders_db = diagram.get_element_by_alias("orders_db")
    assert len(diagram.relationships) == 2
    assert diagram.relationships[0].get_participants() == (customer, shop)
    assert diagram.relationships[1].get_participants() == (shop, orders_db)
    assert spied_add_relationship.call_count == len(diagram.relationships)


def test_json_to_diagram_converter__add_relationships__no_relationships(
    system_context_diagram_dict: dict[str, Any],
    mocker: MockerFixture,
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    spied_add_relationship = mocker.patch.object(converter, "_add_relationship")
    parent = object()

    converter._add_relationships(parent)

    spied_add_relationship.assert_not_called()


def test_json_to_diagram_converter__add_relationship__resolution_error(
    missing_target_system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(
        missing_target_system_context_diagram_dict
    )
    with converter._diagram:
        converter._add_elements(converter._diagram_schema)
    relationship_schema = converter._diagram_schema.relationships[0]
    expected_error = (
        "Could not resolve an element with alias or label: 'missing_system'"
    )

    with pytest.raises(ElementResolutionError, match=expected_error):
        converter._add_relationship(relationship_schema)


def test_json_to_diagram_converter__add_layouts(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    diagram = converter._diagram
    with diagram:
        converter._add_elements(converter._diagram_schema)

    with diagram:
        converter._add_layouts()

    customer = diagram.get_element_by_alias("customer")
    shop = diagram.get_element_by_alias("shop")
    orders_db = diagram.get_element_by_alias("orders_db")
    assert len(diagram.layouts) == 2
    assert diagram.layouts[0].from_element == customer
    assert diagram.layouts[0].to_element == shop
    assert diagram.layouts[0].layout_type == LayoutType.LAY_R
    assert diagram.layouts[1].from_element == shop
    assert diagram.layouts[1].to_element == orders_db
    assert diagram.layouts[1].layout_type == LayoutType.LAY_D


def test_json_to_diagram_converter__add_layouts__resolution_error(
    missing_target_system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(
        missing_target_system_context_diagram_dict
    )
    diagram = converter._diagram
    expected_error = (
        "Could not resolve an element with alias or label: 'missing_system'"
    )

    with pytest.raises(ElementResolutionError, match=expected_error):
        converter._add_layouts()

    assert not diagram.layouts


def test_json_to_diagram_converter__add_base_elements__non_dynamic_diagram(
    system_context_diagram_dict: dict[str, Any],
    mocker: MockerFixture,
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    add_relationship = mocker.patch.object(converter, "_add_relationship")

    converter._add_base_elements()

    add_relationship.assert_not_called()


def test_json_to_diagram_converter__add_base_elements__dynamic_diagram(
    dynamic_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(dynamic_diagram_dict)
    diagram = converter._diagram
    with diagram:
        converter._add_elements(converter._diagram_schema)

    with diagram:
        converter._add_base_elements()

    customer = diagram.get_element_by_alias("customer")
    shop = diagram.get_element_by_alias("shop")
    orders_db = diagram.get_element_by_alias("orders_db")
    assert len(diagram.base_elements) == 4
    assert isinstance(diagram.base_elements[0], Relationship)
    assert isinstance(diagram.base_elements[1], increment)
    assert isinstance(diagram.base_elements[2], Relationship)
    assert isinstance(diagram.base_elements[3], set_index)
    assert diagram.base_elements[0].get_participants() == (customer, shop)
    assert diagram.base_elements[1].offset == 2
    assert diagram.base_elements[2].get_participants() == (shop, orders_db)
    assert diagram.base_elements[3].new_index == 10


def test_json_to_diagram_converter__set_render_options__plantuml(
    diagram_with_plantuml_render_options: dict[str, Any],
):
    converter = JSONToDiagramConverter(diagram_with_plantuml_render_options)
    diagram = converter._diagram
    expected_plantuml_render_options = PlantUMLRenderOptions(
        layout=DiagramLayout.LAYOUT_LEFT_RIGHT,
        layout_with_legend=True,
        layout_as_sketch=False,
        set_sketch_style=None,
        show_legend=ShowLegend(hide_stereotype=False, details="Normal"),
        show_floating_legend=None,
        hide_stereotype=False,
        hide_person_sprite=False,
        show_person_sprite=None,
        show_person_portrait=False,
        show_person_outline=False,
        without_property_header=False,
        legend_title="System",
        tags=[
            ElementTag(
                tag_stereo="external",
                legend_text="External dependency",
                legend_sprite=None,
                sprite="cloud",
                font_color=None,
                border_color=None,
                shadowing=False,
                shape=None,
                technology=None,
                border_style=None,
                border_thickness=None,
            )
        ],
        styles=[],
    )
    with diagram:
        converter._add_elements(converter._diagram_schema)

    with diagram:
        converter._set_render_options()

    assert diagram.render_options is not None
    assert diagram.render_options.plantuml is not None
    assert diagram.render_options.plantuml == expected_plantuml_render_options


def test_json_to_diagram_converter__set_render_options__mermaid(
    diagram_with_mermaid_render_options: dict[str, Any],
):
    converter = JSONToDiagramConverter(diagram_with_mermaid_render_options)
    diagram = converter._diagram
    expected_mermaid_render_options = MermaidRenderOptions(
        update_layout_config=UpdateLayoutConfig(
            c4_shape_in_row=2,
            c4_boundary_in_row=4,
        ),
        styles=[
            ElementStyle(
                element="customer",
                bg_color="#e8f5e9",
                font_color="#1b5e20",
                border_color="#66bb6a",
            ),
            RelStyle(
                from_element="customer",
                to_element="retail_platform",
                text_color="#e8f5e9",
                line_color="#66bb6a",
                offset_x=10,
                offset_y=20,
            ),
        ],
    )
    with diagram:
        converter._add_elements(converter._diagram_schema)

    with diagram:
        converter._set_render_options()

    assert diagram.render_options is not None
    assert diagram.render_options.mermaid is not None
    assert diagram.render_options.mermaid == expected_mermaid_render_options


def test_json_to_diagram_converter__set_render_options(
    diagram_with_render_options: dict[str, Any],
):
    converter = JSONToDiagramConverter(diagram_with_render_options)
    diagram = converter._diagram
    expected_plantuml_render_options = PlantUMLRenderOptions(
        layout=DiagramLayout.LAYOUT_LEFT_RIGHT,
        layout_with_legend=True,
        layout_as_sketch=False,
        set_sketch_style=None,
        show_legend=ShowLegend(hide_stereotype=False, details="Normal"),
        show_floating_legend=None,
        hide_stereotype=False,
        hide_person_sprite=False,
        show_person_sprite=None,
        show_person_portrait=False,
        show_person_outline=False,
        without_property_header=False,
        legend_title="System",
        tags=[
            ElementTag(
                tag_stereo="external",
                legend_text="External dependency",
                legend_sprite=None,
                sprite="cloud",
                font_color=None,
                border_color=None,
                shadowing=False,
                shape=None,
                technology=None,
                border_style=None,
                border_thickness=None,
            )
        ],
        styles=[],
    )
    expected_mermaid_render_options = MermaidRenderOptions(
        update_layout_config=UpdateLayoutConfig(
            c4_shape_in_row=2,
            c4_boundary_in_row=4,
        )
    )
    with diagram:
        converter._add_elements(converter._diagram_schema)

    with diagram:
        converter._set_render_options()

    assert diagram.render_options is not None
    assert diagram.render_options.plantuml is not None
    assert diagram.render_options.plantuml == expected_plantuml_render_options
    assert diagram.render_options.mermaid is not None
    assert diagram.render_options.mermaid == expected_mermaid_render_options


def test_json_to_diagram_converter__convert(
    nested_system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(nested_system_context_diagram_dict)

    diagram = converter.convert()

    customer = diagram.get_element_by_alias("customer")
    shop = diagram.get_element_by_alias("shop")
    orders_db = diagram.get_element_by_alias("orders_db")
    assert diagram.title == "Nested Shop"
    assert diagram.elements == [customer]
    assert len(diagram.boundaries) == 1
    assert len(diagram.relationships) == 1
    relationship1 = diagram.relationships[0]
    assert isinstance(relationship1, Rel)
    assert relationship1.get_participants() == (customer, shop)
    assert relationship1.label == "Uses"
    assert relationship1.technology == "HTTPS"
    assert len(diagram.layouts) == 2
    assert diagram.layouts[0].from_element == customer
    assert diagram.layouts[0].to_element == shop
    assert diagram.layouts[0].layout_type == LayoutType.LAY_R
    assert diagram.layouts[1].from_element == shop
    assert diagram.layouts[1].to_element == orders_db
    assert diagram.layouts[1].layout_type == LayoutType.LAY_D
    shop_boundary = diagram.boundaries[0]
    assert isinstance(shop_boundary, SystemBoundary)
    assert shop_boundary.label == "Online Shop Platform"
    assert shop_boundary.elements == [shop]
    assert len(shop_boundary.boundaries) == 1
    assert len(shop_boundary.relationships) == 1
    shop_relationship1 = shop_boundary.relationships[0]
    assert isinstance(shop_relationship1, RelDown)
    assert shop_relationship1.get_participants() == (shop, orders_db)
    assert shop_relationship1.label == "Reads/Writes"
    assert shop_relationship1.technology == "SQL"
    storage_boundary = shop_boundary.boundaries[0]
    assert isinstance(storage_boundary, SystemBoundary)
    assert storage_boundary.label == "Storage"
    assert storage_boundary.elements == [orders_db]


def test_json_to_diagram_converter__convert__resolution_error(
    missing_target_system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(
        missing_target_system_context_diagram_dict
    )
    expected_error = (
        "Could not resolve an element with alias or label: 'missing_system'"
    )

    with pytest.raises(ElementResolutionError, match=expected_error):
        converter.convert()


def test_json_to_diagram_converter__convert__duplicated_alias():
    data = {
        "type": "SystemContextDiagram",
        "title": "Broken Diagram",
        "elements": [
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer 1",
            },
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer 2",
            },
        ],
    }
    converter = JSONToDiagramConverter(data)
    expected_error = re.escape(
        "Duplicated alias 'customer': "
        "Person(alias='customer', label='Customer 1')."
    )

    with pytest.raises(ConversionError, match=expected_error):
        converter.convert()


def test_diagram_from_dict(
    nested_system_context_diagram_dict: dict[str, Any],
    mocker: MockerFixture,
):
    spied_converter = mocker.spy(JSONToDiagramConverter, "__init__")
    spied_convert = mocker.spy(JSONToDiagramConverter, "convert")

    diagram = diagram_from_dict(nested_system_context_diagram_dict)

    spied_converter.assert_called_once_with(
        mocker.ANY,  # self
        nested_system_context_diagram_dict,
    )
    spied_convert.assert_called_once()
    assert spied_convert.spy_return == diagram


@pytest.mark.parametrize(
    "src",
    [
        '{"type": "SystemContextDiagram", "title": "Online Shop"}',
        b'{"type": "SystemContextDiagram", "title": "Online Shop"}',
    ],
)
def test_diagram_from_json__string_or_bytes(
    mocker: MockerFixture,
    src: str | bytes,
):
    data = {
        "type": "SystemContextDiagram",
        "title": "Online Shop",
    }
    spied_diagram_from_dict = mocker.spy(converter_module, "diagram_from_dict")

    diagram = diagram_from_json(src)

    assert isinstance(diagram, SystemContextDiagram)
    assert spied_diagram_from_dict.spy_return == diagram
    spied_diagram_from_dict.assert_called_once_with(data)


def test_diagram_from_json__path(
    tmp_path: Path,
    mocker: MockerFixture,
):
    path = tmp_path / "diagram.json"
    path.write_text(
        '{"type": "SystemContextDiagram", "title": "Online Shop"}',
        encoding="utf-8",
    )
    data = {
        "type": "SystemContextDiagram",
        "title": "Online Shop",
    }
    spied_diagram_from_dict = mocker.spy(converter_module, "diagram_from_dict")

    diagram = diagram_from_json(path)

    assert isinstance(diagram, SystemContextDiagram)
    assert spied_diagram_from_dict.spy_return == diagram
    spied_diagram_from_dict.assert_called_once_with(data)


@pytest.mark.parametrize(
    "src",
    [
        StringIO('{"type": "SystemContextDiagram", "title": "Online Shop"}'),
        BytesIO(b'{"type": "SystemContextDiagram", "title": "Online Shop"}'),
    ],
)
def test_diagram_from_json__file_object(
    mocker: MockerFixture,
    src: IO[str] | IO[bytes],
):
    data = {
        "type": "SystemContextDiagram",
        "title": "Online Shop",
    }
    spied_diagram_from_dict = mocker.spy(converter_module, "diagram_from_dict")

    diagram = diagram_from_json(src)

    assert isinstance(diagram, SystemContextDiagram)
    assert spied_diagram_from_dict.spy_return == diagram
    spied_diagram_from_dict.assert_called_once_with(data)


@pytest.mark.parametrize(
    "src",
    [
        "{invalid json}",
        b"{invalid json}",
        StringIO("{invalid json}"),
        BytesIO(b"{invalid json}"),
    ],
)
def test_diagram_from_json__invalid_json(
    mocker: MockerFixture,
    src: str | bytes | IO[str] | IO[bytes],
):
    spied_diagram_from_dict = mocker.spy(converter_module, "diagram_from_dict")
    expected_error = re.escape(
        "Failed to parse JSON diagram: "
        "Expecting property name enclosed in double quotes: "
        "line 1 column 2 (char 1)"
    )

    with pytest.raises(DiagramJSONSchemaParsingError, match=expected_error):
        diagram_from_json(src)

    spied_diagram_from_dict.assert_not_called()


def test_diagram_from_json__invalid_json_in_path(
    tmp_path: Path,
    mocker: MockerFixture,
):
    path = tmp_path / "diagram.json"
    path.write_text("{invalid json}", encoding="utf-8")
    spied_diagram_from_dict = mocker.spy(converter_module, "diagram_from_dict")

    with pytest.raises(DiagramJSONSchemaParsingError):
        diagram_from_json(path)

    spied_diagram_from_dict.assert_not_called()


@pytest.mark.parametrize(
    "src",
    [
        '{"type": "SystemContextDiagram", "title": "Online Shop"}',
        StringIO('{"type": "SystemContextDiagram", "title": "Online Shop"}'),
    ],
)
def test_diagram_from_json__propagates_error(
    mocker: MockerFixture,
    src: str | IO[str],
):
    mocker.patch.object(
        converter_module,
        "diagram_from_dict",
        side_effect=ValueError("invalid structure/schema"),
    )

    with pytest.raises(ValueError, match="invalid structure/schema"):
        diagram_from_json(src)

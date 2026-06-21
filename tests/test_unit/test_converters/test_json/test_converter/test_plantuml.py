from __future__ import annotations

import re
from typing import Any

import pytest

from c4 import Rel, Relationship, SystemBoundary
from c4.contrib.plantuml import (
    Layout,
    LayoutType,
    RelDown,
    increment,
    set_index,
)
from c4.converters.exceptions import (
    DiagramJSONSchemaValidationError,
    ElementResolutionError,
)
from c4.converters.json.converter import JSONToDiagramConverter
from c4.renderers.plantuml.options import (
    DiagramLayout,
    ElementTag,
    PlantUMLRenderOptions,
    ShowLegend,
)


def _get_ordered_layouts(diagram: Any) -> list[Layout]:
    return [
        item for item in diagram.ordered_elements if isinstance(item, Layout)
    ]


@pytest.fixture()
def system_context_diagram_dict() -> dict[str, Any]:
    return {
        "backend": "plantuml",
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
        "backend": "plantuml",
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
        "backend": "plantuml",
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
        "steps": [
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
    }


@pytest.fixture()
def missing_target_system_context_diagram_dict() -> dict[str, Any]:
    return {
        "backend": "plantuml",
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


@pytest.fixture()
def diagram_with_plantuml_render_options() -> dict[str, Any]:
    return {
        "backend": "plantuml",
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
                "type": "System",
                "label": "Retail Platform",
                "alias": "retail_platform",
                "description": (
                    "Core platform for catalog, checkout, and order management."
                ),
                "tags": ["system", "core"],
                "link": "https://retail.example.com",
            },
        ],
        "render_options": {
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
    }


def test_json_to_diagram_converter__plantuml_backend_adds_layouts(
    system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(system_context_diagram_dict)
    diagram = converter._diagram
    with diagram:
        converter._add_elements(converter._diagram_schema)

    with diagram:
        converter._add_plantuml_layouts()

    customer = diagram.get_element_by_alias("customer")
    shop = diagram.get_element_by_alias("shop")
    orders_db = diagram.get_element_by_alias("orders_db")
    layouts = _get_ordered_layouts(diagram)
    assert len(layouts) == 2
    assert layouts[0].from_element == customer
    assert layouts[0].to_element == shop
    assert layouts[0].layout_type == LayoutType.LAY_R
    assert layouts[1].from_element == shop
    assert layouts[1].to_element == orders_db
    assert layouts[1].layout_type == LayoutType.LAY_D


def test_json_to_diagram_converter__plantuml_backend_layout_resolution_error(
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
        converter._add_plantuml_layouts()

    assert not _get_ordered_layouts(diagram)


def test_json_to_diagram_converter__plantuml_backend_dynamic_index_statements(
    dynamic_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(dynamic_diagram_dict)
    diagram = converter._diagram
    with diagram:
        converter._add_elements(converter._diagram_schema)

    with diagram:
        converter._add_relationships(converter._diagram_schema)

    customer = diagram.get_element_by_alias("customer")
    shop = diagram.get_element_by_alias("shop")
    orders_db = diagram.get_element_by_alias("orders_db")
    assert len(diagram.ordered_elements) == 7
    assert isinstance(diagram.ordered_elements[3], Relationship)
    assert isinstance(diagram.ordered_elements[4], increment)
    assert isinstance(diagram.ordered_elements[5], Relationship)
    assert isinstance(diagram.ordered_elements[6], set_index)
    assert diagram.ordered_elements[3].get_participants() == (customer, shop)
    assert diagram.ordered_elements[4].offset == 2
    assert diagram.ordered_elements[5].get_participants() == (shop, orders_db)
    assert diagram.ordered_elements[6].new_index == 10


def test_json_to_diagram_converter__plantuml_backend_dynamic_boundary_steps():
    data = {
        "backend": "plantuml",
        "type": "DynamicDiagram",
        "title": "Online Shop",
        "boundaries": [
            {
                "type": "SystemBoundary",
                "alias": "shop_boundary",
                "label": "Shop",
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
                ],
                "steps": [
                    {
                        "type": "REL",
                        "from": "customer",
                        "to": "shop",
                        "label": "Uses",
                    },
                    {
                        "type": "increment",
                        "offset": 2,
                    },
                ],
            }
        ],
        "steps": [
            {
                "type": "set_index",
                "new_index": 10,
            }
        ],
    }

    diagram = JSONToDiagramConverter(data).convert()

    shop_boundary = diagram.boundaries[0]
    assert isinstance(shop_boundary, SystemBoundary)
    assert len(shop_boundary.ordered_elements) == 4
    assert isinstance(shop_boundary.ordered_elements[2], Relationship)
    assert isinstance(shop_boundary.ordered_elements[3], increment)
    assert isinstance(diagram.ordered_elements[1], set_index)


def test_json_to_diagram_converter__plantuml_backend_sets_render_options(
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


def test_json_to_diagram_converter__plantuml_backend_direct_render_options():
    data = {
        "backend": "plantuml",
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "render_options": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "hide_stereotype": False,
        },
    }
    converter = JSONToDiagramConverter(data)

    diagram = converter.convert()

    assert diagram.render_options is not None
    assert diagram.render_options.plantuml == PlantUMLRenderOptions(
        layout=DiagramLayout.LAYOUT_LEFT_RIGHT,
        hide_stereotype=False,
    )
    assert diagram.render_options.mermaid is None


def test_json_to_diagram_converter__plantuml_backend_rejects_nested_options():
    data = {
        "backend": "plantuml",
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "render_options": {
            "plantuml": {
                "layout": "LAYOUT_LEFT_RIGHT",
            },
        },
    }

    with pytest.raises(
        DiagramJSONSchemaValidationError,
        match="root->SystemContextDiagram->render_options->plantuml: Extra inputs are not permitted",
    ):
        JSONToDiagramConverter(data).convert()


def test_json_to_diagram_converter__plantuml_fields_become_extensions():
    data = {
        "backend": "plantuml",
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "elements": [
            {
                "type": "System",
                "label": "Retail Platform",
                "alias": "retail_platform",
                "stereotype": "Core System",
                "sprite": "server",
                "tags": ["core"],
                "link": "https://retail.example.com",
                "base_shape": "RoundedBox",
            },
        ],
    }
    converter = JSONToDiagramConverter(data)

    diagram = converter.convert()
    element = diagram.get_element_by_alias("retail_platform")

    assert element is not None
    assert element.extensions == {
        "plantuml": {
            "type": "Core System",
            "sprite": "server",
            "tags": ["core"],
            "link": "https://retail.example.com",
            "base_shape": "RoundedBox",
        }
    }


def test_json_to_diagram_converter__plantuml_backend_converts_layouts_and_shortcuts(
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
    relationship = diagram.relationships[0]
    assert isinstance(relationship, Rel)
    assert relationship.get_participants() == (customer, shop)
    layouts = _get_ordered_layouts(diagram)
    assert len(layouts) == 2
    assert layouts[0].from_element == customer
    assert layouts[0].to_element == shop
    assert layouts[0].layout_type == LayoutType.LAY_R
    assert layouts[1].from_element == shop
    assert layouts[1].to_element == orders_db
    assert layouts[1].layout_type == LayoutType.LAY_D
    shop_boundary = diagram.boundaries[0]
    assert isinstance(shop_boundary, SystemBoundary)
    assert shop_boundary.elements == [shop]
    assert len(shop_boundary.relationships) == 1
    shop_relationship = shop_boundary.relationships[0]
    assert isinstance(shop_relationship, RelDown)
    assert shop_relationship.get_participants() == (shop, orders_db)


def test_json_to_diagram_converter__plantuml_backend_layout_resolution_from_convert(
    missing_target_system_context_diagram_dict: dict[str, Any],
):
    converter = JSONToDiagramConverter(
        missing_target_system_context_diagram_dict
    )
    expected_error = re.escape(
        "Could not resolve an element with alias or label: 'missing_system'"
    )

    with pytest.raises(ElementResolutionError, match=expected_error):
        converter.convert()

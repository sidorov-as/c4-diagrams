from typing import Any

import pytest

from c4.converters.exceptions import DiagramJSONSchemaValidationError
from c4.converters.json.converter import (
    JSONToDiagramConverter,
    diagram_from_dict,
)
from c4.enums import RendererEnum
from c4.renderers import D2RenderOptions


def test_json_to_diagram_converter__d2_backend_sets_render_options():
    data: dict[str, Any] = {
        "backend": "d2",
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "elements": [
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer",
            },
            {
                "type": "System",
                "alias": "retail_platform",
                "label": "Retail Platform",
            },
        ],
        "relationships": [
            {
                "type": "BI_REL",
                "from": "customer",
                "to": "retail_platform",
                "label": "Uses",
            }
        ],
        "render_options": {
            "direction": "down",
            "layout": "elk",
            "theme": 4,
            "title_near": "bottom-center",
            "sequence_diagram": True,
            "auto_number_relationships": True,
            "include_type_label": False,
            "include_technology": False,
            "include_properties": True,
            "bidirectional_relationships": "single_edge",
            "fully_qualified_relationships": False,
        },
    }

    diagram, backend = diagram_from_dict(data)

    assert backend is RendererEnum.D2
    assert diagram.render_options is not None
    assert diagram.render_options.d2 == D2RenderOptions(
        direction="down",
        layout="elk",
        theme=4,
        title_near="bottom-center",
        sequence_diagram=True,
        auto_number_relationships=True,
        include_type_label=False,
        include_technology=False,
        include_properties=True,
        bidirectional_relationships="single_edge",
        fully_qualified_relationships=False,
    )
    assert diagram.render_options.plantuml is None
    assert diagram.render_options.mermaid is None


def test_json_to_diagram_converter__d2_backend_accepts_no_render_options():
    data: dict[str, Any] = {
        "backend": "d2",
        "type": "SystemContextDiagram",
        "elements": [{"type": "System", "alias": "shop", "label": "Shop"}],
    }

    diagram, backend = diagram_from_dict(data)

    assert backend is RendererEnum.D2
    assert diagram.render_options is None


def test_json_to_diagram_converter__core_diagram_without_d2_options_still_validates():
    data: dict[str, Any] = {
        "type": "SystemContextDiagram",
        "elements": [{"type": "System", "alias": "shop", "label": "Shop"}],
    }

    diagram, backend = diagram_from_dict(data)

    assert backend is None
    assert diagram.render_options is None


def test_json_to_diagram_converter__d2_backend_rejects_invalid_direction():
    data: dict[str, Any] = {
        "backend": "d2",
        "type": "SystemContextDiagram",
        "render_options": {"direction": "diagonal"},
    }

    with pytest.raises(DiagramJSONSchemaValidationError, match="direction"):
        JSONToDiagramConverter(data)


def test_json_to_diagram_converter__d2_backend_rejects_invalid_option_type():
    data: dict[str, Any] = {
        "backend": "d2",
        "type": "SystemContextDiagram",
        "render_options": {"include_properties": {"enabled": True}},
    }

    with pytest.raises(
        DiagramJSONSchemaValidationError,
        match="include_properties",
    ):
        JSONToDiagramConverter(data)


def test_json_to_diagram_converter__d2_fields_become_extensions():
    data: dict[str, Any] = {
        "backend": "d2",
        "type": "ContainerDiagram",
        "elements": [
            {
                "type": "Person",
                "alias": "customer",
                "label": "Customer",
                "shape": "person",
                "style": {"fill": "#eef", "stroke_dash": 2},
                "icon": "https://example.com/user.svg",
                "near": "top-center",
                "tooltip": "External user",
                "link": "https://example.com/users",
                "classes": ["actor", "external"],
            }
        ],
        "boundaries": [
            {
                "type": "ContainerBoundary",
                "alias": "backend",
                "label": "Backend",
                "direction": "down",
                "elements": [
                    {
                        "type": "Container",
                        "alias": "api",
                        "label": "API",
                        "technology": "Python",
                    }
                ],
            }
        ],
        "relationships": [
            {
                "type": "BI_REL",
                "from": "customer",
                "to": "api",
                "label": "Uses",
                "style": {"animated": True, "stroke": "blue"},
                "classes": ["important"],
                "tooltip": "Bidirectional sync",
            }
        ],
    }

    diagram = JSONToDiagramConverter(data).convert()
    customer = diagram.get_element_by_alias("customer")
    backend = diagram.get_element_by_alias("backend")
    relationship = diagram.relationships[0]

    assert customer is not None
    assert customer.extensions == {
        "d2": {
            "shape": "person",
            "style": {"fill": "#eef", "stroke_dash": 2},
            "icon": "https://example.com/user.svg",
            "near": "top-center",
            "tooltip": "External user",
            "link": "https://example.com/users",
            "classes": ["actor", "external"],
        }
    }
    assert backend is not None
    assert backend.extensions == {"d2": {"direction": "down"}}
    assert relationship.extensions == {
        "d2": {
            "style": {"animated": True, "stroke": "blue"},
            "classes": ["important"],
            "tooltip": "Bidirectional sync",
        }
    }


def test_json_to_diagram_converter__d2_backend_rejects_invalid_extension_field():
    data: dict[str, Any] = {
        "backend": "d2",
        "type": "SystemContextDiagram",
        "elements": [
            {
                "type": "System",
                "alias": "shop",
                "label": "Shop",
                "extensions": {
                    "d2": {"shape": "rectangle", "style": {"fill": "#fff"}},
                    "plantuml": {"sprite": "server"},
                },
                "shape": "cloud",
                "tooltip": "Primary system",
            }
        ],
    }

    with pytest.raises(DiagramJSONSchemaValidationError, match="extensions"):
        JSONToDiagramConverter(data).convert()


def test_json_to_diagram_converter__d2_backend_rejects_invalid_style_key():
    data: dict[str, Any] = {
        "backend": "d2",
        "type": "SystemContextDiagram",
        "elements": [
            {
                "type": "System",
                "alias": "shop",
                "label": "Shop",
                "style": {"unknown": "value"},
            }
        ],
    }

    with pytest.raises(DiagramJSONSchemaValidationError, match="unknown"):
        JSONToDiagramConverter(data).convert()

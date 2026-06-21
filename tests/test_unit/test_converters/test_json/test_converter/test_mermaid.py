from __future__ import annotations

import re
from typing import Any

import pytest

from c4.converters.exceptions import DiagramJSONSchemaValidationError
from c4.converters.json.converter import JSONToDiagramConverter
from c4.renderers import MermaidRenderOptions
from c4.renderers.mermaid.options import (
    ElementStyle,
    RelStyle,
    UpdateLayoutConfig,
)


@pytest.fixture()
def diagram_with_mermaid_render_options():
    return {
        "backend": "mermaid",
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "elements": [
            {
                "type": "Person",
                "label": "Customer",
                "alias": "customer",
                "description": "Places orders through the storefront.",
            },
            {
                "type": "PersonExt",
                "label": "Support Agent",
                "alias": "support_agent",
                "description": "Handles issues in an external CRM.",
            },
            {
                "type": "System",
                "label": "Retail Platform",
                "alias": "retail_platform",
                "description": (
                    "Core platform for catalog, checkout, and order management."
                ),
            },
            {
                "type": "SystemExt",
                "label": "Payment Gateway",
                "alias": "payment_gateway",
                "description": "Processes card payments.",
            },
        ],
        "boundaries": [
            {
                "type": "EnterpriseBoundary",
                "label": "Acme Corp",
                "alias": "acme_enterprise",
                "description": "Internal systems owned by Acme.",
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
        "render_options": {
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
        },
    }


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


def test_json_to_diagram_converter__set_empty_render_options__mermaid():
    data = {
        "backend": "mermaid",
        "type": "SystemContextDiagram",
        "render_options": {},
    }

    diagram = JSONToDiagramConverter(data).convert()

    assert diagram.render_options is not None
    assert diagram.render_options.mermaid == MermaidRenderOptions()
    assert diagram.render_options.plantuml is None


def test_json_to_diagram_converter__mermaid_backend_rejects_plantuml_fields():
    data = {
        "backend": "mermaid",
        "type": "SystemContextDiagram",
        "title": "Retail Platform",
        "elements": [
            {
                "type": "System",
                "label": "Retail Platform",
                "alias": "retail_platform",
                "sprite": "server",
            },
        ],
    }

    with pytest.raises(
        DiagramJSONSchemaValidationError,
        match="root->SystemContextDiagram->elements\\[0\\]->MermaidSystemSchema->sprite: Extra inputs are not permitted",
    ):
        JSONToDiagramConverter(data).convert()


def test_json_to_diagram_converter__mermaid_backend_rejects_relationship_to_boundary():
    data = {
        "backend": "mermaid",
        "type": "SystemContextDiagram",
        "elements": [
            {
                "type": "Person",
                "label": "Customer",
                "alias": "customer",
            },
        ],
        "boundaries": [
            {
                "type": "SystemBoundary",
                "label": "Platform",
                "alias": "platform",
                "elements": [
                    {
                        "type": "System",
                        "label": "Web App",
                        "alias": "web_app",
                    },
                ],
            },
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "platform",
                "label": "Uses",
            },
        ],
    }
    expected_error = (
        "Mermaid relationships cannot target boundaries: "
        "customer -> platform targets SystemBoundary(platform). "
        "Use a concrete nested element instead."
    )

    with pytest.raises(
        DiagramJSONSchemaValidationError,
        match=re.escape(expected_error),
    ):
        JSONToDiagramConverter(data).convert()


def test_json_to_diagram_converter__mermaid_backend_allows_relationship_to_nested_element():
    data = {
        "backend": "mermaid",
        "type": "SystemContextDiagram",
        "elements": [
            {
                "type": "Person",
                "label": "Customer",
                "alias": "customer",
            },
        ],
        "boundaries": [
            {
                "type": "SystemBoundary",
                "label": "Platform",
                "alias": "platform",
                "elements": [
                    {
                        "type": "System",
                        "label": "Web App",
                        "alias": "web_app",
                    },
                ],
            },
        ],
        "relationships": [
            {
                "type": "REL",
                "from": "customer",
                "to": "web_app",
                "label": "Uses",
            },
        ],
    }

    diagram = JSONToDiagramConverter(data).convert()

    assert diagram.relationships[0].to_element is not None
    assert diagram.relationships[0].to_element.alias == "web_app"


def test_json_to_diagram_converter__mermaid_backend_rejects_dynamic_index():
    data = {
        "backend": "mermaid",
        "type": "DynamicDiagram",
        "title": "Retail Platform",
        "relationships": [
            {
                "type": "increment",
                "offset": 2,
            },
        ],
    }

    with pytest.raises(
        DiagramJSONSchemaValidationError,
        match="root->DynamicDiagram->relationships\\[0\\]->type: Input should be 'REL'",
    ):
        JSONToDiagramConverter(data).convert()

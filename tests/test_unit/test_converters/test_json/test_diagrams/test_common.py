from c4.converters.json.converter import JSONToDiagramConverter
from c4.diagrams.core import DiagramElementProperties
from tests.test_unit.test_converters.test_json.test_diagrams.conftest import (
    GetDiagramSchema,
)


def test_add_properties__show_header(
    get_diagram_schema: GetDiagramSchema,
):
    data = {
        "type": "SystemContextDiagram",
        "elements": [
            {
                "type": "Person",
                "label": "Store Manager",
                "alias": "store_manager",
                "description": "Manages product catalog and promotions.",
                "stereotype": "Business User",
                "sprite": "user",
                "tags": ["person", "internal"],
                "link": "https://intranet.example.com",
                "properties": {
                    "properties": [
                        ["Department", "Retail Ops"],
                        ["Role", "Manager"],
                    ]
                },
            }
        ],
    }
    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()
    element = diagram.elements[0]

    properties = element.properties

    assert isinstance(properties, DiagramElementProperties)
    assert properties.show_header is True
    assert properties.header == ["Property", "Value"]
    assert properties.properties == [
        ["Department", "Retail Ops"],
        ["Role", "Manager"],
    ]


def test_add_properties__show_header_is_false(
    get_diagram_schema: GetDiagramSchema,
):
    data = {
        "type": "SystemContextDiagram",
        "elements": [
            {
                "type": "Person",
                "label": "Store Manager",
                "alias": "store_manager",
                "description": "Manages product catalog and promotions.",
                "stereotype": "Business User",
                "sprite": "user",
                "tags": ["person", "internal"],
                "link": "https://intranet.example.com",
                "properties": {
                    "show_header": False,
                    "header": ["Override", "Header"],
                    "properties": [
                        ["Department", "Retail Ops"],
                        ["Role", "Manager"],
                    ],
                },
            }
        ],
    }
    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()
    element = diagram.elements[0]

    properties = element.properties

    assert isinstance(properties, DiagramElementProperties)
    assert properties.show_header is False
    assert properties.header == ["Property", "Value"]
    assert properties.properties == [
        ["Department", "Retail Ops"],
        ["Role", "Manager"],
    ]


def test_add_properties__override_header(
    get_diagram_schema: GetDiagramSchema,
):
    data = {
        "type": "SystemContextDiagram",
        "elements": [
            {
                "type": "Person",
                "label": "Store Manager",
                "alias": "store_manager",
                "description": "Manages product catalog and promotions.",
                "stereotype": "Business User",
                "sprite": "user",
                "tags": ["person", "internal"],
                "link": "https://intranet.example.com",
                "properties": {
                    "show_header": True,
                    "header": ["Override", "Header"],
                    "properties": [
                        ["Department", "Retail Ops"],
                        ["Role", "Manager"],
                    ],
                },
            }
        ],
    }
    converter = JSONToDiagramConverter(data)
    diagram = converter.convert()
    element = diagram.elements[0]

    properties = element.properties

    assert isinstance(properties, DiagramElementProperties)
    assert properties.show_header is True
    assert properties.header == ["Override", "Header"]
    assert properties.properties == [
        ["Department", "Retail Ops"],
        ["Role", "Manager"],
    ]

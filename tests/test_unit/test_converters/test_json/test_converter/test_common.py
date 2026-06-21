from __future__ import annotations

import re
import textwrap
from importlib import import_module
from io import BytesIO, StringIO
from pathlib import Path
from typing import IO, Any

import pytest
from pytest_mock import MockerFixture

from c4 import (
    Person,
    Rel,
    Relationship,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemDb,
)
from c4.contrib.mermaid.converters.json.schemas import (
    MermaidSystemContextDiagramSchema,
)
from c4.contrib.plantuml.converters.json.schemas import (
    PlantUMLSystemContextDiagramSchema,
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
    diagram_backend_from_json,
    diagram_from_dict,
    diagram_from_json,
)
from c4.converters.json.schemas.backends.core import (
    CoreSystemContextDiagramSchema,
)
from c4.converters.json.schemas.diagrams.system_context import PersonSchema
from c4.enums import RendererEnum


def test_json_schema_backends_keep_backend_fields_out_of_shared_schemas():
    person_schema = PersonSchema.model_json_schema()
    core_schema = CoreSystemContextDiagramSchema.model_json_schema()
    mermaid_schema = MermaidSystemContextDiagramSchema.model_json_schema()
    plantuml_schema = PlantUMLSystemContextDiagramSchema.model_json_schema()

    assert set(person_schema["properties"]) == {
        "type",
        "label",
        "description",
        "alias",
        "properties",
    }
    assert "backend" not in core_schema["properties"]
    assert "layouts" not in core_schema["properties"]
    assert "render_options" not in core_schema["properties"]
    assert "layouts" not in mermaid_schema["properties"]
    assert "render_options" in mermaid_schema["properties"]
    assert "layouts" in plantuml_schema["properties"]
    assert "render_options" in plantuml_schema["properties"]


def test_json_to_diagram_converter__core_rejects_plantuml_relationship(
    system_context_diagram_dict: dict[str, Any],
):
    system_context_diagram_dict["relationships"][0]["type"] = "REL_BACK"

    with pytest.raises(DiagramJSONSchemaValidationError) as exc_info:
        JSONToDiagramConverter(system_context_diagram_dict)

    assert "Input should be 'REL'" in str(exc_info.value)


def test_module_entrypoint_import_is_side_effect_free():
    module = import_module("c4.__main__")

    assert module.entrypoint


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
                            }
                        ],
                    }
                ],
                "relationships": [
                    {
                        "type": "REL",
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
                "type": "REL",
                "from": "shop",
                "to": "orders_db",
                "label": "Reads/Writes",
                "technology": "SQL",
            },
        ],
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


def test_json_to_diagram_converter__add_relationships__dynamic_diagram(
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
    assert len(diagram.ordered_elements) == 5
    assert isinstance(diagram.ordered_elements[3], Relationship)
    assert isinstance(diagram.ordered_elements[4], Relationship)
    assert diagram.ordered_elements[3].get_participants() == (customer, shop)
    assert diagram.ordered_elements[4].get_participants() == (shop, orders_db)


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
    shop_boundary = diagram.boundaries[0]
    assert isinstance(shop_boundary, SystemBoundary)
    assert shop_boundary.label == "Online Shop Platform"
    assert shop_boundary.elements == [shop]
    assert len(shop_boundary.boundaries) == 1
    assert len(shop_boundary.relationships) == 1
    shop_relationship1 = shop_boundary.relationships[0]
    assert isinstance(shop_relationship1, Rel)
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

    diagram, backend = diagram_from_dict(nested_system_context_diagram_dict)

    spied_converter.assert_called_once_with(
        mocker.ANY,  # self
        nested_system_context_diagram_dict,
    )
    spied_convert.assert_called_once()
    assert spied_convert.spy_return == diagram
    assert backend is None


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

    diagram, backend = diagram_from_json(src)

    assert isinstance(diagram, SystemContextDiagram)
    assert backend is None
    assert spied_diagram_from_dict.spy_return == (diagram, backend)
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

    diagram, backend = diagram_from_json(path)

    assert isinstance(diagram, SystemContextDiagram)
    assert backend is None
    assert spied_diagram_from_dict.spy_return == (diagram, backend)
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

    diagram, backend = diagram_from_json(src)

    assert isinstance(diagram, SystemContextDiagram)
    assert backend is None
    assert spied_diagram_from_dict.spy_return == (diagram, backend)
    spied_diagram_from_dict.assert_called_once_with(data)


@pytest.mark.parametrize(
    ("src", "data", "expected_backend"),
    [
        (
            '{"type": "SystemContextDiagram", "title": "Online Shop"}',
            {
                "type": "SystemContextDiagram",
                "title": "Online Shop",
            },
            None,
        ),
        (
            (
                b'{"type": "SystemContextDiagram", '
                b'"title": "Online Shop", "backend": "plantuml"}'
            ),
            {
                "type": "SystemContextDiagram",
                "title": "Online Shop",
                "backend": "plantuml",
            },
            RendererEnum.PLANTUML,
        ),
    ],
)
def test_diagram_backend_from_json__string_or_bytes(
    mocker: MockerFixture,
    src: str | bytes,
    data: dict[str, Any],
    expected_backend: RendererEnum | None,
):
    spied_parse_diagram_backend = mocker.spy(
        JSONToDiagramConverter, "parse_diagram_backend"
    )

    backend = diagram_backend_from_json(src)

    assert backend == expected_backend
    assert spied_parse_diagram_backend.spy_return == expected_backend
    spied_parse_diagram_backend.assert_called_once_with(data)


def test_diagram_backend_from_json__path(
    tmp_path: Path,
    mocker: MockerFixture,
):
    path = tmp_path / "diagram.json"
    path.write_text(
        (
            '{"type": "SystemContextDiagram", '
            '"title": "Online Shop", "backend": "mermaid"}'
        ),
        encoding="utf-8",
    )
    data = {
        "type": "SystemContextDiagram",
        "title": "Online Shop",
        "backend": "mermaid",
    }
    spied_parse_diagram_backend = mocker.spy(
        JSONToDiagramConverter, "parse_diagram_backend"
    )

    backend = diagram_backend_from_json(path)

    assert backend == RendererEnum.MERMAID
    assert spied_parse_diagram_backend.spy_return == RendererEnum.MERMAID
    spied_parse_diagram_backend.assert_called_once_with(data)


@pytest.mark.parametrize(
    "src",
    [
        StringIO(
            '{"type": "SystemContextDiagram", '
            '"title": "Online Shop", "backend": "plantuml"}'
        ),
        BytesIO(
            b'{"type": "SystemContextDiagram", '
            b'"title": "Online Shop", "backend": "plantuml"}'
        ),
    ],
)
def test_diagram_backend_from_json__file_object(
    mocker: MockerFixture,
    src: IO[str] | IO[bytes],
):
    data = {
        "type": "SystemContextDiagram",
        "title": "Online Shop",
        "backend": "plantuml",
    }
    spied_parse_diagram_backend = mocker.spy(
        JSONToDiagramConverter, "parse_diagram_backend"
    )

    backend = diagram_backend_from_json(src)

    assert backend == RendererEnum.PLANTUML
    assert spied_parse_diagram_backend.spy_return == RendererEnum.PLANTUML
    spied_parse_diagram_backend.assert_called_once_with(data)


@pytest.mark.parametrize(
    "src",
    [
        "{invalid json}",
        b"{invalid json}",
        StringIO("{invalid json}"),
        BytesIO(b"{invalid json}"),
    ],
)
def test_diagram_backend_from_json__invalid_json(
    mocker: MockerFixture,
    src: str | bytes | IO[str] | IO[bytes],
):
    spied_parse_diagram_backend = mocker.spy(
        JSONToDiagramConverter, "parse_diagram_backend"
    )
    expected_error = re.escape(
        "Failed to parse JSON diagram: "
        "Expecting property name enclosed in double quotes: "
        "line 1 column 2 (char 1)"
    )

    with pytest.raises(DiagramJSONSchemaParsingError, match=expected_error):
        diagram_backend_from_json(src)

    spied_parse_diagram_backend.assert_not_called()


def test_diagram_backend_from_json__invalid_json_in_path(
    tmp_path: Path,
    mocker: MockerFixture,
):
    path = tmp_path / "diagram.json"
    path.write_text("{invalid json}", encoding="utf-8")
    spied_parse_diagram_backend = mocker.spy(
        JSONToDiagramConverter, "parse_diagram_backend"
    )

    with pytest.raises(DiagramJSONSchemaParsingError):
        diagram_backend_from_json(path)

    spied_parse_diagram_backend.assert_not_called()


def test_diagram_backend_from_json__propagates_error(
    mocker: MockerFixture,
):
    mocker.patch.object(
        JSONToDiagramConverter,
        "parse_diagram_backend",
        side_effect=ValueError("invalid structure/schema"),
    )

    with pytest.raises(ValueError, match="invalid structure/schema"):
        diagram_backend_from_json(
            '{"type": "SystemContextDiagram", "title": "Online Shop"}'
        )


def test_diagram_backend_from_json__validation_error():
    expected_error = re.escape(
        "root->backend: Input should be 'plantuml', 'mermaid', "
        "'structurizr' or 'd2'"
    )

    with pytest.raises(DiagramJSONSchemaValidationError, match=expected_error):
        diagram_backend_from_json(
            '{"type": "SystemContextDiagram", '
            '"title": "Online Shop", "backend": "unknown"}'
        )


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

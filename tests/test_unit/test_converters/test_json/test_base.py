from typing import Generic

import pytest
from pydantic import ConfigDict

from c4.converters.json.schemas.base import BaseSchemaItem, TDiagramElement
from c4.diagrams.core import BaseDiagramElement


class _TestSchemaItem(BaseSchemaItem):
    """
    Docstrings goes here.
    """


class _TestSchemaItemWithCustomDescription(BaseSchemaItem):
    """
    Docstrings goes here.
    """

    model_config = ConfigDict(
        json_schema_extra={"description": "Custom description"}
    )


class _NonDiagramElement: ...


class _TestDiagramElement(BaseDiagramElement): ...


class _TestSchemaItemWithElement(BaseSchemaItem[_TestDiagramElement]): ...


class _TestSchemaItemWithElementGeneric(
    _TestSchemaItemWithElement,
    Generic[TDiagramElement],
): ...


class _TestSchemaItemWithDeclaredElement(BaseSchemaItem):
    __diagram_element__ = _TestDiagramElement


class _TestSchemaItemWithInvalidElement(BaseSchemaItem[_NonDiagramElement]): ...


def test_base_schema_item__to_diagram_element__not_provided():
    expected_error = f"__diagram_element__ not provided for {_TestSchemaItem!r}"
    item = _TestSchemaItem()

    with pytest.raises(ValueError, match=expected_error):
        item.to_diagram_element()


def test_base_schema_item__jsonschema():
    schema = _TestSchemaItem.model_json_schema()

    assert schema["title"] == "_TestSchemaItem"
    assert schema.get("description") is None


def test_base_schema_item__jsonschema__custom_description():
    schema = _TestSchemaItemWithCustomDescription.model_json_schema()

    assert schema["title"] == "_TestSchemaItemWithCustomDescription"
    assert schema["description"] == "Custom description"


def test_base_schema_item__jsonschema__diagram_element():
    schema = _TestSchemaItemWithElement.model_json_schema()

    assert schema["title"] == "_TestDiagramElement"
    assert schema.get("description") is None


@pytest.mark.parametrize(
    ("schema_item", "expected_element_class"),
    [
        (_TestSchemaItemWithElement, _TestDiagramElement),
        (_TestSchemaItemWithElementGeneric, _TestDiagramElement),
        (_TestSchemaItemWithDeclaredElement, _TestDiagramElement),
        (_TestSchemaItem, None),
        (_TestSchemaItemWithInvalidElement, None),
    ],
)
def test_base_schema_item__resolve_diagram_element_class(
    schema_item: type[BaseSchemaItem],
    expected_element_class: type[BaseDiagramElement],
):
    assert schema_item.__diagram_element__ is expected_element_class

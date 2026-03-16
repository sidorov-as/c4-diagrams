from __future__ import annotations

from typing import Annotated, Literal

import pytest
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from c4.converters.json.converter import format_validation_error


class ElementSchema(BaseModel):
    title: str
    technology: str


class DiagramSchema(BaseModel):
    title: str
    elements: list[ElementSchema]


class SystemContextDiagramSchema(BaseModel):
    type: Literal["SystemContextDiagram"]
    title: str


class ContainerDiagramSchema(BaseModel):
    type: Literal["ContainerDiagram"]
    title: str


AnyDiagramSchema = Annotated[
    SystemContextDiagramSchema | ContainerDiagramSchema,
    Field(discriminator="type"),
]

DIAGRAM_SCHEMA_ADAPTER = TypeAdapter(AnyDiagramSchema)


@pytest.fixture()
def nested_validation_error() -> ValidationError:
    with pytest.raises(ValidationError) as exc_info:
        DiagramSchema.model_validate({
            "title": "Online Shop",
            "elements": [
                {
                    "title": "Web App",
                    "technology": "Python",
                },
                {
                    "title": 123,
                    "technology": None,
                },
            ],
        })

    return exc_info.value


@pytest.fixture()
def union_tag_invalid_validation_error() -> ValidationError:
    with pytest.raises(ValidationError) as exc_info:
        DIAGRAM_SCHEMA_ADAPTER.validate_python({
            "type": "UnknownDiagramType",
            "title": "Online Shop",
        })

    return exc_info.value


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            {
                "title": "Online Shop",
                "elements": [
                    {
                        "title": "Web App",
                        "technology": "Python",
                    },
                    {
                        "title": 123,
                        "technology": "Django",
                    },
                ],
            },
            "root->elements[1]->title: Input should be a valid string",
        ),
        (
            {
                "title": "Online Shop",
                "elements": [
                    {
                        "title": "Web App",
                        "technology": "Python",
                    },
                    {
                        "title": "API",
                        "technology": None,
                    },
                ],
            },
            "root->elements[1]->technology: Input should be a valid string",
        ),
    ],
)
def test_format_validation_error_formats_nested_item_path(
    data: dict[str, object],
    expected: str,
):
    with pytest.raises(ValidationError) as exc_info:
        DiagramSchema.model_validate(data)

    result = format_validation_error(exc_info.value)

    assert result == expected


def test_format_validation_error_formats_union_tag_invalid_as_plain_message(
    union_tag_invalid_validation_error: ValidationError,
):
    expected_error = (
        "Input tag 'UnknownDiagramType' found using 'type' does not "
        "match any of the expected tags: 'SystemContextDiagram', "
        "'ContainerDiagram'"
    )

    result = format_validation_error(union_tag_invalid_validation_error)

    assert result == expected_error


def test_format_validation_error_formats_multiple_nested_errors(
    nested_validation_error: ValidationError,
):
    expected_error = (
        "root->elements[1]->title: Input should be a valid string\n"
        "root->elements[1]->technology: Input should be a valid string"
    )

    result = format_validation_error(nested_validation_error)

    assert result == expected_error


def test_format_validation_error_formats_root_level_model_error():
    expected_error = (
        "root: Input should be a valid dictionary or instance of DiagramSchema"
    )
    with pytest.raises(ValidationError) as exc_info:
        DiagramSchema.model_validate("invalid")

    result = format_validation_error(exc_info.value)

    assert result == expected_error


def test_format_validation_error_formats_missing_nested_field():
    with pytest.raises(ValidationError) as exc_info:
        DiagramSchema.model_validate({
            "title": "Online Shop",
            "elements": [
                {
                    "title": "Web App",
                }
            ],
        })

    result = format_validation_error(exc_info.value)

    assert result == "root->elements[0]->technology: Field required"


def test_format_validation_error_formats_missing_top_level_field():
    with pytest.raises(ValidationError) as exc_info:
        DiagramSchema.model_validate({
            "elements": [],
        })

    result = format_validation_error(exc_info.value)

    assert result == "root->title: Field required"

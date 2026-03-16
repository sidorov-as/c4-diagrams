from typing import Any, Protocol

import pytest

from c4.converters.json.converter import (
    AnyDiagramSchema,
    JSONToDiagramConverter,
)


@pytest.fixture()
def get_diagram_schema():
    def with_params(data: dict[str, Any]) -> AnyDiagramSchema:
        converter = JSONToDiagramConverter(data)
        converter.convert()
        return converter._diagram_schema

    return with_params


class GetDiagramSchema(Protocol):
    def __call__(self, data: dict[str, Any]) -> AnyDiagramSchema: ...

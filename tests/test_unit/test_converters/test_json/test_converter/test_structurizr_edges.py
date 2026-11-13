from __future__ import annotations

import copy

import pytest
from pydantic import ValidationError

from c4.contrib.structurizr.converters.json.converter import (
    JSONToStructurizrWorkspaceConverter,
)
from c4.contrib.structurizr.converters.json.schemas import (
    StructurizrWorkspaceSchema,
)

BASE = {
    "backend": "structurizr",
    "model": {
        "software_systems": [
            {
                "id": "shop",
                "name": "Shop",
                "containers": [{"id": "api", "name": "API"}],
            }
        ],
        "deployment": {
            "environments": [
                {
                    "name": "Live",
                    "deployment_nodes": [
                        {
                            "id": "region",
                            "name": "Region",
                            "deployment_nodes": [
                                {
                                    "id": "server",
                                    "name": "Server",
                                    "container_instances": [
                                        {"id": "api_1", "container": "api"}
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ]
        },
    },
    "views": {"items": []},
}


def _data() -> dict:
    return copy.deepcopy(BASE)


def _converter() -> JSONToStructurizrWorkspaceConverter:
    return JSONToStructurizrWorkspaceConverter(
        StructurizrWorkspaceSchema.model_validate(_data())
    )


def test_nested_deployment_nodes_convert_to_child_nodes():
    workspace = StructurizrWorkspaceSchema.model_validate(
        _data()
    ).to_workspace()

    assert [node.name for node in workspace.model.deployment_nodes] == [
        "Region",
        "Server",
    ]
    assert workspace.model.container_instances[0].parent_node.name == "Server"


def test_element_style_from_json_is_applied():
    data = _data()
    data["model"]["software_systems"][0]["style"] = {"background": "#ff0000"}

    workspace = StructurizrWorkspaceSchema.model_validate(data).to_workspace()

    assert workspace.model.software_systems[0].style_properties


def test_unknown_element_reference_is_rejected():
    with pytest.raises(ValueError, match="Unknown Structurizr element"):
        _converter()._element("missing")


def test_aliases_are_sanitized_and_unique():
    converter = _converter()

    assert converter._alias("1st") == "element_1st"
    assert converter._alias("class") == "element_class"
    assert converter._alias("a-b") == "a_b"
    assert converter._alias("a_b") == "a_b_2"
    assert converter._alias("a-b") == "a_b"


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (
            lambda d: d["model"]["software_systems"].append({
                "id": "shop",
                "name": "Again",
            }),
            "Duplicate workspace element id",
        ),
        (
            lambda d: d["model"]["deployment"]["environments"].append({
                "name": "Live"
            }),
            "Duplicate deployment environment",
        ),
        (
            lambda d: d["model"]["deployment"]["environments"][0][
                "deployment_nodes"
            ][0]["deployment_nodes"][0]["container_instances"][0].update(
                container="shop"
            ),
            "Unknown container instance reference",
        ),
        (
            lambda d: d["model"]["deployment"]["environments"][0][
                "deployment_nodes"
            ][0]["deployment_nodes"][0]["container_instances"].append({
                "id": "api_1",
                "container": "api",
            }),
            "Duplicate element id",
        ),
        (
            lambda d: d["views"]["items"].append({
                "type": "component",
                "scope": "shop",
            }),
            "component view scope must reference a container",
        ),
        (
            lambda d: d["views"]["items"].append({
                "type": "deployment",
                "scope": "api",
                "environment": "Live",
            }),
            "deployment view scope must reference a software system",
        ),
    ],
)
def test_schema_rejects_invalid_documents(mutate, message):
    data = _data()
    mutate(data)

    with pytest.raises(ValidationError, match=message):
        StructurizrWorkspaceSchema.model_validate(data)


def test_unscoped_dynamic_view_and_string_animation_selectors_are_valid():
    data = _data()
    data["views"]["items"] = [
        {
            "type": "dynamic",
            "steps": [{"from": "shop", "to": "api", "description": "x"}],
        },
        {
            "type": "container",
            "scope": "shop",
            "animation": [["*"], [{"id": "api"}]],
        },
    ]

    schema = StructurizrWorkspaceSchema.model_validate(data)

    assert schema.views.items[0].scope is None
    schema.to_workspace()

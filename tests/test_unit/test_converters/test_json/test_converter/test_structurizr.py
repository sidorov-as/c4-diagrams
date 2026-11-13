from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.converters.json.schemas import (
    StructurizrWorkspaceSchema,
)
from c4.converters.exceptions import DiagramJSONSchemaValidationError
from c4.converters.json.converter import diagram_from_dict
from c4.enums import RendererEnum
from tests.test_unit.test_converters.test_json.test_diagrams.test_structurizr import (
    complete_workspace,
    minimal_workspace,
)


def test_diagram_from_dict_converts_minimal_structurizr_workspace():
    workspace, backend = diagram_from_dict(minimal_workspace())

    assert isinstance(workspace, Workspace)
    assert workspace.name == "Workspace"
    assert backend is RendererEnum.STRUCTURIZR


def test_diagram_from_dict_converts_complete_structurizr_workspace():
    workspace, backend = diagram_from_dict(complete_workspace())

    assert isinstance(workspace, Workspace)
    assert backend is RendererEnum.STRUCTURIZR
    assert workspace.name == "Payments"
    assert workspace.theme is None
    assert len(workspace.views) == 6


def test_dynamic_steps_are_view_local_when_converted():
    workspace = StructurizrWorkspaceSchema.model_validate(
        complete_workspace()
    ).to_workspace()

    assert len(workspace.model.relationships) == 3


def test_diagram_from_dict_reports_invalid_structurizr_references():
    data = minimal_workspace()
    data["model"]["relationships"] = [
        {"from": "customer", "to": "missing"},
    ]

    with pytest.raises(
        DiagramJSONSchemaValidationError,
        match=re.escape(
            "root: Value error, model->relationships[0]->to: Unknown element "
            "id 'missing'"
        ),
    ):
        diagram_from_dict(data)


def test_structurizr_json_uses_opaque_ids_for_instances_and_references():
    workspace = StructurizrWorkspaceSchema.model_validate({
        "backend": "structurizr",
        "model": {
            "software_systems": [{"id": "payments-api", "name": "Payments"}],
            "deployment": {
                "environments": [
                    {
                        "name": "Production",
                        "deployment_nodes": [
                            {
                                "id": "server/1",
                                "name": "Server",
                                "software_system_instances": [
                                    {
                                        "id": "payments/primary",
                                        "software_system": "payments-api",
                                        "tags": ["Primary"],
                                    }
                                ],
                            }
                        ],
                    }
                ],
            },
        },
        "views": {"items": []},
    }).to_workspace()

    instance = workspace.model.software_system_instances[0]
    assert instance.alias == "payments_primary"
    assert instance.model_element.alias == "payments_api"


def test_structurizr_json_distinguishes_empty_instance_metadata_from_omission():
    data = complete_workspace()
    instance = data["model"]["deployment"]["environments"][0][
        "deployment_nodes"
    ][0]["container_instances"][0]
    instance["tags"] = []
    instance["properties"] = {}

    workspace = StructurizrWorkspaceSchema.model_validate(data).to_workspace()
    converted = workspace.model.container_instances[0]

    assert converted.tags == ()
    assert converted.properties == {}


def test_structurizr_json_requires_an_explicit_instance_target():
    with pytest.raises(ValidationError, match="Field required"):
        StructurizrWorkspaceSchema.model_validate({
            "backend": "structurizr",
            "model": {
                "software_systems": [{"id": "payments", "name": "Payments"}],
                "deployment": {
                    "environments": [
                        {
                            "name": "Production",
                            "deployment_nodes": [
                                {
                                    "id": "server",
                                    "name": "Server",
                                    "software_system_instances": [
                                        {"id": "payments_primary"}
                                    ],
                                }
                            ],
                        }
                    ],
                },
            },
            "views": {"items": []},
        })


def test_structurizr_json_rejects_deployment_views_for_empty_environments():
    with pytest.raises(ValidationError, match="Unknown deployment environment"):
        StructurizrWorkspaceSchema.model_validate({
            "backend": "structurizr",
            "model": {
                "software_systems": [{"id": "payments", "name": "Payments"}],
                "deployment": {"environments": [{"name": "Production"}]},
            },
            "views": {
                "items": [
                    {
                        "type": "deployment",
                        "scope": "payments",
                        "environment": "Production",
                    }
                ]
            },
        })

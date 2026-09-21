from __future__ import annotations

import re

import pytest
from pydantic import ValidationError

from c4.contrib.structurizr.converters.json.schemas import (
    StructurizrWorkspaceSchema,
)


def minimal_workspace() -> dict:
    return {
        "backend": "structurizr",
        "model": {"people": [{"id": "customer", "name": "Customer"}]},
        "views": {"items": [{"type": "system_landscape", "key": "landscape"}]},
    }


def complete_workspace() -> dict:
    return {
        "backend": "structurizr",
        "name": "Payments",
        "description": "Payments architecture",
        "styles": {
            "elements": [
                {
                    "target": "Critical",
                    "properties": {"background": "#ffcc00", "color": "#111111"},
                }
            ],
            "relationships": [
                {"target": "Persistent", "properties": {"thickness": 4}}
            ],
        },
        "model": {
            "people": [
                {
                    "id": "customer",
                    "name": "Customer",
                    "tags": ["External"],
                    "properties": {"segment": "retail"},
                    "url": "https://example.com/customer",
                }
            ],
            "software_systems": [
                {
                    "id": "payments",
                    "name": "Payments",
                    "description": "Collects money.",
                    "containers": [
                        {
                            "id": "web",
                            "name": "Web App",
                            "description": "Customer checkout UI.",
                            "technology": "Django",
                        },
                        {
                            "id": "api",
                            "name": "API",
                            "description": "Checkout API.",
                            "technology": "FastAPI",
                            "tags": ["Critical"],
                            "components": [
                                {
                                    "id": "checkout",
                                    "name": "Checkout",
                                    "technology": "Python",
                                }
                            ],
                        },
                        {
                            "id": "database",
                            "name": "Database",
                            "technology": "PostgreSQL",
                            "tags": ["Storage"],
                        },
                    ],
                }
            ],
            "relationships": [
                {
                    "from": "customer",
                    "to": "web",
                    "description": "Uses",
                    "technology": "HTTPS",
                },
                {
                    "from": "web",
                    "to": "api",
                    "description": "Calls",
                    "technology": "JSON/HTTPS",
                },
                {
                    "from": "api",
                    "to": "database",
                    "description": "Reads from and writes to",
                    "technology": "SQL",
                    "tags": ["Persistent"],
                },
            ],
            "deployment": {
                "environments": [
                    {
                        "name": "Production",
                        "deployment_nodes": [
                            {
                                "id": "k8s",
                                "name": "Kubernetes",
                                "infrastructure_nodes": [
                                    {"id": "ingress", "name": "Ingress"}
                                ],
                                "container_instances": [
                                    {"id": "api_instance", "container": "api"}
                                ],
                            }
                        ],
                    }
                ]
            },
        },
        "views": {
            "items": [
                {"type": "system_landscape", "key": "landscape"},
                {
                    "type": "system_context",
                    "scope": "payments",
                    "key": "context",
                    "include": [{"id": "customer"}, {"id": "payments"}],
                    "exclude": ["relationship.tag==Deprecated"],
                },
                {
                    "type": "container",
                    "scope": "payments",
                    "key": "containers",
                    "include": ["*", "element.tag==Storage"],
                    "auto_layout": {"rank_direction": "TopBottom"},
                    "animation": [
                        [{"id": "customer"}, {"id": "web"}],
                        [{"id": "api"}, {"id": "database"}],
                    ],
                },
                {"type": "component", "scope": "api", "key": "components"},
                {
                    "type": "dynamic",
                    "scope": "payments",
                    "key": "checkout-flow",
                    "steps": [
                        {
                            "from": "customer",
                            "to": "web",
                            "description": "Starts checkout",
                            "technology": "HTTPS",
                        },
                        {
                            "from": "web",
                            "to": "api",
                            "description": "Submits checkout",
                            "technology": "JSON/HTTPS",
                        },
                        {
                            "from": "api",
                            "to": "database",
                            "description": "Persists checkout",
                            "technology": "SQL",
                        },
                    ],
                },
                {
                    "type": "deployment",
                    "scope": "payments",
                    "environment": "Production",
                    "key": "production",
                },
            ]
        },
    }


def test_structurizr_workspace_schema_accepts_minimal_and_complete_payloads():
    assert (
        StructurizrWorkspaceSchema.model_validate(minimal_workspace()).name
        == "Workspace"
    )
    assert (
        StructurizrWorkspaceSchema.model_validate(complete_workspace()).name
        == "Payments"
    )


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda data: data.pop("backend"), "backend"),
        (lambda data: data.__setitem__("backend", "mermaid"), "structurizr"),
        (lambda data: data.__setitem__("unexpected", True), "unexpected"),
        (
            lambda data: data["model"]["people"][0].__setitem__(
                "unexpected", True
            ),
            "unexpected",
        ),
        (
            lambda data: data["model"].__setitem__(
                "relationships",
                [{"from": "customer", "to": "customer", "unexpected": True}],
            ),
            "unexpected",
        ),
        (
            lambda data: data["views"]["items"][0].__setitem__(
                "unexpected", True
            ),
            "unexpected",
        ),
        (
            lambda data: data.__setitem__(
                "styles",
                {"elements": [{"target": "Person", "unexpected": True}]},
            ),
            "unexpected",
        ),
        (
            lambda data: data.__setitem__(
                "render_options", {"unexpected": True}
            ),
            "unexpected",
        ),
    ],
)
def test_structurizr_workspace_schema_rejects_unknown_or_invalid_fields(
    mutation, message: str
):
    data = minimal_workspace()
    mutation(data)

    with pytest.raises(ValidationError, match=message):
        StructurizrWorkspaceSchema.model_validate(data)


def test_structurizr_workspace_schema_rejects_invalid_references_and_scopes():
    data = minimal_workspace()
    data["model"]["relationships"] = [{"from": "customer", "to": "missing"}]

    with pytest.raises(
        ValidationError,
        match=re.escape(
            "model->relationships[0]->to: Unknown element id 'missing'"
        ),
    ):
        StructurizrWorkspaceSchema.model_validate(data)

    data = minimal_workspace()
    data["views"]["items"] = [{"type": "container", "scope": "customer"}]
    with pytest.raises(
        ValidationError,
        match=re.escape(
            "views->items[0]->scope: container view scope must reference"
        ),
    ):
        StructurizrWorkspaceSchema.model_validate(data)


@pytest.mark.parametrize("environment", ["Missing", None])
def test_structurizr_workspace_schema_rejects_unknown_or_missing_deployment_environment(
    environment: str | None,
):
    data = minimal_workspace()
    view = {"type": "deployment"}
    if environment is not None:
        view["environment"] = environment
    data["views"]["items"] = [view]

    with pytest.raises(ValidationError, match="environment"):
        StructurizrWorkspaceSchema.model_validate(data)


def test_structurizr_workspace_schema_preserves_dynamic_step_order_without_model_relationships():
    data = complete_workspace()
    schema = StructurizrWorkspaceSchema.model_validate(data)
    dynamic = next(
        view for view in schema.views.items if view.type == "dynamic"
    )

    assert [step.description for step in dynamic.steps] == [
        "Starts checkout",
        "Submits checkout",
        "Persists checkout",
    ]
    assert len(schema.model.relationships) == 3

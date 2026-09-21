from __future__ import annotations

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import (
    StructurizrIdentifierRegistry,
    StructurizrRenderer,
)


def test_identifier_registry_sanitizes_aliases():
    assert StructurizrIdentifierRegistry.sanitize("api") == "api"
    assert (
        StructurizrIdentifierRegistry.sanitize("api-service") == "api_service"
    )
    assert (
        StructurizrIdentifierRegistry.sanitize("api.service") == "api_service"
    )
    assert (
        StructurizrIdentifierRegistry.sanitize("api service") == "api_service"
    )
    assert StructurizrIdentifierRegistry.sanitize("-api") == "el_api"
    assert StructurizrIdentifierRegistry.sanitize("123_api") == "el_123_api"
    assert StructurizrIdentifierRegistry.sanitize("") == "element"
    assert StructurizrIdentifierRegistry.sanitize("Тест") == "element"
    assert (
        StructurizrIdentifierRegistry.sanitize("api___service") == "api_service"
    )


def test_identifier_registry_avoids_structurizr_keywords():
    assert StructurizrIdentifierRegistry.sanitize("workspace") == "workspace_id"
    assert (
        StructurizrIdentifierRegistry.sanitize("softwareSystem")
        == "softwareSystem_id"
    )
    assert (
        StructurizrIdentifierRegistry.sanitize("autoLayout") == "autoLayout_id"
    )


def test_identifier_registry_avoids_renderer_reserved_words():
    assert StructurizrIdentifierRegistry.sanitize("rel") == "rel_id"
    assert StructurizrIdentifierRegistry.sanitize("rel1") == "rel1_id"


def test_identifier_registry_uses_aliases_not_labels():
    registry = StructurizrIdentifierRegistry()
    identifiers = {"user": registry.register_alias("user")}

    assert identifiers["user"].identifier == "user"
    assert "customer" not in identifiers


def test_identifier_registry_suffixes_sanitized_collisions_in_order():
    registry = StructurizrIdentifierRegistry()
    identifiers = {
        alias: registry.register_alias(alias)
        for alias in ("api.service", "api-service", "api service")
    }

    assert identifiers["api.service"].identifier == "api_service"
    assert identifiers["api-service"].identifier == "api_service_1"
    assert identifiers["api service"].identifier == "api_service_2"


def test_identifier_registry_suffixes_reserved_word_collisions_in_order():
    registry = StructurizrIdentifierRegistry()
    identifiers = {
        alias: registry.register_alias(alias)
        for alias in ("workspace", "workspace_id")
    }

    assert identifiers["workspace"].identifier == "workspace_id"
    assert identifiers["workspace_id"].identifier == "workspace_id_1"


def test_identifier_registry_relationship_ids_are_stable_and_deterministic():
    registry = StructurizrIdentifierRegistry()

    assert registry.next_relationship_id() == "rel1"
    assert registry.next_relationship_id() == "rel2"
    assert registry.next_relationship_id() == "rel3"


def test_identifier_registry_registering_same_alias_is_idempotent():
    registry = StructurizrIdentifierRegistry()

    assert registry.register_alias("api").identifier == "api"
    assert registry.register_alias("api").identifier == "api"


def test_renderer_outputs_sanitized_identifiers_for_mutated_aliases():
    renderer: StructurizrRenderer[Workspace] = StructurizrRenderer()

    with Workspace("Landscape") as workspace:
        with workspace.model as model:
            customer = model.Person("Customer", alias="customer")
            payments = model.SoftwareSystem("Payments", alias="payments")
            customer.uses(payments, "Uses")

    customer.alias = "123 customer"
    payments.alias = "workspace"

    result = renderer.render(workspace)
    workspace_builder = renderer._last_workspace_builder

    assert 'el_123_customer = person "Customer"' in result
    assert 'workspace_id = softwareSystem "Payments"' in result
    assert 'el_123_customer -> workspace_id "Uses"' in result
    assert workspace_builder is not None
    assert workspace_builder.to_dict()["model"]["relationships"] == [
        {
            "id": "rel1",
            "sourceId": "el_123_customer",
            "destinationId": "workspace_id",
            "description": "Uses",
            "technology": None,
            "tags": ["Relationship"],
            "url": None,
            "properties": {},
        }
    ]

from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import ConfigDict, Field

from c4 import (
    Component,
    ComponentDb,
    ComponentDbExt,
    ComponentDiagram,
    ComponentExt,
    ComponentQueue,
    ComponentQueueExt,
    ContainerBoundary,
    EnterpriseBoundary,
    SystemBoundary,
)
from c4.converters.json.schemas.diagrams.common import (
    BaseDiagramSchema,
    BoundaryBase,
    ElementBase,
    RelationshipSchema,
    TypeDiagram,
    WithBoundaryRelationship,
    WithTechnology,
)
from c4.converters.json.schemas.diagrams.container import (
    ContainerDbExtSchema,
    ContainerDbSchema,
    ContainerExtSchema,
    ContainerQueueExtSchema,
    ContainerQueueSchema,
    ContainerSchema,
)
from c4.converters.json.schemas.diagrams.system_context import (
    PersonExtSchema,
    PersonSchema,
    SystemDbExtSchema,
    SystemDbSchema,
    SystemExtSchema,
    SystemQueueExtSchema,
    SystemQueueSchema,
    SystemSchema,
)
from c4.diagrams.core import Boundary


class ComponentSchema(
    ElementBase[Component],
    WithTechnology,
):
    """
    This schema describes the
    [`Component`][c4.diagrams.component.Component]
    diagram component.
    """

    type: Literal["Component"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "Component",
                    "label": "Order Service",
                    "alias": "order_service",
                    "description": (
                        "Coordinates order creation, validation, and "
                        "state transitions."
                    ),
                    "technology": "Python / FastAPI",
                    "properties": {
                        "properties": [
                            ["Owner", "Orders Team"],
                            ["Runtime", "Python 3.12"],
                        ]
                    },
                }
            ]
        }
    )


class ComponentExtSchema(
    ElementBase[ComponentExt],
    WithTechnology,
):
    """
    This schema describes the
    [`ComponentExt`][c4.diagrams.component.ComponentExt]
    diagram component.
    """

    type: Literal["ComponentExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ComponentExt",
                    "label": "Fraud Check API",
                    "alias": "fraud_check_api",
                    "description": (
                        "External component used to score orders "
                        "for fraud risk."
                    ),
                    "technology": "REST API",
                    "properties": {
                        "properties": [
                            ["Provider", "FraudCo"],
                            ["SLA", "99.9%"],
                        ]
                    },
                }
            ]
        }
    )


class ComponentDbSchema(
    ElementBase[ComponentDb],
    WithTechnology,
):
    """
    This schema describes the
    [`ComponentDb`][c4.diagrams.component.ComponentDb]
    diagram component.
    """

    type: Literal["ComponentDb"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ComponentDb",
                    "label": "Order Store",
                    "alias": "order_store",
                    "description": (
                        "Persists orders, payment references, and "
                        "order status history."
                    ),
                    "technology": "PostgreSQL",
                    "properties": {
                        "properties": [
                            ["Engine", "PostgreSQL 16"],
                            ["Backup", "Daily"],
                        ]
                    },
                }
            ]
        }
    )


class ComponentDbExtSchema(
    ElementBase[ComponentDbExt],
    WithTechnology,
):
    """
    This schema describes the
    [`ComponentDbExt`][c4.diagrams.component.ComponentDbExt]
    diagram component.
    """

    type: Literal["ComponentDbExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ComponentDbExt",
                    "label": "Tax Rules Database",
                    "alias": "tax_rules_db",
                    "description": (
                        "External reference database containing "
                        "jurisdiction tax rules."
                    ),
                    "technology": "Vendor DB",
                    "properties": {
                        "properties": [
                            ["Provider", "TaxCo"],
                            ["Access", "Read-only"],
                        ]
                    },
                }
            ]
        }
    )


class ComponentQueueSchema(ElementBase[ComponentQueue], WithTechnology):
    """
    This schema describes the
    [`ComponentQueue`][c4.diagrams.component.ComponentQueue]
    diagram component.
    """

    type: Literal["ComponentQueue"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ComponentQueue",
                    "label": "Order Events Bus",
                    "alias": "order_events_bus",
                    "description": (
                        "Publishes order lifecycle events for "
                        "downstream consumers."
                    ),
                    "technology": "Kafka",
                    "properties": {
                        "properties": [
                            ["Retention", "7 days"],
                            ["Format", "JSON"],
                        ]
                    },
                }
            ]
        }
    )


class ComponentQueueExtSchema(ElementBase[ComponentQueueExt], WithTechnology):
    """
    This schema describes the
    [`ComponentQueueExt`][c4.diagrams.component.ComponentQueueExt]
    diagram component.
    """

    type: Literal["ComponentQueueExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ComponentQueueExt",
                    "label": "Shipping Updates Topic",
                    "alias": "shipping_updates_topic",
                    "description": (
                        "External topic carrying shipment tracking "
                        "and delivery updates."
                    ),
                    "technology": "Kafka",
                    "properties": {
                        "properties": [
                            ["Broker", "Managed Kafka"],
                            ["Format", "Avro"],
                        ]
                    },
                }
            ]
        }
    )


class ContainerBoundarySchema(
    BoundaryBase[ContainerBoundary],
    WithBoundaryRelationship,
):
    """
    This schema describes the
    [`ContainerBoundary`][c4.diagrams.container.ContainerBoundary]
    diagram component.
    """

    type: Literal["ContainerBoundary"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[AnyElement] = Field(
        default_factory=list, description="Elements may be nested arbitrarily."
    )
    boundaries: list[AnyBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ContainerBoundary",
                    "label": "Checkout Subsystem",
                    "alias": "checkout_boundary",
                    "description": "Groups checkout-related containers.",
                    "properties": {
                        "properties": [
                            ["Owner", "Checkout Team"],
                            ["Domain", "Commerce"],
                        ]
                    },
                    "elements": [
                        {
                            "type": "Container",
                            "label": "Checkout API",
                            "alias": "checkout_api",
                            "description": (
                                "Handles cart and checkout operations."
                            ),
                            "technology": "FastAPI",
                        },
                        {
                            "type": "ContainerDb",
                            "label": "Checkout DB",
                            "alias": "checkout_db",
                            "description": (
                                "Stores carts and checkout sessions."
                            ),
                            "technology": "PostgreSQL",
                        },
                    ],
                    "relationships": [
                        {
                            "type": "REL",
                            "from": "checkout_api",
                            "to": "checkout_db",
                            "label": "Reads and writes",
                            "technology": "SQL",
                        }
                    ],
                }
            ]
        }
    )


class EnterpriseBoundarySchema(
    BoundaryBase[EnterpriseBoundary],
    WithBoundaryRelationship,
):
    """
    This schema describes the
    [`EnterpriseBoundary`][c4.diagrams.system_context.EnterpriseBoundary]
    diagram component.
    """

    type: Literal["EnterpriseBoundary"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[AnyElement] = Field(
        default_factory=list, description="Elements may be nested arbitrarily."
    )
    boundaries: list[AnyBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "EnterpriseBoundary",
                    "label": "Acme Corp",
                    "alias": "acme",
                    "description": (
                        "Enterprise boundary containing internal platforms."
                    ),
                    "properties": {
                        "properties": [
                            ["Region", "EU"],
                            ["Department", "Digital"],
                        ]
                    },
                    "relationships": [
                        {
                            "type": "REL",
                            "from": "customer_portal",
                            "to": "shared_identity",
                            "label": "Authenticates via",
                            "technology": "OIDC",
                        }
                    ],
                    "elements": [
                        {
                            "type": "System",
                            "label": "Customer Portal",
                            "alias": "customer_portal",
                            "description": "Entry point for customers.",
                        },
                        {
                            "type": "System",
                            "label": "Shared Identity",
                            "alias": "shared_identity",
                            "description": "Central authentication service.",
                        },
                    ],
                    "boundaries": [
                        {
                            "type": "SystemBoundary",
                            "label": "Commerce Domain",
                            "alias": "commerce_domain",
                        }
                    ],
                }
            ]
        }
    )


class SystemBoundarySchema(
    BoundaryBase[SystemBoundary],
    WithBoundaryRelationship,
):
    """
    This schema describes the
    [`SystemBoundary`][c4.diagrams.system_context.SystemBoundary]
    diagram component.
    """

    type: Literal["SystemBoundary"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[AnyElement] = Field(
        default_factory=list, description="Elements may be nested arbitrarily."
    )
    boundaries: list[AnyBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "SystemBoundary",
                    "label": "Commerce Platform",
                    "alias": "commerce_platform",
                    "description": (
                        "Boundary for the commerce system and its "
                        "internal components."
                    ),
                    "properties": {
                        "properties": [
                            ["Owner", "Commerce Team"],
                            ["Environment", "Production"],
                        ]
                    },
                    "relationships": [
                        {
                            "type": "REL",
                            "from": "web_storefront",
                            "to": "orders_db",
                            "label": "Reads and writes orders",
                            "technology": "SQL",
                        }
                    ],
                    "elements": [
                        {
                            "type": "System",
                            "label": "Web Storefront",
                            "alias": "web_storefront",
                            "description": (
                                "Frontend for browsing and checkout."
                            ),
                        },
                        {
                            "type": "SystemDb",
                            "label": "Orders DB",
                            "alias": "orders_db",
                            "description": "Stores orders and payment state.",
                        },
                    ],
                }
            ]
        }
    )


class BoundarySchema(
    BoundaryBase[Boundary],
    WithBoundaryRelationship,
):
    """
    This schema describes the
    [`Boundary`][c4.diagrams.core.Boundary]
    diagram component.
    """

    type: Literal["Boundary"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    elements: list[AnyElement] = Field(
        default_factory=list, description="Elements may be nested arbitrarily."
    )
    boundaries: list[AnyBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "Boundary",
                    "label": "Commerce Platform",
                    "alias": "commerce_platform",
                    "description": (
                        "Boundary for the commerce system and its "
                        "internal components."
                    ),
                    "properties": {
                        "properties": [
                            ["Owner", "Commerce Team"],
                            ["Environment", "Production"],
                        ]
                    },
                    "relationships": [
                        {
                            "type": "REL",
                            "from": "web_storefront",
                            "to": "orders_db",
                            "label": "Reads and writes orders",
                            "technology": "SQL",
                        }
                    ],
                    "elements": [
                        {
                            "type": "System",
                            "label": "Web Storefront",
                            "alias": "web_storefront",
                            "description": (
                                "Frontend for browsing and checkout."
                            ),
                        },
                        {
                            "type": "SystemDb",
                            "label": "Orders DB",
                            "alias": "orders_db",
                            "description": "Stores orders and payment state.",
                        },
                    ],
                }
            ]
        }
    )


AnyElement = (
    PersonSchema
    | PersonExtSchema
    | SystemSchema
    | SystemExtSchema
    | SystemDbSchema
    | SystemDbExtSchema
    | SystemQueueSchema
    | SystemQueueExtSchema
    | ContainerSchema
    | ContainerExtSchema
    | ContainerDbSchema
    | ContainerDbExtSchema
    | ContainerQueueSchema
    | ContainerQueueExtSchema
    | ComponentSchema
    | ComponentExtSchema
    | ComponentDbSchema
    | ComponentDbExtSchema
    | ComponentQueueSchema
    | ComponentQueueExtSchema
)

AnyBoundary = (
    BoundarySchema
    | EnterpriseBoundarySchema
    | SystemBoundarySchema
    | ContainerBoundarySchema
)


class ComponentDiagramSchema(BaseDiagramSchema):
    """
    This schema describes the
    [`ComponentDiagram`][c4.diagrams.component.ComponentDiagram]
    spec.
    """

    type: Literal["ComponentDiagram"] = Field(
        ..., description="Type of the diagram.", frozen=True
    )
    elements: list[AnyElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[AnyBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )

    __diagram_class__: ClassVar[TypeDiagram] = ComponentDiagram

    model_config = ConfigDict(
        json_schema_extra={"title": __diagram_class__.__name__}
    )

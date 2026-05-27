from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import ConfigDict, Field

from c4 import (
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDbExt,
    ContainerDiagram,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
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


class ContainerSchema(
    ElementBase[Container],
    WithTechnology,
):
    """
    This schema describes the
    [`Container`][c4.diagrams.container.Container]
    diagram component.
    """

    type: Literal["Container"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "Container",
                    "label": "Backend API",
                    "alias": "backend_api",
                    "description": (
                        "Main backend API serving web and mobile clients."
                    ),
                    "technology": "Python / FastAPI",
                    "properties": {
                        "properties": [
                            ["Runtime", "Python 3.12"],
                            ["Team", "Platform"],
                        ]
                    },
                }
            ]
        }
    )


class ContainerExtSchema(
    ElementBase[ContainerExt],
    WithTechnology,
):
    """
    This schema describes the
    [`ContainerExt`][c4.diagrams.container.ContainerExt]
    diagram component.
    """

    type: Literal["ContainerExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ContainerExt",
                    "label": "Recommendation Engine API",
                    "alias": "recommendation_api",
                    "description": (
                        "External API that returns personalized "
                        "product recommendations."
                    ),
                    "technology": "REST API",
                    "properties": {
                        "properties": [["SLA", "99.9%"], ["Owner", "Partner"]]
                    },
                }
            ]
        }
    )


class ContainerDbSchema(
    ElementBase[ContainerDb],
    WithTechnology,
):
    """
    This schema describes the
    [`ContainerDb`][c4.diagrams.container.ContainerDb]
    diagram component.
    """

    type: Literal["ContainerDb"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ContainerDb",
                    "label": "Catalog Database",
                    "alias": "catalog_db",
                    "description": (
                        "Stores products, categories, and pricing data."
                    ),
                    "technology": "PostgreSQL",
                    "properties": {
                        "properties": [
                            ["Engine", "PostgreSQL 16"],
                            ["Replication", "Streaming"],
                        ]
                    },
                }
            ]
        }
    )


class ContainerDbExtSchema(
    ElementBase[ContainerDbExt],
    WithTechnology,
):
    """
    This schema describes the
    [`ContainerDbExt`][c4.diagrams.container.ContainerDbExt]
    diagram component.
    """

    type: Literal["ContainerDbExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ContainerDbExt",
                    "label": "Fraud Vendor Database",
                    "alias": "fraud_vendor_db",
                    "description": (
                        "External datastore used to look up fraud signals."
                    ),
                    "technology": "Vendor DB",
                    "properties": {
                        "properties": [
                            ["Provider", "FraudCo"],
                            ["Access", "Read-only"],
                        ]
                    },
                }
            ]
        }
    )


class ContainerQueueSchema(
    ElementBase[ContainerQueue],
    WithTechnology,
):
    """
    This schema describes the
    [`ContainerQueue`][c4.diagrams.container.ContainerQueue]
    diagram component.
    """

    type: Literal["ContainerQueue"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ContainerQueue",
                    "label": "Payment Events Queue",
                    "alias": "payment_events_queue",
                    "description": (
                        "Carries asynchronous payment status updates."
                    ),
                    "technology": "RabbitMQ",
                    "properties": {
                        "properties": [
                            ["Durable", "true"],
                            ["DLQ", "payment_events_dlq"],
                        ]
                    },
                }
            ]
        }
    )


class ContainerQueueExtSchema(
    ElementBase[ContainerQueueExt],
    WithTechnology,
):
    """
    This schema describes the
    [`ContainerQueueExt`][c4.diagrams.container.ContainerQueueExt]
    diagram component.
    """

    type: Literal["ContainerQueueExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "ContainerQueueExt",
                    "label": "Partner Fulfillment Topic",
                    "alias": "partner_fulfillment_topic",
                    "description": (
                        "External topic with fulfillment status updates."
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
                    "boundaries": [],
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
                            "elements": [],
                            "boundaries": [],
                            "relationships": [],
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
                    "boundaries": [],
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
                    "boundaries": [],
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
)

AnyBoundary = (
    BoundarySchema
    | EnterpriseBoundarySchema
    | SystemBoundarySchema
    | ContainerBoundarySchema
)


class ContainerDiagramSchema(BaseDiagramSchema):
    """
    This schema describes the
    [`ContainerDiagram`][c4.diagrams.container.ContainerDiagram]
    spec.
    """

    type: Literal["ContainerDiagram"] = Field(
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

    __diagram_class__: ClassVar[TypeDiagram] = ContainerDiagram

    model_config = ConfigDict(
        json_schema_extra={"title": __diagram_class__.__name__}
    )

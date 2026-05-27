from __future__ import annotations

from typing import ClassVar, Generic, Literal

from pydantic import ConfigDict, Field

from c4 import (
    EnterpriseBoundary,
    Person,
    PersonExt,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemLandscapeDiagram,
    SystemQueue,
    SystemQueueExt,
)
from c4.converters.json.schemas.base import TDiagramElement
from c4.converters.json.schemas.diagrams.common import (
    BaseDiagramSchema,
    BoundaryBase,
    ElementBase,
    RelationshipSchema,
    TypeDiagram,
    WithBoundaryRelationship,
)
from c4.diagrams.core import Boundary


class PersonSchema(ElementBase[Person]):
    """
    This schema describes the [`Person`][c4.diagrams.system_context.Person]
    diagram component.
    """

    type: Literal["Person"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "Person",
                    "label": "Store Manager",
                    "alias": "store_manager",
                    "description": "Manages product catalog and promotions.",
                    "properties": {
                        "properties": [
                            ["Department", "Retail Ops"],
                            ["Role", "Manager"],
                        ]
                    },
                }
            ]
        }
    )


class PersonExtSchema(ElementBase[PersonExt]):
    """
    This schema describes the
    [`PersonExt`][c4.diagrams.system_context.PersonExt] diagram component.
    """

    type: Literal["PersonExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "PersonExt",
                    "label": "Auditor",
                    "alias": "auditor",
                    "description": "External compliance reviewer.",
                    "properties": {
                        "properties": [
                            ["Organization", "Compliance Partner"],
                            ["Access", "Read-only"],
                        ]
                    },
                }
            ]
        }
    )


class SystemSchema(ElementBase[System]):
    """
    This schema describes the
    [`System`][c4.diagrams.system_context.System] diagram component.
    """

    type: Literal["System"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "System",
                    "label": "Inventory Service",
                    "alias": "inventory_service",
                    "description": "Tracks stock levels and reservation state.",
                    "properties": {
                        "properties": [
                            ["Language", "Python"],
                            ["Team", "Supply Chain"],
                        ]
                    },
                }
            ]
        }
    )


class SystemExtSchema(ElementBase[SystemExt]):
    """
    This schema describes the
    [`SystemExt`][c4.diagrams.system_context.SystemExt] diagram component.
    """

    type: Literal["SystemExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "SystemExt",
                    "label": "Shipping Provider",
                    "alias": "shipping_provider",
                    "description": (
                        "External logistics platform for shipment "
                        "booking and tracking."
                    ),
                    "properties": {
                        "properties": [["Protocol", "REST"], ["SLA", "99.9%"]]
                    },
                }
            ]
        }
    )


class SystemDbSchema(ElementBase[SystemDb]):
    """
    This schema describes the
    [`SystemDb`][c4.diagrams.system_context.SystemDb]
    diagram component.
    """

    type: Literal["SystemDb"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "SystemDb",
                    "label": "Customer Profile DB",
                    "alias": "customer_profile_db",
                    "description": (
                        "Stores customer preferences and account metadata."
                    ),
                    "properties": {
                        "properties": [
                            ["Engine", "PostgreSQL"],
                            ["Backup", "Daily"],
                        ]
                    },
                }
            ]
        }
    )


class SystemDbExtSchema(ElementBase[SystemDbExt]):
    """
    This schema describes the
    [`SystemDbExt`][c4.diagrams.system_context.SystemDbExt]
    diagram component.
    """

    type: Literal["SystemDbExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "SystemDbExt",
                    "label": "Credit Bureau DB",
                    "alias": "credit_bureau_db",
                    "description": (
                        "External database with risk assessment data."
                    ),
                    "properties": {
                        "properties": [
                            ["Provider", "RiskCo"],
                            ["Access", "Read-only"],
                        ]
                    },
                }
            ]
        }
    )


class SystemQueueSchema(ElementBase[SystemQueue]):
    """
    This schema describes the
    [`SystemQueue`][c4.diagrams.system_context.SystemQueue]
    diagram component.
    """

    type: Literal["SystemQueue"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "SystemQueue",
                    "label": "Order Events Stream",
                    "alias": "order_events_stream",
                    "description": "Internal stream of order lifecycle events.",
                    "properties": {
                        "properties": [
                            ["Retention", "7 days"],
                            ["Partitions", "12"],
                        ]
                    },
                }
            ]
        }
    )


class SystemQueueExtSchema(ElementBase[SystemQueueExt]):
    """
    This schema describes the
    [`SystemQueueExt`][c4.diagrams.system_context.SystemQueueExt]
    diagram component.
    """

    type: Literal["SystemQueueExt"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "SystemQueueExt",
                    "label": "Partner Events Topic",
                    "alias": "partner_events_topic",
                    "description": (
                        "External event topic carrying delivery status updates."
                    ),
                    "properties": {
                        "properties": [["Broker", "Kafka"], ["Format", "Avro"]]
                    },
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
)


class SystemContextBoundaryBase(
    BoundaryBase,
    WithBoundaryRelationship,
    Generic[TDiagramElement],
):
    elements: list[AnyElement] = Field(
        default_factory=list, description="Elements may be nested arbitrarily."
    )
    boundaries: list[AnyBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
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


class EnterpriseBoundarySchema(SystemContextBoundaryBase[EnterpriseBoundary]):
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


class SystemBoundarySchema(SystemContextBoundaryBase[SystemBoundary]):
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


AnyBoundary = BoundarySchema | EnterpriseBoundarySchema | SystemBoundarySchema


class SystemContextBase:
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


class SystemContextDiagramSchema(BaseDiagramSchema, SystemContextBase):
    """
    This schema describes the
    [`SystemContextDiagram`][c4.diagrams.system_context.SystemContextDiagram]
    spec.
    """

    type: Literal["SystemContextDiagram"] = Field(
        ..., description="Type of the diagram.", frozen=True
    )

    __diagram_class__: ClassVar[TypeDiagram] = SystemContextDiagram

    model_config = ConfigDict(
        json_schema_extra={"title": __diagram_class__.__name__}
    )


class SystemLandscapeDiagramSchema(BaseDiagramSchema, SystemContextBase):
    """
    This schema describes the
    [`SystemLandscapeDiagram`][c4.diagrams.system_context.SystemLandscapeDiagram]
    spec.
    """

    type: Literal["SystemLandscapeDiagram"] = Field(
        ..., description="Type of the diagram.", frozen=True
    )

    __diagram_class__: ClassVar[TypeDiagram] = SystemLandscapeDiagram

    model_config = ConfigDict(
        json_schema_extra={"title": __diagram_class__.__name__}
    )

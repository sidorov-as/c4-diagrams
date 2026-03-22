from __future__ import annotations

from typing import Any, ClassVar, Generic, Literal

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
    WithBaseShape,
    WithBoundaryRelationship,
    WithType,
)


class PersonSchema(ElementBase[Person], WithType):
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
                    "stereotype": "Business User",
                    "sprite": "user",
                    "tags": ["person", "internal"],
                    "link": "https://intranet.example.com",
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


class PersonExtSchema(ElementBase[PersonExt], WithType):
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
                    "stereotype": "External User",
                    "sprite": "user",
                    "tags": ["person", "external"],
                    "link": "https://partner.example.com",
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


class SystemSchema(ElementBase[System], WithType, WithBaseShape):
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
                    "stereotype": "Software System",
                    "sprite": "server",
                    "tags": ["system", "internal"],
                    "link": "https://inventory.example.com",
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


class SystemExtSchema(ElementBase[SystemExt], WithType, WithBaseShape):
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
                    "stereotype": "External System",
                    "sprite": "truck",
                    "tags": ["system", "external"],
                    "link": "https://shipping.example.com",
                    "properties": {
                        "properties": [["Protocol", "REST"], ["SLA", "99.9%"]]
                    },
                }
            ]
        }
    )


class SystemDbSchema(ElementBase[SystemDb], WithType):
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
                    "stereotype": "Database",
                    "sprite": "database",
                    "tags": ["database", "internal"],
                    "link": "https://db.example.com/customer-profile",
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


class SystemDbExtSchema(ElementBase[SystemDbExt], WithType):
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
                    "stereotype": "External Database",
                    "sprite": "database",
                    "tags": ["database", "external"],
                    "link": "https://partner.example.com/risk",
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


class SystemQueueSchema(ElementBase[SystemQueue], WithType):
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
                    "stereotype": "Queue",
                    "sprite": "queue",
                    "tags": ["queue", "internal"],
                    "link": "https://kafka.example.com/topics/order-events",
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


class SystemQueueExtSchema(ElementBase[SystemQueueExt], WithType):
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
                    "stereotype": "External Queue",
                    "sprite": "queue",
                    "tags": ["queue", "external"],
                    "link": "https://partner.example.com/events",
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
                    "tags": ["enterprise"],
                    "link": "https://acme.example.com",
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
                    "tags": ["system_boundary"],
                    "link": "https://docs.example.com/commerce",
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


AnyBoundary = EnterpriseBoundarySchema | SystemBoundarySchema


SYSTEM_CONTEXT_DIAGRAM_MINIMAL_EXAMPLE: dict[str, Any] = {
    "type": "SystemContextDiagram",
    "elements": [
        {"type": "Person", "alias": "user", "label": "User"},
        {"type": "System", "alias": "app", "label": "My App"},
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "user",
            "to": "app",
            "label": "Uses",
            "technology": "HTTPS",
        }
    ],
}

SYSTEM_CONTEXT_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    "type": "SystemContextDiagram",
    "title": "Retail Platform",
    "elements": [
        {
            "type": "Person",
            "label": "Customer",
            "alias": "customer",
            "description": "Places orders through the storefront.",
            "tags": ["Primary"],
        },
        {
            "type": "PersonExt",
            "label": "Support Agent",
            "alias": "support_agent",
            "description": "Handles issues in an external CRM.",
            "tags": ["External"],
        },
        {
            "type": "SystemExt",
            "label": "Payment Gateway",
            "alias": "payment_gateway",
            "description": "Processes card payments.",
            "tags": ["External"],
        },
        {
            "type": "SystemExt",
            "label": "CRM Platform",
            "alias": "crm_platform",
            "description": "External CRM used by support agents.",
            "tags": ["External"],
        },
    ],
    "boundaries": [
        {
            "type": "EnterpriseBoundary",
            "label": "Acme Corp",
            "alias": "acme_enterprise",
            "description": "Internal systems owned by Acme.",
            "tags": ["Enterprise"],
            "elements": [
                {
                    "type": "System",
                    "label": "Retail Platform",
                    "alias": "retail_platform",
                    "description": (
                        "Core platform for catalog, checkout, and "
                        "order management."
                    ),
                    "tags": ["Core"],
                    "link": "https://retail.example.com",
                }
            ],
            "boundaries": [],
            "relationships": [],
        }
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "customer",
            "to": "retail_platform",
            "label": "Browses and places orders",
            "technology": "HTTPS",
            "tags": ["Synchronous"],
        },
        {
            "type": "REL",
            "from": "retail_platform",
            "to": "payment_gateway",
            "label": "Charges card",
            "technology": "REST API",
            "tags": ["Synchronous"],
        },
        {
            "type": "REL",
            "from": "support_agent",
            "to": "crm_platform",
            "label": "Manages customer issues",
            "technology": "Web UI",
            "tags": ["Manual"],
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "customer", "to": "retail_platform"},
        {"type": "LAY_R", "from": "retail_platform", "to": "payment_gateway"},
        {"type": "LAY_D", "from": "support_agent", "to": "crm_platform"},
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "layout_with_legend": True,
            "show_legend": {"details": "Normal", "hide_stereotype": False},
            "legend_title": "System Context",
            "hide_stereotype": False,
            "tags": [
                {
                    "type": "PersonTag",
                    "tag_stereo": "Primary",
                    "legend_text": "Primary user",
                    "sprite": "person",
                },
                {
                    "type": "ExternalPersonTag",
                    "tag_stereo": "External",
                    "legend_text": "External person",
                    "sprite": "person",
                },
                {
                    "type": "SystemTag",
                    "tag_stereo": "Core",
                    "legend_text": "Core internal system",
                    "sprite": "server",
                },
                {
                    "type": "ExternalSystemTag",
                    "tag_stereo": "External",
                    "legend_text": "External dependency",
                    "sprite": "cloud",
                },
                {
                    "type": "BoundaryTag",
                    "tag_stereo": "Enterprise",
                    "legend_text": "Enterprise boundary",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "Synchronous",
                    "legend_text": "Synchronous integration",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "Manual",
                    "legend_text": "Manual interaction",
                },
            ],
        }
    },
}


SYSTEM_LANDSCAPE_DIAGRAM_MINIMAL_EXAMPLE: dict[str, Any] = {
    "type": "SystemLandscapeDiagram",
    "elements": [
        {"type": "Person", "alias": "user", "label": "User"},
        {"type": "System", "alias": "app", "label": "My App"},
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "user",
            "to": "app",
            "label": "Uses",
            "technology": "HTTPS",
        }
    ],
}

SYSTEM_LANDSCAPE_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    **SYSTEM_CONTEXT_DIAGRAM_ADVANCED_EXAMPLE,
    "type": "SystemLandscapeDiagram",
}


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
        json_schema_extra={
            "title": __diagram_class__.__name__,
            "examples": [
                SYSTEM_CONTEXT_DIAGRAM_MINIMAL_EXAMPLE,
                SYSTEM_CONTEXT_DIAGRAM_ADVANCED_EXAMPLE,
            ],
        }
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
        json_schema_extra={
            "title": __diagram_class__.__name__,
            "examples": [
                SYSTEM_LANDSCAPE_DIAGRAM_MINIMAL_EXAMPLE,
                SYSTEM_LANDSCAPE_DIAGRAM_ADVANCED_EXAMPLE,
            ],
        }
    )

from __future__ import annotations

from typing import Any, ClassVar, Literal

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
    WithBaseShape,
    WithBoundaryRelationship,
    WithTechnology,
    WithType,
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
    WithBaseShape,
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
                    "base_shape": "RoundedBox",
                    "sprite": "server",
                    "tags": ["component", "core"],
                    "link": "https://docs.example.com/order-service",
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
    WithBaseShape,
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
                    "base_shape": "RoundedBox",
                    "sprite": "cloud",
                    "tags": ["component", "external"],
                    "link": "https://partner.example.com/fraud",
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
                    "sprite": "database",
                    "tags": ["component", "database"],
                    "link": "https://db-admin.example.com/orders",
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
                    "sprite": "database",
                    "tags": ["component", "database", "external"],
                    "link": "https://partner.example.com/tax-db",
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
                    "sprite": "queue",
                    "tags": ["component", "queue"],
                    "link": "https://kafka.example.com/topics/order-events",
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
                    "sprite": "queue",
                    "tags": ["component", "queue", "external"],
                    "link": "https://partner.example.com/events",
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
                    "tags": ["container_boundary"],
                    "link": "https://docs.example.com/checkout",
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


class BoundarySchema(
    BoundaryBase[Boundary],
    WithType,
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
                    "stereotype": "boundary",
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


COMPONENT_DIAGRAM_MINIMAL_EXAMPLE: dict[str, Any] = {
    "type": "ComponentDiagram",
    "title": "Checkout API - Component Diagram",
    "elements": [
        {
            "type": "Component",
            "label": "Checkout Controller",
            "alias": "checkout_controller",
            "description": (
                "Receives checkout requests and orchestrates payment flow."
            ),
            "technology": "FastAPI",
            "tags": ["Entrypoint"],
        },
        {
            "type": "Component",
            "label": "Payment Service",
            "alias": "payment_service",
            "description": (
                "Creates payment intents and handles payment state updates."
            ),
            "technology": "Python",
            "tags": ["CoreComponent"],
        },
        {
            "type": "ComponentDb",
            "label": "Payment Store",
            "alias": "payment_store",
            "description": "Stores payment records and statuses.",
            "technology": "PostgreSQL",
            "tags": ["ComponentDatabase"],
        },
        {
            "type": "ComponentExt",
            "label": "Payment Gateway API",
            "alias": "payment_gateway_api",
            "description": (
                "External API for payment authorization and capture."
            ),
            "technology": "REST API",
            "tags": ["ExternalComponent"],
        },
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "checkout_controller",
            "to": "payment_service",
            "label": "Calls",
            "technology": "Python call",
        },
        {
            "type": "REL",
            "from": "payment_service",
            "to": "payment_store",
            "label": "Reads and writes",
            "technology": "SQL",
        },
        {
            "type": "REL",
            "from": "payment_service",
            "to": "payment_gateway_api",
            "label": "Creates payments via",
            "technology": "HTTPS/JSON",
        },
    ],
    "layouts": [
        {
            "type": "LAY_R",
            "from": "checkout_controller",
            "to": "payment_service",
        },
        {"type": "LAY_D", "from": "payment_service", "to": "payment_store"},
        {
            "type": "LAY_R",
            "from": "payment_service",
            "to": "payment_gateway_api",
        },
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "layout_with_legend": True,
            "show_legend": {
                "details": "Normal",
                "hide_stereotype": False,
            },
            "legend_title": "Checkout Component Legend",
            "tags": [
                {
                    "type": "ComponentTag",
                    "tag_stereo": "Entrypoint",
                    "legend_text": "API entrypoint component",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#e3f2fd",
                    "font_color": "#0d47a1",
                    "border_color": "#42a5f5",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "FastAPI",
                    "border_style": "BoldLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ComponentTag",
                    "tag_stereo": "CoreComponent",
                    "legend_text": "Internal core component",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#e8f0fe",
                    "font_color": "#0d47a1",
                    "border_color": "#64b5f6",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "Python",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ComponentTag",
                    "tag_stereo": "ComponentDatabase",
                    "legend_text": "Internal component database",
                    "legend_sprite": "database",
                    "sprite": "database",
                    "bg_color": "#fff8e1",
                    "font_color": "#5d4037",
                    "border_color": "#ffb300",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "technology": "PostgreSQL",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                },
                {
                    "type": "ExternalComponentTag",
                    "tag_stereo": "ExternalComponent",
                    "legend_text": "External component dependency",
                    "legend_sprite": "cloud",
                    "sprite": "cloud",
                    "bg_color": "#f5f5f5",
                    "font_color": "#424242",
                    "border_color": "#9e9e9e",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "technology": "REST API",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                },
            ],
        }
    },
}

COMPONENT_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    "type": "ComponentDiagram",
    "title": "Order Processing API - Component Diagram",
    "elements": [
        {
            "type": "Component",
            "label": "Order Controller",
            "alias": "order_controller",
            "description": (
                "HTTP entrypoint for order submission and status queries."
            ),
            "technology": "FastAPI",
            "sprite": "server",
            "tags": ["Entrypoint", "CoreComponent"],
        },
        {
            "type": "Component",
            "label": "Order Application Service",
            "alias": "order_app_service",
            "description": (
                "Coordinates validation, payment, and order creation."
            ),
            "technology": "Python",
            "sprite": "server",
            "tags": ["CoreComponent", "Orders"],
        },
        {
            "type": "Component",
            "label": "Inventory Checker",
            "alias": "inventory_checker",
            "description": (
                "Verifies stock availability before an order is confirmed."
            ),
            "technology": "Python",
            "sprite": "server",
            "tags": ["CoreComponent"],
        },
        {
            "type": "Component",
            "label": "Payment Adapter",
            "alias": "payment_adapter",
            "description": "Wraps external payment provider calls.",
            "technology": "Python",
            "sprite": "server",
            "tags": ["CoreComponent", "Payments"],
        },
        {
            "type": "ComponentDb",
            "label": "Order Database",
            "alias": "order_db",
            "description": (
                "Stores orders, line items, and order status history."
            ),
            "technology": "PostgreSQL",
            "sprite": "database",
            "tags": ["ComponentDatabase"],
        },
        {
            "type": "ComponentExt",
            "label": "Payment Gateway API",
            "alias": "payment_gateway_api",
            "description": (
                "External provider API for payment authorization and capture."
            ),
            "technology": "REST API",
            "sprite": "cloud",
            "tags": ["ExternalComponent"],
        },
        {
            "type": "ComponentQueue",
            "label": "Order Events Bus",
            "alias": "order_events_bus",
            "description": ("Publishes order-created and order-paid events."),
            "technology": "Kafka",
            "sprite": "queue",
            "tags": ["AsyncComponent"],
        },
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "order_controller",
            "to": "order_app_service",
            "label": "Invokes",
            "technology": "Python call",
            "tags": ["SyncCall"],
        },
        {
            "type": "REL",
            "from": "order_app_service",
            "to": "inventory_checker",
            "label": "Checks stock via",
            "technology": "Python call",
            "tags": ["SyncCall"],
        },
        {
            "type": "REL",
            "from": "order_app_service",
            "to": "payment_adapter",
            "label": "Requests payment through",
            "technology": "Python call",
            "tags": ["SyncCall"],
        },
        {
            "type": "REL",
            "from": "payment_adapter",
            "to": "payment_gateway_api",
            "label": "Authorizes payment via",
            "technology": "HTTPS/JSON",
            "tags": ["ExternalCall"],
        },
        {
            "type": "REL",
            "from": "order_app_service",
            "to": "order_db",
            "label": "Reads and writes",
            "technology": "SQL",
            "tags": ["DataAccess"],
        },
        {
            "type": "REL",
            "from": "order_app_service",
            "to": "order_events_bus",
            "label": "Publishes events to",
            "technology": "Kafka",
            "tags": ["AsyncFlow"],
        },
    ],
    "layouts": [
        {
            "type": "LAY_R",
            "from": "order_controller",
            "to": "order_app_service",
        },
        {
            "type": "LAY_R",
            "from": "order_app_service",
            "to": "inventory_checker",
        },
        {"type": "LAY_D", "from": "order_app_service", "to": "order_db"},
        {"type": "LAY_R", "from": "inventory_checker", "to": "payment_adapter"},
        {
            "type": "LAY_R",
            "from": "payment_adapter",
            "to": "payment_gateway_api",
        },
        {"type": "LAY_D", "from": "payment_adapter", "to": "order_events_bus"},
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "layout_with_legend": True,
            "legend_title": "Order Processing Component Legend",
            "show_legend": {"details": "Normal", "hide_stereotype": False},
            "tags": [
                {
                    "type": "ComponentTag",
                    "tag_stereo": "Entrypoint",
                    "legend_text": "HTTP/API entrypoint component",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#e3f2fd",
                    "font_color": "#0d47a1",
                    "border_color": "#42a5f5",
                    "border_style": "BoldLine",
                    "border_thickness": "2",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "FastAPI",
                },
                {
                    "type": "ComponentTag",
                    "tag_stereo": "CoreComponent",
                    "legend_text": "Internal business component",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#e8f5e9",
                    "font_color": "#1b5e20",
                    "border_color": "#66bb6a",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "Python",
                },
                {
                    "type": "ComponentTag",
                    "tag_stereo": "Orders",
                    "legend_text": "Order management component",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#fff3e0",
                    "font_color": "#e65100",
                    "border_color": "#fb8c00",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "Python",
                },
                {
                    "type": "ComponentTag",
                    "tag_stereo": "Payments",
                    "legend_text": "Payment-related component",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#ede7f6",
                    "font_color": "#311b92",
                    "border_color": "#7e57c2",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "Python",
                },
                {
                    "type": "ComponentTag",
                    "tag_stereo": "ComponentDatabase",
                    "legend_text": "Internal component database",
                    "legend_sprite": "database",
                    "sprite": "database",
                    "bg_color": "#fff8e1",
                    "font_color": "#5d4037",
                    "border_color": "#ffb300",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "technology": "PostgreSQL",
                },
                {
                    "type": "ExternalComponentTag",
                    "tag_stereo": "ExternalComponent",
                    "legend_text": "External component dependency",
                    "legend_sprite": "cloud",
                    "sprite": "cloud",
                    "bg_color": "#f5f5f5",
                    "font_color": "#424242",
                    "border_color": "#9e9e9e",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "technology": "REST API",
                },
                {
                    "type": "ComponentTag",
                    "tag_stereo": "AsyncComponent",
                    "legend_text": "Internal asynchronous component",
                    "legend_sprite": "queue",
                    "sprite": "queue",
                    "bg_color": "#f3e5f5",
                    "font_color": "#6a1b9a",
                    "border_color": "#ab47bc",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "technology": "Kafka",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "SyncCall",
                    "legend_text": "Synchronous internal call",
                    "line_color": "#1e88e5",
                    "text_color": "#1565c0",
                    "line_style": "SolidLine",
                    "line_thickness": "1",
                    "technology": "Python call",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "ExternalCall",
                    "legend_text": "External service call",
                    "line_color": "#78909c",
                    "text_color": "#455a64",
                    "line_style": "DashedLine",
                    "line_thickness": "1",
                    "technology": "HTTPS/JSON",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "DataAccess",
                    "legend_text": "Database access",
                    "line_color": "#8d6e63",
                    "text_color": "#6d4c41",
                    "line_style": "DashedLine",
                    "line_thickness": "1",
                    "technology": "SQL",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "AsyncFlow",
                    "legend_text": "Asynchronous event flow",
                    "legend_sprite": "queue",
                    "sprite": "queue",
                    "line_color": "#8e24aa",
                    "text_color": "#6a1b9a",
                    "line_style": "DottedLine",
                    "line_thickness": "2",
                    "technology": "Kafka",
                },
            ],
            "styles": [
                {
                    "type": "ElementStyle",
                    "element_name": "component",
                    "shape": "RoundedBoxShape",
                    "border_style": "SolidLine",
                },
                {
                    "type": "RelStyle",
                    "line_color": "#546e7a",
                    "text_color": "#37474f",
                },
            ],
        }
    },
}


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
        json_schema_extra={
            "title": __diagram_class__.__name__,
            "examples": [
                COMPONENT_DIAGRAM_MINIMAL_EXAMPLE,
                COMPONENT_DIAGRAM_ADVANCED_EXAMPLE,
            ],
        }
    )

from __future__ import annotations

from typing import Any, ClassVar, Literal

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
)
from c4.converters.json.schemas.diagrams.system_context import (
    EnterpriseBoundarySchema,
    PersonExtSchema,
    PersonSchema,
    SystemBoundarySchema,
    SystemDbExtSchema,
    SystemDbSchema,
    SystemExtSchema,
    SystemQueueExtSchema,
    SystemQueueSchema,
    SystemSchema,
)


class ContainerSchema(
    ElementBase[Container],
    WithTechnology,
    WithBaseShape,
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
                    "base_shape": "RoundedBox",
                    "technology": "Python / FastAPI",
                    "sprite": "server",
                    "tags": ["container", "api", "core"],
                    "link": "https://api.example.com",
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
    WithBaseShape,
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
                    "base_shape": "RoundedBox",
                    "technology": "REST API",
                    "sprite": "cloud",
                    "tags": ["container", "external", "api"],
                    "link": "https://partner.example.com/recommendations",
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
                    "sprite": "database",
                    "tags": ["container", "database", "internal"],
                    "link": "https://db-admin.example.com/catalog",
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
                    "sprite": "database",
                    "tags": ["container", "database", "external"],
                    "link": "https://vendor.example.com",
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
                    "sprite": "queue",
                    "tags": ["container", "queue", "internal"],
                    "link": "https://ops.example.com/rabbitmq",
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
                    "sprite": "queue",
                    "tags": ["container", "queue", "external"],
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
    EnterpriseBoundarySchema | SystemBoundarySchema | ContainerBoundarySchema
)


CONTAINER_DIAGRAM_MINIMAL_EXAMPLE: dict[str, Any] = {}
CONTAINER_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    "type": "ContainerDiagram",
    "title": "Online Shop - Container Diagram",
    "elements": [
        {
            "type": "Person",
            "label": "Customer",
            "alias": "customer",
            "description": "Browses products and places orders.",
            "stereotype": "Primary User",
            "sprite": "user",
            "tags": ["Customer"],
            "properties": {"properties": [["Channel", "Web / Mobile"]]},
        },
        {
            "type": "PersonExt",
            "label": "Support Agent",
            "alias": "support_agent",
            "description": (
                "Investigates customer issues from an external support tool."
            ),
            "stereotype": "External User",
            "sprite": "user",
            "tags": ["ExternalPerson"],
        },
        {
            "type": "System",
            "label": "Online Shop",
            "alias": "online_shop",
            "description": "Customer-facing commerce platform.",
            "stereotype": "Software System",
            "base_shape": "RoundedBox",
            "sprite": "server",
            "tags": ["CoreSystem"],
            "link": "https://shop.example.com",
        },
        {
            "type": "SystemExt",
            "label": "Payment Provider",
            "alias": "payment_provider",
            "description": "Processes card payments and payment webhooks.",
            "stereotype": "External System",
            "base_shape": "RoundedBox",
            "sprite": "cloud",
            "tags": ["ExternalSystem"],
            "link": "https://payments.example.com",
        },
        {
            "type": "Container",
            "label": "Web Application",
            "alias": "web_app",
            "description": "Serves the storefront and checkout UI.",
            "technology": "React + Next.js",
            "base_shape": "RoundedBox",
            "sprite": "browser",
            "tags": ["Frontend"],
            "properties": {
                "properties": [
                    ["Runtime", "Node.js"],
                    ["Team", "Storefront"],
                ]
            },
        },
        {
            "type": "Container",
            "label": "Backend API",
            "alias": "backend_api",
            "description": "Handles catalog, carts, checkout, and order APIs.",
            "technology": "Python / FastAPI",
            "base_shape": "RoundedBox",
            "sprite": "server",
            "tags": ["Backend", "CoreRuntime"],
            "properties": {
                "properties": [
                    ["Runtime", "Python 3.12"],
                    ["Team", "Platform"],
                ]
            },
        },
        {
            "type": "ContainerDb",
            "label": "Orders Database",
            "alias": "orders_db",
            "description": "Stores orders, payments, and status transitions.",
            "technology": "PostgreSQL",
            "sprite": "database",
            "tags": ["DataStore"],
            "properties": {
                "properties": [
                    ["Engine", "PostgreSQL 16"],
                    ["HA", "Primary / Replica"],
                ]
            },
        },
        {
            "type": "ContainerQueue",
            "label": "Order Events Queue",
            "alias": "order_events",
            "description": "Publishes asynchronous order lifecycle events.",
            "technology": "Kafka",
            "sprite": "queue",
            "tags": ["AsyncChannel"],
            "properties": {
                "properties": [["Retention", "7 days"], ["Format", "JSON"]]
            },
        },
        {
            "type": "ContainerExt",
            "label": "Recommendation API",
            "alias": "recommendation_api",
            "description": "Returns personalized product recommendations.",
            "technology": "REST API",
            "base_shape": "RoundedBox",
            "sprite": "cloud",
            "tags": ["ExternalContainer"],
        },
        {
            "type": "ContainerDbExt",
            "label": "Fraud Signals DB",
            "alias": "fraud_db",
            "description": "External datastore containing fraud intelligence.",
            "technology": "Vendor DB",
            "sprite": "database",
            "tags": ["ExternalDataStore"],
        },
        {
            "type": "ContainerQueueExt",
            "label": "Shipping Events Topic",
            "alias": "shipping_events",
            "description": "External topic used by logistics partner.",
            "technology": "Kafka",
            "sprite": "queue",
            "tags": ["ExternalAsyncChannel"],
        },
    ],
    "boundaries": [
        {
            "type": "EnterpriseBoundary",
            "label": "Acme Corp",
            "alias": "acme",
            "description": "Enterprise boundary for internal platforms.",
            "tags": ["EnterpriseBoundary"],
            "properties": {
                "properties": [
                    ["Region", "EU"],
                    ["Business Unit", "Digital Commerce"],
                ]
            },
            "elements": [
                {
                    "type": "System",
                    "label": "Online Shop",
                    "alias": "shop_system_inside_enterprise",
                    "description": (
                        "Reference system inside the enterprise boundary."
                    ),
                    "tags": ["CoreSystem"],
                }
            ],
            "boundaries": [],
            "relationships": [],
        },
        {
            "type": "SystemBoundary",
            "label": "Online Shop Platform",
            "alias": "shop_boundary",
            "description": "Main system boundary for the commerce platform.",
            "tags": ["SystemBoundary"],
            "properties": {
                "properties": [
                    ["Owner", "Commerce Team"],
                    ["Environment", "Production"],
                ]
            },
            "elements": [
                {
                    "type": "Container",
                    "label": "Web Application",
                    "alias": "web_app_in_boundary",
                    "description": "Customer-facing frontend.",
                    "technology": "React + Next.js",
                    "tags": ["Frontend"],
                }
            ],
            "boundaries": [],
            "relationships": [],
        },
        {
            "type": "ContainerBoundary",
            "label": "Checkout Subsystem",
            "alias": "checkout_boundary",
            "description": "Groups checkout-related containers.",
            "tags": ["ContainerBoundary"],
            "properties": {
                "properties": [
                    ["Owner", "Checkout Team"],
                    ["Criticality", "High"],
                ]
            },
            "elements": [
                {
                    "type": "Container",
                    "label": "Checkout API",
                    "alias": "checkout_api",
                    "description": (
                        "Handles checkout and payment orchestration."
                    ),
                    "technology": "Python / FastAPI",
                    "tags": ["Backend"],
                },
                {
                    "type": "ContainerDb",
                    "label": "Checkout DB",
                    "alias": "checkout_db",
                    "description": "Stores checkout sessions.",
                    "technology": "PostgreSQL",
                    "tags": ["DataStore"],
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
                    "tags": ["DataAccess"],
                }
            ],
        },
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "customer",
            "to": "web_app",
            "label": "Uses",
            "technology": "HTTPS",
            "tags": ["SyncRequest"],
        },
        {
            "type": "REL",
            "from": "web_app",
            "to": "backend_api",
            "label": "Calls",
            "technology": "HTTPS/JSON",
            "tags": ["SyncRequest"],
        },
        {
            "type": "REL",
            "from": "backend_api",
            "to": "orders_db",
            "label": "Reads and writes",
            "technology": "SQL",
            "tags": ["DataAccess"],
        },
        {
            "type": "REL",
            "from": "backend_api",
            "to": "order_events",
            "label": "Publishes order events",
            "technology": "Kafka",
            "tags": ["AsyncRequest"],
        },
        {
            "type": "REL",
            "from": "backend_api",
            "to": "payment_provider",
            "label": "Creates payment intents",
            "technology": "REST API",
            "tags": ["ExternalCall"],
        },
        {
            "type": "REL",
            "from": "backend_api",
            "to": "recommendation_api",
            "label": "Fetches recommendations",
            "technology": "REST API",
            "tags": ["ExternalCall"],
        },
        {
            "type": "REL",
            "from": "backend_api",
            "to": "fraud_db",
            "label": "Checks fraud signals",
            "technology": "JDBC",
            "tags": ["ExternalCall"],
        },
        {
            "type": "REL",
            "from": "shipping_events",
            "to": "backend_api",
            "label": "Delivers shipping updates",
            "technology": "Kafka",
            "tags": ["AsyncRequest"],
        },
        {
            "type": "REL",
            "from": "support_agent",
            "to": "backend_api",
            "label": "Queries order state",
            "technology": "HTTPS",
            "tags": ["SupportFlow"],
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "customer", "to": "web_app"},
        {"type": "LAY_R", "from": "web_app", "to": "backend_api"},
        {"type": "LAY_D", "from": "backend_api", "to": "orders_db"},
        {"type": "LAY_R", "from": "backend_api", "to": "payment_provider"},
        {"type": "LAY_D", "from": "backend_api", "to": "order_events"},
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "layout_with_legend": True,
            "layout_as_sketch": False,
            "set_sketch_style": {
                "bg_color": "#ffffff",
                "font_color": "#222222",
                "warning_color": "#cc3300",
                "font_name": "Inter",
                "footer_warning": "Architecture draft",
                "footer_text": "Container view",
            },
            "show_legend": {
                "details": "Normal",
                "hide_stereotype": False,
            },
            "show_floating_legend": {
                "details": "Small",
                "hide_stereotype": True,
                "alias": "legend_box",
            },
            "hide_stereotype": False,
            "hide_person_sprite": False,
            "show_person_sprite": {"alias": "person"},
            "show_person_outline": True,
            "show_person_portrait": False,
            "show_element_descriptions": True,
            "show_foot_boxes": False,
            "show_index": False,
            "without_property_header": False,
            "legend_title": "Container Diagram Legend",
            "tags": [
                {
                    "type": "PersonTag",
                    "tag_stereo": "Customer",
                    "legend_text": "Primary customer actor",
                    "legend_sprite": "user",
                    "sprite": "user",
                    "bg_color": "#e8f5e9",
                    "font_color": "#1b5e20",
                    "border_color": "#66bb6a",
                    "shadowing": False,
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                },
                {
                    "type": "ExternalPersonTag",
                    "tag_stereo": "ExternalPerson",
                    "legend_text": "External support user",
                    "legend_sprite": "user",
                    "sprite": "user",
                    "bg_color": "#f5f5f5",
                    "font_color": "#424242",
                    "border_color": "#9e9e9e",
                    "shadowing": False,
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                },
                {
                    "type": "SystemTag",
                    "tag_stereo": "CoreSystem",
                    "legend_text": "Core internal system",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#e8f0fe",
                    "font_color": "#0d47a1",
                    "border_color": "#64b5f6",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ExternalSystemTag",
                    "tag_stereo": "ExternalSystem",
                    "legend_text": "External system dependency",
                    "legend_sprite": "cloud",
                    "sprite": "cloud",
                    "bg_color": "#f5f5f5",
                    "font_color": "#424242",
                    "border_color": "#9e9e9e",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "Frontend",
                    "legend_text": "User-facing frontend container",
                    "legend_sprite": "browser",
                    "sprite": "browser",
                    "bg_color": "#e3f2fd",
                    "font_color": "#0d47a1",
                    "border_color": "#64b5f6",
                    "shadowing": True,
                    "technology": "Web UI",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "Backend",
                    "legend_text": "Backend application container",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#ede7f6",
                    "font_color": "#311b92",
                    "border_color": "#673ab7",
                    "shadowing": True,
                    "technology": "Python / FastAPI",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "CoreRuntime",
                    "legend_text": "Core runtime container",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#ede7f6",
                    "font_color": "#4527a0",
                    "border_color": "#7e57c2",
                    "shadowing": True,
                    "technology": "Python 3.12",
                    "border_style": "BoldLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "DataStore",
                    "legend_text": "Internal data store",
                    "legend_sprite": "database",
                    "sprite": "database",
                    "bg_color": "#fff8e1",
                    "font_color": "#5d4037",
                    "border_color": "#ffb300",
                    "shadowing": False,
                    "technology": "PostgreSQL",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "AsyncChannel",
                    "legend_text": "Internal asynchronous channel",
                    "legend_sprite": "queue",
                    "sprite": "queue",
                    "bg_color": "#fff3e0",
                    "font_color": "#e65100",
                    "border_color": "#fb8c00",
                    "shadowing": False,
                    "technology": "Kafka",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                },
                {
                    "type": "ExternalContainerTag",
                    "tag_stereo": "ExternalContainer",
                    "legend_text": "External container dependency",
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
                {
                    "type": "ExternalContainerTag",
                    "tag_stereo": "ExternalDataStore",
                    "legend_text": "External data store",
                    "legend_sprite": "database",
                    "sprite": "database",
                    "bg_color": "#f5f5f5",
                    "font_color": "#424242",
                    "border_color": "#9e9e9e",
                    "shadowing": False,
                    "technology": "Vendor DB",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                },
                {
                    "type": "ExternalContainerTag",
                    "tag_stereo": "ExternalAsyncChannel",
                    "legend_text": "External asynchronous channel",
                    "legend_sprite": "queue",
                    "sprite": "queue",
                    "bg_color": "#f3e5f5",
                    "font_color": "#6a1b9a",
                    "border_color": "#ab47bc",
                    "shadowing": False,
                    "technology": "Kafka",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                },
                {
                    "type": "BoundaryTag",
                    "tag_stereo": "EnterpriseBoundary",
                    "legend_text": "Enterprise boundary",
                    "bg_color": "#fafafa",
                    "font_color": "#424242",
                    "border_color": "#9e9e9e",
                    "shadowing": False,
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                },
                {
                    "type": "BoundaryTag",
                    "tag_stereo": "SystemBoundary",
                    "legend_text": "System boundary",
                    "bg_color": "#fff8e1",
                    "font_color": "#5d4037",
                    "border_color": "#ffb300",
                    "shadowing": False,
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "BoundaryTag",
                    "tag_stereo": "ContainerBoundary",
                    "legend_text": "Container boundary",
                    "bg_color": "#f1f8e9",
                    "font_color": "#33691e",
                    "border_color": "#8bc34a",
                    "shadowing": False,
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "SyncRequest",
                    "legend_text": "Synchronous request/response flow",
                    "text_color": "#1565c0",
                    "line_color": "#1e88e5",
                    "line_style": "SolidLine",
                    "line_thickness": "1",
                    "technology": "HTTPS/JSON",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "DataAccess",
                    "legend_text": "Database access",
                    "text_color": "#6d4c41",
                    "line_color": "#8d6e63",
                    "line_style": "DashedLine",
                    "line_thickness": "1",
                    "technology": "SQL",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "AsyncRequest",
                    "legend_text": "Asynchronous messaging flow",
                    "legend_sprite": "queue",
                    "sprite": "queue",
                    "text_color": "#6a1b9a",
                    "line_color": "#8e24aa",
                    "line_style": "DottedLine",
                    "line_thickness": "2",
                    "technology": "Kafka",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "ExternalCall",
                    "legend_text": "External service/data call",
                    "text_color": "#455a64",
                    "line_color": "#78909c",
                    "line_style": "DashedLine",
                    "line_thickness": "1",
                    "technology": "REST API / JDBC",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "SupportFlow",
                    "legend_text": "Support access flow",
                    "text_color": "#2e7d32",
                    "line_color": "#43a047",
                    "line_style": "SolidLine",
                    "line_thickness": "1",
                    "technology": "HTTPS",
                },
            ],
            "styles": [
                {
                    "type": "ElementStyle",
                    "element_name": "backend_api",
                    "bg_color": "#ede7f6",
                    "font_color": "#311b92",
                    "border_color": "#673ab7",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "Python / FastAPI",
                    "legend_text": "Core backend service",
                    "legend_sprite": "server",
                    "border_style": "BoldLine",
                    "border_thickness": "2",
                },
                {
                    "type": "SystemBoundaryStyle",
                    "element_name": "shop_boundary",
                    "bg_color": "#fff8e1",
                    "font_color": "#5d4037",
                    "border_color": "#ffb300",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "stereotype": "System",
                    "legend_text": "System boundary",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ContainerBoundaryStyle",
                    "element_name": "checkout_boundary",
                    "bg_color": "#f1f8e9",
                    "font_color": "#33691e",
                    "border_color": "#8bc34a",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "stereotype": "Container",
                    "legend_text": "Container boundary",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                },
                {
                    "type": "RelStyle",
                    "text_color": "#37474f",
                    "line_color": "#546e7a",
                },
            ],
        }
    },
}


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
        json_schema_extra={
            "title": __diagram_class__.__name__,
            "examples": [
                CONTAINER_DIAGRAM_MINIMAL_EXAMPLE,
                CONTAINER_DIAGRAM_ADVANCED_EXAMPLE,
            ],
        }
    )

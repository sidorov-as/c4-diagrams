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


CONTAINER_DIAGRAM_MINIMAL_EXAMPLE: dict[str, Any] = {
    "type": "ContainerDiagram",
    "title": "Web App",
    "elements": [
        {
            "type": "Person",
            "alias": "user",
            "label": "User",
            "tags": ["User"],
        }
    ],
    "boundaries": [
        {
            "type": "SystemBoundary",
            "alias": "system",
            "label": "Simple System",
            "tags": ["SystemBoundary"],
            "elements": [
                {
                    "type": "Container",
                    "alias": "web",
                    "label": "Web App",
                    "technology": "React",
                    "tags": ["Frontend"],
                },
                {
                    "type": "Container",
                    "alias": "api",
                    "label": "API",
                    "technology": "Python",
                    "tags": ["Backend"],
                },
                {
                    "type": "ContainerDb",
                    "alias": "db",
                    "label": "Database",
                    "technology": "PostgreSQL",
                    "tags": ["Database"],
                },
            ],
            "boundaries": [],
            "relationships": [],
        }
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "user",
            "to": "web",
            "label": "Uses",
            "tags": ["Sync"],
        },
        {
            "type": "REL",
            "from": "web",
            "to": "api",
            "label": "Calls",
            "tags": ["Sync"],
        },
        {
            "type": "REL",
            "from": "api",
            "to": "db",
            "label": "Reads/Writes",
            "tags": ["Data"],
        },
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "styles": [
                {
                    "type": "ElementStyle",
                    "element_name": "container",
                    "bg_color": "#eeeeff",
                }
            ],
            "tags": [
                {"type": "PersonTag", "tag_stereo": "User"},
                {"type": "ContainerTag", "tag_stereo": "Frontend"},
                {"type": "ContainerTag", "tag_stereo": "Backend"},
                {"type": "ContainerTag", "tag_stereo": "Database"},
                {"type": "BoundaryTag", "tag_stereo": "SystemBoundary"},
                {"type": "RelTag", "tag_stereo": "Sync"},
                {"type": "RelTag", "tag_stereo": "Data"},
            ],
        }
    },
}

CONTAINER_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    "type": "ContainerDiagram",
    "title": "Online Shop - Container Diagram",
    "elements": [
        {
            "type": "Person",
            "alias": "customer",
            "label": "Customer",
            "description": "Browses products and places orders.",
            "sprite": "user",
            "stereotype": "Primary User",
            "tags": ["Customer"],
            "properties": {"properties": [["Channel", "Web / Mobile"]]},
        },
        {
            "type": "PersonExt",
            "alias": "support_agent",
            "label": "Support Agent",
            "description": (
                "Investigates customer issues from an external support tool."
            ),
            "sprite": "user",
            "stereotype": "External User",
            "tags": ["ExternalSupport"],
            "properties": {"properties": [["Organization", "Support Vendor"]]},
        },
        {
            "type": "SystemExt",
            "alias": "payment_provider",
            "label": "Payment Provider",
            "description": "Processes card payments and payment webhooks.",
            "sprite": "cloud",
            "stereotype": "External System",
            "tags": ["ExternalSystem"],
        },
        {
            "type": "ContainerExt",
            "alias": "recommendation_api",
            "label": "Recommendation API",
            "description": "Returns personalized product recommendations.",
            "sprite": "cloud",
            "technology": "REST API",
            "tags": ["ExternalContainer"],
        },
        {
            "type": "ContainerDbExt",
            "alias": "fraud_db",
            "label": "Fraud Signals DB",
            "description": (
                "External datastore containing fraud intelligence."
            ),
            "sprite": "database",
            "technology": "Vendor DB",
            "tags": ["ExternalDataStore"],
        },
        {
            "type": "ContainerQueueExt",
            "alias": "shipping_events",
            "label": "Shipping Events Topic",
            "description": "External topic used by logistics partner.",
            "sprite": "queue",
            "technology": "Kafka",
            "tags": ["ExternalAsyncChannel"],
        },
    ],
    "boundaries": [
        {
            "type": "EnterpriseBoundary",
            "alias": "acme",
            "label": "Acme Corp",
            "description": "Enterprise boundary for internal platforms.",
            "tags": ["EnterpriseBoundary"],
            "properties": {
                "properties": [
                    ["Region", "EU"],
                    ["Business Unit", "Digital Commerce"],
                ]
            },
            "elements": [],
            "boundaries": [
                {
                    "type": "SystemBoundary",
                    "alias": "shop_boundary",
                    "label": "Online Shop Platform",
                    "description": (
                        "Main system boundary for the commerce platform."
                    ),
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
                            "alias": "web_app",
                            "label": "Web Application",
                            "description": (
                                "Serves the storefront and checkout UI."
                            ),
                            "sprite": "browser",
                            "technology": "React + Next.js",
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
                            "alias": "backend_api",
                            "label": "Backend API",
                            "description": (
                                "Handles catalog, carts, checkout, and "
                                "order APIs."
                            ),
                            "sprite": "server",
                            "technology": "Python / FastAPI",
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
                            "alias": "orders_db",
                            "label": "Orders Database",
                            "description": (
                                "Stores orders, payments, and "
                                "status transitions."
                            ),
                            "sprite": "database",
                            "technology": "PostgreSQL",
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
                            "alias": "order_events",
                            "label": "Order Events Queue",
                            "description": (
                                "Publishes asynchronous order lifecycle events."
                            ),
                            "sprite": "queue",
                            "technology": "Kafka",
                            "tags": ["AsyncChannel"],
                            "properties": {
                                "properties": [
                                    ["Retention", "7 days"],
                                    ["Format", "JSON"],
                                ]
                            },
                        },
                    ],
                    "boundaries": [
                        {
                            "type": "ContainerBoundary",
                            "alias": "checkout_boundary",
                            "label": "Checkout Subsystem",
                            "description": (
                                "Groups checkout-related containers."
                            ),
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
                                    "alias": "checkout_api",
                                    "label": "Checkout API",
                                    "description": (
                                        "Handles checkout and "
                                        "payment orchestration."
                                    ),
                                    "technology": "Python / FastAPI",
                                    "tags": ["Backend"],
                                },
                                {
                                    "type": "ContainerDb",
                                    "alias": "checkout_db",
                                    "label": "Checkout DB",
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
                        }
                    ],
                    "relationships": [],
                }
            ],
            "relationships": [],
        }
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
        {"type": "LAY_D", "from": "backend_api", "to": "order_events"},
        {"type": "LAY_R", "from": "backend_api", "to": "payment_provider"},
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "layout_as_sketch": False,
            "layout_with_legend": True,
            "legend_title": "Container Diagram Legend",
            "hide_stereotype": False,
            "hide_person_sprite": False,
            "show_person_outline": True,
            "show_person_portrait": False,
            "show_person_sprite": {"alias": "person"},
            "show_legend": {"details": "Normal", "hide_stereotype": False},
            "show_floating_legend": {
                "alias": "legend_box",
                "details": "Small",
                "hide_stereotype": True,
            },
            "set_sketch_style": {
                "bg_color": "#ffffff",
                "font_color": "#222222",
                "font_name": "Inter",
                "footer_text": "Container view",
                "footer_warning": "Architecture draft",
                "warning_color": "#cc3300",
            },
            "without_property_header": False,
            "styles": [
                {
                    "type": "ElementStyle",
                    "element_name": "container",
                    "bg_color": "#ede7f6",
                    "border_color": "#673ab7",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "font_color": "#311b92",
                    "legend_text": "Application container",
                    "legend_sprite": "server",
                    "shape": "RoundedBoxShape",
                    "shadowing": True,
                },
                {
                    "type": "SystemBoundaryStyle",
                    "element_name": "systemboundary",
                    "bg_color": "#fff8e1",
                    "border_color": "#ffb300",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "font_color": "#5d4037",
                    "legend_text": "System boundary",
                    "shape": "RoundedBoxShape",
                    "shadowing": False,
                },
                {
                    "type": "ContainerBoundaryStyle",
                    "element_name": "containerboundary",
                    "bg_color": "#f1f8e9",
                    "border_color": "#8bc34a",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "font_color": "#33691e",
                    "legend_text": "Container boundary",
                    "shape": "RoundedBoxShape",
                    "shadowing": False,
                },
                {
                    "type": "RelStyle",
                    "line_color": "#546e7a",
                    "text_color": "#37474f",
                },
            ],
            "tags": [
                {
                    "type": "PersonTag",
                    "tag_stereo": "Customer",
                    "bg_color": "#e8f5e9",
                    "border_color": "#66bb6a",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "font_color": "#1b5e20",
                    "legend_sprite": "user",
                    "legend_text": "Primary customer actor",
                    "sprite": "user",
                    "shadowing": False,
                },
                {
                    "type": "ExternalPersonTag",
                    "tag_stereo": "ExternalSupport",
                    "bg_color": "#f5f5f5",
                    "border_color": "#9e9e9e",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "font_color": "#424242",
                    "legend_sprite": "user",
                    "legend_text": "External support user",
                    "sprite": "user",
                    "shadowing": False,
                },
                {
                    "type": "ExternalSystemTag",
                    "tag_stereo": "ExternalSystem",
                    "bg_color": "#f5f5f5",
                    "border_color": "#9e9e9e",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "font_color": "#424242",
                    "legend_sprite": "cloud",
                    "legend_text": "External system dependency",
                    "sprite": "cloud",
                    "shape": "RoundedBoxShape",
                    "shadowing": False,
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "Frontend",
                    "bg_color": "#e3f2fd",
                    "border_color": "#64b5f6",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "font_color": "#0d47a1",
                    "legend_sprite": "browser",
                    "legend_text": "User-facing frontend container",
                    "sprite": "browser",
                    "technology": "Web UI",
                    "shadowing": True,
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "Backend",
                    "bg_color": "#ede7f6",
                    "border_color": "#673ab7",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "font_color": "#311b92",
                    "legend_sprite": "server",
                    "legend_text": "Backend application container",
                    "sprite": "server",
                    "technology": "Python / FastAPI",
                    "shadowing": True,
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "CoreRuntime",
                    "bg_color": "#ede7f6",
                    "border_color": "#7e57c2",
                    "border_style": "BoldLine",
                    "border_thickness": "2",
                    "font_color": "#4527a0",
                    "legend_sprite": "server",
                    "legend_text": "Core runtime container",
                    "sprite": "server",
                    "technology": "Python 3.12",
                    "shadowing": True,
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "DataStore",
                    "bg_color": "#fff8e1",
                    "border_color": "#ffb300",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "font_color": "#5d4037",
                    "legend_sprite": "database",
                    "legend_text": "Internal data store",
                    "sprite": "database",
                    "technology": "PostgreSQL",
                    "shadowing": False,
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "AsyncChannel",
                    "bg_color": "#fff3e0",
                    "border_color": "#fb8c00",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "font_color": "#e65100",
                    "legend_sprite": "queue",
                    "legend_text": "Internal asynchronous channel",
                    "sprite": "queue",
                    "technology": "Kafka",
                    "shadowing": False,
                },
                {
                    "type": "ExternalContainerTag",
                    "tag_stereo": "ExternalContainer",
                    "bg_color": "#f5f5f5",
                    "border_color": "#9e9e9e",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "font_color": "#424242",
                    "legend_sprite": "cloud",
                    "legend_text": "External container dependency",
                    "sprite": "cloud",
                    "technology": "REST API",
                    "shape": "RoundedBoxShape",
                    "shadowing": False,
                },
                {
                    "type": "ExternalContainerTag",
                    "tag_stereo": "ExternalDataStore",
                    "bg_color": "#f5f5f5",
                    "border_color": "#9e9e9e",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "font_color": "#424242",
                    "legend_sprite": "database",
                    "legend_text": "External data store",
                    "sprite": "database",
                    "technology": "Vendor DB",
                    "shadowing": False,
                },
                {
                    "type": "ExternalContainerTag",
                    "tag_stereo": "ExternalAsyncChannel",
                    "bg_color": "#f3e5f5",
                    "border_color": "#ab47bc",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "font_color": "#6a1b9a",
                    "legend_sprite": "queue",
                    "legend_text": "External asynchronous channel",
                    "sprite": "queue",
                    "technology": "Kafka",
                    "shadowing": False,
                },
                {
                    "type": "BoundaryTag",
                    "tag_stereo": "EnterpriseBoundary",
                    "bg_color": "#fafafa",
                    "border_color": "#9e9e9e",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "font_color": "#424242",
                    "legend_text": "Enterprise boundary",
                    "shadowing": False,
                },
                {
                    "type": "BoundaryTag",
                    "tag_stereo": "SystemBoundary",
                    "bg_color": "#fff8e1",
                    "border_color": "#ffb300",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "font_color": "#5d4037",
                    "legend_text": "System boundary",
                    "shadowing": False,
                },
                {
                    "type": "BoundaryTag",
                    "tag_stereo": "ContainerBoundary",
                    "bg_color": "#f1f8e9",
                    "border_color": "#8bc34a",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "font_color": "#33691e",
                    "legend_text": "Container boundary",
                    "shadowing": False,
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "SyncRequest",
                    "legend_text": "Synchronous request/response flow",
                    "line_color": "#1e88e5",
                    "line_style": "SolidLine",
                    "line_thickness": "1",
                    "technology": "HTTPS/JSON",
                    "text_color": "#1565c0",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "DataAccess",
                    "legend_text": "Database access",
                    "line_color": "#8d6e63",
                    "line_style": "DashedLine",
                    "line_thickness": "1",
                    "technology": "SQL",
                    "text_color": "#6d4c41",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "AsyncRequest",
                    "legend_text": "Asynchronous messaging flow",
                    "legend_sprite": "queue",
                    "sprite": "queue",
                    "line_color": "#8e24aa",
                    "line_style": "DottedLine",
                    "line_thickness": "2",
                    "technology": "Kafka",
                    "text_color": "#6a1b9a",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "ExternalCall",
                    "legend_text": "External service/data call",
                    "line_color": "#78909c",
                    "line_style": "DashedLine",
                    "line_thickness": "1",
                    "technology": "REST API / JDBC",
                    "text_color": "#455a64",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "SupportFlow",
                    "legend_text": "Support access flow",
                    "line_color": "#43a047",
                    "line_style": "SolidLine",
                    "line_thickness": "1",
                    "technology": "HTTPS",
                    "text_color": "#2e7d32",
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

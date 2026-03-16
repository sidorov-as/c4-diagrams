from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import ConfigDict, Field

from c4 import (
    ContainerBoundary,
    DynamicDiagram,
    EnterpriseBoundary,
    SystemBoundary,
)
from c4.converters.json.schemas.diagrams.common import (
    BaseDiagramSchema,
    BaseSchemaItem,
    BoundaryBase,
    TypeDiagram,
)
from c4.converters.json.schemas.diagrams.common import (
    RelationshipSchema as RelationshipBase,
)
from c4.converters.json.schemas.diagrams.component import (
    ComponentDbExtSchema,
    ComponentDbSchema,
    ComponentExtSchema,
    ComponentQueueExtSchema,
    ComponentQueueSchema,
    ComponentSchema,
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
from c4.diagrams.core import increment, set_index


class IncrementSchema(BaseSchemaItem[increment]):
    """
    This schema describes the
    [`increment`][c4.diagrams.core.increment]
    diagram component.
    """

    type: Literal["increment"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    offset: int | None = Field(
        default=1, description="The amount to increment the index by."
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"type": "increment", "offset": 1}]}
    )


class SetIndexSchema(BaseSchemaItem[set_index]):
    """
    This schema describes the
    [`set_index`][c4.diagrams.core.set_index]
    diagram component.
    """

    type: Literal["set_index"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    new_index: int = Field(
        ..., description="The value to assign to the internal index."
    )

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"type": "set_index", "new_index": 10}]}
    )


class DynamicRelationshipSchema(RelationshipBase):
    index: str | None = Field(
        None, description="Optional index associated with the relationship."
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "REL",
                    "from": "customer",
                    "to": "online_shop",
                    "label": "Submits order",
                    "description": "Customer starts the checkout flow.",
                    "technology": "HTTPS",
                    "tags": ["request_flow"],
                    "index": "1",
                }
            ]
        }
    )


class DynamicEnterpriseBoundarySchema(BoundaryBase[EnterpriseBoundary]):
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


class DynamicSystemBoundarySchema(BoundaryBase[SystemBoundary]):
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
                        "Boundary for the commerce system and its"
                        " internal components."
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


class DynamicContainerBoundarySchema(BoundaryBase[ContainerBoundary]):
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
    | ComponentSchema
    | ComponentExtSchema
    | ComponentDbSchema
    | ComponentDbExtSchema
    | ComponentQueueSchema
    | ComponentQueueExtSchema
)

AnyBoundary = (
    DynamicEnterpriseBoundarySchema
    | DynamicSystemBoundarySchema
    | DynamicContainerBoundarySchema
)

AnyRelationship = DynamicRelationshipSchema | IncrementSchema | SetIndexSchema


DYNAMIC_DIAGRAM_MINIMAL_EXAMPLE: dict[str, Any] = {
    "type": "DynamicDiagram",
    "title": "Checkout Flow - Minimal Dynamic View",
    "elements": [
        {
            "type": "Person",
            "label": "Customer",
            "alias": "customer",
            "description": "Places an order through the storefront.",
            "tags": ["person"],
        },
        {
            "type": "System",
            "label": "Online Shop",
            "alias": "online_shop",
            "description": "Main commerce system.",
            "tags": ["system"],
        },
        {
            "type": "SystemExt",
            "label": "Payment Gateway",
            "alias": "payment_gateway",
            "description": "Processes card payments.",
            "tags": ["external"],
        },
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "customer",
            "to": "online_shop",
            "label": "Submits checkout",
            "technology": "HTTPS",
            "index": "1",
        },
        {
            "type": "REL",
            "from": "online_shop",
            "to": "payment_gateway",
            "label": "Creates payment",
            "technology": "REST API",
            "index": "2",
        },
        {
            "type": "REL_BACK",
            "from": "payment_gateway",
            "to": "online_shop",
            "label": "Returns payment result",
            "technology": "HTTPS",
            "index": "3",
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "customer", "to": "online_shop"},
        {"type": "LAY_R", "from": "online_shop", "to": "payment_gateway"},
    ],
}

DYNAMIC_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    "type": "DynamicDiagram",
    "title": "Checkout and Fulfillment - Dynamic Diagram",
    "elements": [
        {
            "type": "Person",
            "label": "Customer",
            "alias": "customer",
            "description": "Initiates checkout and order placement.",
            "stereotype": "Primary User",
            "sprite": "user",
            "tags": ["primary_actor"],
        },
        {
            "type": "PersonExt",
            "label": "Warehouse Operator",
            "alias": "warehouse_operator",
            "description": (
                "Receives fulfillment requests in an external warehouse system."
            ),
            "stereotype": "External User",
            "sprite": "user",
            "tags": ["external_actor"],
        },
        {
            "type": "System",
            "label": "Online Shop",
            "alias": "online_shop",
            "description": (
                "Main system coordinating cart, checkout, and order placement."
            ),
            "stereotype": "Software System",
            "base_shape": "RoundedBox",
            "sprite": "server",
            "tags": ["core_system"],
        },
        {
            "type": "SystemDb",
            "label": "Orders Database",
            "alias": "orders_db",
            "description": "Stores created orders and status changes.",
            "stereotype": "Database",
            "sprite": "database",
            "tags": ["data_store"],
        },
        {
            "type": "SystemQueue",
            "label": "Order Events Stream",
            "alias": "order_events",
            "description": "Publishes order-created and order-paid events.",
            "stereotype": "Queue",
            "sprite": "queue",
            "tags": ["async_channel"],
        },
        {
            "type": "SystemExt",
            "label": "Payment Gateway",
            "alias": "payment_gateway",
            "description": "External payment processor.",
            "stereotype": "External System",
            "base_shape": "RoundedBox",
            "sprite": "cloud",
            "tags": ["external_system"],
        },
        {
            "type": "SystemExt",
            "label": "Warehouse System",
            "alias": "warehouse_system",
            "description": "External fulfillment platform.",
            "stereotype": "External System",
            "base_shape": "RoundedBox",
            "sprite": "truck",
            "tags": ["external_system"],
        },
    ],
    "boundaries": [
        {
            "type": "EnterpriseBoundary",
            "label": "Acme Retail",
            "alias": "acme_enterprise",
            "description": "Enterprise scope of the dynamic interaction.",
            "tags": ["enterprise"],
            "elements": [
                {
                    "type": "System",
                    "label": "Online Shop",
                    "alias": "online_shop_inside",
                    "description": "Reference system inside enterprise scope.",
                }
            ],
            "boundaries": [],
            "properties": {
                "properties": [["Region", "EU"], ["Domain", "Commerce"]]
            },
        },
        {
            "type": "SystemBoundary",
            "label": "Checkout Runtime",
            "alias": "shop_system",
            "description": "System runtime relevant to checkout flow.",
            "tags": ["system_boundary"],
            "elements": [
                {
                    "type": "SystemDb",
                    "label": "Orders Database",
                    "alias": "orders_db_inside",
                    "description": "Order persistence runtime.",
                },
                {
                    "type": "SystemQueue",
                    "label": "Order Events Stream",
                    "alias": "order_events_inside",
                    "description": "Async integration channel.",
                },
            ],
            "boundaries": [],
            "properties": {
                "properties": [
                    ["Owner", "Commerce Team"],
                    ["Criticality", "High"],
                ]
            },
        },
    ],
    "relationships": [
        {"type": "set_index", "new_index": 1},
        {
            "type": "REL",
            "from": "customer",
            "to": "online_shop",
            "label": "Opens checkout",
            "technology": "HTTPS",
            "tags": ["request_flow"],
            "index": "1",
        },
        {"type": "increment", "offset": 1},
        {
            "type": "REL",
            "from": "online_shop",
            "to": "payment_gateway",
            "label": "Creates payment intent",
            "technology": "REST API",
            "tags": ["external_call"],
            "index": "2",
        },
        {"type": "increment", "offset": 1},
        {
            "type": "REL_BACK",
            "from": "payment_gateway",
            "to": "online_shop",
            "label": "Returns authorization result",
            "technology": "HTTPS",
            "tags": ["external_call"],
            "index": "3",
        },
        {"type": "increment", "offset": 1},
        {
            "type": "REL",
            "from": "online_shop",
            "to": "orders_db",
            "label": "Stores order",
            "technology": "SQL",
            "tags": ["persistence"],
            "index": "4",
        },
        {"type": "increment", "offset": 1},
        {
            "type": "REL",
            "from": "online_shop",
            "to": "order_events",
            "label": "Publishes order created event",
            "technology": "Kafka",
            "tags": ["async_flow"],
            "index": "5",
        },
        {"type": "increment", "offset": 5},
        {
            "type": "REL",
            "from": "order_events",
            "to": "warehouse_system",
            "label": "Delivers fulfillment request",
            "technology": "Kafka",
            "tags": ["async_flow"],
            "index": "10",
        },
        {"type": "increment", "offset": 1},
        {
            "type": "REL",
            "from": "warehouse_system",
            "to": "warehouse_operator",
            "label": "Shows picking request",
            "technology": "Internal UI",
            "tags": ["human_step"],
            "index": "11",
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "customer", "to": "online_shop"},
        {"type": "LAY_R", "from": "online_shop", "to": "payment_gateway"},
        {"type": "LAY_D", "from": "online_shop", "to": "orders_db"},
        {"type": "LAY_D", "from": "online_shop", "to": "order_events"},
        {"type": "LAY_R", "from": "order_events", "to": "warehouse_system"},
        {
            "type": "LAY_R",
            "from": "warehouse_system",
            "to": "warehouse_operator",
        },
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
                "footer_warning": "Dynamic flow draft",
                "footer_text": "Checkout scenario",
            },
            "show_legend": {"details": "Normal", "hide_stereotype": False},
            "show_floating_legend": {
                "details": "Small",
                "hide_stereotype": True,
                "alias": "legend_box",
            },
            "hide_stereotype": False,
            "hide_person_sprite": False,
            "show_person_sprite": {"alias": "person"},
            "show_person_outline": True,
            "show_element_descriptions": True,
            "show_index": True,
            "legend_title": "Dynamic Diagram Legend",
            "tags": [
                {
                    "type": "PersonTag",
                    "tag_stereo": "PrimaryActor",
                    "legend_text": "Primary business actor",
                    "legend_sprite": "user",
                    "sprite": "user",
                    "bg_color": "#fff3e0",
                    "font_color": "#e65100",
                    "border_color": "#fb8c00",
                    "shadowing": False,
                    "stereotype": "person",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                },
                {
                    "tag_stereo": "CoreSystem",
                    "legend_text": "Core participating system",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#e8f5e9",
                    "font_color": "#1b5e20",
                    "border_color": "#66bb6a",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "type": "software system",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "tag_stereo": "AsyncFlow",
                    "legend_text": "Asynchronous flow",
                    "legend_sprite": "queue",
                    "sprite": "queue",
                    "text_color": "#6a1b9a",
                    "line_color": "#8e24aa",
                    "line_style": "DottedLine",
                    "line_thickness": "2",
                    "technology": "Kafka",
                },
            ],
            "styles": [
                {
                    "type": "ElementStyle",
                    "element_name": "payment_gateway",
                    "bg_color": "#fce4ec",
                    "font_color": "#880e4f",
                    "border_color": "#ec407a",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "sprite": "cloud",
                    "technology": "REST API",
                    "legend_text": "Payment provider",
                    "legend_sprite": "cloud",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                },
                {
                    "type": "ElementStyle",
                    "element_name": "shop_system",
                    "bg_color": "#e3f2fd",
                    "font_color": "#0d47a1",
                    "border_color": "#64b5f6",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "technology": "System Boundary",
                    "legend_text": "Checkout runtime scope",
                    "legend_sprite": "server",
                    "border_style": "DashedLine",
                    "border_thickness": "1",
                    "stereotype": "System",
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


class DynamicDiagramSchema(BaseDiagramSchema):
    """
    This schema describes the
    [`DynamicDiagram`][c4.diagrams.dynamic.DynamicDiagram]
    spec.
    """

    type: Literal["DynamicDiagram"] = Field(
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
    relationships: list[AnyRelationship] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )

    __diagram_class__: ClassVar[TypeDiagram] = DynamicDiagram

    model_config = ConfigDict(
        json_schema_extra={
            "title": __diagram_class__.__name__,
            "examples": [
                DYNAMIC_DIAGRAM_MINIMAL_EXAMPLE,
                DYNAMIC_DIAGRAM_MINIMAL_EXAMPLE,
            ],
        }
    )

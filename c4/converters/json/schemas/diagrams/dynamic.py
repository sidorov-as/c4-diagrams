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
    WithType,
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
from c4.diagrams.core import Boundary, increment, set_index


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


class DynamicEnterpriseBoundarySchema(
    BoundaryBase[EnterpriseBoundary],
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


class DynamicSystemBoundarySchema(
    BoundaryBase[SystemBoundary],
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


class DynamicBoundarySchema(
    BoundaryBase[Boundary],
    WithType,
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
    DynamicBoundarySchema
    | DynamicEnterpriseBoundarySchema
    | DynamicSystemBoundarySchema
    | DynamicContainerBoundarySchema
)

AnyRelationship = DynamicRelationshipSchema | IncrementSchema | SetIndexSchema


DYNAMIC_DIAGRAM_MINIMAL_EXAMPLE: dict[str, Any] = {
    "type": "DynamicDiagram",
    "title": "Login Flow",
    "elements": [
        {
            "type": "Person",
            "label": "User",
            "alias": "user",
            "description": "Signs in to the application.",
            "tags": ["person", "end_user"],
        },
        {
            "type": "System",
            "label": "Web App",
            "alias": "web_app",
            "description": "Main application used by customers.",
            "tags": ["system", "app"],
        },
        {
            "type": "SystemExt",
            "label": "Identity Provider",
            "alias": "idp",
            "description": "External authentication service.",
            "tags": ["system", "external"],
        },
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "user",
            "to": "web_app",
            "label": "Opens sign-in page",
            "technology": "HTTPS",
            "index": "1",
            "tags": ["request"],
        },
        {
            "type": "REL",
            "from": "web_app",
            "to": "idp",
            "label": "Authenticates user",
            "technology": "OIDC",
            "index": "2",
            "tags": ["auth_flow"],
        },
        {
            "type": "REL_BACK",
            "from": "idp",
            "to": "web_app",
            "label": "Returns identity token",
            "technology": "OIDC",
            "index": "3",
            "tags": ["auth_flow", "response"],
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "user", "to": "web_app"},
        {"type": "LAY_R", "from": "web_app", "to": "idp"},
    ],
    "render_options": {
        "plantuml": {
            "tags": [
                {
                    "type": "PersonTag",
                    "tag_stereo": "end_user",
                    "legend_text": "Application user",
                },
                {
                    "type": "SystemTag",
                    "tag_stereo": "app",
                    "legend_text": "Internal application",
                },
                {
                    "type": "ExternalSystemTag",
                    "tag_stereo": "external",
                    "legend_text": "External dependency",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "auth_flow",
                    "legend_text": "Authentication call",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "response",
                    "legend_text": "Response",
                },
            ]
        }
    },
}

DYNAMIC_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    "type": "DynamicDiagram",
    "title": "Order Fulfillment Flow",
    "elements": [
        {
            "type": "Person",
            "label": "Customer",
            "alias": "customer",
            "description": "Places orders in the online store.",
            "tags": ["person", "customer"],
        },
        {
            "type": "System",
            "label": "Online Store",
            "alias": "online_store",
            "description": "Customer-facing commerce platform.",
            "stereotype": "Software System",
            "tags": ["system", "core"],
        },
        {
            "type": "SystemExt",
            "label": "Payment Gateway",
            "alias": "payment_gateway",
            "description": "External provider that authorizes card payments.",
            "stereotype": "External System",
            "tags": ["system", "external"],
        },
        {
            "type": "SystemExt",
            "label": "Warehouse System",
            "alias": "warehouse_system",
            "description": (
                "External warehouse platform that reserves and ships items."
            ),
            "stereotype": "External System",
            "tags": ["system", "external", "fulfillment"],
        },
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "customer",
            "to": "online_store",
            "label": "Places order",
            "technology": "HTTPS",
            "index": "1",
            "tags": ["request"],
        },
        {
            "type": "REL",
            "from": "online_store",
            "to": "payment_gateway",
            "label": "Authorizes payment",
            "technology": "REST API",
            "index": "2",
            "tags": ["payment_call", "request"],
        },
        {
            "type": "REL_BACK",
            "from": "payment_gateway",
            "to": "online_store",
            "label": "Returns authorization result",
            "technology": "HTTPS",
            "index": "3",
            "tags": ["payment_call", "response"],
        },
        {
            "type": "REL",
            "from": "online_store",
            "to": "warehouse_system",
            "label": "Sends fulfillment request",
            "technology": "AMQP",
            "index": "4",
            "tags": ["fulfillment_call"],
        },
        {
            "type": "REL_BACK",
            "from": "warehouse_system",
            "to": "online_store",
            "label": "Confirms reservation",
            "technology": "AMQP",
            "index": "5",
            "tags": ["fulfillment_call", "response"],
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "customer", "to": "online_store"},
        {"type": "LAY_R", "from": "online_store", "to": "payment_gateway"},
        {"type": "LAY_D", "from": "payment_gateway", "to": "warehouse_system"},
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "legend_title": "Dynamic Flow Legend",
            "show_legend": {"details": "Normal"},
            "tags": [
                {
                    "type": "PersonTag",
                    "tag_stereo": "customer",
                    "legend_text": "Customer actor",
                    "bg_color": "#08427B",
                    "font_color": "#FFFFFF",
                    "border_color": "#052E56",
                },
                {
                    "type": "SystemTag",
                    "tag_stereo": "core",
                    "legend_text": "Core internal system",
                    "bg_color": "#1168BD",
                    "font_color": "#FFFFFF",
                    "border_color": "#0B4884",
                },
                {
                    "type": "ExternalSystemTag",
                    "tag_stereo": "external",
                    "legend_text": "External system",
                    "bg_color": "#999999",
                    "font_color": "#FFFFFF",
                    "border_color": "#6B6B6B",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "payment_call",
                    "legend_text": "Payment interaction",
                    "text_color": "#0B4884",
                    "line_color": "#0B4884",
                    "line_style": "BoldLine",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "fulfillment_call",
                    "legend_text": "Fulfillment interaction",
                    "text_color": "#1B5E20",
                    "line_color": "#1B5E20",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "response",
                    "legend_text": "Response message",
                    "text_color": "#6B6B6B",
                    "line_color": "#6B6B6B",
                    "line_style": "DottedLine",
                },
            ],
            "styles": [
                {
                    "type": "ElementStyle",
                    "element_name": "person",
                    "font_color": "#FFFFFF",
                },
                {
                    "type": "ElementStyle",
                    "element_name": "system",
                    "font_color": "#FFFFFF",
                },
                {
                    "type": "RelStyle",
                    "text_color": "#222222",
                    "line_color": "#444444",
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

from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import ConfigDict, Field

from c4 import (
    DeploymentDiagram,
    DeploymentNode,
    DeploymentNodeLeft,
    DeploymentNodeRight,
    Node,
    NodeLeft,
    NodeRight,
)
from c4.converters.json.schemas.diagrams.common import (
    BaseDiagramSchema,
    BoundaryBase,
    RelationshipSchema,
    TypeDiagram,
    WithBoundaryRelationship,
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


class NodeBase(WithBoundaryRelationship, WithType):
    sprite: str | None = Field(
        None, description="Optional sprite name to visually represent the node."
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


class NodeSchema(
    BoundaryBase[Node],
    NodeBase,
):
    """
    This schema describes the
    [`Node`][c4.diagrams.deployment.Node]
    diagram component.
    """

    type: Literal["Node"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "Node",
                    "label": "AWS Account",
                    "alias": "aws_account",
                    "description": (
                        "Top-level cloud account hosting the "
                        "production platform."
                    ),
                    "stereotype": "Cloud Account",
                    "sprite": "cloud",
                    "tags": ["node", "cloud"],
                    "link": "https://console.aws.amazon.com/",
                    "properties": {
                        "properties": [
                            ["Environment", "Production"],
                            ["Region Scope", "eu-central-1"],
                        ]
                    },
                    "elements": [],
                    "boundaries": [],
                    "relationships": [],
                }
            ]
        }
    )


class NodeLeftSchema(BoundaryBase[NodeLeft], NodeBase):
    """
    This schema describes the
    [`NodeLeft`][c4.diagrams.deployment.NodeLeft]
    diagram component.
    """

    type: Literal["NodeLeft"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "NodeLeft",
                    "label": "Public Network",
                    "alias": "public_network",
                    "description": (
                        "Ingress-facing network segment for public endpoints."
                    ),
                    "stereotype": "Network Segment",
                    "sprite": "network",
                    "tags": ["node", "network"],
                    "properties": {
                        "properties": [
                            ["Exposure", "Internet-facing"],
                            ["Zone", "DMZ"],
                        ]
                    },
                    "elements": [],
                    "boundaries": [],
                    "relationships": [],
                }
            ]
        }
    )


class NodeRightSchema(BoundaryBase[NodeRight], NodeBase):
    """
    This schema describes the
    [`NodeRight`][c4.diagrams.deployment.NodeRight]
    diagram component.
    """

    type: Literal["NodeRight"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "NodeRight",
                    "label": "Private Network",
                    "alias": "private_network",
                    "description": (
                        "Internal network segment for application and "
                        "data services."
                    ),
                    "stereotype": "Network Segment",
                    "sprite": "network",
                    "tags": ["node", "private"],
                    "properties": {
                        "properties": [
                            ["Exposure", "Internal only"],
                            ["CIDR", "10.0.0.0/16"],
                        ]
                    },
                    "elements": [],
                    "boundaries": [],
                    "relationships": [],
                }
            ]
        }
    )


class DeploymentNodeSchema(
    BoundaryBase[DeploymentNode],
    NodeBase,
):
    """
    This schema describes the
    [`DeploymentNode`][c4.diagrams.deployment.DeploymentNode]
    diagram component.
    """

    type: Literal["DeploymentNode"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "DeploymentNode",
                    "label": "Kubernetes Cluster",
                    "alias": "k8s_cluster",
                    "description": (
                        "Primary runtime cluster for web and API workloads."
                    ),
                    "stereotype": "Runtime Environment",
                    "sprite": "server",
                    "tags": ["deployment_node", "compute"],
                    "link": "https://kubernetes.io/",
                    "properties": {
                        "properties": [
                            ["Platform", "EKS"],
                            ["Region", "eu-central-1"],
                        ]
                    },
                    "elements": [],
                    "boundaries": [],
                    "relationships": [],
                }
            ]
        }
    )


class DeploymentNodeLeftSchema(BoundaryBase[DeploymentNodeLeft], NodeBase):
    """
    This schema describes the
    [`DeploymentNodeLeft`][c4.diagrams.deployment.DeploymentNodeLeft]
    diagram component.
    """

    type: Literal["DeploymentNodeLeft"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "DeploymentNodeLeft",
                    "label": "Edge Load Balancer",
                    "alias": "edge_lb",
                    "description": (
                        "Receives public HTTPS traffic and forwards "
                        "requests to the cluster."
                    ),
                    "stereotype": "Ingress",
                    "sprite": "router",
                    "tags": ["deployment_node", "edge"],
                    "properties": {
                        "properties": [
                            ["Type", "Application Load Balancer"],
                            ["TLS", "Enabled"],
                        ]
                    },
                    "elements": [],
                    "boundaries": [],
                    "relationships": [],
                }
            ]
        }
    )


class DeploymentNodeRightSchema(BoundaryBase[DeploymentNodeRight], NodeBase):
    """
    This schema describes the
    [`DeploymentNodeRight`][c4.diagrams.deployment.DeploymentNodeRight]
    diagram component.
    """

    type: Literal["DeploymentNodeRight"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "DeploymentNodeRight",
                    "label": "Managed Database Service",
                    "alias": "managed_db_service",
                    "description": (
                        "Managed relational database deployment for "
                        "transactional workloads."
                    ),
                    "stereotype": "Data Platform",
                    "sprite": "database",
                    "tags": ["deployment_node", "database"],
                    "properties": {
                        "properties": [
                            ["Engine", "PostgreSQL"],
                            ["Availability", "Multi-AZ"],
                        ]
                    },
                    "elements": [],
                    "boundaries": [],
                    "relationships": [],
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
    NodeSchema
    | NodeLeftSchema
    | NodeRightSchema
    | DeploymentNodeSchema
    | DeploymentNodeLeftSchema
    | DeploymentNodeRightSchema
)


DEPLOYMENT_DIAGRAM_MINIMAL_EXAMPLE: dict[str, Any] = {
    "type": "DeploymentDiagram",
    "title": "Web App Deployment",
    "elements": [
        {
            "type": "Person",
            "alias": "user",
            "label": "User",
            "description": "Uses the web application.",
            "tags": ["person"],
        }
    ],
    "boundaries": [
        {
            "type": "DeploymentNodeLeft",
            "alias": "web_node",
            "label": "Web Server",
            "description": "Hosts the frontend application.",
            "stereotype": "Compute Node",
            "sprite": "server",
            "tags": ["runtime_node"],
            "elements": [
                {
                    "type": "Container",
                    "alias": "web_app",
                    "label": "Web App",
                    "description": "Customer-facing web application.",
                    "technology": "Next.js",
                    "tags": ["frontend"],
                }
            ],
            "relationships": [],
            "boundaries": [],
        },
        {
            "type": "DeploymentNodeRight",
            "alias": "db_node",
            "label": "Database Server",
            "description": "Hosts the application database.",
            "stereotype": "Data Node",
            "sprite": "database",
            "tags": ["data_node"],
            "elements": [
                {
                    "type": "ContainerDb",
                    "alias": "app_db",
                    "label": "App Database",
                    "description": "Stores application data.",
                    "technology": "PostgreSQL",
                    "tags": ["database"],
                }
            ],
            "relationships": [],
            "boundaries": [],
        },
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "user",
            "to": "web_node",
            "label": "Uses",
            "technology": "HTTPS",
            "tags": ["encrypted_traffic"],
        },
        {
            "type": "REL",
            "from": "web_node",
            "to": "db_node",
            "label": "Reads and writes",
            "technology": "TLS / SQL",
            "tags": ["encrypted_traffic"],
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "user", "to": "web_node"},
        {"type": "LAY_R", "from": "web_node", "to": "db_node"},
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "tags": [
                {
                    "type": "PersonTag",
                    "tag_stereo": "person",
                    "legend_text": "End user",
                    "sprite": "user",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "frontend",
                    "legend_text": "Frontend container",
                    "sprite": "browser",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "database",
                    "legend_text": "Database container",
                    "sprite": "database",
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "runtime_node",
                    "legend_text": "Runtime deployment node",
                    "sprite": "server",
                    "technology": "Runtime",
                    "shape": "RoundedBoxShape",
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "data_node",
                    "legend_text": "Data deployment node",
                    "sprite": "database",
                    "technology": "Data",
                    "shape": "RoundedBoxShape",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "encrypted_traffic",
                    "legend_text": "Encrypted communication",
                    "sprite": "lock",
                    "technology": "TLS",
                },
            ],
        }
    },
}

DEPLOYMENT_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    "type": "DeploymentDiagram",
    "title": "Online Shop - Production Deployment",
    "elements": [
        {
            "type": "Person",
            "alias": "customer",
            "label": "Customer",
            "description": "Uses the online shop through a browser.",
            "tags": ["person"],
        },
        {
            "type": "ContainerExt",
            "alias": "payment_gateway",
            "label": "Payment Gateway",
            "description": "External service that processes card payments.",
            "technology": "HTTPS API",
            "tags": ["external_service"],
        },
    ],
    "boundaries": [
        {
            "type": "Node",
            "alias": "aws_prod",
            "label": "AWS Production Account",
            "description": "Production cloud account for the online shop.",
            "stereotype": "Cloud Account",
            "sprite": "cloud",
            "tags": ["cloud_account"],
            "properties": {
                "properties": [
                    ["Environment", "Production"],
                    ["Region", "eu-central-1"],
                ]
            },
            "elements": [],
            "relationships": [],
            "boundaries": [
                {
                    "type": "NodeLeft",
                    "alias": "public_subnet",
                    "label": "Public Subnet",
                    "description": "Internet-facing network segment.",
                    "stereotype": "Network Segment",
                    "sprite": "network",
                    "tags": ["public_network"],
                    "elements": [],
                    "relationships": [],
                    "boundaries": [
                        {
                            "type": "DeploymentNodeLeft",
                            "alias": "alb",
                            "label": "Application Load Balancer",
                            "description": (
                                "Terminates TLS and routes requests to "
                                "the web tier."
                            ),
                            "stereotype": "Ingress",
                            "sprite": "router",
                            "tags": ["edge_node"],
                            "elements": [
                                {
                                    "type": "Container",
                                    "alias": "web_app",
                                    "label": "Web Application",
                                    "description": (
                                        "Serves the storefront UI."
                                    ),
                                    "technology": "Next.js",
                                    "tags": ["frontend"],
                                }
                            ],
                            "relationships": [],
                            "boundaries": [],
                        }
                    ],
                },
                {
                    "type": "NodeRight",
                    "alias": "private_subnet",
                    "label": "Private Subnet",
                    "description": (
                        "Internal network segment for application "
                        "and data services."
                    ),
                    "stereotype": "Network Segment",
                    "sprite": "network",
                    "tags": ["private_network"],
                    "elements": [],
                    "relationships": [],
                    "boundaries": [
                        {
                            "type": "DeploymentNode",
                            "alias": "app_cluster",
                            "label": "Kubernetes Cluster",
                            "description": (
                                "Runs backend services and "
                                "asynchronous workers."
                            ),
                            "stereotype": "Runtime Environment",
                            "sprite": "server",
                            "tags": ["runtime_node"],
                            "properties": {
                                "properties": [
                                    ["Platform", "EKS"],
                                    ["Autoscaling", "Enabled"],
                                ]
                            },
                            "elements": [
                                {
                                    "type": "Container",
                                    "alias": "backend_api",
                                    "label": "Backend API",
                                    "description": (
                                        "Handles catalog, checkout, and "
                                        "order processing."
                                    ),
                                    "technology": "Python / FastAPI",
                                    "tags": ["backend"],
                                },
                                {
                                    "type": "ContainerQueue",
                                    "alias": "order_events",
                                    "label": "Order Events",
                                    "description": (
                                        "Internal asynchronous event stream."
                                    ),
                                    "technology": "Kafka",
                                    "tags": ["message_bus"],
                                },
                            ],
                            "relationships": [],
                            "boundaries": [],
                        },
                        {
                            "type": "DeploymentNodeRight",
                            "alias": "db_service",
                            "label": "Managed PostgreSQL",
                            "description": (
                                "Managed relational database service."
                            ),
                            "stereotype": "Data Platform",
                            "sprite": "database",
                            "tags": ["data_node"],
                            "properties": {
                                "properties": [
                                    ["Service", "RDS"],
                                    ["Mode", "Multi-AZ"],
                                ]
                            },
                            "elements": [
                                {
                                    "type": "ContainerDb",
                                    "alias": "orders_db",
                                    "label": "Orders Database",
                                    "description": (
                                        "Stores orders, payments, and "
                                        "fulfillment data."
                                    ),
                                    "technology": "PostgreSQL",
                                    "tags": ["database"],
                                }
                            ],
                            "relationships": [],
                            "boundaries": [],
                        },
                    ],
                },
            ],
        }
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "customer",
            "to": "alb",
            "label": "Uses",
            "technology": "HTTPS",
            "tags": ["encrypted_traffic"],
        },
        {
            "type": "REL",
            "from": "alb",
            "to": "app_cluster",
            "label": "Routes traffic to",
            "technology": "HTTPS",
            "tags": ["encrypted_traffic"],
        },
        {
            "type": "REL",
            "from": "app_cluster",
            "to": "db_service",
            "label": "Reads and writes",
            "technology": "TLS / SQL",
            "tags": ["encrypted_traffic"],
        },
        {
            "type": "REL",
            "from": "app_cluster",
            "to": "payment_gateway",
            "label": "Calls",
            "technology": "HTTPS/JSON",
            "tags": ["encrypted_traffic"],
        },
        {
            "type": "REL",
            "from": "backend_api",
            "to": "order_events",
            "label": "Publishes events to",
            "technology": "Kafka",
            "tags": ["async_flow"],
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "customer", "to": "alb"},
        {"type": "LAY_R", "from": "alb", "to": "app_cluster"},
        {"type": "LAY_D", "from": "app_cluster", "to": "db_service"},
        {"type": "LAY_R", "from": "app_cluster", "to": "payment_gateway"},
    ],
    "render_options": {
        "plantuml": {
            "layout": "LAYOUT_LEFT_RIGHT",
            "layout_with_legend": True,
            "legend_title": "Deployment Legend",
            "hide_stereotype": False,
            "hide_person_sprite": False,
            "show_person_outline": True,
            "show_person_sprite": {"alias": "person"},
            "show_legend": {"details": "Normal", "hide_stereotype": False},
            "styles": [
                {
                    "type": "RelStyle",
                    "line_color": "#546e7a",
                    "text_color": "#37474f",
                }
            ],
            "tags": [
                {
                    "type": "PersonTag",
                    "tag_stereo": "person",
                    "legend_text": "End user",
                    "sprite": "user",
                    "bg_color": "#e8f5e9",
                    "border_color": "#66bb6a",
                    "font_color": "#1b5e20",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ExternalContainerTag",
                    "tag_stereo": "external_service",
                    "legend_text": "External service",
                    "sprite": "cloud",
                    "bg_color": "#f3e5f5",
                    "border_color": "#ab47bc",
                    "font_color": "#4a148c",
                    "border_style": "DashedLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "frontend",
                    "legend_text": "Frontend container",
                    "sprite": "browser",
                    "bg_color": "#e3f2fd",
                    "border_color": "#42a5f5",
                    "font_color": "#0d47a1",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "backend",
                    "legend_text": "Backend container",
                    "sprite": "server",
                    "bg_color": "#ede7f6",
                    "border_color": "#7e57c2",
                    "font_color": "#311b92",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "database",
                    "legend_text": "Database container",
                    "sprite": "database",
                    "bg_color": "#fff3e0",
                    "border_color": "#fb8c00",
                    "font_color": "#e65100",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "ContainerTag",
                    "tag_stereo": "message_bus",
                    "legend_text": "Message queue / stream",
                    "sprite": "queue",
                    "bg_color": "#fce4ec",
                    "border_color": "#ec407a",
                    "font_color": "#880e4f",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "cloud_account",
                    "legend_text": "Cloud account boundary",
                    "legend_sprite": "cloud",
                    "sprite": "cloud",
                    "bg_color": "#eef6ff",
                    "border_color": "#64b5f6",
                    "font_color": "#0d47a1",
                    "technology": "Infrastructure",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "shape": "RoundedBoxShape",
                    "shadowing": True,
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "public_network",
                    "legend_text": "Public network zone",
                    "legend_sprite": "network",
                    "sprite": "network",
                    "bg_color": "#f1f8e9",
                    "border_color": "#8bc34a",
                    "font_color": "#33691e",
                    "technology": "DMZ",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "shape": "RoundedBoxShape",
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "private_network",
                    "legend_text": "Private network zone",
                    "legend_sprite": "network",
                    "sprite": "network",
                    "bg_color": "#fbe9e7",
                    "border_color": "#ff8a65",
                    "font_color": "#bf360c",
                    "technology": "Internal",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "shape": "RoundedBoxShape",
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "edge_node",
                    "legend_text": "Ingress deployment node",
                    "legend_sprite": "router",
                    "sprite": "router",
                    "bg_color": "#e1f5fe",
                    "border_color": "#29b6f6",
                    "font_color": "#01579b",
                    "technology": "Ingress",
                    "border_style": "BoldLine",
                    "border_thickness": "2",
                    "shape": "RoundedBoxShape",
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "runtime_node",
                    "legend_text": "Runtime deployment node",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#e8f5e9",
                    "border_color": "#66bb6a",
                    "font_color": "#1b5e20",
                    "technology": "Runtime",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "shape": "RoundedBoxShape",
                    "shadowing": True,
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "data_node",
                    "legend_text": "Data deployment node",
                    "legend_sprite": "database",
                    "sprite": "database",
                    "bg_color": "#fff8e1",
                    "border_color": "#ffb300",
                    "font_color": "#ff6f00",
                    "technology": "Data Platform",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                    "shape": "RoundedBoxShape",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "encrypted_traffic",
                    "legend_text": "Encrypted communication",
                    "legend_sprite": "lock",
                    "sprite": "lock",
                    "line_color": "#1976d2",
                    "text_color": "#0d47a1",
                    "line_style": "SolidLine",
                    "line_thickness": "2",
                    "technology": "TLS",
                },
                {
                    "type": "RelTag",
                    "tag_stereo": "async_flow",
                    "legend_text": "Asynchronous event flow",
                    "legend_sprite": "queue",
                    "sprite": "queue",
                    "line_color": "#8e24aa",
                    "text_color": "#4a148c",
                    "line_style": "DashedLine",
                    "line_thickness": "2",
                    "technology": "Kafka",
                },
            ],
        }
    },
}


class DeploymentDiagramSchema(BaseDiagramSchema):
    """
    This schema describes the
    [`DeploymentDiagram`][c4.diagrams.deployment.DeploymentDiagram]
    spec.
    """

    type: Literal["DeploymentDiagram"] = Field(
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

    __diagram_class__: ClassVar[TypeDiagram] = DeploymentDiagram

    model_config = ConfigDict(
        json_schema_extra={
            "title": __diagram_class__.__name__,
            "examples": [
                DEPLOYMENT_DIAGRAM_MINIMAL_EXAMPLE,
                DEPLOYMENT_DIAGRAM_ADVANCED_EXAMPLE,
            ],
        }
    )

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
    "title": "Online Shop - Deployment Diagram",
    "elements": [
        {
            "type": "Container",
            "label": "Web Application",
            "alias": "web_app",
            "description": "Customer-facing web application.",
            "technology": "Next.js",
            "tags": ["frontend"],
        },
        {
            "type": "Container",
            "label": "Backend API",
            "alias": "backend_api",
            "description": (
                "Main backend API for catalog, checkout, and orders."
            ),
            "technology": "Python / FastAPI",
            "tags": ["backend"],
        },
        {
            "type": "ContainerDb",
            "label": "Orders Database",
            "alias": "orders_db",
            "description": "Stores orders and payment references.",
            "technology": "PostgreSQL",
            "tags": ["database"],
        },
    ],
    "boundaries": [
        {
            "type": "DeploymentNodeLeft",
            "label": "Load Balancer",
            "alias": "load_balancer",
            "description": "Public HTTPS entrypoint.",
            "stereotype": "Ingress",
            "sprite": "router",
            "elements": [
                {
                    "type": "Container",
                    "label": "Web Application",
                    "alias": "web_app_lb",
                    "description": "Public web tier replica.",
                    "technology": "Next.js",
                }
            ],
            "boundaries": [],
            "relationships": [],
        },
        {
            "type": "DeploymentNode",
            "label": "Application Server",
            "alias": "app_server",
            "description": "Runtime host for backend workloads.",
            "stereotype": "Compute Node",
            "sprite": "server",
            "elements": [
                {
                    "type": "Container",
                    "label": "Backend API",
                    "alias": "backend_api_hosted",
                    "description": (
                        "API process deployed on application server."
                    ),
                    "technology": "Python / FastAPI",
                }
            ],
            "boundaries": [],
            "relationships": [],
        },
        {
            "type": "DeploymentNodeRight",
            "label": "Database Server",
            "alias": "db_server",
            "description": "Managed database node for transactional data.",
            "stereotype": "Data Node",
            "sprite": "database",
            "elements": [
                {
                    "type": "ContainerDb",
                    "label": "Orders Database",
                    "alias": "orders_db_hosted",
                    "description": "Primary orders database instance.",
                    "technology": "PostgreSQL",
                }
            ],
            "boundaries": [],
            "relationships": [],
        },
    ],
    "relationships": [
        {
            "type": "REL",
            "from": "load_balancer",
            "to": "app_server",
            "label": "Routes requests to",
            "technology": "HTTPS",
        },
        {
            "type": "REL",
            "from": "app_server",
            "to": "db_server",
            "label": "Reads and writes",
            "technology": "TLS / SQL",
        },
    ],
}

DEPLOYMENT_DIAGRAM_ADVANCED_EXAMPLE: dict[str, Any] = {
    "type": "DeploymentDiagram",
    "title": "Online Shop - Deployment Diagram",
    "elements": [
        {
            "type": "Person",
            "label": "Customer",
            "alias": "customer",
            "description": "Uses the storefront over the internet.",
            "tags": ["person"],
        },
        {
            "type": "Container",
            "label": "Web Application",
            "alias": "web_app",
            "description": "Customer-facing web application.",
            "technology": "Next.js",
            "tags": ["frontend"],
        },
        {
            "type": "Container",
            "label": "Backend API",
            "alias": "backend_api",
            "description": "Handles catalog, checkout, and order processing.",
            "technology": "Python / FastAPI",
            "tags": ["backend"],
        },
        {
            "type": "ContainerQueue",
            "label": "Order Events",
            "alias": "order_events",
            "description": "Internal asynchronous event stream.",
            "technology": "Kafka",
            "tags": ["async"],
        },
        {
            "type": "ContainerDb",
            "label": "Orders Database",
            "alias": "orders_db",
            "description": "Stores orders and payment data.",
            "technology": "PostgreSQL",
            "tags": ["database"],
        },
        {
            "type": "ContainerExt",
            "label": "Payment Gateway",
            "alias": "payment_gateway",
            "description": "External payment processing service.",
            "technology": "REST API",
            "tags": ["external"],
        },
    ],
    "boundaries": [
        {
            "type": "Node",
            "label": "AWS Production Account",
            "alias": "aws_prod",
            "description": "Production cloud account.",
            "stereotype": "Cloud Account",
            "sprite": "cloud",
            "tags": ["node", "cloud"],
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
                    "label": "Public Subnet",
                    "alias": "public_subnet",
                    "description": "Internet-facing network zone.",
                    "stereotype": "Network Segment",
                    "sprite": "network",
                    "tags": ["node", "public"],
                    "elements": [],
                    "relationships": [],
                    "boundaries": [
                        {
                            "type": "DeploymentNodeLeft",
                            "label": "Application Load Balancer",
                            "alias": "alb",
                            "description": (
                                "Terminates TLS and routes traffic to "
                                "the web tier."
                            ),
                            "stereotype": "Ingress",
                            "sprite": "router",
                            "tags": ["edge_node"],
                            "elements": [
                                {
                                    "type": "Container",
                                    "label": "Web Application",
                                    "alias": "web_app_alb",
                                    "description": (
                                        "Web application deployment behind "
                                        "the ALB."
                                    ),
                                    "technology": "Next.js",
                                }
                            ],
                            "boundaries": [],
                            "relationships": [],
                        }
                    ],
                },
                {
                    "type": "NodeRight",
                    "label": "Private Subnet",
                    "alias": "private_subnet",
                    "description": (
                        "Internal network zone for application and "
                        "data services."
                    ),
                    "stereotype": "Network Segment",
                    "sprite": "network",
                    "tags": ["node", "private"],
                    "elements": [],
                    "relationships": [],
                    "boundaries": [
                        {
                            "type": "DeploymentNode",
                            "label": "Kubernetes Cluster",
                            "alias": "k8s_cluster",
                            "description": (
                                "Runtime cluster for stateless services."
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
                                    "label": "Backend API",
                                    "alias": "backend_api_cluster",
                                    "description": "Backend API pods.",
                                    "technology": "Python / FastAPI",
                                },
                                {
                                    "type": "ContainerQueue",
                                    "label": "Order Events",
                                    "alias": "order_events_cluster",
                                    "description": (
                                        "Internal messaging topic/broker "
                                        "access.",
                                    ),
                                    "technology": "Kafka",
                                },
                            ],
                            "boundaries": [],
                            "relationships": [],
                        },
                        {
                            "type": "DeploymentNodeRight",
                            "label": "Managed PostgreSQL",
                            "alias": "postgres_service",
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
                                    "label": "Orders Database",
                                    "alias": "orders_db_rds",
                                    "description": (
                                        "Primary production orders database."
                                    ),
                                    "technology": "PostgreSQL",
                                }
                            ],
                            "boundaries": [],
                            "relationships": [],
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
            "to": "k8s_cluster",
            "label": "Routes traffic to",
            "technology": "HTTPS",
            "tags": ["encrypted_traffic"],
        },
        {
            "type": "REL",
            "from": "k8s_cluster",
            "to": "postgres_service",
            "label": "Reads and writes",
            "technology": "TLS / SQL",
            "tags": ["encrypted_traffic"],
        },
        {
            "type": "REL",
            "from": "k8s_cluster",
            "to": "payment_gateway",
            "label": "Calls",
            "technology": "HTTPS/JSON",
            "tags": ["encrypted_traffic"],
        },
        {
            "type": "REL",
            "from": "k8s_cluster",
            "to": "order_events",
            "label": "Publishes events to",
            "technology": "Kafka",
            "tags": ["async_flow"],
        },
    ],
    "layouts": [
        {"type": "LAY_R", "from": "customer", "to": "alb"},
        {"type": "LAY_R", "from": "alb", "to": "k8s_cluster"},
        {"type": "LAY_D", "from": "k8s_cluster", "to": "postgres_service"},
        {"type": "LAY_R", "from": "k8s_cluster", "to": "payment_gateway"},
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
                "footer_warning": "Infrastructure draft",
                "footer_text": "Deployment view",
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
            "legend_title": "Deployment Legend",
            "tags": [
                {
                    "type": "NodeTag",
                    "tag_stereo": "CloudNode",
                    "legend_text": "Infrastructure / environment node",
                    "legend_sprite": "cloud",
                    "sprite": "cloud",
                    "bg_color": "#eef6ff",
                    "font_color": "#0d47a1",
                    "border_color": "#64b5f6",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "Infrastructure",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "NodeTag",
                    "tag_stereo": "RuntimeNode",
                    "legend_text": "Runtime deployment node",
                    "legend_sprite": "server",
                    "sprite": "server",
                    "bg_color": "#e8f5e9",
                    "font_color": "#1b5e20",
                    "border_color": "#66bb6a",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "technology": "Runtime",
                    "border_style": "SolidLine",
                    "border_thickness": "2",
                },
                {
                    "type": "",
                    "tag_stereo": "EncryptedTraffic",
                    "legend_text": "Encrypted communication",
                    "legend_sprite": "lock",
                    "sprite": "lock",
                    "text_color": "#0d47a1",
                    "line_color": "#1976d2",
                    "line_style": "SolidLine",
                    "line_thickness": "2",
                    "technology": "TLS",
                },
            ],
            "styles": [
                {
                    "type": "ElementStyle",
                    "element_name": "k8s_cluster",
                    "bg_color": "#ede7f6",
                    "font_color": "#311b92",
                    "border_color": "#7e57c2",
                    "shadowing": True,
                    "shape": "RoundedBoxShape",
                    "sprite": "server",
                    "technology": "EKS",
                    "legend_text": "Primary runtime cluster",
                    "legend_sprite": "server",
                    "border_style": "BoldLine",
                    "border_thickness": "2",
                    "stereotype": "DeploymentNode",
                },
                {
                    "type": "ElementStyle",
                    "element_name": "postgres_service",
                    "bg_color": "#fff3e0",
                    "font_color": "#e65100",
                    "border_color": "#fb8c00",
                    "shadowing": False,
                    "shape": "RoundedBoxShape",
                    "sprite": "database",
                    "technology": "RDS PostgreSQL",
                    "legend_text": "Managed database node",
                    "legend_sprite": "database",
                    "border_style": "SolidLine",
                    "border_thickness": "1",
                    "stereotype": "DeploymentNode",
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

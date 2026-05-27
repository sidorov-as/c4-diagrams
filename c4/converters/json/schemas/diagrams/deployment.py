from __future__ import annotations

from typing import ClassVar, Literal

from pydantic import ConfigDict, Field

from c4 import (
    DeploymentDiagram,
    DeploymentNode,
    Node,
)
from c4.converters.json.schemas.diagrams.common import (
    BaseDiagramSchema,
    BoundaryBase,
    RelationshipSchema,
    TypeDiagram,
    WithBoundaryRelationship,
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


class NodeBase(WithBoundaryRelationship):
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
                    "properties": {
                        "properties": [
                            ["Environment", "Production"],
                            ["Region Scope", "eu-central-1"],
                        ]
                    },
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
                    "properties": {
                        "properties": [
                            ["Platform", "EKS"],
                            ["Region", "eu-central-1"],
                        ]
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
    | ContainerSchema
    | ContainerExtSchema
    | ContainerDbSchema
    | ContainerDbExtSchema
    | ContainerQueueSchema
    | ContainerQueueExtSchema
)

AnyBoundary = NodeSchema | DeploymentNodeSchema


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
        json_schema_extra={"title": __diagram_class__.__name__}
    )

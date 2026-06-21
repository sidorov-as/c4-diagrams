from __future__ import annotations

# mypy: disable-error-code=assignment
import warnings
from enum import unique
from typing import Any, Literal, cast

from pydantic import ConfigDict, Field

from c4.compat import StrEnum
from c4.contrib.c4_macros import NodeLeft, NodeRight
from c4.contrib.mermaid.converters.json.render_options import (
    MermaidRenderOptionsSchema,
)
from c4.converters.json.schemas.base import TypeDiagramElement
from c4.converters.json.schemas.diagrams import deployment as deployment_core
from c4.converters.json.schemas.diagrams import system_context as context_core
from c4.converters.json.schemas.diagrams.common import (
    BoundaryBase,
    RelationshipSchema,
)
from c4.converters.json.schemas.diagrams.component import (
    ComponentDiagramSchema,
)
from c4.converters.json.schemas.diagrams.container import (
    ContainerDiagramSchema,
)
from c4.converters.json.schemas.diagrams.deployment import (
    DeploymentDiagramSchema,
)
from c4.converters.json.schemas.diagrams.dynamic import DynamicDiagramSchema
from c4.diagrams.core import Relationship
from c4.diagrams.core import RelationshipType as CoreRelationshipType
from c4.diagrams.core.enums import EnumDescriptionsMixin
from c4.enums import RendererEnum


@unique
class MermaidRelationshipType(EnumDescriptionsMixin, StrEnum):
    """Relationship types supported by Mermaid C4 diagrams."""

    REL = "REL"
    BI_REL = "BI_REL"
    REL_BACK = "REL_BACK"
    REL_D = "REL_D"
    REL_DOWN = "REL_DOWN"
    REL_U = "REL_U"
    REL_UP = "REL_UP"
    REL_L = "REL_L"
    REL_LEFT = "REL_LEFT"
    REL_R = "REL_R"
    REL_RIGHT = "REL_RIGHT"

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: Any,
        handler: Any,
    ) -> dict[str, Any]:
        """Use the portable relationship type title in generated JSON Schema."""
        json_schema = handler(core_schema)
        json_schema["title"] = "RelationshipType"
        return json_schema  # type: ignore[no-any-return]

    @classmethod
    def get_descriptions(cls) -> dict[MermaidRelationshipType, str]:
        """Return Mermaid relationship type descriptions."""
        relationship_descriptions = CoreRelationshipType.get_descriptions()
        return {
            member: relationship_descriptions[
                CoreRelationshipType(member.value)
            ]
            for member in cls
        }


warnings.filterwarnings(
    "ignore",
    message=r'Field name ".*" in ".*" shadows an attribute in parent ".*"',
    category=UserWarning,
    module=__name__,
)


class MermaidBackendMixin:
    """Mixin for Mermaid JSON schemas."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    backend: Literal[RendererEnum.MERMAID.value] = Field(  # type: ignore[name-defined]
        ..., description="JSON schema backend."
    )
    render_options: MermaidRenderOptionsSchema | None = Field(
        None,
        description="Mermaid-specific render options.",
    )


class MermaidRelationshipSchema(RelationshipSchema):
    """JSON schema for relationships supported by Mermaid C4 diagrams."""

    type: MermaidRelationshipType = Field(
        ..., description="Type of the relationship."
    )
    from_: str = Field(
        ...,
        min_length=1,
        description=(
            "The source element alias (or unique label). For Mermaid, this "
            "must resolve to a concrete element, not a boundary."
        ),
        alias="from",
    )
    to: str = Field(
        ...,
        min_length=1,
        description=(
            "The destination element alias (or unique label). For Mermaid, "
            "this must resolve to a concrete element, not a boundary."
        ),
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "REL_BACK",
                    "from": "idp",
                    "to": "web_app",
                    "label": "Returns identity token",
                    "technology": "OIDC",
                }
            ]
        }
    )

    def _get_diagram_element_class(self) -> TypeDiagramElement | None:
        """Return the relationship class for the Mermaid relationship type."""
        return Relationship.get_relationship_by_type(
            CoreRelationshipType(self.type.value)
        )


class MermaidBoundaryFields:
    """Mixin for Mermaid boundary convenience fields."""

    stereotype: str | None = Field(
        None,
        description="Optional Mermaid boundary type/stereotype label.",
    )

    def _to_diagram_element_kwargs(self) -> dict[str, Any]:
        """Move Mermaid boundary fields into the `mermaid` constructor kwarg."""
        data = cast(
            dict[str, Any],
            super()._to_diagram_element_kwargs(),  # type: ignore[misc]
        )
        stereotype = data.pop("stereotype", None)
        if stereotype:
            existing_kwarg_mermaid = data.pop("mermaid", None) or {}
            extensions = data.get("extensions") or {}
            mermaid_extensions = extensions.get("mermaid") or {}
            data["mermaid"] = {
                **mermaid_extensions,
                **existing_kwarg_mermaid,
                "type": stereotype,
            }

            if "mermaid" in extensions:
                extensions = {
                    key: value
                    for key, value in extensions.items()
                    if key != "mermaid"
                }

            if extensions:
                data["extensions"] = extensions
            else:
                data.pop("extensions", None)

        return data


class MermaidPersonSchema(context_core.PersonSchema):
    """Mermaid JSON schema for a person."""


class MermaidPersonExtSchema(context_core.PersonExtSchema):
    """Mermaid JSON schema for an external person."""


class MermaidSystemSchema(context_core.SystemSchema):
    """Mermaid JSON schema for a software system."""


class MermaidSystemExtSchema(context_core.SystemExtSchema):
    """Mermaid JSON schema for an external software system."""


class MermaidSystemDbSchema(context_core.SystemDbSchema):
    """Mermaid JSON schema for a database-like system."""


class MermaidSystemDbExtSchema(context_core.SystemDbExtSchema):
    """Mermaid JSON schema for an external database-like system."""


class MermaidSystemQueueSchema(context_core.SystemQueueSchema):
    """Mermaid JSON schema for a queue-like system."""


class MermaidSystemQueueExtSchema(context_core.SystemQueueExtSchema):
    """Mermaid JSON schema for an external queue-like system."""


MermaidSystemContextElement = (
    MermaidPersonSchema
    | MermaidPersonExtSchema
    | MermaidSystemSchema
    | MermaidSystemExtSchema
    | MermaidSystemDbSchema
    | MermaidSystemDbExtSchema
    | MermaidSystemQueueSchema
    | MermaidSystemQueueExtSchema
)


class MermaidBoundarySchema(
    MermaidBoundaryFields,
    context_core.BoundarySchema,
):
    """Mermaid JSON schema for a generic boundary."""

    elements: list[MermaidSystemContextElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[MermaidSystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "Boundary",
                    "label": "Commerce Platform",
                    "alias": "commerce_platform",
                    "stereotype": "enterprise",
                    "description": "Boundary for the commerce system.",
                    "relationships": [
                        {
                            "type": "REL_BACK",
                            "from": "orders_db",
                            "to": "web_storefront",
                            "label": "Returns order history",
                            "technology": "SQL",
                        }
                    ],
                    "elements": [
                        {
                            "type": "System",
                            "label": "Web Storefront",
                            "alias": "web_storefront",
                        },
                        {
                            "type": "SystemDb",
                            "label": "Orders DB",
                            "alias": "orders_db",
                        },
                    ],
                    "boundaries": [],
                }
            ]
        }
    )


class MermaidEnterpriseBoundarySchema(
    MermaidBoundaryFields,
    context_core.EnterpriseBoundarySchema,
):
    """Mermaid JSON schema for an enterprise boundary."""

    elements: list[MermaidSystemContextElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[MermaidSystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class MermaidSystemBoundarySchema(
    MermaidBoundaryFields,
    context_core.SystemBoundarySchema,
):
    """Mermaid JSON schema for a system boundary."""

    elements: list[MermaidSystemContextElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[MermaidSystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


MermaidSystemContextBoundary = (
    MermaidBoundarySchema
    | MermaidEnterpriseBoundarySchema
    | MermaidSystemBoundarySchema
)


class MermaidSystemContextDiagramSchema(
    MermaidBackendMixin,
    context_core.SystemContextDiagramSchema,
):
    """Mermaid JSON schema for a system context diagram."""

    elements: list[MermaidSystemContextElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[MermaidSystemContextBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class MermaidSystemLandscapeDiagramSchema(
    MermaidBackendMixin,
    context_core.SystemLandscapeDiagramSchema,
):
    """Mermaid JSON schema for a system landscape diagram."""

    elements: list[MermaidSystemContextElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[MermaidSystemContextBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class MermaidContainerDiagramSchema(
    MermaidBackendMixin,
    ContainerDiagramSchema,
):
    """Mermaid JSON schema for a container diagram."""

    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class MermaidComponentDiagramSchema(
    MermaidBackendMixin,
    ComponentDiagramSchema,
):
    """Mermaid JSON schema for a component diagram."""

    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class MermaidNodeLeftSchema(
    BoundaryBase[NodeLeft],
    deployment_core.NodeBase,
):
    """Mermaid JSON schema for a left-aligned deployment node."""

    type: Literal["NodeLeft"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[MermaidDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[MermaidDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class MermaidNodeRightSchema(
    BoundaryBase[NodeRight],
    deployment_core.NodeBase,
):
    """Mermaid JSON schema for a right-aligned deployment node."""

    type: Literal["NodeRight"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[MermaidDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[MermaidDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


MermaidDeploymentElement = deployment_core.AnyElement
MermaidDeploymentBoundary = (
    deployment_core.NodeSchema
    | MermaidNodeLeftSchema
    | MermaidNodeRightSchema
    | deployment_core.DeploymentNodeSchema
)


class MermaidDeploymentDiagramSchema(
    MermaidBackendMixin,
    DeploymentDiagramSchema,
):
    """Mermaid JSON schema for a deployment diagram."""

    elements: list[MermaidDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[MermaidDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class MermaidDynamicDiagramSchema(
    MermaidBackendMixin,
    DynamicDiagramSchema,
):
    """Mermaid JSON schema for a dynamic diagram."""

    relationships: list[MermaidRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )

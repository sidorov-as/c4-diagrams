from __future__ import annotations

# mypy: disable-error-code=assignment
import warnings
from typing import Any, Literal, cast

from pydantic import ConfigDict, Field

from c4.contrib.c4_macros import NodeLeft, NodeRight
from c4.contrib.plantuml import (
    DeploymentNodeLeft,
    DeploymentNodeRight,
    Layout,
    LayoutType,
    increment,
    set_index,
)
from c4.contrib.plantuml.converters.json.render_options import (
    PlantUMLRenderOptionsSchema,
)
from c4.converters.json.schemas.base import BaseSchemaItem, TypeDiagramElement
from c4.converters.json.schemas.diagrams import component as component_core
from c4.converters.json.schemas.diagrams import container as container_core
from c4.converters.json.schemas.diagrams import deployment as deployment_core
from c4.converters.json.schemas.diagrams import dynamic as dynamic_core
from c4.converters.json.schemas.diagrams import system_context as context_core
from c4.converters.json.schemas.diagrams.common import (
    BoundaryBase,
    RelationshipSchema,
)
from c4.diagrams.core import Relationship, RelationshipType
from c4.enums import RendererEnum

warnings.filterwarnings(
    "ignore",
    message=r'Field name ".*" in ".*" shadows an attribute in parent ".*"',
    category=UserWarning,
    module=__name__,
)


class PlantUMLBackendMixin:
    """Mixin for PlantUML JSON schemas."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    backend: Literal[RendererEnum.PLANTUML.value] = Field(  # type: ignore[name-defined]
        ..., description="JSON schema backend."
    )
    layouts: list[LayoutSchema] = Field(
        default_factory=list,
        description="PlantUML relative layout constraints between elements.",
    )
    render_options: PlantUMLRenderOptionsSchema | None = Field(
        None,
        description="PlantUML-specific render options.",
    )


class PlantUMLExtensionsMixin:
    """Mixin that maps PlantUML convenience fields into constructor kwargs."""

    def _with_plantuml_extensions(
        self,
        data: dict[str, Any],
        keys: frozenset[str],
    ) -> dict[str, Any]:
        """
        Move PlantUML JSON convenience fields into the runtime DSL
        `plantuml` constructor kwarg.
        """
        plantuml: dict[str, Any] = {}
        for key in sorted(keys):
            value = data.pop(key, None)
            if value is None:
                continue

            if key == "type_":
                plantuml["type"] = value
            else:
                plantuml[key] = value

        if plantuml:
            existing_kwarg_plantuml = data.pop("plantuml", None) or {}
            extensions = data.get("extensions") or {}
            existing_plantuml = extensions.get("plantuml") or {}
            data["plantuml"] = {
                **existing_plantuml,
                **existing_kwarg_plantuml,
                **plantuml,
            }

            if "plantuml" in extensions:
                extensions = {
                    key: value
                    for key, value in extensions.items()
                    if key != "plantuml"
                }

            if extensions:
                data["extensions"] = extensions
            else:
                data.pop("extensions", None)

        return data


class PlantUMLElementFields(PlantUMLExtensionsMixin):
    """Mixin for PlantUML element convenience fields."""

    technology: str | None = Field(
        None,
        description="Optional technology label where supported by the element.",
    )
    sprite: str | None = Field(
        None, description="Optional PlantUML sprite/icon reference."
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Optional PlantUML tags for styling or grouping.",
    )
    link: str | None = Field(
        None, description="Optional PlantUML URL associated with the element."
    )
    type_: str | None = Field(
        None,
        description="Optional PlantUML custom type/stereotype label.",
        alias="stereotype",
    )
    base_shape: str | None = Field(
        None,
        description="Optional PlantUML base shape override.",
    )

    def _to_diagram_element_kwargs(self) -> dict[str, Any]:
        """Move PlantUML element fields into backend extension kwargs."""
        data = cast(
            dict[str, Any],
            super()._to_diagram_element_kwargs(),  # type: ignore[misc]
        )

        return cast(
            dict[str, Any],
            self._with_plantuml_extensions(
                data,
                frozenset(("sprite", "tags", "link", "type_", "base_shape")),
            ),
        )


class PlantUMLBoundaryFields(PlantUMLExtensionsMixin):
    """Mixin for PlantUML boundary convenience fields."""

    tags: list[str] = Field(
        default_factory=list,
        description="Optional PlantUML tags for styling or grouping.",
    )
    link: str | None = Field(
        None, description="Optional PlantUML URL associated with the boundary."
    )
    type_: str | None = Field(
        None,
        description="Optional PlantUML custom type/stereotype label.",
        alias="stereotype",
    )

    def _to_diagram_element_kwargs(self) -> dict[str, Any]:
        """Move PlantUML boundary fields into backend extension kwargs."""
        data = cast(
            dict[str, Any],
            super()._to_diagram_element_kwargs(),  # type: ignore[misc]
        )

        return cast(
            dict[str, Any],
            self._with_plantuml_extensions(
                data,
                frozenset(("tags", "link", "type_")),
            ),
        )


class PlantUMLNodeFields(PlantUMLBoundaryFields):
    """Mixin for PlantUML deployment node convenience fields."""

    sprite: str | None = Field(
        None, description="Optional PlantUML sprite/icon reference."
    )

    def _to_diagram_element_kwargs(self) -> dict[str, Any]:
        """Move PlantUML node fields into backend extension kwargs."""
        data = cast(dict[str, Any], super()._to_diagram_element_kwargs())

        return cast(
            dict[str, Any],
            self._with_plantuml_extensions(
                data,
                frozenset(("sprite", "tags", "link", "type_")),
            ),
        )


class PlantUMLRelationshipSchema(
    PlantUMLExtensionsMixin,
    RelationshipSchema,
):
    """JSON schema for relationships supported by PlantUML C4 diagrams."""

    type: RelationshipType = Field(..., description="Type of the relationship.")
    sprite: str | None = Field(
        None,
        description="Optional PlantUML sprite/icon for the relationship.",
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Optional PlantUML relationship tags.",
    )
    link: str | None = Field(
        None,
        description="Optional PlantUML URL associated with the relationship.",
    )
    index: str | None = Field(
        None,
        description="Optional PlantUML dynamic relationship index.",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "REL_R",
                    "from": "web_app",
                    "to": "orders_api",
                    "label": "Calls",
                    "technology": "HTTPS",
                    "sprite": "cloud",
                    "tags": ["sync"],
                    "link": "https://example.com/contracts/orders",
                    "index": "2",
                }
            ]
        }
    )

    def _to_diagram_element_kwargs(self) -> dict[str, Any]:
        """Move PlantUML relationship fields into backend extension kwargs."""
        data = super()._to_diagram_element_kwargs()

        return self._with_plantuml_extensions(
            data,
            frozenset(("sprite", "tags", "link", "index")),
        )

    def _get_diagram_element_class(self) -> TypeDiagramElement | None:
        """Return the relationship class for the PlantUML relationship type."""
        return Relationship.get_relationship_by_type(self.type)


class LayoutSchema(BaseSchemaItem[Layout]):
    """JSON schema for a PlantUML relative layout constraint."""

    type: LayoutType = Field(..., description="Type of the layout.")
    from_: str = Field(
        ...,
        min_length=1,
        description="The source element alias (or unique label).",
        alias="from",
    )
    to: str = Field(
        ...,
        min_length=1,
        description="The destination element alias (or unique label).",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "LAY_R",
                    "from": "web_app",
                    "to": "orders_api",
                }
            ]
        }
    )

    def _get_diagram_element_class(self) -> TypeDiagramElement | None:
        """Return the layout class for this layout type."""
        return Layout.get_layout_by_type(self.type)


class IncrementSchema(BaseSchemaItem[increment]):
    """JSON schema for a PlantUML dynamic diagram increment step."""

    type: Literal["increment"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    offset: int | None = Field(
        default=1, description="The amount to increment the index by."
    )


class SetIndexSchema(BaseSchemaItem[set_index]):
    """JSON schema for a PlantUML dynamic diagram set-index step."""

    type: Literal["set_index"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    new_index: int = Field(
        ..., description="The value to assign to the internal index."
    )


class PlantUMLPersonSchema(
    PlantUMLElementFields,
    context_core.PersonSchema,
):
    """PlantUML JSON schema for a person."""


class PlantUMLPersonExtSchema(
    PlantUMLElementFields,
    context_core.PersonExtSchema,
):
    """PlantUML JSON schema for an external person."""


class PlantUMLSystemSchema(
    PlantUMLElementFields,
    context_core.SystemSchema,
):
    """PlantUML JSON schema for a software system."""


class PlantUMLSystemExtSchema(
    PlantUMLElementFields,
    context_core.SystemExtSchema,
):
    """PlantUML JSON schema for an external software system."""


class PlantUMLSystemDbSchema(
    PlantUMLElementFields,
    context_core.SystemDbSchema,
):
    """PlantUML JSON schema for a database-like system."""


class PlantUMLSystemDbExtSchema(
    PlantUMLElementFields,
    context_core.SystemDbExtSchema,
):
    """PlantUML JSON schema for an external database-like system."""


class PlantUMLSystemQueueSchema(
    PlantUMLElementFields,
    context_core.SystemQueueSchema,
):
    """PlantUML JSON schema for a queue-like system."""


class PlantUMLSystemQueueExtSchema(
    PlantUMLElementFields,
    context_core.SystemQueueExtSchema,
):
    """PlantUML JSON schema for an external queue-like system."""


PlantUMLSystemContextElement = (
    PlantUMLPersonSchema
    | PlantUMLPersonExtSchema
    | PlantUMLSystemSchema
    | PlantUMLSystemExtSchema
    | PlantUMLSystemDbSchema
    | PlantUMLSystemDbExtSchema
    | PlantUMLSystemQueueSchema
    | PlantUMLSystemQueueExtSchema
)


class PlantUMLBoundarySchema(
    PlantUMLBoundaryFields,
    context_core.BoundarySchema,
):
    """PlantUML JSON schema for a generic boundary."""

    elements: list[PlantUMLSystemContextElement] = Field(
        default_factory=list,
        description="Elements nested inside this boundary.",
    )
    boundaries: list[PlantUMLSystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries nested inside this boundary.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside this boundary.",
    )
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "type": "Boundary",
                    "label": "Commerce Platform",
                    "alias": "commerce_platform",
                    "stereotype": "enterprise",
                    "tags": ["Domain"],
                    "link": "https://example.com/domains/commerce",
                    "description": "Boundary for the commerce system.",
                    "relationships": [
                        {
                            "type": "REL_R",
                            "from": "web_storefront",
                            "to": "orders_api",
                            "label": "Calls",
                            "technology": "HTTPS",
                            "tags": ["sync"],
                        }
                    ],
                    "elements": [
                        {
                            "type": "System",
                            "label": "Web Storefront",
                            "alias": "web_storefront",
                            "sprite": "browser",
                        },
                        {
                            "type": "System",
                            "label": "Orders API",
                            "alias": "orders_api",
                            "sprite": "server",
                        },
                    ],
                    "boundaries": [],
                }
            ]
        }
    )


class PlantUMLEnterpriseBoundarySchema(
    PlantUMLBoundaryFields,
    context_core.EnterpriseBoundarySchema,
):
    """PlantUML JSON schema for an enterprise boundary."""

    elements: list[PlantUMLSystemContextElement] = Field(
        default_factory=list,
        description="Elements nested inside this boundary.",
    )
    boundaries: list[PlantUMLSystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries nested inside this boundary.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside this boundary.",
    )


class PlantUMLSystemBoundarySchema(
    PlantUMLBoundaryFields,
    context_core.SystemBoundarySchema,
):
    """PlantUML JSON schema for a system boundary."""

    elements: list[PlantUMLSystemContextElement] = Field(
        default_factory=list,
        description="Elements nested inside this boundary.",
    )
    boundaries: list[PlantUMLSystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries nested inside this boundary.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside this boundary.",
    )


PlantUMLSystemContextBoundary = (
    PlantUMLBoundarySchema
    | PlantUMLEnterpriseBoundarySchema
    | PlantUMLSystemBoundarySchema
)


class PlantUMLSystemContextDiagramSchema(
    PlantUMLBackendMixin,
    context_core.SystemContextDiagramSchema,
):
    """PlantUML JSON schema for a system context diagram."""

    elements: list[PlantUMLSystemContextElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLSystemContextBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLSystemLandscapeDiagramSchema(
    PlantUMLBackendMixin,
    context_core.SystemLandscapeDiagramSchema,
):
    """PlantUML JSON schema for a system landscape diagram."""

    elements: list[PlantUMLSystemContextElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLSystemContextBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLContainerSchema(
    PlantUMLElementFields,
    container_core.ContainerSchema,
):
    """PlantUML JSON schema for a container."""


class PlantUMLContainerExtSchema(
    PlantUMLElementFields,
    container_core.ContainerExtSchema,
):
    """PlantUML JSON schema for an external container."""


class PlantUMLContainerDbSchema(
    PlantUMLElementFields,
    container_core.ContainerDbSchema,
):
    """PlantUML JSON schema for a database-like container."""


class PlantUMLContainerDbExtSchema(
    PlantUMLElementFields,
    container_core.ContainerDbExtSchema,
):
    """PlantUML JSON schema for an external database-like container."""


class PlantUMLContainerQueueSchema(
    PlantUMLElementFields,
    container_core.ContainerQueueSchema,
):
    """PlantUML JSON schema for a queue-like container."""


class PlantUMLContainerQueueExtSchema(
    PlantUMLElementFields,
    container_core.ContainerQueueExtSchema,
):
    """PlantUML JSON schema for an external queue-like container."""


PlantUMLContainerElement = (
    PlantUMLSystemContextElement
    | PlantUMLContainerSchema
    | PlantUMLContainerExtSchema
    | PlantUMLContainerDbSchema
    | PlantUMLContainerDbExtSchema
    | PlantUMLContainerQueueSchema
    | PlantUMLContainerQueueExtSchema
)


class PlantUMLContainerBoundarySchema(
    PlantUMLBoundaryFields,
    container_core.ContainerBoundarySchema,
):
    """PlantUML JSON schema for a container boundary."""

    elements: list[PlantUMLContainerElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLContainerBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class PlantUMLContainerEnterpriseBoundarySchema(
    PlantUMLBoundaryFields,
    container_core.EnterpriseBoundarySchema,
):
    """PlantUML JSON schema for an enterprise boundary in container diagrams."""

    elements: list[PlantUMLContainerElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLContainerBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class PlantUMLContainerSystemBoundarySchema(
    PlantUMLBoundaryFields,
    container_core.SystemBoundarySchema,
):
    """PlantUML JSON schema for a system boundary in a container diagram."""

    elements: list[PlantUMLContainerElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLContainerBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


PlantUMLContainerBoundary = (
    PlantUMLContainerBoundarySchema
    | PlantUMLContainerEnterpriseBoundarySchema
    | PlantUMLContainerSystemBoundarySchema
)


class PlantUMLContainerDiagramSchema(
    PlantUMLBackendMixin,
    container_core.ContainerDiagramSchema,
):
    """PlantUML JSON schema for a container diagram."""

    elements: list[PlantUMLContainerElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLContainerBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLComponentSchema(
    PlantUMLElementFields,
    component_core.ComponentSchema,
):
    """PlantUML JSON schema for a component."""


class PlantUMLComponentExtSchema(
    PlantUMLElementFields,
    component_core.ComponentExtSchema,
):
    """PlantUML JSON schema for an external component."""


class PlantUMLComponentDbSchema(
    PlantUMLElementFields,
    component_core.ComponentDbSchema,
):
    """PlantUML JSON schema for a database-like component."""


class PlantUMLComponentDbExtSchema(
    PlantUMLElementFields,
    component_core.ComponentDbExtSchema,
):
    """PlantUML JSON schema for an external database-like component."""


class PlantUMLComponentQueueSchema(
    PlantUMLElementFields,
    component_core.ComponentQueueSchema,
):
    """PlantUML JSON schema for a queue-like component."""


class PlantUMLComponentQueueExtSchema(
    PlantUMLElementFields,
    component_core.ComponentQueueExtSchema,
):
    """PlantUML JSON schema for an external queue-like component."""


PlantUMLComponentElement = (
    PlantUMLContainerElement
    | PlantUMLComponentSchema
    | PlantUMLComponentExtSchema
    | PlantUMLComponentDbSchema
    | PlantUMLComponentDbExtSchema
    | PlantUMLComponentQueueSchema
    | PlantUMLComponentQueueExtSchema
)


class PlantUMLComponentContainerBoundarySchema(
    PlantUMLBoundaryFields,
    component_core.ContainerBoundarySchema,
):
    """PlantUML JSON schema for a container boundary in a component diagram."""

    elements: list[PlantUMLComponentElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLComponentBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class PlantUMLComponentEnterpriseBoundarySchema(
    PlantUMLBoundaryFields,
    component_core.EnterpriseBoundarySchema,
):
    """PlantUML JSON schema for an enterprise boundary in component diagrams."""

    elements: list[PlantUMLComponentElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLComponentBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class PlantUMLComponentSystemBoundarySchema(
    PlantUMLBoundaryFields,
    component_core.SystemBoundarySchema,
):
    """PlantUML JSON schema for a system boundary in a component diagram."""

    elements: list[PlantUMLComponentElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLComponentBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class PlantUMLComponentBoundarySchema(
    PlantUMLBoundaryFields,
    component_core.BoundarySchema,
):
    """PlantUML JSON schema for a generic boundary in a component diagram."""

    elements: list[PlantUMLComponentElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLComponentBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


PlantUMLComponentBoundary = (
    PlantUMLComponentContainerBoundarySchema
    | PlantUMLComponentEnterpriseBoundarySchema
    | PlantUMLComponentSystemBoundarySchema
    | PlantUMLComponentBoundarySchema
)


class PlantUMLComponentDiagramSchema(
    PlantUMLBackendMixin,
    component_core.ComponentDiagramSchema,
):
    """PlantUML JSON schema for a component diagram."""

    elements: list[PlantUMLComponentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLComponentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLNodeSchema(
    PlantUMLNodeFields,
    deployment_core.NodeSchema,
):
    """PlantUML JSON schema for a deployment node."""

    elements: list[PlantUMLDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLNodeLeftSchema(
    PlantUMLNodeFields,
    BoundaryBase[NodeLeft],
    deployment_core.NodeBase,
):
    """PlantUML JSON schema for a left-aligned deployment node."""

    type: Literal["NodeLeft"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[PlantUMLDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLNodeRightSchema(
    PlantUMLNodeFields,
    BoundaryBase[NodeRight],
    deployment_core.NodeBase,
):
    """PlantUML JSON schema for a right-aligned deployment node."""

    type: Literal["NodeRight"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[PlantUMLDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLDeploymentNodeSchema(
    PlantUMLNodeFields,
    deployment_core.DeploymentNodeSchema,
):
    """PlantUML JSON schema for a deployment-specific node."""

    elements: list[PlantUMLDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLDeploymentNodeLeftSchema(
    PlantUMLNodeFields,
    BoundaryBase[DeploymentNodeLeft],
    deployment_core.NodeBase,
):
    """PlantUML JSON schema for a left-aligned deployment-specific node."""

    type: Literal["DeploymentNodeLeft"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[PlantUMLDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class PlantUMLDeploymentNodeRightSchema(
    PlantUMLNodeFields,
    BoundaryBase[DeploymentNodeRight],
    deployment_core.NodeBase,
):
    """PlantUML JSON schema for a right-aligned deployment-specific node."""

    type: Literal["DeploymentNodeRight"] = Field(
        ...,
        description="Discriminator identifying the element type.",
        frozen=True,
    )
    elements: list[PlantUMLDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


PlantUMLDeploymentElement = PlantUMLContainerElement
PlantUMLDeploymentBoundary = (
    PlantUMLNodeSchema
    | PlantUMLNodeLeftSchema
    | PlantUMLNodeRightSchema
    | PlantUMLDeploymentNodeSchema
    | PlantUMLDeploymentNodeLeftSchema
    | PlantUMLDeploymentNodeRightSchema
)


class PlantUMLDeploymentDiagramSchema(
    PlantUMLBackendMixin,
    deployment_core.DeploymentDiagramSchema,
):
    """PlantUML JSON schema for a deployment diagram."""

    elements: list[PlantUMLDeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLDeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[PlantUMLRelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


PlantUMLDynamicStep = (
    PlantUMLRelationshipSchema | IncrementSchema | SetIndexSchema
)


class PlantUMLDynamicStepsMixin:
    """Mixin for PlantUML dynamic diagram steps."""

    model_config = ConfigDict(extra="forbid", populate_by_name=False)

    relationships: list[PlantUMLDynamicStep] = Field(
        default_factory=list,
        alias="steps",
        description="Dynamic diagram steps.",
    )


class PlantUMLDynamicEnterpriseBoundarySchema(
    PlantUMLDynamicStepsMixin,
    PlantUMLBoundaryFields,
    dynamic_core.DynamicEnterpriseBoundarySchema,
):
    """PlantUML JSON schema for an enterprise boundary in a dynamic diagram."""

    elements: list[PlantUMLDynamicElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLDynamicBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )


class PlantUMLDynamicSystemBoundarySchema(
    PlantUMLDynamicStepsMixin,
    PlantUMLBoundaryFields,
    dynamic_core.DynamicSystemBoundarySchema,
):
    """PlantUML JSON schema for a system boundary in a dynamic diagram."""

    elements: list[PlantUMLDynamicElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLDynamicBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )


class PlantUMLDynamicBoundarySchema(
    PlantUMLDynamicStepsMixin,
    PlantUMLBoundaryFields,
    dynamic_core.DynamicBoundarySchema,
):
    """PlantUML JSON schema for a generic boundary in a dynamic diagram."""

    elements: list[PlantUMLDynamicElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLDynamicBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )


class PlantUMLDynamicContainerBoundarySchema(
    PlantUMLDynamicStepsMixin,
    PlantUMLBoundaryFields,
    dynamic_core.DynamicContainerBoundarySchema,
):
    """PlantUML JSON schema for a container boundary in a dynamic diagram."""

    elements: list[PlantUMLDynamicElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[PlantUMLDynamicBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )


PlantUMLDynamicElement = PlantUMLComponentElement
PlantUMLDynamicBoundary = (
    PlantUMLDynamicBoundarySchema
    | PlantUMLDynamicEnterpriseBoundarySchema
    | PlantUMLDynamicSystemBoundarySchema
    | PlantUMLDynamicContainerBoundarySchema
)


class PlantUMLDynamicDiagramSchema(
    PlantUMLDynamicStepsMixin,
    PlantUMLBackendMixin,
    dynamic_core.DynamicDiagramSchema,
):
    """PlantUML JSON schema for a dynamic diagram."""

    elements: list[PlantUMLDynamicElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[PlantUMLDynamicBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )

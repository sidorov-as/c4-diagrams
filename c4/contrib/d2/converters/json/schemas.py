from __future__ import annotations

# mypy: disable-error-code=assignment
import warnings
from enum import unique
from typing import Any, Literal, cast

from pydantic import ConfigDict, Field

from c4.compat import StrEnum
from c4.contrib.d2.converters.json.render_options import (
    D2RenderOptionsSchema,
    D2StyleSchema,
)
from c4.contrib.d2.extensions import D2Direction
from c4.converters.json.schemas.base import TypeDiagramElement
from c4.converters.json.schemas.diagrams import component as component_core
from c4.converters.json.schemas.diagrams import container as container_core
from c4.converters.json.schemas.diagrams import deployment as deployment_core
from c4.converters.json.schemas.diagrams import dynamic as dynamic_core
from c4.converters.json.schemas.diagrams import system_context as context_core
from c4.converters.json.schemas.diagrams.common import RelationshipSchema
from c4.diagrams.core import Relationship
from c4.diagrams.core import RelationshipType as CoreRelationshipType
from c4.diagrams.core.enums import EnumDescriptionsMixin
from c4.enums import RendererEnum

warnings.filterwarnings(
    "ignore",
    message=r'Field name ".*" in ".*" shadows an attribute in parent ".*"',
    category=UserWarning,
    module=__name__,
)


@unique
class D2RelationshipType(EnumDescriptionsMixin, StrEnum):
    """Relationship types supported by D2 C4 diagrams."""

    REL = "REL"
    BI_REL = "BI_REL"

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: Any,
        handler: Any,
    ) -> dict[str, Any]:
        """
        Use the portable relationship type title in generated JSON Schema.
        """
        json_schema = handler(core_schema)
        json_schema["title"] = "RelationshipType"
        return json_schema  # type: ignore[no-any-return]

    @classmethod
    def get_descriptions(cls) -> dict[D2RelationshipType, str]:
        relationship_descriptions = CoreRelationshipType.get_descriptions()
        return {
            member: relationship_descriptions[
                CoreRelationshipType(member.value)
            ]
            for member in cls
        }


class D2BackendMixin:
    """Mixin for D2 JSON schemas."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    backend: Literal[RendererEnum.D2.value] = Field(  # type: ignore[name-defined]
        ..., description="JSON schema backend."
    )
    render_options: D2RenderOptionsSchema | None = Field(
        None,
        description="D2-specific render options.",
    )


class D2ExtensionsMixin:
    """Mixin that maps D2 convenience fields into constructor kwargs."""

    def _with_d2_extensions(
        self,
        data: dict[str, Any],
        keys: frozenset[str],
    ) -> dict[str, Any]:
        """
        Move D2 JSON convenience fields into the runtime DSL
        `d2` kwarg.
        """
        d2: dict[str, Any] = {}
        for key in sorted(keys):
            value = data.pop(key, None)
            if value is not None:
                if key == "style":
                    value = self._to_d2_style(value)
                d2[key] = value

        if d2:
            existing_kwarg_d2 = data.pop("d2", None) or {}
            extensions = data.get("extensions") or {}
            existing_d2 = extensions.get("d2") or {}
            data["d2"] = {
                **existing_d2,
                **existing_kwarg_d2,
                **d2,
            }

            if "d2" in extensions:
                extensions = {
                    key: value
                    for key, value in extensions.items()
                    if key != "d2"
                }

            if extensions:
                data["extensions"] = extensions
            else:
                data.pop("extensions", None)

        return data

    @staticmethod
    def _to_d2_style(value: Any) -> dict[str, Any]:
        """Return style data using runtime extension key names."""
        if isinstance(value, D2StyleSchema):
            return value.to_model()

        if isinstance(value, dict):
            return {
                key: style_value
                for key, style_value in value.items()
                if style_value is not None
            }

        return cast(dict[str, Any], value)


class D2ElementFields(D2ExtensionsMixin):
    """Mixin for D2 node/container convenience fields."""

    shape: str | None = Field(None, description="Optional D2 shape.")
    style: D2StyleSchema | None = Field(
        None,
        description="Optional D2 style attributes.",
    )
    icon: str | None = Field(None, description="Optional D2 icon URL.")
    near: str | None = Field(None, description="Optional D2 near reference.")
    tooltip: str | None = Field(None, description="Optional D2 tooltip.")
    link: str | None = Field(None, description="Optional D2 link URL.")
    classes: list[str] | None = Field(
        None,
        description="Optional D2 classes.",
    )
    direction: D2Direction | None = Field(
        None,
        description="Optional D2 layout direction for a container.",
    )

    def _to_diagram_element_kwargs(self) -> dict[str, Any]:
        """Move D2 element fields into backend extension kwargs."""
        data = cast(
            dict[str, Any],
            super()._to_diagram_element_kwargs(),  # type: ignore[misc]
        )

        return cast(
            dict[str, Any],
            self._with_d2_extensions(
                data,
                frozenset((
                    "shape",
                    "style",
                    "icon",
                    "near",
                    "tooltip",
                    "link",
                    "classes",
                    "direction",
                )),
            ),
        )


class D2RelationshipSchema(D2ExtensionsMixin, RelationshipSchema):
    """JSON schema for relationships supported by D2 C4 diagrams."""

    type: D2RelationshipType = Field(
        ..., description="Type of the relationship."
    )
    style: D2StyleSchema | None = Field(
        None,
        description="Optional D2 style attributes.",
    )
    icon: str | None = Field(None, description="Optional D2 icon URL.")
    near: str | None = Field(None, description="Optional D2 near reference.")
    tooltip: str | None = Field(None, description="Optional D2 tooltip.")
    link: str | None = Field(None, description="Optional D2 link URL.")
    classes: list[str] | None = Field(
        None,
        description="Optional D2 classes.",
    )

    def _to_diagram_element_kwargs(self) -> dict[str, Any]:
        """Move D2 relationship fields into backend extension kwargs."""
        data = super()._to_diagram_element_kwargs()

        return self._with_d2_extensions(
            data,
            frozenset(("style", "icon", "near", "tooltip", "link", "classes")),
        )

    def _get_diagram_element_class(self) -> TypeDiagramElement | None:
        """Return the relationship class for the D2 relationship type."""
        return Relationship.get_relationship_by_type(
            CoreRelationshipType(self.type.value)
        )


class D2PersonSchema(D2ElementFields, context_core.PersonSchema):
    """D2 JSON schema for a person."""


class D2PersonExtSchema(D2ElementFields, context_core.PersonExtSchema):
    """D2 JSON schema for an external person."""


class D2SystemSchema(D2ElementFields, context_core.SystemSchema):
    """D2 JSON schema for a software system."""


class D2SystemExtSchema(D2ElementFields, context_core.SystemExtSchema):
    """D2 JSON schema for an external software system."""


class D2SystemDbSchema(D2ElementFields, context_core.SystemDbSchema):
    """D2 JSON schema for a database-like system."""


class D2SystemDbExtSchema(D2ElementFields, context_core.SystemDbExtSchema):
    """D2 JSON schema for an external database-like system."""


class D2SystemQueueSchema(D2ElementFields, context_core.SystemQueueSchema):
    """D2 JSON schema for a queue-like system."""


class D2SystemQueueExtSchema(
    D2ElementFields,
    context_core.SystemQueueExtSchema,
):
    """D2 JSON schema for an external queue-like system."""


D2SystemContextElement = (
    D2PersonSchema
    | D2PersonExtSchema
    | D2SystemSchema
    | D2SystemExtSchema
    | D2SystemDbSchema
    | D2SystemDbExtSchema
    | D2SystemQueueSchema
    | D2SystemQueueExtSchema
)


class D2BoundarySchema(D2ElementFields, context_core.BoundarySchema):
    """D2 JSON schema for a generic boundary."""

    elements: list[D2SystemContextElement] = Field(
        default_factory=list,
        description="Elements nested inside this boundary.",
    )
    boundaries: list[D2SystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries nested inside this boundary.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside this boundary.",
    )


class D2EnterpriseBoundarySchema(
    D2ElementFields,
    context_core.EnterpriseBoundarySchema,
):
    """D2 JSON schema for an enterprise boundary."""

    elements: list[D2SystemContextElement] = Field(
        default_factory=list,
        description="Elements nested inside this boundary.",
    )
    boundaries: list[D2SystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries nested inside this boundary.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside this boundary.",
    )


class D2SystemBoundarySchema(
    D2ElementFields,
    context_core.SystemBoundarySchema,
):
    """D2 JSON schema for a system boundary."""

    elements: list[D2SystemContextElement] = Field(
        default_factory=list,
        description="Elements nested inside this boundary.",
    )
    boundaries: list[D2SystemContextBoundary] = Field(
        default_factory=list,
        description="Boundaries nested inside this boundary.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside this boundary.",
    )


D2SystemContextBoundary = (
    D2BoundarySchema | D2EnterpriseBoundarySchema | D2SystemBoundarySchema
)


class D2SystemContextDiagramSchema(
    D2BackendMixin,
    context_core.SystemContextDiagramSchema,
):
    """D2 JSON schema for a system context diagram."""

    elements: list[D2SystemContextElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[D2SystemContextBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class D2SystemLandscapeDiagramSchema(
    D2BackendMixin,
    context_core.SystemLandscapeDiagramSchema,
):
    """D2 JSON schema for a system landscape diagram."""

    elements: list[D2SystemContextElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[D2SystemContextBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class D2ContainerSchema(D2ElementFields, container_core.ContainerSchema):
    """D2 JSON schema for a container."""


class D2ContainerExtSchema(D2ElementFields, container_core.ContainerExtSchema):
    """D2 JSON schema for an external container."""


class D2ContainerDbSchema(D2ElementFields, container_core.ContainerDbSchema):
    """D2 JSON schema for a database-like container."""


class D2ContainerDbExtSchema(
    D2ElementFields,
    container_core.ContainerDbExtSchema,
):
    """D2 JSON schema for an external database-like container."""


class D2ContainerQueueSchema(
    D2ElementFields,
    container_core.ContainerQueueSchema,
):
    """D2 JSON schema for a queue-like container."""


class D2ContainerQueueExtSchema(
    D2ElementFields,
    container_core.ContainerQueueExtSchema,
):
    """D2 JSON schema for an external queue-like container."""


D2ContainerElement = (
    D2SystemContextElement
    | D2ContainerSchema
    | D2ContainerExtSchema
    | D2ContainerDbSchema
    | D2ContainerDbExtSchema
    | D2ContainerQueueSchema
    | D2ContainerQueueExtSchema
)


class D2ContainerBoundarySchema(
    D2ElementFields,
    container_core.ContainerBoundarySchema,
):
    """D2 JSON schema for a container boundary."""

    elements: list[D2ContainerElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2ContainerBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2ContainerEnterpriseBoundarySchema(
    D2ElementFields,
    container_core.EnterpriseBoundarySchema,
):
    """D2 JSON schema for an enterprise boundary in container diagrams."""

    elements: list[D2ContainerElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2ContainerBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2ContainerSystemBoundarySchema(
    D2ElementFields,
    container_core.SystemBoundarySchema,
):
    """D2 JSON schema for a system boundary in a container diagram."""

    elements: list[D2ContainerElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2ContainerBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2ContainerGenericBoundarySchema(
    D2ElementFields,
    container_core.BoundarySchema,
):
    """D2 JSON schema for a generic boundary in container diagrams."""

    elements: list[D2ContainerElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2ContainerBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


D2ContainerBoundary = (
    D2ContainerBoundarySchema
    | D2ContainerEnterpriseBoundarySchema
    | D2ContainerSystemBoundarySchema
    | D2ContainerGenericBoundarySchema
)


class D2ContainerDiagramSchema(
    D2BackendMixin,
    container_core.ContainerDiagramSchema,
):
    """D2 JSON schema for a container diagram."""

    elements: list[D2ContainerElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[D2ContainerBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class D2ComponentSchema(D2ElementFields, component_core.ComponentSchema):
    """D2 JSON schema for a component."""


class D2ComponentExtSchema(D2ElementFields, component_core.ComponentExtSchema):
    """D2 JSON schema for an external component."""


class D2ComponentDbSchema(D2ElementFields, component_core.ComponentDbSchema):
    """D2 JSON schema for a database-like component."""


class D2ComponentDbExtSchema(
    D2ElementFields,
    component_core.ComponentDbExtSchema,
):
    """D2 JSON schema for an external database-like component."""


class D2ComponentQueueSchema(
    D2ElementFields,
    component_core.ComponentQueueSchema,
):
    """D2 JSON schema for a queue-like component."""


class D2ComponentQueueExtSchema(
    D2ElementFields,
    component_core.ComponentQueueExtSchema,
):
    """D2 JSON schema for an external queue-like component."""


D2ComponentElement = (
    D2ContainerElement
    | D2ComponentSchema
    | D2ComponentExtSchema
    | D2ComponentDbSchema
    | D2ComponentDbExtSchema
    | D2ComponentQueueSchema
    | D2ComponentQueueExtSchema
)


class D2ComponentContainerBoundarySchema(
    D2ElementFields,
    component_core.ContainerBoundarySchema,
):
    """D2 JSON schema for a container boundary in a component diagram."""

    elements: list[D2ComponentElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2ComponentBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2ComponentEnterpriseBoundarySchema(
    D2ElementFields,
    component_core.EnterpriseBoundarySchema,
):
    """D2 JSON schema for an enterprise boundary in component diagrams."""

    elements: list[D2ComponentElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2ComponentBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2ComponentSystemBoundarySchema(
    D2ElementFields,
    component_core.SystemBoundarySchema,
):
    """D2 JSON schema for a system boundary in a component diagram."""

    elements: list[D2ComponentElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2ComponentBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2ComponentBoundarySchema(
    D2ElementFields,
    component_core.BoundarySchema,
):
    """D2 JSON schema for a generic boundary in a component diagram."""

    elements: list[D2ComponentElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2ComponentBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


D2ComponentBoundary = (
    D2ComponentContainerBoundarySchema
    | D2ComponentEnterpriseBoundarySchema
    | D2ComponentSystemBoundarySchema
    | D2ComponentBoundarySchema
)


class D2ComponentDiagramSchema(
    D2BackendMixin,
    component_core.ComponentDiagramSchema,
):
    """D2 JSON schema for a component diagram."""

    elements: list[D2ComponentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[D2ComponentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


D2DeploymentElement = D2ContainerElement


class D2NodeSchema(D2ElementFields, deployment_core.NodeSchema):
    """D2 JSON schema for a deployment node."""

    elements: list[D2DeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[D2DeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


class D2DeploymentNodeSchema(
    D2ElementFields,
    deployment_core.DeploymentNodeSchema,
):
    """D2 JSON schema for a deployment-specific node."""

    elements: list[D2DeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[D2DeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


D2DeploymentBoundary = D2NodeSchema | D2DeploymentNodeSchema


class D2DeploymentDiagramSchema(
    D2BackendMixin,
    deployment_core.DeploymentDiagramSchema,
):
    """D2 JSON schema for a deployment diagram."""

    elements: list[D2DeploymentElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[D2DeploymentBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )


D2DynamicElement = D2ComponentElement


class D2DynamicEnterpriseBoundarySchema(
    D2ElementFields,
    dynamic_core.DynamicEnterpriseBoundarySchema,
):
    """D2 JSON schema for an enterprise boundary in dynamic diagrams."""

    elements: list[D2DynamicElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2DynamicBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2DynamicSystemBoundarySchema(
    D2ElementFields,
    dynamic_core.DynamicSystemBoundarySchema,
):
    """D2 JSON schema for a system boundary in dynamic diagrams."""

    elements: list[D2DynamicElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2DynamicBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2DynamicBoundarySchema(
    D2ElementFields,
    dynamic_core.DynamicBoundarySchema,
):
    """D2 JSON schema for a generic boundary in dynamic diagrams."""

    elements: list[D2DynamicElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2DynamicBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


class D2DynamicContainerBoundarySchema(
    D2ElementFields,
    dynamic_core.DynamicContainerBoundarySchema,
):
    """D2 JSON schema for a container boundary in dynamic diagrams."""

    elements: list[D2DynamicElement] = Field(
        default_factory=list,
        description="Elements may be nested arbitrarily.",
    )
    boundaries: list[D2DynamicBoundary] = Field(
        default_factory=list,
        description="Boundaries may be nested arbitrarily.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Relationships declared inside the boundary.",
    )


D2DynamicBoundary = (
    D2DynamicBoundarySchema
    | D2DynamicEnterpriseBoundarySchema
    | D2DynamicSystemBoundarySchema
    | D2DynamicContainerBoundarySchema
)


class D2DynamicDiagramSchema(D2BackendMixin, dynamic_core.DynamicDiagramSchema):
    """D2 JSON schema for a dynamic diagram."""

    elements: list[D2DynamicElement] = Field(
        default_factory=list,
        description="Top-level elements.",
    )
    boundaries: list[D2DynamicBoundary] = Field(
        default_factory=list,
        description="Top-level boundaries.",
    )
    relationships: list[D2RelationshipSchema] = Field(
        default_factory=list,
        description="Top-level relationships.",
    )

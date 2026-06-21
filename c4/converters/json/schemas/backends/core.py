from __future__ import annotations

from pydantic import ConfigDict

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
from c4.converters.json.schemas.diagrams.system_context import (
    SystemContextDiagramSchema,
    SystemLandscapeDiagramSchema,
)


class CoreBackendMixin:
    """Mixin for backend-neutral JSON schemas."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CoreSystemContextDiagramSchema(
    CoreBackendMixin,
    SystemContextDiagramSchema,
):
    """Backend-neutral schema for a system context diagram."""


class CoreSystemLandscapeDiagramSchema(
    CoreBackendMixin,
    SystemLandscapeDiagramSchema,
):
    """Backend-neutral schema for a system landscape diagram."""


class CoreContainerDiagramSchema(
    CoreBackendMixin,
    ContainerDiagramSchema,
):
    """Backend-neutral schema for a container diagram."""


class CoreComponentDiagramSchema(
    CoreBackendMixin,
    ComponentDiagramSchema,
):
    """Backend-neutral schema for a component diagram."""


class CoreDeploymentDiagramSchema(
    CoreBackendMixin,
    DeploymentDiagramSchema,
):
    """Backend-neutral schema for a deployment diagram."""


class CoreDynamicDiagramSchema(
    CoreBackendMixin,
    DynamicDiagramSchema,
):
    """Backend-neutral schema for a dynamic diagram."""

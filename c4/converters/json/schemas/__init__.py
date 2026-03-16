from c4.converters.json.schemas.diagrams.component import (
    ComponentDiagramSchema,
)
from c4.converters.json.schemas.diagrams.container import (
    ContainerDiagramSchema,
)
from c4.converters.json.schemas.diagrams.deployment import (
    DeploymentDiagramSchema,
)
from c4.converters.json.schemas.diagrams.dynamic import (
    DynamicDiagramSchema,
)
from c4.converters.json.schemas.diagrams.system_context import (
    SystemContextDiagramSchema,
    SystemLandscapeDiagramSchema,
)

DIAGRAMS_SCHEMAS = [
    SystemContextDiagramSchema,
    SystemLandscapeDiagramSchema,
    ContainerDiagramSchema,
    ComponentDiagramSchema,
    DeploymentDiagramSchema,
    DynamicDiagramSchema,
]

import pytest

from c4 import (
    ComponentDiagram,
    ContainerDiagram,
    DeploymentDiagram,
    DynamicDiagram,
    SystemContextDiagram,
    SystemLandscapeDiagram,
)
from c4.diagrams.core import Diagram, DiagramType, Element, set_diagram


@pytest.fixture()
def diagram():
    with Diagram() as _diagram:
        yield _diagram


@pytest.fixture()
def component_diagram():
    with ComponentDiagram() as _diagram:
        yield _diagram


@pytest.fixture()
def container_diagram():
    with ContainerDiagram() as _diagram:
        yield _diagram


@pytest.fixture()
def dynamic_diagram():
    with DynamicDiagram() as _diagram:
        yield _diagram


@pytest.fixture()
def deployment_diagram():
    with DeploymentDiagram() as _diagram:
        yield _diagram


@pytest.fixture()
def set_current_diagram():
    diagram_types_map = {
        DiagramType.DIAGRAM: Diagram,
        DiagramType.SYSTEM_CONTEXT_DIAGRAM: SystemContextDiagram,
        DiagramType.SYSTEM_LANDSCAPE_DIAGRAM: SystemLandscapeDiagram,
        DiagramType.CONTAINER_DIAGRAM: ContainerDiagram,
        DiagramType.COMPONENT_DIAGRAM: ComponentDiagram,
        DiagramType.DYNAMIC_DIAGRAM: DynamicDiagram,
        DiagramType.DEPLOYMENT_DIAGRAM: DeploymentDiagram,
    }

    current_diagram = []

    def with_params(element_cls: type[Element]) -> None:
        allowed_diagram_types = element_cls.allowed_diagram_types
        if not allowed_diagram_types:
            diagram_cls = Diagram
        else:
            diagram_cls = diagram_types_map[allowed_diagram_types[0]]

        diagram = diagram_cls()
        set_diagram(diagram)

        current_diagram.append(diagram)

    yield with_params

    if current_diagram:
        set_diagram(None)

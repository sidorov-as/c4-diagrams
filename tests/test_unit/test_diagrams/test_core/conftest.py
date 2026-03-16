import pytest

from c4 import ComponentDiagram
from c4.diagrams.core import Diagram


@pytest.fixture()
def diagram():
    with Diagram() as _diagram:
        yield _diagram


@pytest.fixture()
def component_diagram():
    with ComponentDiagram() as _diagram:
        yield _diagram

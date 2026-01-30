import pytest

from c4.diagrams.core import Diagram


@pytest.fixture()
def diagram():
    with Diagram() as _diagram:
        yield _diagram

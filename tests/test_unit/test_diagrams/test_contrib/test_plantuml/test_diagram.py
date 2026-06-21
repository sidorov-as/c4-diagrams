from c4.contrib.plantuml import LayDown
from c4.diagrams.core import Diagram, Element


def test_diagram_ordered_elements_include_layout():
    with Diagram() as diagram:
        user = Element(label="person")
        frontend = Element(label="frontend")

        layout = LayDown(from_element=user, to_element=frontend)

    assert diagram.ordered_elements == [user, frontend, layout]

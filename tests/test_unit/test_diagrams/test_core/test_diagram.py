import re
from pathlib import Path

import pytest
from pytest_mock import MockFixture, MockType

from c4.diagrams.core import (
    BaseDiagramElement,
    Boundary,
    Diagram,
    Element,
    LayDown,
    get_diagram,
)
from c4.renderers.plantuml import DiagramFormat
from c4.renderers.plantuml.backends import BasePlantUMLBackend


class MockBasePlantUMLBackend(BasePlantUMLBackend):
    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.SVG,  # noqa: A002
    ) -> bytes:
        return ""


@pytest.fixture()
def mocked_renderer(mocker: MockFixture):
    from c4.renderers import PlantUMLRenderer

    return mocker.create_autospec(spec=PlantUMLRenderer)


def test_create_diagram():
    diagram = Diagram()

    assert diagram.title is None
    assert get_diagram() is None


def test_enter_diagram_context():
    diagram = Diagram()
    diagram_before = get_diagram()

    with diagram:
        diagram_context = get_diagram()

    diagram_after = get_diagram()
    assert diagram_before is None
    assert diagram_context == diagram
    assert diagram_after is None


def test_diagram_args():
    with Diagram(title="Sample diagram") as diagram:
        user = Element(label="person")
        bank = Boundary(label="web-site")
        base_element = BaseDiagramElement()

        with bank:
            frontend = Element(label="frontend")
            backend = Element(label="backend")

            frontend >> "Calls" >> backend

        rel_user = user >> "Interacts with" >> frontend

        layout = LayDown(from_element=user, to_element=frontend)

    assert diagram.title == "Sample diagram"
    assert diagram.elements == [user]
    assert diagram.base_elements == [base_element]
    assert diagram.boundaries == [bank]
    assert diagram.layouts == [layout]
    assert diagram.relationships == [rel_user]


def test_diagram_check_alias_duplicated():
    with Diagram() as diagram:
        user = Element(alias="p1", label="person")
        expected_error = re.escape(
            "Duplicated alias 'p1': Element(alias='p1', label='person')"
        )

        with pytest.raises(ValueError, match=expected_error):
            Element(alias="p1", label="any other label")

    assert diagram.elements == [user]


def test_diagram_check_alias_invalid_identifier():
    with Diagram() as diagram:
        expected_error = re.escape(
            "Alias 'invalid identifier' of "
            "Element(alias='invalid identifier', label='...') "
            "must be a valid identifier"
        )

        with pytest.raises(ValueError, match=expected_error):
            Element(alias="invalid identifier", label="...")

    assert not diagram.elements


def test_diagram_as_plantuml(mocker: MockFixture):
    diagram = Diagram()
    mocked_renderer_class = mocker.patch("c4.renderers.PlantUMLRenderer")
    expected_renderer = mocked_renderer_class.return_value
    kwargs = {
        "backend": MockBasePlantUMLBackend(),
    }

    result = diagram.as_plantuml(**kwargs)

    mocked_renderer_class.assert_called_once_with(**kwargs)
    expected_renderer.render.assert_called_once_with(diagram)
    assert result == expected_renderer.render.return_value


def test_diagram_render_empty_renderer_error():
    diagram = Diagram()
    expected_error = "No renderer provided and no default_renderer set"

    with pytest.raises(ValueError, match=expected_error):
        diagram.render()


def test_diagram_render_default(mocked_renderer: MockType):
    diagram = Diagram(default_renderer=mocked_renderer)

    result = diagram.render()

    mocked_renderer.render.assert_called_once_with(diagram)
    assert result == mocked_renderer.render.return_value


def test_diagram_render_provided(mocked_renderer: MockType):
    diagram = Diagram()

    result = diagram.render(renderer=mocked_renderer)

    mocked_renderer.render.assert_called_once_with(diagram)
    assert result == mocked_renderer.render.return_value


def test_diagram_save(tmp_path: Path, mocker: MockFixture):
    diagram = Diagram()
    diagram_output = tmp_path / "diagram.puml"
    mocked_render = mocker.patch.object(
        diagram, "render", return_value="diagram content"
    )

    diagram.save(diagram_output)

    mocked_render.assert_called_once_with(None)
    assert diagram_output.read_text(encoding="utf-8") == "diagram content"


def test_diagram_save_with_provided_renderer(
    tmp_path: Path, mocker: MockFixture, mocked_renderer: MockType
):
    diagram = Diagram()
    diagram_output = tmp_path / "diagram.puml"
    mocked_render = mocker.patch.object(
        diagram, "render", return_value="diagram content"
    )

    diagram.save(diagram_output, renderer=mocked_render)

    mocked_render.assert_called_once_with(mocked_render)
    assert diagram_output.read_text(encoding="utf-8") == "diagram content"


def test_diagram_save_as_plantuml(tmp_path: Path, mocker: MockFixture):
    mocked_renderer_class = mocker.patch("c4.renderers.PlantUMLRenderer")
    expected_renderer = mocked_renderer_class.return_value
    diagram = Diagram()
    diagram_output = tmp_path / "diagram.puml"
    mocked_save = mocker.patch.object(diagram, "save")
    kwargs = {
        "backend": MockBasePlantUMLBackend(),
    }

    diagram.save_as_plantuml(diagram_output, **kwargs)

    mocked_save.assert_called_once_with(
        diagram_output, renderer=expected_renderer
    )
    mocked_renderer_class.assert_called_once_with(**kwargs)

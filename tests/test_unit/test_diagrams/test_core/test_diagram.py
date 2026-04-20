import re
from pathlib import Path

import pytest
from pytest_mock import MockerFixture, MockType

from c4.diagrams.core import (
    BaseDiagramElement,
    Boundary,
    Diagram,
    Element,
    LayDown,
    get_diagram,
)
from c4.enums import DiagramFormat
from c4.renderers import MermaidRenderOptions, RenderOptions
from c4.renderers.mermaid.backends import BaseMermaidBackend
from c4.renderers.plantuml.backends import BasePlantUMLBackend
from c4.renderers.plantuml.options import PlantUMLRenderOptions


class MockBasePlantUMLBackend(BasePlantUMLBackend):
    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.SVG,  # noqa: A002
    ) -> bytes:
        return ""


class MockBaseMermaidBackend(BaseMermaidBackend):
    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.SVG,  # noqa: A002
    ) -> bytes:
        return ""


@pytest.fixture()
def mocked_renderer(mocker: MockerFixture):
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


def test_diagram_ordered_elements():
    with Diagram(title="Sample diagram") as diagram:
        user = Element(label="person")
        bank = Boundary(label="web-site")
        base_element = BaseDiagramElement()

        with bank:
            frontend = Element(label="frontend")
            backend = Element(label="backend")

            rel_front_back = frontend >> "Calls" >> backend

        rel_user = user >> "Interacts with" >> frontend

        layout = LayDown(from_element=user, to_element=frontend)

    assert diagram.ordered_elements == [
        user,
        bank,
        base_element,
        rel_user,
        layout,
    ]
    assert bank.ordered_elements == [frontend, backend, rel_front_back]


def test_diagram_check_alias_duplicated():
    with Diagram() as diagram:
        user = Element(alias="p1", label="person")
        expected_error = re.escape(
            "Duplicated alias 'p1': Element(alias='p1', label='person')."
        )

        with pytest.raises(ValueError, match=expected_error):
            Element(alias="p1", label="any other label")

    assert diagram.elements == [user]


def test_diagram_check_alias_duplicated_generated():
    expected_error = re.escape(
        "Duplicated alias 'person_1': Element(alias='person_1', label='person')."
    )

    with Diagram() as diagram:
        user = Element(label="person")
        user2 = Element(label="person")  # alias - person_1

        with pytest.raises(ValueError, match=expected_error):
            Element(alias="person_1", label="any other label")

    assert diagram.elements == [user, user2]
    assert user.alias == "person"
    assert user2.alias == "person_1"


def test_diagram__unique_alias_generators_per_diagram():
    with Diagram() as diagram:
        user = Element(label="person")

    with Diagram() as diagram2:
        user1 = Element(label="person")

    assert diagram.elements == [user]
    assert user.alias == "person"
    assert diagram2.elements == [user1]
    assert user1.alias == "person"


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


def test_diagram_as_plantuml(mocker: MockerFixture):
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


def test_diagram_as_mermaid(mocker: MockerFixture):
    diagram = Diagram()
    mocked_renderer_class = mocker.patch("c4.renderers.MermaidRenderer")
    expected_renderer = mocked_renderer_class.return_value
    kwargs = {
        "backend": MockBaseMermaidBackend(),
    }

    result = diagram.as_mermaid(**kwargs)

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


def test_diagram_save(tmp_path: Path, mocker: MockerFixture):
    diagram = Diagram()
    diagram_output = tmp_path / "diagram.puml"
    mocked_render = mocker.patch.object(
        diagram, "render", return_value="diagram content"
    )

    diagram.save(diagram_output)

    mocked_render.assert_called_once_with(None)
    assert diagram_output.read_text(encoding="utf-8") == "diagram content"


def test_diagram_save_with_provided_renderer(
    tmp_path: Path, mocker: MockerFixture, mocked_renderer: MockType
):
    diagram = Diagram()
    diagram_output = tmp_path / "diagram.puml"
    mocked_render = mocker.patch.object(
        diagram, "render", return_value="diagram content"
    )

    diagram.save(diagram_output, renderer=mocked_render)

    mocked_render.assert_called_once_with(mocked_render)
    assert diagram_output.read_text(encoding="utf-8") == "diagram content"


def test_diagram_save_as_plantuml(tmp_path: Path, mocker: MockerFixture):
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


def test_diagram_save_as_plantuml_provided_render_options(
    tmp_path: Path,
    mocker: MockerFixture,
):
    mocked_renderer_class = mocker.patch("c4.renderers.PlantUMLRenderer")
    expected_renderer = mocked_renderer_class.return_value
    diagram = Diagram()
    diagram_output = tmp_path / "diagram.puml"
    mocked_save = mocker.patch.object(diagram, "save")
    render_options = PlantUMLRenderOptions()
    kwargs = {
        "backend": MockBasePlantUMLBackend(),
        "render_options": render_options,
    }

    diagram.save_as_plantuml(diagram_output, **kwargs)

    mocked_save.assert_called_once_with(
        diagram_output, renderer=expected_renderer
    )
    mocked_renderer_class.assert_called_once_with(**kwargs)


def test_diagram_save_as_plantuml_render_options_from_diagram(
    tmp_path: Path,
    mocker: MockerFixture,
):
    mocked_renderer_class = mocker.patch("c4.renderers.PlantUMLRenderer")
    expected_renderer = mocked_renderer_class.return_value
    plantuml_render_options = PlantUMLRenderOptions()
    render_options = RenderOptions(plantuml=plantuml_render_options)
    diagram = Diagram(render_options=render_options)
    diagram_output = tmp_path / "diagram.puml"
    mocked_save = mocker.patch.object(diagram, "save")

    kwargs = {
        "backend": MockBasePlantUMLBackend(),
    }

    diagram.save_as_plantuml(diagram_output, **kwargs)

    mocked_save.assert_called_once_with(
        diagram_output, renderer=expected_renderer
    )
    mocked_renderer_class.assert_called_once_with(
        **kwargs,
        render_options=plantuml_render_options,
    )


def test_diagram_save_as_plantuml_override_render_options(
    tmp_path: Path,
    mocker: MockerFixture,
):
    mocked_renderer_class = mocker.patch("c4.renderers.PlantUMLRenderer")
    expected_renderer = mocked_renderer_class.return_value
    render_options = RenderOptions(plantuml=PlantUMLRenderOptions())
    diagram = Diagram(render_options=render_options)
    diagram_output = tmp_path / "diagram.puml"
    mocked_save = mocker.patch.object(diagram, "save")
    kwargs = {
        "backend": MockBasePlantUMLBackend(),
        "render_options": PlantUMLRenderOptions(),
    }

    diagram.save_as_plantuml(diagram_output, **kwargs)

    mocked_save.assert_called_once_with(
        diagram_output, renderer=expected_renderer
    )
    mocked_renderer_class.assert_called_once_with(**kwargs)
    assert kwargs["render_options"] is not render_options.plantuml


def test_diagram_save_as_mermaid(tmp_path: Path, mocker: MockerFixture):
    mocked_renderer_class = mocker.patch("c4.renderers.MermaidRenderer")
    expected_renderer = mocked_renderer_class.return_value
    diagram = Diagram()
    diagram_output = tmp_path / "diagram.puml"
    mocked_save = mocker.patch.object(diagram, "save")
    kwargs = {
        "backend": MockBaseMermaidBackend(),
    }

    diagram.save_as_mermaid(diagram_output, **kwargs)

    mocked_save.assert_called_once_with(
        diagram_output, renderer=expected_renderer
    )
    mocked_renderer_class.assert_called_once_with(**kwargs)


def test_diagram_save_as_mermaid_provided_render_options(
    tmp_path: Path,
    mocker: MockerFixture,
):
    mocked_renderer_class = mocker.patch("c4.renderers.MermaidRenderer")
    expected_renderer = mocked_renderer_class.return_value
    diagram = Diagram()
    diagram_output = tmp_path / "diagram.puml"
    mocked_save = mocker.patch.object(diagram, "save")
    render_options = MermaidRenderOptions()
    kwargs = {
        "backend": MockBaseMermaidBackend(),
        "render_options": render_options,
    }

    diagram.save_as_mermaid(diagram_output, **kwargs)

    mocked_save.assert_called_once_with(
        diagram_output, renderer=expected_renderer
    )
    mocked_renderer_class.assert_called_once_with(**kwargs)


def test_diagram_save_as_mermaid_render_options_from_diagram(
    tmp_path: Path,
    mocker: MockerFixture,
):
    mocked_renderer_class = mocker.patch("c4.renderers.MermaidRenderer")
    expected_renderer = mocked_renderer_class.return_value
    mermaid_render_options = MermaidRenderOptions()
    render_options = RenderOptions(mermaid=mermaid_render_options)
    diagram = Diagram(render_options=render_options)
    diagram_output = tmp_path / "diagram.puml"
    mocked_save = mocker.patch.object(diagram, "save")

    kwargs = {
        "backend": MockBaseMermaidBackend(),
    }

    diagram.save_as_mermaid(diagram_output, **kwargs)

    mocked_save.assert_called_once_with(
        diagram_output, renderer=expected_renderer
    )
    mocked_renderer_class.assert_called_once_with(
        **kwargs,
        render_options=mermaid_render_options,
    )


def test_diagram_save_as_mermaid_override_render_options(
    tmp_path: Path,
    mocker: MockerFixture,
):
    mocked_renderer_class = mocker.patch("c4.renderers.MermaidRenderer")
    expected_renderer = mocked_renderer_class.return_value
    render_options = RenderOptions(mermaid=MermaidRenderOptions())
    diagram = Diagram(render_options=render_options)
    diagram_output = tmp_path / "diagram.puml"
    mocked_save = mocker.patch.object(diagram, "save")
    kwargs = {
        "backend": MockBaseMermaidBackend(),
        "render_options": MermaidRenderOptions(),
    }

    diagram.save_as_mermaid(diagram_output, **kwargs)

    mocked_save.assert_called_once_with(
        diagram_output, renderer=expected_renderer
    )
    mocked_renderer_class.assert_called_once_with(**kwargs)
    assert kwargs["render_options"] is not render_options.plantuml


def test_get_diagram():
    with Diagram() as diagram:
        result = get_diagram()

    assert result is diagram


def test_get_diagram__none():
    with Diagram():
        ...

    result = get_diagram()

    assert result is None


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("example", "Diagram(title='example')"),
        (None, "Diagram()"),
    ],
)
def test_diagram_repr(title: str | None, expected: str):
    diagram = Diagram(title=title)

    assert repr(diagram) == expected


def test_diagram_get_element_by_alias():
    with Diagram(title="Sample diagram") as diagram:
        user = Element(alias="user", label="person")

    assert diagram.get_element_by_alias("user") is user


def test_diagram_get_element_by_alias_none():
    with Diagram(title="Sample diagram") as diagram:
        _ = Element(label="person")

    assert diagram.get_element_by_alias("unknown") is None


def test_diagram_get_elements_by_label():
    with Diagram(title="Sample diagram") as diagram:
        user = Element(label="common-label")
        user2 = Element(label="common-label")
        bank = Boundary(label="common-label")

        with bank:
            _ = Element(label="frontend")
            _ = Element(label="backend")

    result = diagram.get_elements_by_label("common-label")

    assert result == [user, user2, bank]


def test_diagram_get_elements_by_label_empty():
    with Diagram(title="Sample diagram") as diagram:
        _ = Element(label="label")
        _ = Element(label="label")

    result = diagram.get_elements_by_label("unknown")

    assert result == []


def test_diagram_render_options():
    diagram = Diagram()
    render_options = RenderOptions()

    diagram.render_options = render_options

    assert diagram.render_options == render_options

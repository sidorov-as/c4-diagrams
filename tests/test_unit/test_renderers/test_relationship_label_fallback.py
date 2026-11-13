import shutil
import subprocess
from pathlib import Path

import pytest

from c4 import Container, ContainerDiagram
from c4.renderers import (
    MermaidRenderOptionsBuilder,
    PlantUMLRenderOptionsBuilder,
)
from c4.renderers.d2.renderer import D2Renderer
from c4.renderers.mermaid.renderer import MermaidRenderer
from c4.renderers.plantuml.renderer import PlantUMLRenderer


def build_diagram(label: str | None = None, technology: str | None = None):
    with ContainerDiagram() as diagram:
        a = Container("A", "Service A", alias="a")
        b = Container("B", "Service B", alias="b")
        relationship = a >> b
        relationship.label = label
        relationship.technology = technology

    return diagram


def build_renderers(**kwargs):
    plantuml_options = PlantUMLRenderOptionsBuilder()
    mermaid_options = MermaidRenderOptionsBuilder()
    if "label" in kwargs:
        plantuml_options.default_relationship_label(kwargs["label"])
        mermaid_options.default_relationship_label(kwargs["label"])

    return {
        "plantuml": PlantUMLRenderer(render_options=plantuml_options.build()),
        "mermaid": MermaidRenderer(render_options=mermaid_options.build()),
    }


@pytest.mark.parametrize("backend", ["plantuml", "mermaid"])
def test_default_label(backend: str):
    output = build_renderers()[backend].render(build_diagram())

    assert 'Rel(a, b, "uses")' in output


@pytest.mark.parametrize("backend", ["plantuml", "mermaid"])
def test_default_label_with_technology(backend: str):
    output = build_renderers()[backend].render(
        build_diagram(technology="HTTPS")
    )

    assert 'Rel(a, b, "uses", "HTTPS")' in output


@pytest.mark.parametrize("backend", ["plantuml", "mermaid"])
def test_custom_label(backend: str):
    output = build_renderers(label="relates to")[backend].render(
        build_diagram()
    )

    assert 'Rel(a, b, "relates to")' in output


@pytest.mark.parametrize("backend", ["plantuml", "mermaid"])
def test_fallback_disabled(backend: str):
    output = build_renderers(label=None)[backend].render(build_diagram())

    assert "uses" not in output
    assert "Rel(a, b)" in output


@pytest.mark.parametrize("backend", ["plantuml", "mermaid"])
def test_explicit_empty_label_is_kept(backend: str):
    output = build_renderers()[backend].render(build_diagram(label=""))

    assert 'Rel(a, b, "")' in output
    assert "uses" not in output


@pytest.mark.parametrize("backend", ["plantuml", "mermaid"])
def test_model_is_not_changed_by_rendering(backend: str):
    diagram = build_diagram()

    build_renderers()[backend].render(diagram)
    output = build_renderers(label="other")[backend].render(diagram)

    assert diagram.relationships[0].label is None
    assert 'Rel(a, b, "other")' in output


def test_d2_has_no_placeholder():
    output = D2Renderer().render(build_diagram())

    assert "uses" not in output


@pytest.mark.skipif(shutil.which("plantuml") is None, reason="no plantuml")
def test_plantuml_renders_unlabeled_relationship(tmp_path: Path):
    source = tmp_path / "diagram.puml"
    source.write_text(build_renderers()["plantuml"].render(build_diagram()))

    result = subprocess.run(  # noqa: S603
        [shutil.which("plantuml"), "-failfast2", "-tsvg", str(source)],
        capture_output=True,
        text=True,
        check=False,
    )

    if "SocketException" in result.stderr or "UnknownHost" in result.stderr:
        pytest.skip("C4-PlantUML include is not reachable")

    assert result.returncode == 0, result.stderr
    assert (tmp_path / "diagram.svg").exists()


@pytest.mark.skipif(shutil.which("mmdc") is None, reason="no mmdc")
def test_mermaid_renders_unlabeled_relationship(tmp_path: Path):
    source = tmp_path / "diagram.mmd"
    source.write_text(build_renderers()["mermaid"].render(build_diagram()))

    result = subprocess.run(  # noqa: S603
        [
            shutil.which("mmdc"),
            "-i",
            str(source),
            "-o",
            str(tmp_path / "o.svg"),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from c4.contrib.likec4 import (
    Between,
    Children,
    Descendants,
    Incoming,
    InOut,
    Link,
    Outgoing,
    Project,
    RawPredicate,
    Where,
    Wildcard,
)
from c4.contrib.likec4.converters.json import LikeC4ProjectSchema
from c4.contrib.likec4.converters.python import (
    ProjectPythonCodegen,
    project_to_python_code,
)
from c4.converters.python.converter import diagram_to_python_code
from c4.diagrams.core import Diagram
from c4.enums import RendererEnum

EXAMPLES = Path(__file__).parents[4] / "docs" / "assets" / "examples"


def _execute(source: str) -> Project:
    compile(source, "<generated LikeC4 code>", "exec")
    namespace: dict[str, Any] = {}
    exec(source, namespace)  # noqa: S102 - executing generated source is the test.
    return namespace["project"]


def _round_trip(project: Project) -> str:
    source = project_to_python_code(project)

    assert _execute(source).render() == project.render()
    assert ProjectPythonCodegen().generate(project) == source
    return source


@pytest.mark.parametrize("name", ["minimal", "advanced"])
def test_committed_python_examples_are_generated_code(name):
    schema = LikeC4ProjectSchema.model_validate_json(
        (EXAMPLES / f"json/likec4/project.{name}.json").read_text("utf-8")
    )
    project = schema.to_project()

    source = project_to_python_code(project)

    assert source == (EXAMPLES / f"likec4/project.{name}.py").read_text("utf-8")
    assert _execute(source).render() == project.render()


def test_empty_project():
    source = _round_trip(Project())

    assert (
        source
        == "from c4.contrib.likec4 import Project\n\n\nproject = Project()\n"
    )


def test_project_name_and_view_key():
    project = Project("Shop", view_key="index")
    project.views.element_view("index")

    source = _round_trip(project)

    assert "Project('Shop', view_key='index')" in source
    assert _execute(source).view_key == "index"


def test_every_construct_round_trips():
    project = Project("All")
    spec = project.specification
    spec.color("brand", "#0b5fff")
    spec.element(
        "actor",
        title="Actor",
        technology="t",
        description="d",
        notation="N",
        tags=["hot"],
        shape="person",
        iconColor="brand",
        opacity=50,
    )
    spec.element("system").element("service")
    spec.relationship("async", technology="MQ", description="d", line="dashed")
    spec.tag("hot", color="red")
    spec.deployment_node("vm", title="VM", color="gray")
    model = project.model
    user = model.element("actor", "User", alias="user", tags=["hot"])
    system = model.element(
        "system",
        "Sys tem",
        summary="s",
        description="line [[x]]",
        technology="py",
        icon="tech:go",
        metadata={"a": "b", "c": ["d", "e"]},
        links=[Link("https://x.io"), Link("https://y.io", "Y")],
        color="brand",
    )
    api = system.element("service", "API")
    only_alias = model.element("service", alias="worker")
    nested = api.element("service", "Inner")
    nested.set_style(icon="tech:rust")
    user.uses(api, "uses")
    api.uses(
        only_alias,
        kind="async",
        bidirectional=True,
        description="d",
        technology="MQ",
        tags=["hot"],
        metadata={"k": "v"},
        links=["https://z.io"],
        navigate_to="flow",
        color="red",
        head="open",
    )
    node = project.deployment.node("vm", "Host", alias="host", color="green")
    inner = project.deployment.node(
        "vm",
        "Inner",
        parent=node,
        tags=["hot"],
        metadata={"m": "n"},
        links=["https://q.io"],
    )
    anonymous = inner.instance(api)
    named = node.instance(
        only_alias,
        "w1",
        title="Worker",
        description="d",
        technology="t",
        tags=["hot"],
        metadata={"m": "n"},
        links=["https://i.io"],
        color="red",
    )
    other = project.deployment.node("vm", "Other")
    anonymous.uses(other, "calls", kind="async", head="open")
    named.uses(other, "x", tags=["hot"])
    views = project.views
    index = views.element_view(
        "index",
        "Index",
        of=system,
        description="d",
        tags=["hot"],
        links=["https://v.io"],
    )
    index.include(
        Wildcard(),
        Children(system),
        Descendants(system),
        Where(Children(system), tag="hot", kind="service"),
        Between(api, system, both=True),
        Incoming(api),
        Outgoing(api),
        InOut(api),
        RawPredicate("system.** where tag is #hot"),
        navigate_to="flow",
    ).exclude(only_alias).style(api, color="red", opacity=20).auto_layout(
        "BottomTop", 5, 6
    )
    views.element_view("bare")
    deployed = views.deployment_view("deployed", "Deployed")
    deployed.include(
        node, Children(node), anonymous, Where(Wildcard(), kind="vm")
    ).exclude(other).style(node, color="gray").auto_layout("LeftRight")
    flow = views.dynamic_view(
        "flow",
        "Flow",
        variant="sequence",
        description="d",
        tags=["hot"],
        links=["https://f.io"],
    )
    flow.step(
        user,
        api,
        "go",
        description="d",
        technology="t",
        notes="n",
        navigate_to="flow",
        color="red",
    )
    flow.back(user, api, "back")

    source = _round_trip(project)

    assert "tech:rust" in source
    assert "set_style(icon=" in source
    assert (
        "api_instance = inner_2.instance(api)" in source
    )  # referenced anonymous instance


def test_unreferenced_anonymous_instances_have_no_variable():
    project = Project()
    project.specification.element("service").deployment_node("vm")
    service = project.model.element("service", "S")
    vm = project.deployment.node("vm", "VM")
    vm.instance(service)

    source = _round_trip(project)

    assert "vm.instance(s)" in source
    assert "= vm.instance" not in source


def test_generated_variable_names_are_unique_and_valid():
    project = Project()
    project.specification.element("service")
    model = project.model
    model.element("service", "class")
    model.element("service", "class")
    model.element("service", "1st")
    model.element("service", "project")
    model.element("service", "Ünï cödé")
    project.views.element_view("model")

    source = _round_trip(project)

    assert "class_ = model.element" in source
    assert "class_2 = model.element" in source
    assert "project_2 = model.element" in source


def test_long_calls_are_wrapped():
    project = Project()
    project.specification.element("service")
    project.model.element(
        "service", "A title", description="and more", technology="py"
    )
    project.model.element("service", "A short one", alias="short_alias")

    source = _round_trip(project)

    assert (
        "a_title = model.element(\n    'service',\n    'A title',\n" in source
    )
    assert all(len(line) <= 79 for line in source.splitlines())


def test_long_import_lists_are_wrapped():
    project = Project()
    project.specification.element("service")
    s = project.model.element("service", "S")
    t = project.model.element("service", "T")
    project.views.element_view("v").include(
        Wildcard(),
        Children(s),
        Descendants(s),
        Where(s, tag="x"),
        Between(s, t),
        RawPredicate("x"),
    )
    project.specification.tag("x")

    source = project_to_python_code(project)

    assert source.startswith("from c4.contrib.likec4 import (\n    Between,")


def test_diagram_to_python_code_accepts_projects():
    project = Project("P")

    assert diagram_to_python_code(project, RendererEnum.LIKEC4) == (
        project_to_python_code(project)
    )
    assert diagram_to_python_code(project) == project_to_python_code(project)


def test_diagram_to_python_code_rejects_mismatched_backends():
    with pytest.raises(ValueError, match="requires the LikeC4 backend"):
        diagram_to_python_code(Project(), RendererEnum.D2)
    with pytest.raises(ValueError, match="requires a LikeC4 Project"):
        diagram_to_python_code(Diagram(), RendererEnum.LIKEC4)


def test_between_instances_keeps_their_variables():
    from c4.contrib.likec4.converters.python import _collect_instances

    project = Project()
    project.specification.element("service").deployment_node("vm")
    service = project.model.element("service", "S", alias="s")
    vm = project.deployment.node("vm", "VM", alias="vm")
    first = vm.instance(service, "one")
    second = vm.instance(service, "two")

    found: set[int] = set()
    _collect_instances(Between(first, second), found)

    assert found == {id(first), id(second)}


def test_unsupported_view_type_is_rejected():
    project = Project()
    project.views.all.append(SimpleNamespace(key="odd"))  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="Unsupported LikeC4 view"):
        project_to_python_code(project)


def test_unsupported_predicate_item_is_rejected():
    with pytest.raises(TypeError, match="predicate item"):
        ProjectPythonCodegen()._item(object())


def test_variable_names_fall_back_to_item():
    codegen = ProjectPythonCodegen()

    assert codegen._variable(object(), "²") == "item"


def test_deployment_without_instances_round_trips():
    project = Project()
    project.specification.deployment_node("vm")
    project.deployment.node("vm", "VM", alias="vm")

    source = _round_trip(project)

    assert "instance" not in source


def test_dynamic_view_with_diagram_variant_round_trips():
    project = Project()
    project.specification.element("service")
    a = project.model.element("service", "A", alias="a")
    b = project.model.element("service", "B", alias="b")
    project.views.dynamic_view("flow", variant="diagram").step(a, b, "calls")

    source = _round_trip(project)

    assert "variant" not in source

import pytest

from c4.contrib.likec4 import Link, Project
from c4.contrib.likec4.workspace import Element


@pytest.fixture
def project() -> Project:
    project = Project("Shop")
    (
        project.specification
        .element("system", shape="component")
        .element("service")
        .relationship("async", line="dotted", head="diamond")
        .tag("critical")
        .tag("deprecated", color="red")
        .color("brand", "#112233")
    )
    return project


def test_sections_are_persistent():
    project = Project()

    assert project.model is project.model
    assert project.specification is project.specification


def test_project_is_a_context_manager():
    with Project("Shop") as project:
        assert project.name == "Shop"


def test_declared_kinds_keep_defaults_and_order(project):
    spec = project.specification
    spec.deployment_node("vm", notation="VM", color="gray")

    assert list(spec.element_kinds) == ["system", "service"]
    assert spec.element_kinds["system"].style == {"shape": "component"}
    assert spec.relationship_kinds["async"].style == {
        "line": "dotted",
        "head": "diamond",
    }
    assert spec.deployment_kinds["vm"].notation == "VM"
    assert spec.tags["deprecated"].color == "red"
    assert spec.colors["brand"].value == "#112233"


def test_kind_defaults_are_stored():
    spec = Project().specification
    spec.element(
        "service",
        title="Service",
        technology="Go",
        description="d",
        notation="Svc",
        tags=["critical"],
    )

    kind = spec.element_kinds["service"]
    assert (kind.title, kind.technology, kind.description) == (
        "Service",
        "Go",
        "d",
    )
    assert kind.notation == "Svc"
    assert kind.tags == ("critical",)


@pytest.mark.parametrize(
    "declare",
    [
        lambda s: s.element("a").element("a"),
        lambda s: s.deployment_node("a").deployment_node("a"),
        lambda s: s.relationship("a").relationship("a"),
        lambda s: s.tag("a").tag("a"),
        lambda s: s.color("a", "#fff").color("a", "#000"),
    ],
)
def test_duplicate_declaration_is_rejected(declare):
    with pytest.raises(ValueError, match="already declared"):
        declare(Project().specification)


def test_same_name_may_exist_in_different_categories():
    spec = Project().specification
    spec.element("service").relationship("service").tag("service")

    assert "service" in spec.element_kinds
    assert "service" in spec.relationship_kinds


def test_tags_are_declared_without_hash():
    with pytest.raises(ValueError, match="without '#'"):
        Project().specification.tag("#critical")


@pytest.mark.parametrize("name", ["", "1a", "a b", "a.b", "a-", "a#"])
def test_invalid_kind_names_are_rejected(name):
    with pytest.raises(ValueError, match="Element kind"):
        Project().specification.element(name)


@pytest.mark.parametrize("value", ["red", "#12", "rgb(1,2)", ""])
def test_invalid_color_value_is_rejected(value):
    with pytest.raises(ValueError, match="Color value"):
        Project().specification.color("x", value)


@pytest.mark.parametrize("value", ["#abc", "#aabbcc", "rgba(1, 2, 3, 0.5)"])
def test_valid_color_values(value):
    assert Project().specification.color("x", value).colors["x"].value == value


@pytest.mark.parametrize(
    "style",
    [{"shape": "triangle"}, {"opacity": 101}, {"color": "#fff"}, {"bad": 1}],
)
def test_invalid_style_is_rejected(style):
    with pytest.raises(ValueError):
        Project().specification.element("x", **style)


def test_style_accepts_snake_case_and_percent_opacity():
    spec = Project().specification.element(
        "x", opacity="80%", text_size="lg", icon_position="left", multiple=True
    )

    assert spec.element_kinds["x"].style == {
        "iconPosition": "left",
        "opacity": 80,
        "textSize": "lg",
        "multiple": True,
    }


def test_nesting_by_parent_child_method_and_with_block(project):
    model = project.model
    cloud = model.element("system", "Cloud")
    backend = model.element("service", "Backend", parent=cloud)
    api = backend.element("service", "API")
    with cloud:
        queue = model.element("service", "Queue")
        with queue:
            worker = model.element("service", "Worker")
    top = model.element("system", "Top")

    assert api.parent is backend
    assert backend.parent is cloud
    assert cloud.children == [backend, queue]
    assert worker.parent is queue
    assert [e.name for e in model.roots] == ["Cloud", "Top"]
    assert [e.name for e in model.elements] == [
        "Cloud",
        "Backend",
        "API",
        "Queue",
        "Worker",
        "Top",
    ]
    assert top.parent is None
    assert api.ancestors() == [backend, cloud]
    assert cloud.descendants() == [backend, api, queue, worker]


def test_with_block_outside_restores_root_level(project):
    model = project.model
    with model.element("system", "A"):
        pass

    assert model.element("system", "B").parent is None


def test_element_carries_all_properties(project):
    element = project.model.element(
        "service",
        "API",
        alias="api",
        summary="short",
        description="long",
        technology="Go",
        tags=["critical", "critical"],
        icon="tech:go",
        metadata={"owner": "team", "tiers": ["a", "b"]},
        links=["https://x.io", ("https://y.io", "Y"), Link("z", "Z")],
        color="primary",
    )

    assert element.alias == "api"
    assert element.summary == "short"
    assert element.description == "long"
    assert element.technology == "Go"
    assert element.tags == ("critical",)
    assert element.icon == "tech:go"
    assert element.metadata == {"owner": "team", "tiers": ("a", "b")}
    assert element.links == (
        Link("https://x.io"),
        Link("https://y.io", "Y"),
        Link("z", "Z"),
    )
    assert element.style == {"color": "primary"}
    assert repr(element) == "Element('service', 'API')"


def test_set_style_merges(project):
    element = project.model.element("service", "API", color="red")

    element.set_style(shape="queue")

    assert element.style == {"color": "red", "shape": "queue"}


def test_summary_limit():
    model = Project().model

    assert model.element("a", "ok", summary="x" * 150).summary == "x" * 150
    with pytest.raises(ValueError, match="150"):
        model.element("a", "long", summary="x" * 151)


def test_element_has_no_navigate_to():
    with pytest.raises(ValueError, match="Unknown element style property"):
        Project().model.element("a", "x", navigate_to="view")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"metadata": {"1bad": "v"}},
        {"metadata": {"k": 1}},
        {"metadata": {"k": [1]}},
        {"metadata": ["k"]},
        {"tags": "critical"},
        {"tags": ["#critical"]},
        {"links": "https://x.io"},
        {"links": [1]},
    ],
)
def test_invalid_properties_are_rejected(kwargs):
    with pytest.raises((TypeError, ValueError)):
        Project().model.element("a", "x", **kwargs)


def test_element_needs_title_or_alias():
    model = Project().model

    with pytest.raises(ValueError, match="title or an alias"):
        model.element("a")
    assert model.element("a", alias="only").name == "only"


def test_parent_from_another_model_is_rejected():
    other = Project().model.element("a", "Other")

    with pytest.raises(ValueError, match="another model"):
        Project().model.element("a", "x", parent=other)


def test_invalid_alias_is_rejected():
    with pytest.raises(ValueError, match="Element alias"):
        Project().model.element("a", "x", alias="a.b")


def test_ownership_mismatch_raises():
    model = Project().model
    first = model.element("a", "first")
    second = model.element("a", "second")
    first.__enter__()

    with pytest.raises(RuntimeError, match="ownership"):
        second.__exit__(None, None, None)


def test_typed_bidirectional_relationship(project):
    model = project.model
    a = model.element("service", "A")
    b = model.element("service", "B")

    rel = model.relate(
        a,
        b,
        "events",
        kind="async",
        bidirectional=True,
        technology="Kafka",
        description="d",
        tags=["critical"],
        metadata={"k": "v"},
        links=["https://x.io"],
        navigate_to="flow",
        color="red",
        line="dashed",
    )

    assert model.relationships == [rel]
    assert (rel.source, rel.target) == (a, b)
    assert rel.kind == "async"
    assert rel.bidirectional is True
    assert rel.technology == "Kafka"
    assert rel.tags == ("critical",)
    assert rel.metadata == {"k": "v"}
    assert rel.links == (Link("https://x.io"),)
    assert rel.navigate_to == "flow"
    assert rel.style == {"color": "red", "line": "dashed"}


def test_uses_shortcut(project):
    a = project.model.element("service", "A")
    b = project.model.element("service", "B")

    rel = a.uses(b, "calls")

    assert (rel.source, rel.target, rel.title) == (a, b, "calls")
    assert rel.bidirectional is False


@pytest.mark.parametrize(
    "kwargs",
    [{"kind": "a b"}, {"navigate_to": "a/b"}, {"head": "square"}],
)
def test_invalid_relationship_properties_are_rejected(kwargs):
    model = Project().model
    a = model.element("a", "A")
    b = model.element("a", "B")

    with pytest.raises(ValueError):
        model.relate(a, b, **kwargs)


def test_relationship_endpoint_must_belong_to_model():
    model = Project().model
    a = model.element("a", "A")
    foreign = Project().model.element("a", "F")

    with pytest.raises(ValueError, match="does not belong"):
        model.relate(a, foreign)
    with pytest.raises(ValueError, match="does not belong"):
        model.relate(a, "b")  # type: ignore[arg-type]


def test_element_is_exported():
    assert isinstance(Project().model.element("a", "A"), Element)


def test_model_and_specification_are_context_managers():
    project = Project("Shop")

    with project.specification as spec:
        assert spec is project.specification
    with project.model as model:
        assert model is project.model

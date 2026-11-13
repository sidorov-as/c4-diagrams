import pytest

from c4.contrib.likec4 import (
    Between,
    Children,
    DeploymentView,
    Descendants,
    DynamicStep,
    DynamicView,
    ElementView,
    Incoming,
    InOut,
    Outgoing,
    Project,
    RawPredicate,
    Where,
    Wildcard,
)
from c4.contrib.likec4._views import (
    AutoLayoutRule,
    ExcludeRule,
    IncludeRule,
    StyleRule,
)


@pytest.fixture
def project() -> Project:
    project = Project()
    project.specification.element("system").element("service")
    return project


def test_views_collection_keeps_creation_order(project):
    views = project.views
    first = views.element_view("a")
    second = views.dynamic_view("b")
    third = views.deployment_view("c")

    assert views.all == [first, second, third]
    assert views.all is project.views.all
    assert isinstance(first, ElementView)
    assert isinstance(third, DeploymentView)


def test_element_view_properties(project):
    cloud = project.model.element("system", "Cloud")

    view = project.views.element_view(
        "landscape",
        "Landscape",
        of=cloud,
        description="d",
        tags=["critical"],
        links=["https://x.io"],
    )

    assert view.key == "landscape"
    assert view.scope is cloud
    assert view.description == "d"
    assert view.tags == ("critical",)
    assert repr(view) == "ElementView('landscape')"


def test_scope_must_be_element(project):
    with pytest.raises(TypeError, match="Element"):
        project.views.element_view("v", of="cloud")


@pytest.mark.parametrize("key", ["", "a/b", "1a", "a b", "a-"])
def test_view_key_must_be_identifier(project, key):
    with pytest.raises(ValueError, match="View key"):
        project.views.element_view(key)


def test_rules_keep_declared_order(project):
    api = project.model.element("service", "API")
    db = project.model.element("service", "DB")
    view = project.views.element_view("v")

    view.include(api).exclude(db).include(Wildcard())
    view.style(api, color="red").auto_layout("LeftRight", 80, 100)

    assert view.rules == [
        IncludeRule((api,), None),
        ExcludeRule((db,)),
        IncludeRule((Wildcard(),), None),
        StyleRule((api,), (("color", "red"),)),
        AutoLayoutRule("LeftRight", 80, 100),
    ]
    assert view.layout == AutoLayoutRule("LeftRight", 80, 100)


def test_layout_is_none_without_rule(project):
    assert project.views.element_view("v").layout is None


def test_typed_predicates_are_data(project):
    cloud = project.model.element("system", "Cloud")

    assert Children(cloud).element is cloud
    assert Descendants(cloud).element is cloud
    assert RawPredicate("cloud.** where kind is service").text.startswith(
        "cloud"
    )
    assert Where(Wildcard(), tag="critical").tag == "critical"
    assert Between(cloud, Wildcard()).source is cloud
    assert Between(cloud, Wildcard()).both is False
    assert Incoming(cloud).item is cloud
    assert Outgoing(cloud).item is cloud
    assert InOut(cloud).item is cloud


def test_include_with_navigate_to(project):
    api = project.model.element("service", "API")
    view = project.views.element_view("v").include(api, navigate_to="detail")

    assert view.rules == [IncludeRule((api,), "detail")]


def test_deployment_view_rejects_with_overrides(project):
    view = project.views.deployment_view("v")

    with pytest.raises(TypeError):
        view.include(Wildcard(), navigate_to="x")  # type: ignore[call-arg]


@pytest.mark.parametrize(
    "build",
    [
        lambda v: v.include(),
        lambda v: v.exclude(),
        lambda v: v.style(color="red"),
        lambda v: v.style(Wildcard()),
        lambda v: v.include(Wildcard(), navigate_to="a/b"),
        lambda v: v.auto_layout("Diagonal"),
        lambda v: v.auto_layout("LeftRight", node_sep=10),
        lambda v: v.auto_layout("LeftRight", rank_sep=-1),
        lambda v: v.auto_layout("LeftRight", rank_sep=True),
    ],
)
def test_invalid_rules_are_rejected(project, build):
    with pytest.raises(ValueError):
        build(project.views.element_view("v"))


@pytest.mark.parametrize(
    "build",
    [
        lambda: RawPredicate("  "),
        lambda: Where(Wildcard()),
        lambda: Where(Wildcard(), tag="#x"),
        lambda: Where(RawPredicate("x"), tag="x"),
        lambda: Where(Where(Wildcard(), tag="x"), kind="y"),
        lambda: Between(Between(Wildcard(), Wildcard()), Wildcard()),
        lambda: Between(Wildcard(), RawPredicate("x")),
        lambda: Incoming(Where(Wildcard(), tag="x")),
        lambda: Outgoing(RawPredicate("x")),
        lambda: InOut(Incoming(Wildcard())),
    ],
)
def test_invalid_predicates_are_rejected(build):
    with pytest.raises((ValueError, TypeError)):
        build()


def test_dynamic_steps_are_flat_and_ordered(project):
    customer = project.model.element("service", "Customer")
    web = project.model.element("service", "Web")
    view = project.views.dynamic_view("checkout", "Checkout")

    view.step(customer, web, "open", technology="HTTPS", color="red")
    view.back(customer, web, "show page", notes="n", navigate_to="other")

    forward, backward = view.steps
    assert (forward.source, forward.target, forward.backward) == (
        customer,
        web,
        False,
    )
    assert forward.technology == "HTTPS"
    assert forward.color == "red"
    assert backward.backward is True
    assert (backward.notes, backward.navigate_to) == ("n", "other")
    assert view.variant == "diagram"
    assert isinstance(forward, DynamicStep)


def test_steps_do_not_need_a_relationship(project):
    a = project.model.element("service", "A")
    b = project.model.element("service", "B")

    project.views.dynamic_view("v").step(a, b)

    assert project.model.relationships == []


def test_steps_are_immutable(project):
    a = project.model.element("service", "A")
    view = project.views.dynamic_view("v").step(a, a, "loop")

    with pytest.raises(AttributeError):
        view.steps[0].title = "x"  # type: ignore[misc]
    assert isinstance(view.steps, tuple)


def test_sequence_variant(project):
    assert project.views.dynamic_view("v", variant="sequence").variant == (
        "sequence"
    )
    with pytest.raises(ValueError, match="variant"):
        DynamicView("v", variant="graph")  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "properties",
    [{"metadata": {"k": "v"}}, {"bogus": 1}],
)
def test_step_rejects_unknown_properties(project, properties):
    a = project.model.element("service", "A")

    with pytest.raises(TypeError):
        project.views.dynamic_view("v").step(a, a, **properties)


def test_step_validates_endpoints_and_values(project):
    a = project.model.element("service", "A")
    view = project.views.dynamic_view("v")

    with pytest.raises(TypeError, match="Elements"):
        view.step(a, "b")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="navigate_to"):
        view.step(a, a, navigate_to="a/b")
    with pytest.raises(ValueError, match="color"):
        view.step(a, a, color="#fff")


def test_no_flow_control_members():
    members = set(dir(DynamicView))

    assert not members & {"parallel", "par", "opt", "loop", "alt", "try_"}


def test_dynamic_view_supports_layout(project):
    view = project.views.dynamic_view("v").auto_layout("LeftRight")

    assert view.layout == AutoLayoutRule("LeftRight")

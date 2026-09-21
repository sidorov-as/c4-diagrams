import pytest

from c4.contrib.likec4 import (
    Between,
    Children,
    Incoming,
    InOut,
    Outgoing,
    Project,
    RawPredicate,
    Where,
    Wildcard,
)
from c4.contrib.likec4.renderer import (
    LikeC4Error,
    LikeC4Renderer,
    LikeC4ValidationError,
)


@pytest.fixture
def project() -> Project:
    project = Project()
    spec = project.specification
    spec.element("system").element("service")
    spec.relationship("async")
    spec.tag("critical")
    spec.color("brand", "#fff")
    spec.deployment_node("vm")
    return project


def render(project: Project) -> str:
    return LikeC4Renderer().render(project)


def test_error_hierarchy():
    assert issubclass(LikeC4ValidationError, LikeC4Error)


def test_only_projects_are_accepted():
    with pytest.raises(LikeC4ValidationError, match="Project"):
        LikeC4Renderer().render(object())  # type: ignore[arg-type]


def test_valid_project_passes(project):
    project.model.element("system", "A", tags=["critical"], color="brand")
    project.model.element("system", "B", color="primary")

    render(project)


def test_undeclared_kind_names_element_and_kind(project):
    project.model.element("queue", "Orders", alias="api")

    with pytest.raises(LikeC4ValidationError) as error:
        render(project)

    assert "Orders" in str(error.value)
    assert "queue" in str(error.value)


def test_undeclared_tag_names_element_and_tag(project):
    project.model.element("system", "api", tags=["secret"])

    with pytest.raises(LikeC4ValidationError) as error:
        render(project)

    assert "api" in str(error.value)
    assert "secret" in str(error.value)


@pytest.mark.parametrize(
    "build",
    [
        lambda p: p.model.element("system", "A", color="unknown"),
        lambda p: p.specification.tag("t", color="unknown"),
        lambda p: p.specification.element("k", tags=["nope"]),
        lambda p: p.specification.element("k", color="unknown"),
        lambda p: p.specification.relationship("r", color="unknown"),
        lambda p: p.deployment.node("vm", "N", tags=["nope"]),
        lambda p: p.deployment.node("vm", "N", color="unknown"),
        lambda p: p.views.element_view("v", tags=["nope"]),
    ],
)
def test_undeclared_references_in_declarations_fail(project, build):
    build(project)

    with pytest.raises(LikeC4ValidationError, match="not declared"):
        render(project)


def test_undeclared_deployment_kind(project):
    project.deployment.node("zone", "Zone")

    with pytest.raises(LikeC4ValidationError, match="zone"):
        render(project)


def test_parent_child_relationship_is_rejected(project):
    cloud = project.model.element("system", "Cloud")
    api = cloud.element("service", "API")
    cloud.uses(api, "contains")

    with pytest.raises(LikeC4ValidationError, match="ancestor or descendant"):
        render(project)


def test_relationship_to_descendant_of_sibling_is_fine(project):
    a = project.model.element("system", "A")
    b = project.model.element("system", "B")
    child = b.element("service", "Child")
    a.uses(child)

    render(project)


def test_undeclared_relationship_kind_and_tag(project):
    a = project.model.element("system", "A")
    b = project.model.element("system", "B")
    a.uses(b, kind="sync")

    with pytest.raises(LikeC4ValidationError, match="sync"):
        render(project)


def test_relationship_with_foreign_endpoint(project):
    a = project.model.element("system", "A")
    foreign = Project().model.element("system", "F")
    rel = a.uses(project.model.element("system", "B"))
    rel.target = foreign

    with pytest.raises(LikeC4ValidationError, match="does not belong"):
        render(project)


def test_relationship_navigate_to_must_be_dynamic(project):
    a = project.model.element("system", "A")
    b = project.model.element("system", "B")
    a.uses(b, navigate_to="landscape")
    project.views.element_view("landscape")

    with pytest.raises(LikeC4ValidationError, match="dynamic view"):
        render(project)


def test_links_must_be_valid_uris(project):
    project.model.element("system", "A", links=["not a url"])

    with pytest.raises(LikeC4ValidationError, match="link"):
        render(project)


@pytest.mark.parametrize(
    "url", ["https://x.io/a?b=1", "./doc.md", "../doc.md", "@docs/page"]
)
def test_valid_links(project, url):
    project.model.element("system", "A", links=[url])

    render(project)


def test_duplicate_view_keys_across_types(project):
    project.views.element_view("main")
    project.views.dynamic_view("main")

    with pytest.raises(LikeC4ValidationError, match="main"):
        render(project)


def test_foreign_element_in_view(project):
    foreign = Project().model.element("system", "F")
    project.views.element_view("v").include(foreign)

    with pytest.raises(LikeC4ValidationError, match="does not resolve"):
        render(project)


def test_foreign_scope(project):
    foreign = Project().model.element("system", "F")
    project.views.element_view("v", of=foreign)

    with pytest.raises(LikeC4ValidationError, match="scope"):
        render(project)


def test_deployment_node_in_element_view_is_rejected(project):
    node = project.deployment.node("vm", "VM")
    project.views.element_view("v").include(node)

    with pytest.raises(LikeC4ValidationError, match="does not resolve"):
        render(project)


def test_element_in_deployment_view_is_rejected(project):
    element = project.model.element("system", "A")
    project.views.deployment_view("v").include(element)

    with pytest.raises(LikeC4ValidationError, match="does not resolve"):
        render(project)


def test_free_form_item_needs_raw_predicate(project):
    project.views.element_view("v").include("cloud.api")

    with pytest.raises(LikeC4ValidationError, match="RawPredicate"):
        render(project)


def test_view_predicate_checks(project):
    a = project.model.element("system", "A")
    view = project.views.element_view("v")
    view.include(Where(Children(a), tag="critical", kind="system"))
    view.include(Between(a, Wildcard()), Incoming(a), Outgoing(a), InOut(a))
    view.include(RawPredicate("anything"))
    render(project)

    view.include(Where(Wildcard(), tag="nope"))
    with pytest.raises(LikeC4ValidationError, match="nope"):
        render(project)


def test_view_where_kind_must_be_declared(project):
    project.views.element_view("v").include(Where(Wildcard(), kind="ghost"))

    with pytest.raises(LikeC4ValidationError, match="ghost"):
        render(project)


def test_style_rule_cannot_target_relationship(project):
    a = project.model.element("system", "A")
    project.views.element_view("v").style(Outgoing(a), color="red")

    with pytest.raises(LikeC4ValidationError, match="style rule"):
        render(project)


def test_style_rule_color_must_be_declared(project):
    project.views.element_view("v").style(Wildcard(), color="unknown")

    with pytest.raises(LikeC4ValidationError, match="unknown"):
        render(project)


def test_include_navigate_to_must_exist(project):
    project.views.element_view("v").include(Wildcard(), navigate_to="ghost")

    with pytest.raises(LikeC4ValidationError, match="ghost"):
        render(project)


def test_include_navigate_to_may_name_any_view(project):
    project.views.element_view("v").include(Wildcard(), navigate_to="other")
    project.views.deployment_view("other")

    render(project)


def test_step_navigate_to_must_name_dynamic_view(project):
    a = project.model.element("system", "A")
    project.views.element_view("overview")
    project.views.dynamic_view("flow").step(
        a, a, "loop", navigate_to="overview"
    )

    with pytest.raises(LikeC4ValidationError) as error:
        render(project)

    assert "Step 1" in str(error.value)
    assert "flow" in str(error.value)


def test_step_checks_endpoints_and_color(project):
    a = project.model.element("system", "A")
    foreign = Project().model.element("system", "F")
    view = project.views.dynamic_view("flow").step(a, foreign)

    with pytest.raises(LikeC4ValidationError, match="not in the project"):
        render(project)

    view._nodes.clear()
    view.step(a, a, color="unknown")
    with pytest.raises(LikeC4ValidationError, match="unknown"):
        render(project)


def test_step_navigate_to_dynamic_view_is_fine(project):
    a = project.model.element("system", "A")
    project.views.dynamic_view("other")
    project.views.dynamic_view("flow").step(a, a, navigate_to="other")

    render(project)


def test_anonymous_duplicate_instances(project):
    api = project.model.element("service", "API")
    vm = project.deployment.node("vm", "VM")
    vm.instance(api)
    vm.instance(api)

    with pytest.raises(LikeC4ValidationError, match="unnamed instances"):
        render(project)


def test_named_duplicates_and_other_nodes_are_fine(project):
    api = project.model.element("service", "API")
    vm = project.deployment.node("vm", "VM")
    vm.instance(api, "a")
    vm.instance(api, "b")
    project.deployment.node("vm", "Other").instance(api)

    render(project)


def test_instance_of_unknown_element(project):
    foreign = Project().model.element("service", "F")
    project.deployment.node("vm", "VM").instance(foreign)

    with pytest.raises(LikeC4ValidationError, match="not in the project"):
        render(project)


def test_deployment_relationship_checks(project):
    vm = project.deployment.node("vm", "VM")
    child = vm.node("vm", "Child")
    other = project.deployment.node("vm", "Other")
    vm.uses(child)

    with pytest.raises(LikeC4ValidationError, match="ancestor or descendant"):
        render(project)

    project.deployment.relationships.clear()
    vm.uses(other, kind="sync")
    with pytest.raises(LikeC4ValidationError, match="sync"):
        render(project)

    project.deployment.relationships.clear()
    rel = vm.uses(other)
    rel.target = project.deployment.__class__(project).node("vm", "Ghost")
    with pytest.raises(LikeC4ValidationError, match="does not belong"):
        render(project)


def test_instance_relationship_to_its_node_is_rejected(project):
    api = project.model.element("service", "API")
    vm = project.deployment.node("vm", "VM")
    instance = vm.instance(api, "a")
    instance.uses(vm)

    with pytest.raises(LikeC4ValidationError, match="ancestor or descendant"):
        render(project)

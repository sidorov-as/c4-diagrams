import pytest

from c4.contrib.likec4 import (
    DeploymentInstance,
    DeploymentRelationship,
    Link,
    Project,
)


@pytest.fixture
def project() -> Project:
    project = Project()
    project.specification.element("service")
    (
        project.specification
        .deployment_node("environment")
        .deployment_node("zone")
        .deployment_node("vm")
    )
    return project


@pytest.fixture
def api(project):
    return project.model.element("service", "API")


def test_nodes_nest_by_parent_method_and_with_block(project):
    deployment = project.deployment
    prod = deployment.node("environment", "Prod")
    app_tier = prod.node("zone", "AppTier")
    with prod:
        data = deployment.node("zone", "DataTier")
        with data:
            vm = deployment.node("vm", "DB VM")
    other = deployment.node("environment", "Staging")

    assert app_tier.parent is prod
    assert prod.children == [app_tier, data]
    assert vm.parent is data
    assert [n.name for n in deployment.roots] == ["Prod", "Staging"]
    assert [n.name for n in deployment.nodes] == [
        "Prod",
        "AppTier",
        "DataTier",
        "DB VM",
        "Staging",
    ]
    assert other.parent is None
    assert vm.ancestors() == [data, prod]
    assert prod.descendants() == [app_tier, data, vm]
    assert repr(prod) == "DeploymentNode('environment', 'Prod')"


def test_deployment_is_persistent_and_separate_from_model(project):
    assert project.deployment is project.deployment
    project.deployment.node("environment", "Prod")

    assert project.model.elements == []


def test_node_properties(project):
    node = project.deployment.node(
        "vm",
        "VM",
        alias="vm1",
        description="d",
        technology="EC2",
        tags=["critical"],
        metadata={"region": "eu"},
        links=["https://x.io"],
        color="gray",
    )

    assert node.alias == "vm1"
    assert node.description == "d"
    assert node.technology == "EC2"
    assert node.tags == ("critical",)
    assert node.metadata == {"region": "eu"}
    assert node.links == (Link("https://x.io"),)
    assert node.style == {"color": "gray"}


def test_node_needs_title_or_alias(project):
    with pytest.raises(ValueError, match="title or an alias"):
        project.deployment.node("vm")


def test_invalid_node_alias_and_foreign_parent(project):
    with pytest.raises(ValueError, match="alias"):
        project.deployment.node("vm", "x", alias="a.b")
    foreign = Project().deployment.node("vm", "F")
    with pytest.raises(ValueError, match="another deployment"):
        project.deployment.node("vm", "x", parent=foreign)


def test_named_replicas(project, api):
    vm = project.deployment.node("vm", "VM")

    primary = vm.instance(api, "primary")
    secondary = vm.instance(api, "secondary")

    assert vm.instances == [primary, secondary]
    assert project.deployment.instances == [primary, secondary]
    assert primary.element is api
    assert (primary.alias, secondary.alias) == ("primary", "secondary")
    assert primary.parent is vm
    assert isinstance(primary, DeploymentInstance)


def test_anonymous_instance_and_names(project, api):
    vm = project.deployment.node("vm", "VM")

    anonymous = vm.instance(api)

    assert anonymous.alias is None
    assert anonymous.name == "API"
    assert repr(anonymous) == "DeploymentInstance('API')"
    assert vm.instance(api, "x").name == "x"


def test_instance_in_with_block_and_properties(project, api):
    with project.deployment.node("vm", "VM") as vm:
        instance = project.deployment.instance(
            api,
            "p",
            title="Primary",
            description="d",
            technology="Go",
            tags=["critical"],
            metadata={"k": "v"},
            links=["u"],
            color="red",
        )

    assert instance.parent is vm
    assert instance.title == "Primary"
    assert instance.description == "d"
    assert instance.technology == "Go"
    assert instance.tags == ("critical",)
    assert instance.metadata == {"k": "v"}
    assert instance.links == (Link("u"),)
    assert instance.style == {"color": "red"}


def test_instance_needs_node_and_element(project, api):
    with pytest.raises(ValueError, match="deployment node"):
        project.deployment.instance(api)
    vm = project.deployment.node("vm", "VM")
    with pytest.raises(TypeError, match="Element"):
        vm.instance("cloud.api")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Instance name"):
        vm.instance(api, "a.b")


def test_instance_node_from_another_deployment(project, api):
    foreign = Project().deployment.node("vm", "F")

    with pytest.raises(ValueError, match="another deployment"):
        project.deployment.instance(api, parent=foreign)


def test_node_relationship_with_technology(project):
    deployment = project.deployment
    prod = deployment.node("environment", "Prod")
    app = prod.node("zone", "AppTier")
    data = prod.node("zone", "DataTier")

    rel = app.uses(
        data,
        "internal traffic",
        technology="TCP/5432",
        kind="sync",
        bidirectional=True,
        tags=["critical"],
        metadata={"k": "v"},
        links=["u"],
        description="d",
        color="red",
    )

    assert deployment.relationships == [rel]
    assert isinstance(rel, DeploymentRelationship)
    assert (rel.source, rel.target) == (app, data)
    assert rel.technology == "TCP/5432"
    assert rel.kind == "sync"
    assert rel.bidirectional is True
    assert rel.tags == ("critical",)
    assert rel.metadata == {"k": "v"}
    assert rel.links == (Link("u"),)
    assert rel.description == "d"
    assert rel.style == {"color": "red"}


def test_instance_relationship_and_shortcuts(project, api):
    deployment = project.deployment
    vm = deployment.node("vm", "VM")
    a = vm.instance(api, "a")
    b = vm.instance(api, "b")

    assert a.uses(b, "x").target is b
    assert vm.uses(a).source is vm
    assert deployment.relate(a, vm).target is vm


@pytest.mark.parametrize("kwargs", [{"kind": "a b"}, {"head": "square"}])
def test_invalid_relationship_properties(project, kwargs):
    vm = project.deployment.node("vm", "VM")
    other = project.deployment.node("vm", "Other")

    with pytest.raises(ValueError):
        vm.uses(other, **kwargs)


def test_relationship_endpoints_must_belong_to_deployment(project, api):
    vm = project.deployment.node("vm", "VM")
    foreign = Project().deployment.node("vm", "F")

    with pytest.raises(ValueError, match="does not belong"):
        project.deployment.relate(vm, foreign)
    with pytest.raises(ValueError, match="does not belong"):
        project.deployment.relate(vm, api)  # type: ignore[arg-type]


def test_ownership_mismatch(project):
    deployment = project.deployment
    first = deployment.node("vm", "first")
    second = deployment.node("vm", "second")
    first.__enter__()

    with pytest.raises(RuntimeError, match="ownership"):
        second.__exit__(None, None, None)


def test_deployment_is_a_context_manager(project):
    with project.deployment as deployment:
        assert deployment is project.deployment
    with project.views as views:
        assert views is project.views

import pytest

from c4.contrib.likec4 import Project, Rel


@pytest.fixture
def project() -> Project:
    project = Project()
    project.specification.element("service")
    project.specification.relationship("async")
    project.specification.deployment_node("vm")
    return project


@pytest.fixture
def trio(project):
    model = project.model
    return tuple(model.element("service", name, alias=name) for name in "abc")


def triples(relationships):
    return [(r.source.alias, r.target.alias, r.title) for r in relationships]


def test_rel_is_reusable(project, trio):
    a, b, c = trio
    d = project.model.element("service", "d", alias="d")
    rel = Rel("uses")

    a >> rel >> b
    c >> rel >> d

    assert triples(project.model.relationships) == [
        ("a", "b", "uses"),
        ("c", "d", "uses"),
    ]


def test_rel_second_positional_argument_is_rejected():
    with pytest.raises(TypeError):
        Rel("calls", "long text")


def test_rel_options(project, trio):
    a, b, _ = trio

    rel = (
        a
        >> Rel(
            "title",
            description="long",
            technology="HTTPS",
            kind="async",
            bidirectional=True,
            tags=["hot"],
            line="dashed",
        )
        >> b
    )

    assert (rel.title, rel.description, rel.technology) == (
        "title",
        "long",
        "HTTPS",
    )
    assert rel.kind == "async"
    assert rel.bidirectional is True
    assert rel.tags == ("hot",)
    assert rel.style == {"line": "dashed"}


def test_bidirectional_rel_renders_double_arrow(project, trio):
    a, b, _ = trio
    a >> Rel("syncs", bidirectional=True) >> b

    assert 'a <-> b "syncs"' in project.render()


def test_method_forms(project, trio):
    a, b, _ = trio

    first = a.uses(b, "calls", technology="HTTPS")
    second = b.used_by(a, "calls")

    assert (first.source, first.target) == (a, b)
    assert first.title == "calls"
    assert first.technology == "HTTPS"
    assert (second.source, second.target) == (a, b)


def test_forward_and_reversed_forms_agree(project, trio):
    a, b, _ = trio

    forward = a >> Rel("uses") >> b
    reversed_ = b << Rel("uses") << a
    string_forward = a >> "uses" >> b
    string_reversed = b << "uses" << a

    for rel in (forward, reversed_, string_forward, string_reversed):
        assert (rel.source, rel.target, rel.title) == (a, b, "uses")


def test_one_to_many_and_reversed(project, trio):
    a, b, c = trio

    first = a >> Rel("x") >> [b, c]
    second = [b, c] << Rel("y") << a

    assert isinstance(first, list)
    assert isinstance(second, list)
    assert triples(project.model.relationships) == [
        ("a", "b", "x"),
        ("a", "c", "x"),
        ("a", "b", "y"),
        ("a", "c", "y"),
    ]


def test_many_to_one_and_reversed(project, trio):
    a, b, c = trio

    first = [a, b] >> Rel("x") >> c
    second = c << Rel("y") << [a, b]

    assert isinstance(first, list)
    assert isinstance(second, list)
    assert triples(project.model.relationships) == [
        ("a", "c", "x"),
        ("b", "c", "x"),
        ("a", "c", "y"),
        ("b", "c", "y"),
    ]


def test_unlabeled_lists(project, trio):
    a, b, c = trio

    a >> [b, c]
    [a, b] >> c
    c << [a, b]
    [b, c] << a

    assert len(project.model.relationships) == 8
    assert all(r.title is None for r in project.model.relationships)


@pytest.mark.parametrize("reverse", [False, True])
def test_many_to_many_is_rejected(project, trio, reverse):
    a, b, c = trio
    d = project.model.element("service", "d", alias="d")
    expected = "Either source or destination must be a single element"

    with pytest.raises(ValueError, match=expected):
        if reverse:
            [c, d] << Rel("x") << [a, b]
        else:
            [a, b] >> Rel("x") >> [c, d]

    assert not project.model.relationships


def test_mixed_operators_are_rejected(trio):
    a, b, _ = trio

    with pytest.raises(TypeError):
        a >> Rel("x") << b


def test_unlabeled_relationship_and_pipe(project, trio):
    a, b, c = trio

    plain = a >> b
    labeled = b << c | "reads"

    assert plain.title is None
    assert "a -> b\n" in project.render()
    assert (labeled.source, labeled.target, labeled.title) == (c, b, "reads")


@pytest.mark.parametrize("existing", ["x", ""])
def test_pipe_does_not_overwrite(project, trio, existing):
    a, b, _ = trio

    with pytest.raises(ValueError, match="already has the title"):
        a >> Rel(existing) >> b | "y"

    assert triples(project.model.relationships) == [("a", "b", existing)]


def test_relate_to_is_gone(trio):
    a = trio[0]

    assert not hasattr(a, "relate_to")


def test_deployment_relationships(project):
    api = project.model.element("service", "API", alias="api")
    deployment = project.deployment
    with deployment.node("vm", "Zone", alias="zone"):
        a = deployment.node("vm", "A", alias="za")
        b = deployment.node("vm", "B", alias="zb")
        c = deployment.node("vm", "C", alias="zc")
    instance = a.instance(api, "primary")

    a >> Rel(technology="TCP/5432") >> b
    a >> Rel("replicates") >> [b, c]
    [b, c] >> Rel("syncs") >> a
    b.uses(c, "calls", kind="async")
    c.used_by(b, "x")
    instance >> c
    unlabeled = a >> b | "late"

    relationships = project.deployment.relationships
    assert not hasattr(a, "relate_to")
    assert len(relationships) == 9
    assert relationships[0].technology == "TCP/5432"
    assert unlabeled.title == "late"
    assert relationships[-2].source is instance
    assert relationships[-2].title is None
    text = project.render()
    assert 'zone.za -> zone.zb "replicates"' in text
    assert 'zone.za -> zone.zc "replicates"' in text


def test_deployment_many_to_many_is_rejected(project):
    deployment = project.deployment
    nodes = [
        deployment.node("vm", n, alias=n) for n in ("n1", "n2", "n3", "n4")
    ]

    with pytest.raises(ValueError, match="single element"):
        nodes[:2] >> Rel("x") >> nodes[2:]


def test_deployment_pipe_does_not_overwrite(project):
    deployment = project.deployment
    a = deployment.node("vm", "A", alias="na")
    b = deployment.node("vm", "B", alias="nb")

    with pytest.raises(ValueError, match="already has the title"):
        a >> Rel("x") >> b | "y"

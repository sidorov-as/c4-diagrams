from pathlib import Path

import pytest

from c4.contrib.likec4 import (
    Between,
    Children,
    Descendants,
    Incoming,
    InOut,
    Outgoing,
    Project,
    RawPredicate,
    Where,
    Wildcard,
)
from c4.contrib.likec4.renderer import (
    BaseLikeC4Backend,
    LikeC4BackendConfigurationError,
    LikeC4Renderer,
)
from c4.enums import PNG


def render(project: Project) -> str:
    return project.render()


@pytest.fixture
def project() -> Project:
    project = Project()
    spec = project.specification
    spec.element("system").element("service").element("actor")
    spec.relationship("async").tag("critical").deployment_node("vm")
    return project


def test_block_order_and_empty_blocks_are_omitted(project):
    a = project.model.element("system", "A", alias="a")
    project.deployment.node("vm", "VM").instance(a)
    project.views.element_view("v").include(Wildcard())

    text = render(project)

    positions = [
        text.index(block)
        for block in ("specification {", "model {", "deployment {", "views {")
    ]
    assert positions == sorted(positions)


def test_empty_blocks_are_omitted(project):
    project.model.element("system", "A")

    text = render(project)

    assert "\ndeployment {" not in text
    assert "\nviews {" not in text
    assert text.endswith("\n")


def test_empty_project_renders_a_newline():
    assert render(Project()) == "\n"


def test_rendering_is_deterministic(project):
    a = project.model.element("system", "A")
    b = project.model.element("system", "A")
    a.uses(b)
    project.views.element_view("v").include(a, b)

    assert render(project) == render(project)
    assert LikeC4Renderer().render(project) == render(project)


def test_declared_kinds_render(project):
    project.specification.element(
        "queue",
        title="Queue",
        technology="Kafka",
        description="d",
        notation="Q",
        tags=["critical"],
        shape="queue",
    ).relationship("sync", technology="REST", color="red", line="dashed")
    project.specification.tag("deprecated", color="red").color(
        "brand", "#112233"
    )

    text = render(project)

    assert "element service" in text
    assert "color brand #112233" in text
    assert "tag deprecated { color red }" in text
    assert 'element queue {\n    #critical\n    title "Queue"' in text
    assert '    notation "Q"\n    style { shape queue }' in text
    assert 'relationship sync {\n    technology "REST"' in text
    assert "    color red\n    line dashed\n  }" in text


def test_single_style_kind_collapses_to_one_line():
    project = Project()
    project.specification.element("service", shape="component")

    assert "element service { style { shape component } }" in render(project)


def test_nested_elements_and_fqn_relationships(project):
    cloud = project.model.element("system", "Cloud", alias="cloud")
    backend = cloud.element("system", "Backend", alias="backend")
    api = backend.element("service", "API", alias="api")
    other = project.model.element("system", "Other", alias="other")
    api.uses(other, "calls")

    text = render(project)

    assert (
        '  cloud = system "Cloud" {\n'
        '    backend = system "Backend" {\n'
        '      api = service "API"\n'
        "    }\n"
        "  }"
    ) in text
    assert '  cloud.backend.api -> other "calls"' in text


def test_element_properties(project):
    project.model.element(
        "system",
        "A",
        alias="a",
        summary="short",
        description="long",
        technology="Go",
        tags=["critical"],
        icon="tech:go",
        metadata={"owner": "me", "tiers": ["x", "y"]},
        links=[("https://x.io", "Docs"), "./local.md"],
        color="red",
    )

    text = render(project)

    assert (
        '  a = system "A" {\n'
        "    #critical\n"
        '    summary "short"\n'
        "    description '''long'''\n"
        '    technology "Go"\n'
        "    icon tech:go\n"
        "    style { color red }\n"
        "    metadata {\n"
        '      owner "me"\n'
        '      tiers ["x", "y"]\n'
        "    }\n"
        '    link https://x.io "Docs"\n'
        "    link ./local.md\n"
        "  }"
    ) in text


def test_typed_bidirectional_relationship(project):
    a = project.model.element("system", "A", alias="a")
    b = project.model.element("system", "B", alias="b")
    a.uses(b, "title", kind="async", bidirectional=True)
    a.uses(b, "plain")
    a.uses(b)
    a.uses(
        b,
        "full",
        technology="T",
        description="d",
        tags=["critical"],
        metadata={"k": "v"},
        links=["./x.md"],
        navigate_to="flow",
        color="red",
    )
    project.views.dynamic_view("flow")

    text = render(project)

    assert '  a -[async]<-> b "title"' in text
    assert '  a -> b "plain"\n' in text
    assert "  a -> b\n" in text
    assert (
        '  a -> b "full" {\n'
        "    #critical\n"
        '    technology "T"\n'
        "    description '''d'''\n"
        '    metadata { k "v" }\n'
        "    link ./x.md\n"
        "    navigateTo flow\n"
        "    style { color red }\n"
        "  }"
    ) in text


def test_identifiers_are_normalized_and_collisions_resolved(project):
    project.model.element("system", "Payment API.v2")
    project.model.element("system", "Payment API.v2")
    parent = project.model.element("system", "1st")
    parent.element("system", "Payment API.v2")

    text = render(project)

    assert 'Payment_API_v2 = system "Payment API.v2"' in text
    assert 'Payment_API_v2_2 = system "Payment API.v2"' in text
    assert (
        '  el_1st = system "1st" {\n'
        '    Payment_API_v2 = system "Payment API.v2"\n'
        "  }"
    ) in text


def test_strings_are_escaped(project):
    project.model.element(
        "system", 'say "hi" \\', alias="a", description="see [[a.b]]"
    )

    text = render(project)

    assert 'a = system "say \\"hi\\" \\\\"' in text
    assert "description '''see \\\\[\\\\[a.b]]'''" in text
    assert "[[a.b]]" not in text.replace("\\\\[\\\\[a.b]]", "")


def test_element_view_rules_in_order(project):
    a = project.model.element("system", "A", alias="a")
    b = project.model.element("system", "B", alias="b")
    cloud = project.model.element("system", "Cloud", alias="cloud")
    view = project.views.element_view("v", "Title", of=cloud, tags=["critical"])
    view.include(a, b).exclude(b).include(Wildcard())
    view.include(Children(cloud), Descendants(cloud))
    view.include(Where(Wildcard(), tag="critical"))
    view.include(Where(a, kind="system", tag="critical"))
    view.include(
        Between(a, b),
        Incoming(a),
        Outgoing(a),
        InOut(a),
        Between(a, b, both=True),
    )
    view.include(RawPredicate("cloud.** where kind is service"))
    view.include(a, navigate_to="detail")
    view.include(a, RawPredicate("x"), navigate_to="detail")
    view.style(a, b, color="red", opacity=20).auto_layout("LeftRight", 80, 100)
    project.views.element_view("detail")

    text = render(project)

    assert (
        "  view v of cloud {\n"
        "    #critical\n"
        '    title "Title"\n'
        "    include a, b\n"
        "    exclude b\n"
        "    include *\n"
        "    include cloud.*, cloud.**\n"
        "    include * where tag is #critical\n"
        "    include a where tag is #critical and kind is system\n"
        "    include a -> b\n"
        "    include -> a\n"
        "    include a ->\n"
        "    include -> a ->\n"
        "    include a <-> b\n"
        "    include cloud.** where kind is service\n"
        "    include a with { navigateTo detail }\n"
        "    include a with { navigateTo detail }\n"
        "    include x with { navigateTo detail }\n"
        "    style a, b {\n"
        "      color red\n"
        "      opacity 20%\n"
        "    }\n"
        "    autoLayout LeftRight 80 100\n"
        "  }"
    ) in text


def test_empty_view_and_view_properties(project):
    project.views.element_view("empty", description="d", links=["./x.md"])
    project.views.deployment_view("dep")

    text = render(project)

    assert (
        "  view empty {\n    description '''d'''\n    link ./x.md\n  }" in text
    )
    assert "  deployment view dep {}" in text


def test_scoped_view_uses_fqn(project):
    cloud = project.model.element("system", "Cloud", alias="cloud")
    backend = cloud.element("system", "Backend", alias="backend")
    project.views.element_view("v", of=backend)

    assert "view v of cloud.backend {}" in render(project)


def test_deployment_hierarchy_instances_and_relationships(project):
    api = project.model.element("service", "API", alias="api")
    db = project.model.element("service", "DB", alias="db")
    deployment = project.deployment
    with deployment.node("vm", "Prod", alias="prod") as prod:
        app = deployment.node("vm", "App", alias="app", technology="EC2")
        data = deployment.node("vm", "Data", alias="data")
    app.instance(api, "primary")
    app.instance(api, "secondary")
    data.instance(db)
    app.instance(db, "db_copy", title="Copy", tags=["critical"])
    app.uses(data, "queries", technology="TCP/5432")
    prod.uses(prod.children[0].instances[0], "x")
    deployment.relationships.pop()
    data.instances[0].uses(app, "back", kind="async")
    project.views.deployment_view("dv").include(prod, Children(prod)).style(
        prod, color="green"
    )

    text = render(project)

    assert (
        '  prod = vm "Prod" {\n'
        '    app = vm "App" {\n'
        '      technology "EC2"\n'
        "      primary = instanceOf api\n"
        "      secondary = instanceOf api\n"
        "      db_copy = instanceOf db {\n"
        "        #critical\n"
        '        title "Copy"\n'
        "      }\n"
        "    }\n"
        '    data = vm "Data" { instanceOf db }\n'
        "  }"
    ) in text
    assert '  prod.app -> prod.data "queries" { technology "TCP/5432" }' in text
    assert '  prod.data.db -[async]-> prod.app "back"' in text
    assert (
        "  deployment view dv {\n"
        "    include prod, prod.*\n"
        "    style prod { color green }\n"
        "  }"
    ) in text


def test_instance_with_colliding_implied_identifier_is_named(project):
    api = project.model.element("service", "API", alias="api")
    vm = project.deployment.node("vm", "VM", alias="vm")
    vm.node("vm", "api")
    vm.instance(api)

    text = render(project)

    assert "api_2 = instanceOf api" in text


def test_dynamic_view_steps(project):
    a = project.model.element("system", "A", alias="a")
    b = project.model.element("system", "B", alias="b")
    view = project.views.dynamic_view(
        "flow", "Flow", variant="sequence", description="d"
    )
    view.step(a, b, "call", technology="HTTPS", description="x", color="red")
    view.back(a, b, "return", notes="n", navigate_to="flow")
    view.step(b, a)
    view.auto_layout("LeftRight")
    project.views.dynamic_view("empty")

    text = render(project)

    assert (
        "  dynamic view flow {\n"
        '    title "Flow"\n'
        "    description '''d'''\n"
        "    variant sequence\n"
        '    a -> b "call" {\n'
        "      description '''x'''\n"
        '      technology "HTTPS"\n'
        "      color red\n"
        "    }\n"
        '    a <- b "return" {\n'
        "      notes '''n'''\n"
        "      navigateTo flow\n"
        "    }\n"
        "    b -> a\n"
        "    autoLayout LeftRight\n"
        "  }"
    ) in text
    assert "  dynamic view empty {}" in text


def test_diagram_variant_is_not_emitted(project):
    project.views.dynamic_view("flow")

    assert "variant" not in render(project)


def test_project_save(tmp_path: Path, project):
    project.model.element("system", "A")

    path = project.save(tmp_path / "out" / "a.c4")

    assert path.read_text(encoding="utf-8") == project.render()


def test_project_render_requires_likec4_renderer(project):
    with pytest.raises(TypeError, match="LikeC4Renderer"):
        project.render(object())  # type: ignore[arg-type]


class _Backend(BaseLikeC4Backend):
    def __init__(self) -> None:
        self.calls: list[tuple[str, object, str | None]] = []

    def to_bytes(self, source, *, format, view_key=None):  # noqa: A002
        self.calls.append((source, format, view_key))
        return b"img"


def test_render_bytes_and_file_use_the_backend(tmp_path, project):
    project.model.element("system", "A", alias="a")
    project.views.element_view("index")
    backend = _Backend()
    renderer = LikeC4Renderer(backend=backend)

    assert renderer.render_bytes(project, format=PNG) == b"img"
    target = renderer.render_file(project, tmp_path / "x.png", format=PNG)

    assert target.read_bytes() == b"img"
    assert backend.calls[0] == (renderer.render(project), PNG, "index")
    with pytest.raises(FileExistsError):
        renderer.render_file(
            project, tmp_path / "x.png", format=PNG, overwrite=False
        )


def test_backend_to_file_infers_format_and_needs_extension(tmp_path):
    backend = _Backend()

    backend.to_file("src", tmp_path / "a.png", format=None)
    with pytest.raises(ValueError, match="no extension"):
        backend.to_file("src", tmp_path / "noext", format=None)
    assert backend.calls[0][1] == PNG


def test_render_bytes_uses_configured_view_key(project):
    project.views.element_view("a")
    project.views.element_view("b")
    backend = _Backend()

    LikeC4Renderer(backend=backend, view_key="b").render_bytes(
        project, format=PNG
    )

    assert backend.calls[0][2] == "b"


@pytest.mark.parametrize("count", [0, 2])
def test_render_bytes_needs_view_key_unless_one_view(project, count):
    for index in range(count):
        project.views.element_view(f"v{index}")
    backend = _Backend()

    with pytest.raises(LikeC4BackendConfigurationError, match="view key"):
        LikeC4Renderer(backend=backend).render_bytes(project, format=PNG)
    assert backend.calls == []


@pytest.mark.parametrize("method", ["render_bytes", "render_file"])
def test_export_requires_backend(tmp_path, project, method):
    renderer = LikeC4Renderer()
    project.views.element_view("index")
    args = (project,) if method == "render_bytes" else (project, tmp_path / "x")

    with pytest.raises(LikeC4BackendConfigurationError, match="backend"):
        getattr(renderer, method)(*args, format=PNG)

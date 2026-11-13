from pathlib import Path

import pytest

from c4.contrib.likec4 import (
    C4,
    ElementKind,
    Preset,
    Project,
    RelationshipKind,
    Tag,
)
from c4.contrib.likec4.converters.python import project_to_python_code
from c4.contrib.likec4.renderer.errors import LikeC4ValidationError

KINDS = ["person", "system", "container", "component", "database", "external"]
CONVERTERS_DIR = (
    Path(__file__).parents[5] / "c4" / "contrib" / "likec4" / "converters"
)


def _spec_block(project: Project) -> str:
    return project.render().split("\n}")[0]


def test_use_declares_c4_kinds_in_order():
    project = Project("Shop")

    result = project.specification.use(C4)

    assert result is project.specification
    assert list(project.specification.element_kinds) == KINDS
    block = _spec_block(project)
    assert [block.index(f"element {kind}") for kind in KINDS] == sorted(
        block.index(f"element {kind}") for kind in KINDS
    )


def test_c4_is_data_only():
    assert [kind.name for kind in C4.elements] == KINDS
    assert C4.relationships == ()
    assert C4.tags == ()


def test_with_overrides_in_place_and_appends():
    custom = C4.with_(
        elements=[
            ElementKind("database", title="DB", style={"shape": "cylinder"}),
            ElementKind("queue"),
        ],
        tags=[Tag("critical")],
    )
    project = Project()
    project.specification.use(custom)

    kinds = project.specification.element_kinds
    assert list(kinds) == [*KINDS, "queue"]
    assert kinds["database"].style == {"shape": "cylinder"}
    assert kinds["person"] == C4.elements[0]
    assert "critical" in project.specification.tags
    assert C4.elements[4].style == {"shape": "storage", "color": "secondary"}


def test_user_defined_preset_matches_manual_declaration():
    preset = Preset(elements=(ElementKind("service", title="Service"),))
    used = Project()
    used.specification.use(preset)
    manual = Project()
    manual.specification.element("service", title="Service")

    assert _spec_block(used) == _spec_block(manual)


def test_use_after_manual_declaration_raises():
    project = Project()
    project.specification.element("system")

    with pytest.raises(ValueError, match="system"):
        project.specification.use(C4)


def test_helpers_on_model_and_element():
    project = Project("Shop")
    project.specification.use(C4)
    model = project.model

    customer = model.person("Customer", alias="customer")
    shop = model.system("Shop", alias="shop")
    api = shop.container("API", technology="Go")
    auth = api.component("Auth")
    db = shop.database("DB")
    ext = model.external("Mail")

    assert [e.kind for e in (customer, shop, api, auth, db, ext)] == [
        "person", "system", "container", "component", "database", "external",
    ]  # fmt: skip
    assert api.parent is shop and api.technology == "Go"
    assert auth.parent is api and db.parent is shop
    assert ext.parent is None
    explicit = Project("Shop")
    explicit.specification.use(C4)
    explicit_shop = explicit.model.element("system", "Shop", alias="shop")
    explicit_shop.element("container", "API", technology="Go")
    assert shop.children[0].kind == explicit_shop.children[0].kind


@pytest.mark.parametrize("kind", KINDS)
def test_undeclared_kind_fails_without_new_element(kind):
    project = Project()
    parent = project.model.element("anything", "Anything")

    for owner in (project.model, parent):
        with pytest.raises(ValueError, match=kind) as error:
            getattr(owner, kind)("X")
        assert "use(C4)" in str(error.value)
    assert project.model.elements == [parent]


def test_helper_works_with_hand_declared_kind():
    project = Project()
    project.specification.element("person")

    assert project.model.person("Customer").kind == "person"


def test_nesting_is_not_validated():
    project = Project()
    project.specification.use(C4)

    assert project.model.container("API").parent is None
    assert project.model.person("P").component("C").parent is not None


def test_project_starts_without_kinds_and_element_fails_at_validation():
    project = Project()

    assert project.specification.element_kinds == {}
    project.model.element("system", "Shop")
    with pytest.raises(LikeC4ValidationError, match="system"):
        project.render()


def test_explicit_cheatsheet_specification_equals_c4():
    explicit = Project("Shop")
    spec = explicit.specification
    spec.element("person", title="Person", shape="person", color="blue")
    spec.element("system", title="Software System", color="primary")
    spec.element("container", title="Container", color="secondary")
    spec.element(
        "component", title="Component", shape="component", color="muted"
    )
    spec.element(
        "database", title="Database", shape="storage", color="secondary"
    )
    spec.element(
        "external", title="External System", color="gray", border="dashed"
    )
    preset = Project("Shop")
    preset.specification.use(C4)

    assert _spec_block(explicit) == _spec_block(preset)
    assert preset.specification.element_kinds == spec.element_kinds


def test_converters_emit_explicit_kinds_and_do_not_import_presets():
    project = Project("Shop")
    project.specification.use(C4)
    project.model.system("Shop", alias="shop").container("API", alias="api")

    source = project_to_python_code(project)

    assert "model.element('system'" in source
    assert "model.element('container'" in source
    assert ".use(" not in source
    assert "C4" not in source
    for path in CONVERTERS_DIR.rglob("*.py"):
        text = path.read_text()
        assert "presets" not in text, path
        assert "use(" not in text, path


def test_preset_declares_relationship_kinds_and_rejects_duplicates():
    preset = C4.with_(
        relationships=[RelationshipKind("async", technology="AMQP")]
    )
    project = Project()
    project.specification.use(preset)

    assert list(project.specification.relationship_kinds) == ["async"]
    with pytest.raises(ValueError, match="async"):
        Project().specification.relationship("async").use(preset)

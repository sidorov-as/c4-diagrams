from __future__ import annotations

import pytest

from c4.contrib.structurizr import Rel, Workspace
from c4.contrib.structurizr.renderer import StructurizrRenderer


@pytest.fixture
def model():
    return Workspace("Shop").model


@pytest.fixture
def trio(model):
    return (
        model.Person("A", alias="a"),
        model.Person("B", alias="b"),
        model.SoftwareSystem("C", alias="c"),
    )


def pairs(model):
    return [
        (r.source.alias, r.destination.alias, r.description)
        for r in model.relationships
    ]


def test_rel_is_reusable(model, trio):
    a, b, c = trio
    d = model.SoftwareSystem("D", alias="d")
    rel = Rel("uses")

    a >> rel >> b
    c >> rel >> d

    assert pairs(model) == [("a", "b", "uses"), ("c", "d", "uses")]
    assert rel == Rel("uses")


def test_rel_second_positional_argument_is_rejected():
    with pytest.raises(TypeError):
        Rel("calls", "HTTPS")


def test_rel_has_no_label_alias():
    with pytest.raises(TypeError):
        Rel(label="calls")


def test_rel_keyword_options(model, trio):
    a, b, _ = trio

    result = a >> Rel("calls", technology="HTTPS") >> b

    assert result.description == "calls"
    assert result.technology == "HTTPS"


def test_reversed_form(model, trio):
    a, b, _ = trio

    result = b << Rel("uses") << a

    assert (result.source, result.destination) == (a, b)
    assert pairs(model) == [("a", "b", "uses")]


def test_string_forward_and_reversed_forms(model, trio):
    a, b, c = trio

    forward = a >> "Uses" >> b
    reversed_ = c << "Reads" << a

    assert (forward.source, forward.destination) == (a, b)
    assert forward.description == "Uses"
    assert (reversed_.source, reversed_.destination) == (a, c)
    assert reversed_.description == "Reads"
    assert pairs(model) == [("a", "b", "Uses"), ("a", "c", "Reads")]


def test_string_one_to_many_and_many_to_one_reversed(model, trio):
    a, b, c = trio

    first = a >> "x" >> [b, c]
    second = c << "y" << [a, b]

    assert isinstance(first, list)
    assert isinstance(second, list)
    assert pairs(model) == [
        ("a", "b", "x"),
        ("a", "c", "x"),
        ("a", "c", "y"),
        ("b", "c", "y"),
    ]


def test_string_cannot_follow_a_list_on_the_left(trio):
    a, b, c = trio

    with pytest.raises(TypeError):
        [a, b] >> "x" >> c


def test_string_form_renders_description():
    workspace = Workspace("Shop")
    a = workspace.model.Person("A", alias="a")
    b = workspace.model.SoftwareSystem("B", alias="b")
    a >> "Uses" >> b

    dsl = StructurizrRenderer().render(workspace)

    assert 'a -> b "Uses"' in dsl


def test_one_to_many_and_reversed(model, trio):
    a, b, c = trio

    first = a >> Rel("x") >> [b, c]
    second = [b, c] << Rel("y") << a

    assert isinstance(first, list)
    assert isinstance(second, list)
    assert pairs(model) == [
        ("a", "b", "x"),
        ("a", "c", "x"),
        ("a", "b", "y"),
        ("a", "c", "y"),
    ]


def test_many_to_one_and_reversed(model, trio):
    a, b, c = trio

    first = [a, b] >> Rel("x") >> c
    second = c << Rel("y") << [a, b]

    assert isinstance(first, list)
    assert isinstance(second, list)
    assert pairs(model) == [
        ("a", "c", "x"),
        ("b", "c", "x"),
        ("a", "c", "y"),
        ("b", "c", "y"),
    ]


@pytest.mark.parametrize("reverse", [False, True])
def test_many_to_many_is_rejected(model, trio, reverse):
    a, b, c = trio
    d = model.SoftwareSystem("D", alias="d")
    expected_error = "Either source or destination must be a single element"

    with pytest.raises(ValueError, match=expected_error):
        if reverse:
            [c, d] << Rel("x") << [a, b]
        else:
            [a, b] >> Rel("x") >> [c, d]

    assert not model.relationships


def test_mixed_operators_are_rejected(trio):
    a, b, _ = trio

    with pytest.raises(TypeError):
        a >> Rel("x") << b


def test_unlabeled_relationship_and_pipe(model, trio):
    a, b, c = trio

    plain = a >> b
    labeled = b << c | "reads"

    assert plain.description is None
    assert labeled.description == "reads"
    assert (labeled.source, labeled.destination) == (c, b)


@pytest.mark.parametrize("existing", ["x", ""])
def test_pipe_does_not_overwrite(model, trio, existing):
    a, b, _ = trio

    with pytest.raises(ValueError, match="already has the description"):
        a >> Rel(existing) >> b | "y"

    assert pairs(model) == [("a", "b", existing)]


def test_unlabeled_relationship_renders_without_description():
    workspace = Workspace("Shop")
    a = workspace.model.Person("A", alias="a")
    b = workspace.model.SoftwareSystem("B", alias="b")
    a >> b

    dsl = StructurizrRenderer().render(workspace)

    assert "a -> b {" in dsl or "a -> b\n" in dsl
    assert 'a -> b ""' not in dsl


def test_explicit_empty_description_is_rendered():
    workspace = Workspace("Shop")
    a = workspace.model.Person("A", alias="a")
    b = workspace.model.SoftwareSystem("B", alias="b")
    a >> Rel("") >> b

    dsl = StructurizrRenderer().render(workspace)

    assert 'a -> b ""' in dsl


def test_dynamic_step_from_unlabeled_relationship_has_no_description():
    workspace = Workspace("Shop")
    a = workspace.model.Person("A", alias="a")
    b = workspace.model.SoftwareSystem("B", alias="b")
    relationship = a >> b
    view = workspace.views.DynamicView(b, key="flow", steps=[relationship])

    dsl = StructurizrRenderer().render(workspace)

    assert view.steps[0].description is None
    assert 'a -> b ""' not in dsl
    assert "a -> b" in dsl


def test_dynamic_step_description_is_optional():
    workspace = Workspace("Shop")
    a = workspace.model.Person("A", alias="a")
    b = workspace.model.SoftwareSystem("B", alias="b")
    view = workspace.views.DynamicView(b, key="flow")
    view.step(a, b)

    dsl = StructurizrRenderer().render(workspace)

    assert view.steps[0].description is None
    assert "a -> b\n" in dsl

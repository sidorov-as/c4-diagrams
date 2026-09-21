from __future__ import annotations

import pytest

from c4.contrib.structurizr import Rel, Workspace
from c4.contrib.structurizr.renderer import StructurizrRenderOptions


@pytest.fixture
def workspace() -> Workspace:
    return Workspace("Shop")


def test_invalid_explicit_alias_is_rejected(workspace):
    with pytest.raises(ValueError, match="valid identifier"):
        workspace.model.Person("Customer", alias="not valid")


def test_duplicate_aliases_get_numeric_suffixes(workspace):
    first = workspace.model.Person("Customer", alias="user")
    second = workspace.model.Person("Other", alias="user")

    assert (first.alias, second.alias) == ("user", "user_2")


def test_relationship_expression_cannot_start_a_relationship(workspace):
    target = workspace.model.Person("Customer")

    with pytest.raises(TypeError):
        Rel("uses") >> target


def test_rshift_with_element_creates_empty_relationship(workspace):
    customer = workspace.model.Person("Customer")
    shop = workspace.model.SoftwareSystem("Shop")

    relationship = customer >> shop

    assert relationship.description is None
    assert relationship.source is customer


def test_rshift_with_unsupported_operand_is_not_implemented(workspace):
    customer = workspace.model.Person("Customer")

    with pytest.raises(TypeError):
        customer >> 42


def test_rshift_with_expression_leaves_it_unchanged(workspace):
    customer = workspace.model.Person("Customer")
    expression = Rel("uses")

    bound = customer >> expression

    assert bound.fixed == (customer,)
    assert expression == Rel("uses")


def test_element_repr_names_alias_and_name(workspace):
    customer = workspace.model.Person("Customer", alias="customer")

    assert repr(customer) == "Person(alias='customer', name='Customer')"


def test_ownership_context_mismatch_is_detected(workspace):
    customer = workspace.model.Person("Customer")

    with pytest.raises(RuntimeError, match="ownership context mismatch"):
        workspace.model._pop_owner(customer)


def test_owner_from_another_workspace_is_rejected(workspace):
    foreign = Workspace("Other").model.SoftwareSystem("Foreign")

    with pytest.raises(ValueError, match="Owner must belong"):
        workspace.model.Container("API", owner=foreign)


def test_instance_requires_a_deployment_node(workspace):
    system = workspace.model.SoftwareSystem("Shop")

    with pytest.raises(TypeError, match="require a deployment node"):
        workspace.model.SoftwareSystemInstance(system)


def test_element_style_accepts_an_element_instance(workspace):
    customer = workspace.model.Person("Customer")

    workspace.styles.element(customer, background="#ff0000")

    assert customer.style_properties


def test_dynamic_view_accepts_initial_relationships(workspace):
    customer = workspace.model.Person("Customer")
    shop = workspace.model.SoftwareSystem("Shop")
    relationship = customer.uses(shop, "buys")

    view = workspace.views.DynamicView(steps=[relationship])

    assert [step.description for step in view.steps] == ["buys"]
    assert view.steps[0].relationship is relationship


def test_dynamic_step_endpoints_must_belong_to_the_model(workspace):
    customer = workspace.model.Person("Customer")
    foreign = Workspace("Other").model.Person("Stranger")
    view = workspace.views.DynamicView()

    with pytest.raises(ValueError, match="must belong to this workspace"):
        view.step(customer, foreign, "calls")


def test_dynamic_step_rejects_relationship_and_create_flag(workspace):
    customer = workspace.model.Person("Customer")
    shop = workspace.model.SoftwareSystem("Shop")
    relationship = customer.uses(shop, "buys")
    view = workspace.views.DynamicView()

    with pytest.raises(ValueError, match="not both"):
        view.step(
            customer,
            shop,
            "buys",
            relationship=relationship,
            create_relationship=True,
        )


def test_views_support_indexing_and_length(workspace):
    view = workspace.views.SystemLandscapeView()

    assert len(workspace.views) == 1
    assert workspace.views[0] is view


def test_render_options_can_be_replaced(workspace):
    options = StructurizrRenderOptions()

    workspace.render_options = options

    assert workspace.render_options is options

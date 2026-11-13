from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from c4.contrib.likec4 import Project
from c4.contrib.likec4.converters.json import (
    LikeC4ProjectSchema,
    project_from_dict,
)
from c4.converters.exceptions import (
    ConversionError,
    DiagramJSONSchemaValidationError,
)
from c4.converters.json.converter import diagram_from_dict
from c4.enums import RendererEnum

EXAMPLES = Path(__file__).parents[4] / "docs" / "assets" / "examples"


def _base() -> dict[str, Any]:
    return {
        "backend": "likec4",
        "specification": {
            "elements": [{"name": "system"}, {"name": "service"}],
            "deployment_nodes": [{"name": "vm"}],
        },
        "model": {
            "elements": [
                {
                    "id": "shop",
                    "kind": "system",
                    "title": "Shop",
                    "elements": [
                        {"id": "api", "kind": "service", "title": "API"}
                    ],
                },
                {"id": "db", "kind": "service", "alias": "db"},
            ],
            "relationships": [{"from": "api", "to": "db", "title": "uses"}],
        },
        "deployment": {
            "nodes": [
                {
                    "id": "vm1",
                    "kind": "vm",
                    "title": "VM",
                    "instances": [{"id": "api1", "element": "api"}],
                },
                {"id": "vm2", "kind": "vm", "title": "Other VM"},
            ],
            "relationships": [{"from": "api1", "to": "vm2"}],
        },
        "views": {
            "items": [
                {
                    "type": "element",
                    "key": "index",
                    "rules": [
                        {"rule": "include", "items": [{"type": "wildcard"}]}
                    ],
                },
                {
                    "type": "dynamic",
                    "key": "flow",
                    "steps": [{"from": "api", "to": "db", "title": "go"}],
                },
            ]
        },
    }


def _mutate(path: str, value: Any) -> dict[str, Any]:
    """Return ``_base`` with the dotted ``path`` set to ``value``."""
    data = copy.deepcopy(_base())
    target: Any = data
    *parents, last = path.split(".")
    for part in parents:
        target = target[int(part)] if part.isdigit() else target[part]
    if last.isdigit():
        target[int(last)] = value
    else:
        target[last] = value
    return data


def test_base_document_is_valid_and_converts():
    project = LikeC4ProjectSchema.model_validate(_base()).to_project()

    assert isinstance(project, Project)
    assert [e.name for e in project.model.elements] == ["Shop", "API", "db"]
    assert "api1" not in project.render()  # ids are not DSL identifiers


def test_project_from_dict_returns_renderer():
    project, backend = project_from_dict(_base())

    assert backend is RendererEnum.LIKEC4
    assert project.render().startswith("specification")


def test_diagram_from_dict_dispatches_to_likec4():
    project, backend = diagram_from_dict(_base())

    assert isinstance(project, Project)
    assert backend is RendererEnum.LIKEC4


def test_unknown_field_is_rejected():
    data = _mutate("model.elements.0.colour", "red")

    with pytest.raises(ValidationError, match="colour"):
        LikeC4ProjectSchema.model_validate(data)


def test_backend_discriminator_is_required_and_exact():
    data = _base()
    data["backend"] = "structurizr"

    with pytest.raises(ValidationError):
        LikeC4ProjectSchema.model_validate(data)


def test_wrong_backend_is_not_handled_by_likec4_converter():
    data = _base()
    data["backend"] = "d2"

    with pytest.raises(DiagramJSONSchemaValidationError):
        diagram_from_dict(data)


def test_schema_error_is_wrapped_by_common_converter():
    data = _mutate("model.elements.0.colour", "red")

    with pytest.raises(DiagramJSONSchemaValidationError, match="colour"):
        diagram_from_dict(data)


@pytest.mark.parametrize(
    ("path", "value", "message"),
    [
        ("model.relationships.0.to", "ghost", "Unknown element id 'ghost'"),
        ("model.relationships.0.from", "vm1", "Unknown element id 'vm1'"),
        (
            "deployment.nodes.0.instances.0.element",
            "ghost",
            "Unknown element id 'ghost'",
        ),
        (
            "deployment.relationships.0.to",
            "db",
            "Unknown deployment node or instance id 'db'",
        ),
        ("views.items.1.steps.0.to", "ghost", "Unknown element id 'ghost'"),
        (
            "views.items.0.rules.0.items.0",
            {"type": "element", "id": "vm1"},
            "Unknown element id 'vm1'",
        ),
        (
            "views.items.0.rules.0",
            {
                "rule": "include",
                "items": [{"type": "wildcard"}],
                "navigate_to": "ghost",
            },
            "Unknown view key 'ghost'",
        ),
        (
            "views.items.0",
            {"type": "element", "key": "index", "of": "ghost"},
            "Unknown element id 'ghost'",
        ),
    ],
)
def test_unknown_references_name_the_id(path, value, message):
    with pytest.raises(ValidationError, match=message):
        LikeC4ProjectSchema.model_validate(_mutate(path, value))


def test_deployment_view_items_must_be_deployment_ids():
    data = _base()
    data["views"]["items"].append({
        "type": "deployment",
        "key": "prod",
        "rules": [
            {"rule": "include", "items": [{"type": "element", "id": "api"}]}
        ],
    })

    with pytest.raises(ValidationError, match="Unknown deployment node"):
        LikeC4ProjectSchema.model_validate(data)


def test_duplicate_ids_are_rejected():
    data = _mutate("model.elements.1.id", "shop")

    with pytest.raises(ValidationError, match="Duplicate element id: 'shop'"):
        LikeC4ProjectSchema.model_validate(data)


def test_model_and_deployment_ids_live_in_separate_namespaces():
    data = _mutate("deployment.nodes.0.id", "shop")
    data["deployment"]["relationships"][0]["from"] = "shop"

    LikeC4ProjectSchema.model_validate(data)


def test_duplicate_view_keys_are_rejected():
    data = _base()
    data["views"]["items"][1]["key"] = "index"

    with pytest.raises(ValidationError, match="Duplicate view key"):
        LikeC4ProjectSchema.model_validate(data)


def test_relationship_navigate_to_must_be_dynamic():
    data = _mutate("model.relationships.0.navigate_to", "index")

    with pytest.raises(ValidationError, match="must be a dynamic view"):
        LikeC4ProjectSchema.model_validate(data)


def test_step_navigate_to_must_be_dynamic():
    data = _mutate("views.items.1.steps.0.navigate_to", "index")

    with pytest.raises(ValidationError, match="must be a dynamic view"):
        LikeC4ProjectSchema.model_validate(data)


def test_dynamic_block_entries_are_rejected():
    data = _mutate(
        "views.items.1.steps.0",
        {"parallel": [{"from": "api", "to": "db"}]},
    )

    with pytest.raises(ValidationError):
        LikeC4ProjectSchema.model_validate(data)


def test_element_needs_title_or_alias():
    data = _mutate("model.elements.1", {"id": "db", "kind": "service"})

    with pytest.raises(ValidationError, match="title or alias"):
        LikeC4ProjectSchema.model_validate(data)


def test_element_icon_belongs_in_icon_field():
    data = _mutate("model.elements.1.style", {"icon": "tech:go"})

    with pytest.raises(ValidationError, match="use the icon field"):
        LikeC4ProjectSchema.model_validate(data)


@pytest.mark.parametrize(
    "item",
    [
        {"type": "where", "item": {"type": "wildcard"}},
        {"type": "rel", "source": {"type": "wildcard"}},
        {"type": "between", "source": {"type": "wildcard"}},
        {"type": "incoming"},
        {"type": "raw", "text": ""},
        {"type": "where", "item": {"type": "raw", "text": "x"}, "tag": "t"},
    ],
)
def test_invalid_predicates_are_rejected(item):
    data = _mutate("views.items.0.rules.0.items.0", item)

    with pytest.raises(ValidationError):
        LikeC4ProjectSchema.model_validate(data)


def test_invalid_view_key_in_render_options():
    data = _base()
    data["render_options"] = {"view_key": "ghost"}

    with pytest.raises(ValidationError, match="render_options->view_key"):
        LikeC4ProjectSchema.model_validate(data)


def test_render_options_view_key_reaches_the_project():
    data = _base()
    data["render_options"] = {"view_key": "flow"}

    assert LikeC4ProjectSchema.model_validate(data).to_project().view_key == (
        "flow"
    )


def test_authoring_errors_become_conversion_errors():
    data = _mutate("model.elements.0.style", {"shape": "triangle"})

    with pytest.raises(ConversionError, match="triangle"):
        diagram_from_dict(data)


def test_all_predicates_and_rules_convert():
    data = _base()
    data["model"]["elements"][0]["tags"] = ["hot"]
    data["specification"]["tags"] = [{"name": "hot"}]
    data["views"]["items"][0]["rules"] = [
        {
            "rule": "include",
            "items": [
                {"type": "wildcard"},
                {"type": "children", "of": "shop"},
                {"type": "descendants", "of": "shop"},
                {
                    "type": "where",
                    "item": {"type": "element", "id": "shop"},
                    "tag": "hot",
                    "kind": "system",
                },
                {
                    "type": "between",
                    "source": {"type": "element", "id": "api"},
                    "target": {"type": "element", "id": "db"},
                    "both": True,
                },
                {"type": "incoming", "item": {"type": "element", "id": "db"}},
                {"type": "outgoing", "item": {"type": "element", "id": "db"}},
                {"type": "inout", "item": {"type": "element", "id": "db"}},
                {"type": "raw", "text": "shop.** where tag is #hot"},
            ],
            "navigate_to": "flow",
        },
        {"rule": "exclude", "items": [{"type": "element", "id": "db"}]},
        {
            "rule": "style",
            "targets": [{"type": "element", "id": "shop"}],
            "properties": {"opacity": 40, "multiple": True},
        },
        {"rule": "auto_layout", "direction": "BottomTop", "rank_sep": 10},
    ]

    dsl = LikeC4ProjectSchema.model_validate(data).to_project().render()

    assert "include *, Shop.*, Shop.** with { navigateTo flow }" in dsl
    assert "include Shop where tag is #hot and kind is system" in dsl
    assert "include Shop.API <-> db with" in dsl
    assert "include -> db with" in dsl
    assert "include db -> with" in dsl
    assert "include -> db -> with" in dsl
    assert "include shop.** where tag is #hot with" in dsl
    assert "autoLayout BottomTop 10" in dsl
    assert "opacity 40%" in dsl


@pytest.mark.parametrize("name", ["minimal", "advanced"])
def test_committed_json_examples_render_the_committed_dsl(name):
    schema = LikeC4ProjectSchema.model_validate_json(
        (EXAMPLES / f"json/likec4/project.{name}.json").read_text("utf-8")
    )

    assert schema.to_project().render() == (
        EXAMPLES / f"likec4/project.{name}.c4"
    ).read_text("utf-8")


def test_examples_serialize_back_to_the_same_document():
    path = EXAMPLES / "json/likec4/project.advanced.json"
    data = json.loads(path.read_text("utf-8"))

    schema = LikeC4ProjectSchema.model_validate(data)

    assert schema.model_dump(by_alias=True, exclude_none=True)["backend"] == (
        "likec4"
    )

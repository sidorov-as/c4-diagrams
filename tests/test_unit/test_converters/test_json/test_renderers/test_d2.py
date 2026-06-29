import pytest
from pydantic import TypeAdapter, ValidationError

from c4.contrib.d2.converters.json.render_options import (
    D2LegendElementSchema,
    D2LegendRelSchema,
    D2LegendSchema,
    D2RenderOptionsSchema,
    D2StyleSchema,
)
from c4.contrib.d2.converters.json.schemas import (
    D2ElementFields,
    D2RelationshipType,
)
from c4.diagrams.core import RelationshipType
from c4.renderers.d2.options import (
    D2Legend,
    D2LegendElement,
    D2LegendRel,
    D2RenderOptions,
)


def test_d2_relationship_type__json_schema_uses_portable_title():
    schema = TypeAdapter(D2RelationshipType).json_schema()

    assert schema["title"] == "RelationshipType"


def test_d2_relationship_type__get_descriptions():
    descriptions = D2RelationshipType.get_descriptions()
    core_descriptions = RelationshipType.get_descriptions()

    assert descriptions == {
        D2RelationshipType.REL: core_descriptions[RelationshipType.REL],
        D2RelationshipType.BI_REL: core_descriptions[RelationshipType.BI_REL],
    }


def test_d2_element_fields__merges_convenience_fields_with_extensions():
    class BaseElementFields:
        def _to_diagram_element_kwargs(self):
            return {
                "shape": "cloud",
                "style": D2StyleSchema(fill="#eef", stroke=None),
                "d2": {"tooltip": "kwarg tooltip", "near": "top-center"},
                "extensions": {
                    "d2": {"shape": "rectangle", "icon": "old.svg"},
                    "plantuml": {"sprite": "server"},
                },
            }

    class ElementFields(D2ElementFields, BaseElementFields): ...

    result = ElementFields()._to_diagram_element_kwargs()

    assert result == {
        "d2": {
            "shape": "cloud",
            "icon": "old.svg",
            "tooltip": "kwarg tooltip",
            "near": "top-center",
            "style": {"fill": "#eef"},
        },
        "extensions": {"plantuml": {"sprite": "server"}},
    }


def test_d2_element_fields__removes_extensions_when_d2_is_consumed():
    class BaseElementFields:
        def _to_diagram_element_kwargs(self):
            return {
                "shape": "cloud",
                "extensions": {"d2": {"shape": "rectangle"}},
            }

    class ElementFields(D2ElementFields, BaseElementFields): ...

    result = ElementFields()._to_diagram_element_kwargs()

    assert result == {"d2": {"shape": "cloud"}}


def test_d2_extensions_mixin__converts_style_dict_and_passes_other_values():
    assert D2ElementFields._to_d2_style({"fill": "#eef", "stroke": None}) == {
        "fill": "#eef"
    }
    assert D2ElementFields._to_d2_style("style-token") == "style-token"


def test_d2_render_options_schema__to_render_options():
    schema = D2RenderOptionsSchema(
        direction="down",
        layout="elk",
        theme=3,
        title_near="bottom-center",
        sequence_diagram=True,
        auto_number_relationships=True,
        include_type_label=False,
        include_technology=False,
        include_properties=True,
        bidirectional_relationships="single_edge",
        fully_qualified_relationships=False,
        legend=D2LegendSchema(
            label="Map key",
            items=[
                D2LegendElementSchema(
                    type="element",
                    label="Service",
                    alias="service",
                    shape="rectangle",
                    style=D2StyleSchema(fill="#eef"),
                    classes=["internal"],
                ),
                D2LegendRelSchema(
                    type="relationship",
                    label="Async",
                    alias="async_rel",
                    bidirectional=True,
                    hide_endpoints=True,
                    style=D2StyleSchema(stroke_dash=4),
                ),
            ],
        ),
    )

    result = schema.to_render_options()

    assert result == D2RenderOptions(
        direction="down",
        layout="elk",
        theme=3,
        title_near="bottom-center",
        sequence_diagram=True,
        auto_number_relationships=True,
        include_type_label=False,
        include_technology=False,
        include_properties=True,
        bidirectional_relationships="single_edge",
        fully_qualified_relationships=False,
        legend=D2Legend(
            label="Map key",
            items=[
                D2LegendElement(
                    label="Service",
                    alias="service",
                    shape="rectangle",
                    style={"fill": "#eef"},
                    classes=["internal"],
                ),
                D2LegendRel(
                    label="Async",
                    alias="async_rel",
                    bidirectional=True,
                    hide_endpoints=True,
                    style={"stroke_dash": 4},
                ),
            ],
        ),
    )


def test_d2_render_options_schema__to_render_options_empty():
    schema = D2RenderOptionsSchema()

    result = schema.to_render_options()

    assert result == D2RenderOptions()


def test_d2_render_options_schema__rejects_invalid_direction():
    with pytest.raises(ValidationError, match="Input should be"):
        D2RenderOptionsSchema(direction="diagonal")


def test_d2_render_options_schema__rejects_invalid_layout():
    with pytest.raises(ValidationError, match="Input should be"):
        D2RenderOptionsSchema(layout="tala")


def test_d2_render_options_schema__rejects_invalid_title_near():
    with pytest.raises(ValidationError, match="Input should be"):
        D2RenderOptionsSchema(title_near="center")


def test_d2_render_options_schema__rejects_invalid_option_types():
    with pytest.raises(ValidationError, match="theme"):
        D2RenderOptionsSchema(theme="dark")

    with pytest.raises(ValidationError, match="sequence_diagram"):
        D2RenderOptionsSchema(sequence_diagram=["yes"])

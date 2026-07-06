from pydantic import TypeAdapter

from c4 import Person, SystemContextDiagram
from c4.contrib.mermaid import RelBack
from c4.contrib.mermaid.converters.json.render_options import (
    MermaidElementStyleSchema,
    MermaidRelStyleSchema,
    MermaidRenderOptionsSchema,
    UpdateLayoutConfigSchema,
)
from c4.contrib.mermaid.converters.json.schemas import (
    MermaidBoundaryFields,
    MermaidBoundarySchema,
    MermaidRelationshipSchema,
    MermaidRelationshipType,
)
from c4.diagrams.core import RelationshipType
from c4.renderers import MermaidRenderOptions
from c4.renderers.mermaid.options import (
    ElementStyle,
    RelStyle,
    UpdateLayoutConfig,
)


def test_mermaid_relationship_type__json_schema_uses_portable_title():
    schema = TypeAdapter(MermaidRelationshipType).json_schema()

    assert schema["title"] == "RelationshipType"


def test_mermaid_relationship_type__get_descriptions():
    descriptions = MermaidRelationshipType.get_descriptions()
    core_descriptions = RelationshipType.get_descriptions()

    assert (
        descriptions[MermaidRelationshipType.REL]
        == core_descriptions[RelationshipType.REL]
    )
    assert (
        descriptions[MermaidRelationshipType.REL_BACK]
        == (core_descriptions[RelationshipType.REL_BACK])
    )


def test_mermaid_render_options_schema__to_render_options():
    schema = MermaidRenderOptionsSchema(
        update_layout_config=UpdateLayoutConfigSchema(
            c4_shape_in_row=2,
            c4_boundary_in_row=4,
        ),
        styles=[
            MermaidElementStyleSchema(
                type="ElementStyle",
                element="customer",
                bg_color="#e8f5e9",
                border_color="#66bb6a",
                font_color="#1b5e20",
            ),
            MermaidRelStyleSchema(
                type="RelStyle",
                from_element="customer",
                to_element="retail_platform",
                text_color="#e8f5e9",
                line_color="#66bb6a",
                offset_x=10,
                offset_y=20,
            ),
        ],
    )
    expected_result = MermaidRenderOptions(
        update_layout_config=UpdateLayoutConfig(
            c4_shape_in_row=2,
            c4_boundary_in_row=4,
        ),
        styles=[
            ElementStyle(
                element="customer",
                bg_color="#e8f5e9",
                font_color="#1b5e20",
                border_color="#66bb6a",
            ),
            RelStyle(
                from_element="customer",
                to_element="retail_platform",
                text_color="#e8f5e9",
                line_color="#66bb6a",
                offset_x=10,
                offset_y=20,
            ),
        ],
    )

    result = schema.to_render_options()

    assert result == expected_result


def test_mermaid_render_options_schema__to_render_options_empty():
    schema = MermaidRenderOptionsSchema()
    expected_result = MermaidRenderOptions(
        update_layout_config=None,
        styles=[],
    )

    result = schema.to_render_options()

    assert result == expected_result


def test_mermaid_relationship_schema__supports_mermaid_relationship_types():
    schema = MermaidRelationshipSchema(
        type="REL_BACK",
        from_="database",
        to="backend",
        label="Reads from and writes to",
    )

    with SystemContextDiagram():
        database = Person("Database")
        backend = Person("Backend")
        result = schema.to_diagram_element(
            from_element=database,
            to_element=backend,
        )

    assert isinstance(result, RelBack)
    assert result.relationship_type == RelationshipType.REL_BACK


def test_mermaid_relationship_schema__documents_concrete_endpoint_constraint():
    schema = MermaidRelationshipSchema.model_json_schema()

    assert "not a boundary" in schema["properties"]["from"]["description"]
    assert "not a boundary" in schema["properties"]["to"]["description"]


def test_mermaid_boundary_schema__moves_stereotype_to_extensions():
    schema = MermaidBoundarySchema(
        type="Boundary",
        label="Commerce Platform",
        alias="commerce_platform",
        stereotype="enterprise",
    )

    with SystemContextDiagram():
        result = schema.to_diagram_element()

    assert result.extensions == {"mermaid": {"type": "enterprise"}}


def test_mermaid_boundary_schema__keeps_extensions_empty_without_stereotype():
    schema = MermaidBoundarySchema(
        type="Boundary",
        label="Commerce Platform",
        alias="commerce_platform",
    )

    with SystemContextDiagram():
        result = schema.to_diagram_element()

    assert result.extensions is None


def test_mermaid_boundary_fields__merges_stereotype_with_extensions():
    class BaseBoundaryFields:
        def _to_diagram_element_kwargs(self):
            return {
                "stereotype": "enterprise",
                "extensions": {
                    "mermaid": {"icon": "cloud"},
                    "plantuml": {"sprite": "server"},
                },
            }

    class BoundaryFields(MermaidBoundaryFields, BaseBoundaryFields): ...

    result = BoundaryFields()._to_diagram_element_kwargs()

    assert result == {
        "mermaid": {"icon": "cloud", "type": "enterprise"},
        "extensions": {"plantuml": {"sprite": "server"}},
    }

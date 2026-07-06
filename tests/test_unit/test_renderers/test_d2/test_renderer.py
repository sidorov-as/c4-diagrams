from pathlib import Path
from typing import Any

import pytest

from c4 import (
    Component,
    ComponentDb,
    ComponentDbExt,
    ComponentDiagram,
    ComponentExt,
    ComponentQueue,
    ComponentQueueExt,
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDbExt,
    ContainerDiagram,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
    DeploymentDiagram,
    DeploymentNode,
    DiagramFormat,
    DynamicDiagram,
    EnterpriseBoundary,
    Node,
    Person,
    PersonExt,
    Rel,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemQueue,
    SystemQueueExt,
)
from c4.contrib.c4_macros import BiRel, NodeLeft, NodeRight, RelDown
from c4.contrib.plantuml import (
    DeploymentNodeLeft,
    DeploymentNodeRight,
    Index,
    LastIndex,
    LayDown,
    increment,
    set_index,
)
from c4.diagrams.core import DiagramElementProperties, Element
from c4.enums import STRICT
from c4.exceptions import D2BackendConfigurationError
from c4.renderers.d2 import (
    BaseD2Backend,
    D2Legend,
    D2LegendElement,
    D2LegendRel,
    D2Renderer,
    D2RenderOptions,
    D2UnresolvedRelationshipEndpointError,
    D2UnsupportedDeclarationError,
    validate_d2_diagram,
)
from c4.renderers.d2.formatting import D2StringBuilder
from c4.renderers.d2.identifiers import D2Identifier

_C4_PERSON_CLASS = [
    "classes: {",
    "  c4_person: {",
    '    style.fill: "#f5f1ff"',
    '    style.stroke: "#6f4bb2"',
    '    style.font-color: "#211436"',
    "  }",
    "}",
]


class DummyD2Backend(BaseD2Backend):
    def __init__(self, content: bytes = b"rendered"):
        self.content = content
        self.bytes_calls: list[tuple[str, Any]] = []
        self.file_calls: list[tuple[str, Path, DiagramFormat, bool]] = []

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.PNG,  # noqa: A002
        render_options: D2RenderOptions | None = None,
    ) -> bytes:
        self.bytes_calls.append((diagram, format, render_options))
        return self.content

    def to_file(
        self,
        diagram: str,
        output_path: str | Path,
        *,
        format: DiagramFormat | None = DiagramFormat.PNG,  # noqa: A002
        overwrite: bool = True,
        render_options: D2RenderOptions | None = None,
    ) -> Path:
        output_path = Path(output_path)
        self.file_calls.append((diagram, output_path, format, overwrite))
        output_path.write_bytes(self.content)
        return output_path


def test_renderer_renders_basic_diagram():
    with SystemContextDiagram() as diagram:
        customer = Person("Customer", alias="customer")
        banking = System("Internet Banking", alias="internet_banking")

        customer >> "Uses" >> banking

    result = D2Renderer().render(diagram)

    assert result == "\n".join([
        "direction: right",
        *_C4_PERSON_CLASS,
        "customer: {",
        '  label: "Customer"',
        "  shape: c4-person",
        '  class: ["c4_person"]',
        "}",
        'internet_banking: "Internet Banking"',
        'customer -> internet_banking: "Uses"',
        "",
    ])


def test_renderer_renders_diagram_title():
    with SystemContextDiagram(title="Widgets Context") as diagram:
        System("Widgets", alias="widgets")

    result = D2Renderer().render(diagram)

    assert result == "\n".join([
        "direction: right",
        "__title: ||md",
        "  # Widgets Context",
        "|| {",
        "  near: top-center",
        "}",
        'widgets: "Widgets"',
        "",
    ])


def test_renderer_renders_diagram_title_without_near():
    with SystemContextDiagram(title="Widgets Context") as diagram:
        System("Widgets", alias="widgets")

    result = D2Renderer(
        render_options=D2RenderOptions(title_near=None),
    ).render(diagram)

    assert result == "\n".join([
        "direction: right",
        "__title: ||md",
        "  # Widgets Context",
        "||",
        'widgets: "Widgets"',
        "",
    ])


def test_renderer_renders_diagram_title_with_non_default_near():
    with SystemContextDiagram(title="Widgets Context") as diagram:
        System("Widgets", alias="widgets")

    result = D2Renderer(
        render_options=D2RenderOptions(title_near="bottom-right"),
    ).render(diagram)

    assert "near: bottom-right" in result
    assert "near: top-center" not in result


def test_renderer_renders_diagram_title_markdown_text():
    with SystemContextDiagram(title="SLA | Cost *Review*") as diagram:
        System("Widgets", alias="widgets")

    result = D2Renderer().render(diagram)

    assert "__title: ||md" in result
    assert "  # SLA | Cost *Review*" in result
    assert "\ntitle:" not in result


def test_renderer_emits_enabled_options():
    with SystemContextDiagram() as diagram:
        Person("Customer", alias="customer")

    renderer = D2Renderer(
        render_options=D2RenderOptions(
            direction="down",
            theme=101,
        ),
    )

    result = renderer.render(diagram)

    assert result == "\n".join([
        "direction: down",
        "theme: 101",
        *_C4_PERSON_CLASS,
        "customer: {",
        '  label: "Customer"',
        "  shape: c4-person",
        '  class: ["c4_person"]',
        "}",
        "",
    ])


def test_renderer_renders_dynamic_diagram_as_sequence_diagram():
    with DynamicDiagram() as diagram:
        browser = Person("Browser", alias="browser")
        api = System("API", alias="api")

        browser >> "Requests data" >> api

    renderer = D2Renderer(
        render_options=D2RenderOptions(sequence_diagram=True),
    )

    result = renderer.render(diagram)

    assert result == "\n".join([
        "direction: right",
        "shape: sequence_diagram",
        *_C4_PERSON_CLASS,
        "browser: {",
        '  label: "Browser"',
        "  shape: c4-person",
        '  class: ["c4_person"]',
        "}",
        'api: "API"',
        'browser -> api: "Requests data"',
        "",
    ])


def test_renderer_does_not_render_non_dynamic_diagram_as_sequence_diagram():
    with SystemContextDiagram() as diagram:
        System("API", alias="api")

    renderer = D2Renderer(
        render_options=D2RenderOptions(sequence_diagram=True),
    )

    result = renderer.render(diagram)

    assert result == "\n".join([
        "direction: right",
        'api: "API"',
        "",
    ])


def test_renderer_uses_diagram_render_options():
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    diagram.set_render_options(d2=D2RenderOptions(direction="down"))

    result = D2Renderer().render(diagram)

    assert result == "\n".join([
        "direction: down",
        'system: "System"',
        "",
    ])


def test_renderer_auto_numbers_relationships():
    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        browser = System("Browser", alias="browser")
        api = System("API", alias="api")

        user >> "Submits form" >> browser
        browser >> "POST /orders" >> api

    renderer = D2Renderer(
        render_options=D2RenderOptions(auto_number_relationships=True),
    )

    result = renderer.render(diagram)

    assert result == "\n".join([
        "direction: right",
        *_C4_PERSON_CLASS,
        "user: {",
        '  label: "User"',
        "  shape: c4-person",
        '  class: ["c4_person"]',
        "}",
        'browser: "Browser"',
        'api: "API"',
        'user -> browser: "1. Submits form"',
        'browser -> api: "2. POST /orders"',
        "",
    ])


def test_renderer_auto_numbers_unlabeled_relationship():
    with DynamicDiagram() as diagram:
        browser = System("Browser", alias="browser")
        api = System("API", alias="api")

        browser.uses(api, "")

    renderer = D2Renderer(
        render_options=D2RenderOptions(auto_number_relationships=True),
    )

    result = renderer.render(diagram)

    assert 'browser -> api: "1."' in result


def test_renderer_omits_disabled_options():
    with SystemContextDiagram() as diagram:
        Person("Customer", alias="customer")

    renderer = D2Renderer(render_options=D2RenderOptions(direction=None))

    result = renderer.render(diagram)

    assert result == "\n".join([
        *_C4_PERSON_CLASS,
        "customer: {",
        '  label: "Customer"',
        "  shape: c4-person",
        '  class: ["c4_person"]',
        "}",
        "",
    ])


def test_renderer_renders_legend_before_classes():
    with SystemContextDiagram() as diagram:
        Person("Customer", alias="customer")

    renderer = D2Renderer(
        render_options=D2RenderOptions(
            legend=D2Legend(
                label="Diagram Key",
                items=[
                    D2LegendElement(
                        label="Banking",
                        style={"fill": "#FFE4E1"},
                    ),
                    D2LegendRel(
                        label="Alerting",
                        style={"stroke_dash": 5, "stroke": "#2E8B57"},
                    ),
                    D2LegendRel(
                        label="Authentication",
                        style={"stroke_width": 2, "stroke": "#800080"},
                    ),
                ],
            ),
        ),
    )

    result = renderer.render(diagram)

    assert result == "\n".join([
        "direction: right",
        "vars: {",
        '  d2-legend: "Diagram Key" {',
        "    legend_1: {",
        '      label: "Banking"',
        '      style.fill: "#FFE4E1"',
        "    }",
        "    legend_2_source -> legend_2_target: {",
        '      label: "Alerting"',
        "      style.stroke-dash: 5",
        '      style.stroke: "#2E8B57"',
        "    }",
        "    legend_3_source -> legend_3_target: {",
        '      label: "Authentication"',
        "      style.stroke-width: 2",
        '      style.stroke: "#800080"',
        "    }",
        "    legend_2_source.style.opacity: 0",
        "    legend_2_target.style.opacity: 0",
        "    legend_3_source.style.opacity: 0",
        "    legend_3_target.style.opacity: 0",
        "  }",
        "}",
        *_C4_PERSON_CLASS,
        "customer: {",
        '  label: "Customer"',
        "  shape: c4-person",
        '  class: ["c4_person"]',
        "}",
        "",
    ])


def test_renderer_renders_legend_explicit_aliases_and_endpoints():
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    renderer = D2Renderer(
        render_options=D2RenderOptions(
            legend=D2Legend(
                items=[
                    D2LegendElement(
                        label="System",
                        alias="sample_system",
                        shape="rectangle",
                        icon="https://example.com/system.svg",
                        classes=["sample"],
                    ),
                    D2LegendRel(
                        label="Calls",
                        alias="calls",
                        source="sample_system",
                        target="external_system",
                        classes=["relationship"],
                    ),
                ],
            ),
        ),
    )

    result = renderer.render(diagram)

    assert "sample_system: {" in result
    assert "shape: rectangle" in result
    assert 'icon: "https://example.com/system.svg"' in result
    assert 'class: ["sample"]' in result
    assert "sample_system -> external_system: {" in result
    assert 'class: ["relationship"]' in result
    assert "sample_system.style.opacity: 0" not in result
    assert "external_system.style.opacity: 0" not in result


def test_renderer_renders_bidirectional_legend_relationship():
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    renderer = D2Renderer(
        render_options=D2RenderOptions(
            legend=D2Legend(
                items=[
                    D2LegendRel(
                        label="Sync",
                        bidirectional=True,
                        style={"stroke_width": 2},
                    ),
                ],
            ),
        ),
    )

    result = renderer.render(diagram)

    assert "legend_1_source <-> legend_1_target: {" in result
    assert 'label: "Sync"' in result
    assert "style.stroke-width: 2" in result
    assert "legend_1_source.style.opacity: 0" in result
    assert "legend_1_target.style.opacity: 0" in result


def test_renderer_hides_shared_legend_endpoints_once():
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    renderer = D2Renderer(
        render_options=D2RenderOptions(
            legend=D2Legend(
                items=[
                    D2LegendRel(
                        label="Calls",
                        source="source",
                        target="target",
                        hide_endpoints=True,
                    ),
                    D2LegendRel(
                        label="Publishes",
                        source="source",
                        target="target",
                        hide_endpoints=True,
                    ),
                ],
            ),
        ),
    )

    result = renderer.render(diagram)

    assert result.count("source.style.opacity: 0") == 1
    assert result.count("target.style.opacity: 0") == 1


def test_renderer_includes_technology_in_labels_by_default():
    with SystemContextDiagram() as diagram:
        system = System("API", alias="api")
        system.technology = "Python"

    result = D2Renderer().render(diagram)

    assert 'api: "API\\n[Python]"' in result


def test_renderer_can_omit_technology_from_labels():
    with SystemContextDiagram() as diagram:
        system = System("API", alias="api")
        system.technology = "Python"

    renderer = D2Renderer(
        render_options=D2RenderOptions(include_technology=False),
    )

    result = renderer.render(diagram)

    assert 'api: "API"' in result
    assert "Python" not in result


def test_renderer_renders_element_properties_as_markdown_label():
    with SystemContextDiagram() as diagram:
        System("API", alias="api").with_properties(
            ("Owner", "Platform"),
            ("SLO", "99.9%"),
        )

    result = D2Renderer(
        render_options=D2RenderOptions(include_properties=True),
    ).render(diagram)

    assert "__properties" not in result
    assert result == "\n".join([
        "direction: right",
        "api: ||md",
        "  ## API",
        "",
        "  [Software System]",
        "",
        "  | Property | Value |",
        "  | --- | --- |",
        "  | Owner | Platform |",
        "  | SLO | 99.9% |",
        "|| {",
        "  shape: rectangle",
        "}",
        "",
    ])


def test_renderer_element_markdown_includes_expected_label_parts():
    with ContainerDiagram() as diagram:
        Container(
            "Banking API",
            description="Exposes banking capabilities.",
            technology="Kotlin / Spring Boot",
            alias="api",
        ).with_properties("Owner", "Platform Team")

    result = D2Renderer(
        render_options=D2RenderOptions(include_properties=True),
    ).render(diagram)

    assert result == "\n".join([
        "direction: right",
        "api: ||md",
        "  ## Banking API",
        "",
        "  [Container: Kotlin / Spring Boot]",
        "",
        "  Exposes banking capabilities.",
        "",
        "  | Property | Value |",
        "  | --- | --- |",
        "  | Owner | Platform Team |",
        "|| {",
        "  shape: rectangle",
        "}",
        "",
    ])


def test_renderer_can_omit_type_label_from_markdown_label():
    with ContainerDiagram() as diagram:
        Container(
            "Banking API",
            description="Exposes banking capabilities.",
            technology="Kotlin / Spring Boot",
            alias="api",
        )

    result = D2Renderer(
        render_options=D2RenderOptions(include_type_label=False),
    ).render(diagram)

    assert result == "\n".join([
        "direction: right",
        "api: ||md",
        "  ## Banking API",
        "",
        "  [Kotlin / Spring Boot]",
        "",
        "  Exposes banking capabilities.",
        "|| {",
        "  shape: rectangle",
        "}",
        "",
    ])


def test_renderer_can_omit_type_label_and_technology_from_markdown_label():
    with ContainerDiagram() as diagram:
        Container(
            "Banking API",
            description="Exposes banking capabilities.",
            technology="Kotlin / Spring Boot",
            alias="api",
        )

    result = D2Renderer(
        render_options=D2RenderOptions(
            include_type_label=False,
            include_technology=False,
        ),
    ).render(diagram)

    assert result == "\n".join([
        "direction: right",
        "api: ||md",
        "  ## Banking API",
        "",
        "  Exposes banking capabilities.",
        "|| {",
        "  shape: rectangle",
        "}",
        "",
    ])


def test_renderer_markdown_label_keeps_explicit_shape_override():
    with SystemContextDiagram() as diagram:
        System(
            "API",
            description="Handles requests.",
            alias="api",
            d2={"shape": "hexagon"},
        )

    result = D2Renderer().render(diagram)

    assert "api: ||md" in result
    assert "shape: hexagon" in result
    assert "shape: rectangle" not in result


def test_renderer_boundary_markdown_label_forces_rectangle_shape():
    with SystemContextDiagram() as diagram:
        with EnterpriseBoundary(
            "Acme Retail",
            alias="acme",
            description="Systems owned by Acme Retail.",
        ):
            System("Retail Platform", alias="retail_platform")

    result = D2Renderer().render(diagram)

    assert "acme: {" in result
    assert "  label: ||md" in result
    assert "  shape: rectangle" in result


def test_renderer_boundary_markdown_label_keeps_explicit_shape_override():
    with SystemContextDiagram() as diagram:
        with EnterpriseBoundary(
            "Acme Retail",
            alias="acme",
            description="Systems owned by Acme Retail.",
            d2={"shape": "cloud"},
        ):
            System("Retail Platform", alias="retail_platform")

    result = D2Renderer().render(diagram)

    assert "acme: {" in result
    assert "  shape: cloud" in result
    assert "  shape: rectangle" not in result


def test_renderer_omits_property_table_by_default():
    with SystemContextDiagram() as diagram:
        System("API", alias="api").with_properties("Owner", "Platform")

    result = D2Renderer().render(diagram)

    assert "__properties" not in result
    assert "Owner | Platform" not in result
    assert result == "\n".join([
        "direction: right",
        'api: "API"',
        "",
    ])


def test_renderer_renders_property_table_without_header():
    with SystemContextDiagram() as diagram:
        System("API", alias="api").with_properties(
            "Owner",
            "Platform",
            show_header=False,
        )

    result = D2Renderer(
        render_options=D2RenderOptions(include_properties=True),
    ).render(diagram)

    assert "|  |  |" in result
    assert "| --- | --- |" in result
    assert "| Owner | Platform |" in result
    assert "Property | Value" not in result


def test_renderer_renders_property_table_with_custom_header():
    with SystemContextDiagram() as diagram:
        System("API", alias="api").with_properties(
            "Platform",
            "Core Banking",
            header=("Team", "Domain"),
        )

    result = D2Renderer(
        render_options=D2RenderOptions(include_properties=True),
    ).render(diagram)

    assert "| Team | Domain |" in result
    assert "| --- | --- |" in result
    assert "| Platform | Core Banking |" in result


def test_renderer_escapes_markdown_property_table_cells():
    with SystemContextDiagram() as diagram:
        System("API", alias="api").with_properties(
            "Notes",
            "Reads | writes\naccounts",
        )

    result = D2Renderer(
        render_options=D2RenderOptions(include_properties=True),
    ).render(diagram)

    assert "| Notes | Reads \\| writes<br>accounts |" in result


def test_renderer_renders_relationship_properties_as_markdown_label():
    with SystemContextDiagram() as diagram:
        source = System("Web", alias="web")
        target = System("API", alias="api")
        source.uses(
            target,
            "Calls API",
            description="Sends authenticated requests.",
        ).with_properties("Auth", "OAuth2")

    result = D2Renderer(
        render_options=D2RenderOptions(include_properties=True),
    ).render(diagram)

    assert "__properties" not in result
    assert "web -> api: ||md" in result
    assert "  **Calls API**" in result
    assert "  Sends authenticated requests." in result
    assert "  | Property | Value |" in result
    assert "  | Auth | OAuth2 |" in result


def test_renderer_auto_numbers_unlabeled_markdown_relationship():
    with SystemContextDiagram() as diagram:
        source = System("Web", alias="web")
        target = System("API", alias="api")
        source.uses(
            target,
            "",
            description="Sends authenticated requests.",
        )

    result = D2Renderer(
        render_options=D2RenderOptions(auto_number_relationships=True),
    ).render(diagram)

    assert "web -> api: ||md" in result
    assert "  **1.**" in result
    assert "  Sends authenticated requests." in result


def test_renderer_relationship_markdown_label_can_render_description_only():
    with SystemContextDiagram() as diagram:
        source = System("Web", alias="web")
        target = System("API", alias="api")
        source.uses(
            target,
            "",
            description="Sends authenticated requests.",
        )

    result = D2Renderer().render(diagram)

    assert "web -> api: ||md" in result
    assert "  Sends authenticated requests." in result
    assert "**" not in result


def test_renderer_relationship_markdown_label_can_render_properties_only():
    with SystemContextDiagram() as diagram:
        source = System("Web", alias="web")
        target = System("API", alias="api")
        source.uses(target, "").with_properties("Auth", "OAuth2")

    result = D2Renderer(
        render_options=D2RenderOptions(include_properties=True),
    ).render(diagram)

    assert "web -> api: ||md" in result
    assert "  | Property | Value |" in result
    assert "  | Auth | OAuth2 |" in result


def test_renderer_element_type_label_falls_back_to_class_name():
    class CustomElement(Element): ...

    with SystemContextDiagram():
        element = CustomElement("Custom", alias="custom")

    result = D2Renderer()._element_type_label(element)

    assert result == "CustomElement"


def test_renderer_format_property_table_without_header_or_rows():
    properties = DiagramElementProperties(show_header=False)

    result = D2Renderer()._format_property_table(properties)

    assert result == ""


def test_renderer_renders_relationship_markdown_label_with_edge_attributes():
    with SystemContextDiagram() as diagram:
        source = System("Web", alias="web")
        target = System("API", alias="api")
        source.uses(
            target,
            "Calls API",
            d2={"style": {"animated": True}},
        ).with_properties("Auth", "OAuth2")

    result = D2Renderer(
        render_options=D2RenderOptions(include_properties=True),
    ).render(diagram)

    assert "web -> api: {" in result
    assert "  label: ||md" in result
    assert "    **Calls API**" in result
    assert "    | Auth | OAuth2 |" in result
    assert "  style.animated: true" in result


def test_renderer_renders_d2_extension_values_and_skips_none():
    with SystemContextDiagram() as diagram:
        System(
            "API",
            alias="api",
            d2={
                "shape": "hexagon",
                "tooltip": None,
                "style": {
                    "opacity": 0.5,
                    "animated": True,
                    "stroke_width": 2,
                    "fill": None,
                },
                "classes": ["service", "critical"],
            },
        )

    result = D2Renderer().render(diagram)

    assert "shape: hexagon" in result
    assert "style.opacity: 0.5" in result
    assert "style.animated: true" in result
    assert "style.stroke-width: 2" in result
    assert 'class: ["service"; "critical"]' in result
    assert "tooltip" not in result
    assert "style.fill" not in result


def test_renderer_ignores_non_mapping_d2_extension():
    with SystemContextDiagram() as diagram:
        System("API", alias="api", extensions={"d2": None})

    result = D2Renderer().render(diagram)

    assert result == "\n".join([
        "direction: right",
        'api: "API"',
        "",
    ])


def test_renderer_ignores_non_mapping_d2_style_extension():
    with SystemContextDiagram():
        system = System("API", alias="api", d2={"style": None})

    result = D2Renderer()._d2_attributes(system)

    assert result == []


def test_renderer_adds_unlabeled_relationship_edge():
    builder = D2StringBuilder()

    D2Renderer()._add_relationship_edge(
        builder,
        "source",
        "destination",
        None,
    )

    assert builder.get_result() == "source -> destination"


def test_renderer_adds_attributed_relationship_edge_without_label():
    builder = D2StringBuilder()

    D2Renderer()._add_relationship_edge(
        builder,
        "source",
        "destination",
        None,
        [("style.animated", "true")],
    )

    assert builder.get_result() == "\n".join([
        "source -> destination: {",
        "  style.animated: true",
        "}",
    ])


def test_renderer_relationship_label_can_use_technology_only():
    with SystemContextDiagram():
        relationship = Rel(technology="HTTPS")

    result = D2Renderer()._relationship_label(relationship)

    assert result == '"[HTTPS]"'


def test_renderer_relationship_label_is_none_without_label_or_technology():
    with SystemContextDiagram():
        relationship = Rel()

    result = D2Renderer()._relationship_label(relationship)

    assert result is None


def test_renderer_resolve_relationship_endpoint_reports_missing_alias():
    renderer = D2Renderer()
    with SystemContextDiagram():
        relationship = Rel("Calls")

    with pytest.raises(D2UnresolvedRelationshipEndpointError, match="missing"):
        renderer._resolve_relationship_endpoint(
            "missing",
            (),
            relationship=relationship,
        )


def test_renderer_reference_identifier_keeps_external_nested_path():
    renderer = D2Renderer(
        render_options=D2RenderOptions(fully_qualified_relationships=False),
    )
    identifier = D2Identifier(
        alias="api",
        identifier="api",
        path=("other_boundary", "api"),
    )

    result = renderer._reference_identifier(
        identifier,
        parent_path=("current_boundary",),
    )

    assert result == "other_boundary.api"


def test_renderer_rejects_unknown_render_item():
    with pytest.raises(TypeError, match="Unsupported D2 render item"):
        D2Renderer()._render_item(D2StringBuilder(), object())


def test_renderer_maps_core_element_families(
    assert_match_snapshot,
):
    with ComponentDiagram() as diagram:
        Person("Customer", alias="person")
        PersonExt("External Customer", alias="person_ext")
        System("Banking System", alias="system")
        SystemExt("External System", alias="system_ext")
        SystemDb("System Database", alias="system_db")
        SystemDbExt("External System Database", alias="system_db_ext")
        SystemQueue("System Queue", alias="system_queue")
        SystemQueueExt("External System Queue", alias="system_queue_ext")
        Container("API", technology="Python", alias="container")
        ContainerExt("External API", technology="Go", alias="container_ext")
        ContainerDb(
            "Container Database", technology="PostgreSQL", alias="container_db"
        )
        ContainerDbExt(
            "External Container Database",
            technology="Oracle",
            alias="container_db_ext",
        )
        ContainerQueue(
            "Container Queue", technology="Kafka", alias="container_queue"
        )
        ContainerQueueExt(
            "External Container Queue",
            technology="SQS",
            alias="container_queue_ext",
        )
        Component("Controller", technology="Django", alias="component")
        ComponentExt(
            "External Component", technology="SDK", alias="component_ext"
        )
        ComponentDb(
            "Component Database", technology="SQLite", alias="component_db"
        )
        ComponentDbExt(
            "External Component Database",
            technology="Redis",
            alias="component_db_ext",
        )
        ComponentQueue(
            "Component Queue", technology="RabbitMQ", alias="component_queue"
        )
        ComponentQueueExt(
            "External Component Queue",
            technology="NATS",
            alias="component_queue_ext",
        )

    assert_match_snapshot(
        snapshot_name="d2/core_elements.d2",
        diagram_code=D2Renderer().render(diagram),
    )


def test_renderer_renders_nested_system_boundaries(
    assert_match_snapshot,
):
    with SystemContextDiagram() as diagram:
        with EnterpriseBoundary("Big Bank", alias="big_bank"):
            customer = Person("Customer", alias="customer")

            with SystemBoundary("Online Banking", alias="online_banking"):
                banking = System("Banking System", alias="banking_system")

        customer >> "Uses" >> banking

    assert_match_snapshot(
        snapshot_name="d2/nested_system_boundaries.d2",
        diagram_code=D2Renderer().render(diagram),
    )


def test_renderer_renders_nested_container_boundaries(
    assert_match_snapshot,
):
    with ContainerDiagram() as diagram:
        with ContainerBoundary("Application", alias="application"):
            Container("Web App", technology="React", alias="web_app")

            with ContainerBoundary("Backend", alias="backend"):
                Container("API", technology="Python", alias="api")
                ContainerDb(
                    "Database",
                    technology="PostgreSQL",
                    alias="database",
                )

    assert_match_snapshot(
        snapshot_name="d2/nested_container_boundaries.d2",
        diagram_code=D2Renderer().render(diagram),
    )


def test_renderer_renders_deployment_node_containers(
    assert_match_snapshot,
):
    with DeploymentDiagram() as diagram:
        with Node("AWS", alias="aws"):
            with NodeLeft("Private Subnet", alias="private_subnet"):
                Container("Worker", technology="Python", alias="worker")

            with NodeRight("Public Subnet", alias="public_subnet"):
                Container("Web App", technology="React", alias="web_app")

            with DeploymentNode("EC2", alias="ec2"):
                Container("API", technology="FastAPI", alias="api")

            with DeploymentNodeLeft("Blue Node", alias="blue_node"):
                Container("Blue API", technology="FastAPI", alias="blue_api")

            with DeploymentNodeRight("Green Node", alias="green_node"):
                Container(
                    "Green API",
                    technology="FastAPI",
                    alias="green_api",
                )

    assert_match_snapshot(
        snapshot_name="d2/deployment_nodes.d2",
        diagram_code=D2Renderer().render(diagram),
    )


def test_renderer_renders_relationships(
    assert_match_snapshot,
):
    with SystemContextDiagram() as diagram:
        customer = Person("Customer", alias="customer")

        with SystemBoundary("Online Banking", alias="online_banking"):
            web_app = System("Web App", alias="web_app")
            api = System("API", alias="api")

        customer >> Rel("Uses", technology="HTTPS") >> web_app
        customer >> "Opens" >> web_app
        Rel(
            "Calls",
            description="Sends authenticated requests.",
            from_element=web_app,
            to_element=api,
        ).with_properties("Auth", "OAuth2")
        BiRel(
            "Syncs", technology="Events", from_element=api, to_element=web_app
        )

    assert_match_snapshot(
        snapshot_name="d2/relationships.d2",
        diagram_code=D2Renderer(
            render_options=D2RenderOptions(include_properties=True),
        ).render(diagram),
    )


def test_renderer_can_render_bidirectional_relationship_as_single_edge():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        BiRel("Syncs", from_element=user, to_element=system)

    result = D2Renderer(
        render_options=D2RenderOptions(
            bidirectional_relationships="single_edge",
        ),
    ).render(diagram)

    assert 'user <-> system: "Syncs"' in result
    assert 'user -> system: "Syncs"' not in result
    assert 'system -> user: "Syncs"' not in result


def test_renderer_uses_fully_qualified_nested_relationships_by_default():
    with SystemContextDiagram() as diagram:
        with SystemBoundary("Boundary", alias="boundary"):
            user = Person("User", alias="user")
            system = System("System", alias="system")
            user >> "Uses" >> system

    result = D2Renderer().render(diagram)

    assert 'boundary.user -> boundary.system: "Uses"' in result


def test_renderer_can_render_relative_nested_relationships():
    with SystemContextDiagram() as diagram:
        with SystemBoundary("Boundary", alias="boundary"):
            user = Person("User", alias="user")
            system = System("System", alias="system")
            user >> "Uses" >> system

    result = D2Renderer(
        render_options=D2RenderOptions(
            fully_qualified_relationships=False,
        ),
    ).render(diagram)

    assert 'user -> system: "Uses"' in result


def test_renderer_rejects_unresolved_relationship_endpoints_by_default():
    with SystemContextDiagram():
        unknown = System("Unknown", alias="unknown")

    with SystemContextDiagram() as diagram:
        known = System("Known", alias="known")
        relationship = Rel("Calls")

    relationship.from_element = known
    relationship.to_element = unknown
    diagram.add_ordered_element(relationship)

    with pytest.raises(
        D2UnresolvedRelationshipEndpointError,
        match="unknown",
    ):
        D2Renderer().render(diagram)


def test_renderer_rejects_plantuml_layout_helpers_by_default():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        LayDown(user, system)

    with pytest.raises(ValueError, match="LayDown is not supported"):
        D2Renderer().render(diagram)


def test_renderer_rejects_plantuml_index_statements_by_default():
    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system
        increment()
        set_index(10)

    with pytest.raises(ValueError, match="increment is not supported"):
        D2Renderer().render(diagram)


def test_renderer_rejects_directional_relationships_by_default():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        RelDown("Uses", from_element=user, to_element=system)

    with pytest.raises(D2UnsupportedDeclarationError, match="REL_DOWN"):
        D2Renderer().render(diagram)


@pytest.mark.parametrize(
    "helper_factory, expected_name",
    [
        (lambda user, system: LayDown(user, system), "LayDown"),
        (lambda _user, _system: increment(), "increment"),
        (lambda _user, _system: set_index(10), "set_index"),
    ],
)
def test_renderer_rejects_plantuml_helpers_with_standalone_validator(
    helper_factory,
    expected_name: str,
):
    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        helper_factory(user, system)

    with pytest.raises(ValueError, match=f"{expected_name} is not supported"):
        validate_d2_diagram(diagram)


def test_renderer_ignores_foreign_extension_data_by_default():
    with SystemContextDiagram() as diagram:
        System("System", alias="system", plantuml={"tags": "foo"})

    result = D2Renderer().render(diagram)

    assert 'system: "System"' in result
    assert "foo" not in result


def test_renderer_ignores_plantuml_index_extensions_by_default():
    with DynamicDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        Rel(
            "Uses",
            from_element=user,
            to_element=system,
            plantuml={"index": f"{Index()} {LastIndex()}"},
        )

    result = D2Renderer().render(diagram)

    assert 'user -> system: "Uses"' in result
    assert "Index()" not in result
    assert "LastIndex()" not in result


def test_renderer_rejects_foreign_extension_data_in_strict_extension_mode():
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            extensions={"mermaid": {"shape": "hexagon"}},
        )

    renderer = D2Renderer(extension_validation_mode=STRICT)

    with pytest.raises(ValueError, match="mermaid"):
        renderer.render(diagram)


def test_renderer_render_bytes_requires_backend():
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    with pytest.raises(
        D2BackendConfigurationError,
        match="D2 image export requires a configured backend",
    ):
        D2Renderer().render_bytes(diagram, format=DiagramFormat.SVG)


def test_renderer_render_file_requires_backend(tmp_path: Path):
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    with pytest.raises(
        D2BackendConfigurationError,
        match="D2 image export requires a configured backend",
    ):
        D2Renderer().render_file(
            diagram,
            tmp_path / "diagram.svg",
            format=DiagramFormat.SVG,
        )


def test_renderer_render_bytes_delegates_to_backend():
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    backend = DummyD2Backend(content=b"<svg />")
    result = D2Renderer(backend=backend).render_bytes(
        diagram,
        format=DiagramFormat.SVG,
    )

    assert result == b"<svg />"
    assert backend.bytes_calls == [
        (
            "\n".join([
                "direction: right",
                'system: "System"',
                "",
            ]),
            DiagramFormat.SVG,
            D2RenderOptions(),
        )
    ]


def test_renderer_render_bytes_uses_diagram_render_options():
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    diagram.set_render_options(d2=D2RenderOptions(direction="down"))

    backend = DummyD2Backend(content=b"<svg />")
    result = D2Renderer(backend=backend).render_bytes(
        diagram,
        format=DiagramFormat.SVG,
    )

    assert result == b"<svg />"
    assert backend.bytes_calls == [
        (
            "\n".join([
                "direction: down",
                'system: "System"',
                "",
            ]),
            DiagramFormat.SVG,
            D2RenderOptions(direction="down"),
        )
    ]


def test_renderer_render_bytes_passes_layout_render_option_to_backend():
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    diagram.set_render_options(d2=D2RenderOptions(layout="elk"))

    backend = DummyD2Backend(content=b"<svg />")
    result = D2Renderer(backend=backend).render_bytes(
        diagram,
        format=DiagramFormat.SVG,
    )

    assert result == b"<svg />"
    assert backend.bytes_calls == [
        (
            "\n".join([
                "direction: right",
                'system: "System"',
                "",
            ]),
            DiagramFormat.SVG,
            D2RenderOptions(layout="elk"),
        )
    ]


def test_renderer_render_file_delegates_to_backend(tmp_path: Path):
    with SystemContextDiagram() as diagram:
        System("System", alias="system")

    backend = DummyD2Backend(content=b"<svg />")
    output_path = tmp_path / "diagram.svg"

    result = D2Renderer(backend=backend).render_file(
        diagram,
        output_path,
        format=DiagramFormat.SVG,
        overwrite=False,
    )

    assert result == output_path
    assert output_path.read_bytes() == b"<svg />"
    assert backend.file_calls == [
        (
            "\n".join([
                "direction: right",
                'system: "System"',
                "",
            ]),
            output_path,
            DiagramFormat.SVG,
            False,
        )
    ]

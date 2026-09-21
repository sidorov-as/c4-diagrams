from __future__ import annotations

import pytest

from c4.contrib.structurizr.renderer import (
    AutoLayout,
    StructurizrStringBuilder,
    auto_layout_directive,
    escape_structurizr_string,
    properties_block,
    quote_structurizr_string,
    tags_directive,
)
from c4.contrib.structurizr.renderer.dsl import (
    ordered_style_properties,
    style_value,
)


def test_auto_layout_directive__emits_optional_settings():
    assert (
        auto_layout_directive(
            AutoLayout(
                rank_direction="TopBottom",
                implementation="elk",
                rank_separation=300,
                node_separation=120,
            )
        )
        == "autoLayout tb elk 300 120"
    )
    assert auto_layout_directive(AutoLayout("BottomTop")) == "autoLayout bt"
    assert auto_layout_directive(AutoLayout("RightLeft")) == "autoLayout rl"


def test_properties_block__skips_empty_and_sorts_keys():
    builder = StructurizrStringBuilder()

    properties_block(builder, {})
    properties_block(builder, {"z": "last", "a": "first"})

    assert builder.get_result() == (
        'properties {\n  "a" "first"\n  "z" "last"\n}'
    )


def test_tags_directive__handles_empty_and_non_empty_tags():
    assert tags_directive(()) is None
    assert tags_directive(["Person", "External"]) == 'tags "Person,External"'


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "true"),
        (False, "false"),
        (7, "7"),
        ("#ffffff", "#ffffff"),
        ("RoundedBox", "RoundedBox"),
        ("dashed_value", "dashed_value"),
        ("two words", '"two words"'),
    ],
)
def test_style_value__formats_structurizr_literals(
    value: object, expected: str
):
    assert style_value(value) == expected


def test_ordered_style_properties__uses_structurizr_order_then_alpha_rest():
    assert list(
        ordered_style_properties({
            "zeta": 1,
            "color": "#fff",
            "shape": "Box",
            "alpha": 2,
            "background": "#000",
        })
    ) == ["shape", "background", "color", "alpha", "zeta"]


def test_quote_structurizr_string__escapes_special_characters():
    value = 'line\\one\nline\rtwo\t"quoted"'

    assert escape_structurizr_string(value) == (
        'line\\\\one\\nline\\rtwo\\t\\"quoted\\"'
    )
    assert quote_structurizr_string(value) == (
        '"line\\\\one\\nline\\rtwo\\t\\"quoted\\""'
    )


def test_string_builder__supports_blank_lines_blocks_and_line_splitting():
    builder = StructurizrStringBuilder(indent="    ")
    builder.add("first\nsecond")
    builder.add()
    with builder.block("workspace"):
        builder.add("model")

    assert builder.lines == [
        "first",
        "second",
        "",
        "workspace {",
        "    model",
        "}",
    ]

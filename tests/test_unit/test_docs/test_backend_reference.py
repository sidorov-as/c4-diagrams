from __future__ import annotations

from pathlib import Path

import pytest

from c4.contrib.likec4 import _styles as likec4_styles
from c4.contrib.likec4._views import AUTO_LAYOUT_DIRECTIONS
from c4.contrib.structurizr import _options as structurizr_options
from c4.contrib.structurizr import _styles as structurizr_styles
from docs.scripts import generate_backend_reference as generator


def test_generator_output_is_deterministic():
    assert generator.planned_outputs() == generator.planned_outputs()


def test_checked_in_files_match_generator_output():
    for path, text in generator.planned_outputs().items():
        assert path.read_text(encoding="utf-8") == text, path


def test_replace_region_preserves_surrounding_text():
    text = "intro\n<!-- generated:start a -->\nold\n<!-- generated:end a -->\ntail\n"

    result = generator.replace_region(text, "a", "new")

    assert result.startswith("intro\n")
    assert result.endswith("\ntail\n")
    assert "new" in result
    assert "old" not in result


def test_replace_region_rejects_missing_marker():
    with pytest.raises(ValueError):
        generator.replace_region("no markers", "a", "body")


def _generated(region: str) -> str:
    bodies = {**generator.structurizr_body(), **generator.likec4_body()}
    return bodies[region]


@pytest.mark.parametrize(
    ("region", "values"),
    [
        ("structurizr-values", structurizr_styles.ELEMENT_SHAPES.values()),
        ("structurizr-values", structurizr_styles.BORDERS.values()),
        ("structurizr-values", structurizr_options.RANK_DIRECTIONS),
        ("structurizr-values", structurizr_styles.STYLE_PRESET_CLI_VALUES),
        (
            "structurizr-style-properties",
            structurizr_styles.STYLE_PROPERTY_NAMES.keys(),
        ),
        ("likec4-values", likec4_styles.ELEMENT_SHAPES),
        ("likec4-values", likec4_styles.BORDERS),
        ("likec4-values", likec4_styles.SIZES),
        ("likec4-values", likec4_styles.ICON_POSITIONS),
        ("likec4-values", likec4_styles.LINE_TYPES),
        ("likec4-values", likec4_styles.ARROW_TYPES),
        ("likec4-values", likec4_styles.THEME_COLORS),
        ("likec4-values", AUTO_LAYOUT_DIRECTIONS),
    ],
)
def test_every_public_constant_value_is_in_generated_table(region, values):
    body = _generated(region)

    for value in values:
        assert f"`{value}`" in body


@pytest.mark.parametrize(
    "rule",
    [*generator.STRUCTURIZR_RULES, *generator.LIKEC4_RULES],
    ids=lambda rule: rule.cause[:40],
)
def test_listed_validation_error_classes_exist(rule):
    assert issubclass(generator.import_error_class(rule.error), Exception)


def test_cli_tables_list_every_backend_flag():
    from c4.cli.parser import build_parser

    parser_text = build_parser().format_help()
    assert parser_text
    export = generator.cli_flag_table("export", "--structurizr-")
    for flag in (
        "--structurizr-backend",
        "--structurizr-bin",
        "--structurizr-view-key",
    ):
        assert flag in export
    assert "--structurizr-style-preset" in generator.cli_flag_table(
        "render", "--structurizr-"
    )
    likec4 = generator.cli_flag_table("export", "--likec4-")
    for flag in ("--likec4-backend", "--likec4-bin", "--likec4-view-key"):
        assert flag in likec4


def test_reference_files_exist():
    for path in (generator.STRUCTURIZR_REFERENCE, generator.LIKEC4_REFERENCE):
        assert isinstance(path, Path)
        assert path.exists()

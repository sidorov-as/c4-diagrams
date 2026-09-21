"""Generate the reference tables of the Structurizr and LikeC4 docs.

Only the text between ``<!-- generated:start NAME -->`` and
``<!-- generated:end NAME -->`` markers is written; everything around the
markers is hand-written and preserved. Output is deterministic.
"""

from __future__ import annotations

import argparse
import html
import importlib
import os
import sys
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from c4.cli.parser import build_parser
from c4.contrib.likec4 import _styles as likec4_styles
from c4.contrib.likec4._views import AUTO_LAYOUT_DIRECTIONS
from c4.contrib.structurizr import _options as structurizr_options
from c4.contrib.structurizr import _styles as structurizr_styles
from docs.scripts.backend_call_cases import (
    LIKEC4_CASES,
    STRUCTURIZR_CASES,
    Case,
    clean,
)

DOCS_DIR = Path(__file__).resolve().parents[1]
CLI_DOC = DOCS_DIR / "cli.md"
STRUCTURIZR_REFERENCE = DOCS_DIR / "renderers" / "structurizr" / "reference.md"
LIKEC4_REFERENCE = DOCS_DIR / "renderers" / "likec4" / "reference.md"

# Hand-written pages whose "call -> DSL" tables are generated from
# ``docs/scripts/backend_call_cases.py``.
RENDERERS_DIR = DOCS_DIR / "renderers"
CASE_PAGES = {
    RENDERERS_DIR / "structurizr" / "authoring.md": (
        "structurizr-calls-elements",
        "structurizr-calls-metadata",
        "structurizr-calls-relationships",
    ),
    RENDERERS_DIR / "structurizr" / "views.md": ("structurizr-calls-views",),
    RENDERERS_DIR / "structurizr" / "styles.md": (
        "structurizr-calls-styles",
        "structurizr-calls-options",
    ),
    RENDERERS_DIR / "likec4" / "authoring.md": (
        "likec4-calls-specification",
        "likec4-calls-elements",
        "likec4-calls-relationships",
        "likec4-calls-deployment",
    ),
    RENDERERS_DIR / "likec4" / "views.md": ("likec4-calls-views",),
    RENDERERS_DIR / "likec4" / "styles.md": ("likec4-calls-styles",),
}
ALL_CASES = {**STRUCTURIZR_CASES, **LIKEC4_CASES}

# Flags whose default is resolved at run time (environment or backend).
BIN_FLAG_DEFAULTS = {
    "--structurizr-bin": "structurizr",
    "--likec4-bin": "likec4",
}
CLI_ENV_VARS = ("STRUCTURIZR_BIN", "LIKEC4_BIN")


@dataclass(frozen=True)
class ValidationRule:
    """One documented validation rule and the exception that reports it."""

    cause: str
    error: str  # "module.path:ClassName"


STRUCTURIZR_RULES = (
    ValidationRule(
        "The rendered object is not a `Workspace`.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "A container has no software system parent, or a component has no "
        "container parent.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "A deployment instance does not reference a model element of the "
        "workspace.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "A relationship endpoint does not belong to the workspace.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "A relationship connects a parent with its own descendant.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "A deployment node does not belong to exactly one environment.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "A view that needs a scope has none, or its scope is of the wrong "
        "type or outside the workspace.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "A deployment view names an unknown deployment environment.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "An element `style` mapping has an unknown field or a value of the "
        "wrong type.",
        "c4.contrib.structurizr.renderer.errors:StructurizrRenderingError",
    ),
    ValidationRule(
        "`tags` is not a `list[str]`, or a view scope is passed as an alias "
        "string instead of a model object.",
        "builtins:TypeError",
    ),
    ValidationRule(
        "An `owner`, `parent`, scope or endpoint belongs to another "
        "workspace, or has the wrong type for the factory.",
        "builtins:ValueError",
    ),
    ValidationRule(
        "An export backend is misconfigured (for example a missing view key "
        "or binary).",
        "c4.contrib.structurizr.renderer.errors:"
        "StructurizrBackendConfigurationError",
    ),
)

LIKEC4_RULES = (
    ValidationRule(
        "The rendered object is not a `Project`.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "An element kind, relationship kind, deployment node kind, tag or "
        "custom color is used but not declared in the specification.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "A relationship endpoint does not belong to the project.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "A relationship connects an element with its own ancestor or "
        "descendant.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "A link has no scheme, relative prefix or `@alias`, or contains "
        "whitespace.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "A deployment node holds several unnamed instances of the same "
        "element, or an instance points outside the project model.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "View keys are not unique across all view types.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "A view scope or predicate reference does not resolve to a member "
        "of the project.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "`navigate_to` does not name a view (a dynamic view for relationships "
        "and steps).",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "A view style rule targets a relationship predicate.",
        "c4.contrib.likec4.renderer.errors:LikeC4ValidationError",
    ),
    ValidationRule(
        "The local `likec4` CLI fails to export a view.",
        "c4.contrib.likec4.renderer.errors:LikeC4LocalRenderingError",
    ),
)


def region(name: str, body: str) -> str:
    """Return ``body`` wrapped in generated-region markers."""
    return (
        f"<!-- generated:start {name} -->\n"
        f"{body.strip()}\n"
        f"<!-- generated:end {name} -->"
    )


def replace_region(text: str, name: str, body: str) -> str:
    """Replace the marked region ``name`` in ``text``, keeping the rest."""
    start = f"<!-- generated:start {name} -->"
    end = f"<!-- generated:end {name} -->"
    first = text.find(start)
    last = text.find(end)
    if first == -1 or last == -1 or last < first:
        raise ValueError(f"Generated region {name!r} not found.")
    return text[:first] + region(name, body) + text[last + len(end) :]


def table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> str:
    """Render a Markdown table with escaped cells."""

    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(cell(c) for c in row) + " |" for row in rows)
    return "\n".join(lines)


def block_cell(text: str) -> str:
    """Render multi-line code as an HTML block that survives a table cell."""
    escaped = html.escape(clean(text), quote=False)
    escaped = escaped.replace("|", "&#124;").replace("\n", "&#10;")
    return f"<pre><code>{escaped}</code></pre>"


def case_table(cases: Iterable[Case]) -> str:
    """Render a "Python call -> generated DSL" table for ``cases``."""
    return table(
        ["Python call", "Generated DSL"],
        ([block_cell(case.call), block_cell(case.dsl)] for case in cases),
    )


def code(value: object) -> str:
    return f"`{value}`"


def values_table(title: str, values: Iterable[str]) -> str:
    return f"### {title}\n\n" + ", ".join(
        code(value) for value in sorted(values)
    )


def mapping_table(title: str, mapping: Mapping[str, str], head: str) -> str:
    return f"### {title}\n\n" + table(
        ["Python value", head],
        ([code(key), code(value)] for key, value in mapping.items()),
    )


def validation_table(rules: Iterable[ValidationRule]) -> str:
    return table(
        ["Cause", "Error"],
        ([rule.cause, code(rule.error.rsplit(":", 1)[1])] for rule in rules),
    )


_STYLE_PROPERTIES = structurizr_styles.STYLE_PROPERTY_NAMES


def structurizr_body() -> dict[str, str]:
    return {
        "structurizr-values": "\n\n".join([
            mapping_table(
                "Element shapes",
                dict(structurizr_styles.ELEMENT_SHAPES),
                "Structurizr shape",
            ),
            mapping_table(
                "Borders",
                dict(structurizr_styles.BORDERS),
                "Structurizr border",
            ),
            values_table(
                "Auto-layout rank directions",
                structurizr_options.RANK_DIRECTIONS,
            ),
            values_table(
                "Style presets",
                structurizr_styles.STYLE_PRESET_CLI_VALUES,
            ),
        ]),
        "structurizr-style-properties": table(
            ["Python keyword", "Structurizr style property"],
            (
                [code(key), code(value)]
                for key, value in _STYLE_PROPERTIES.items()
            ),
        ),
        "structurizr-validation": validation_table(STRUCTURIZR_RULES),
    }


def likec4_body() -> dict[str, str]:
    snake = likec4_styles._SNAKE_TO_CAMEL
    return {
        "likec4-values": "\n\n".join([
            values_table("Element shapes", likec4_styles.ELEMENT_SHAPES),
            values_table("Borders", likec4_styles.BORDERS),
            values_table(
                "Sizes (`size`, `text_size`, `padding`, `icon_size`)",
                likec4_styles.SIZES,
            ),
            values_table("Icon positions", likec4_styles.ICON_POSITIONS),
            values_table("Line types", likec4_styles.LINE_TYPES),
            values_table(
                "Arrow types (`head`, `tail`)", likec4_styles.ARROW_TYPES
            ),
            values_table("Theme colors", likec4_styles.THEME_COLORS),
            values_table("Auto-layout directions", AUTO_LAYOUT_DIRECTIONS),
        ]),
        "likec4-style-properties": "\n\n".join([
            "### Element style properties\n\n"
            + table(
                ["Python keyword", "LikeC4 property"],
                (
                    [code(_python_name(key, snake)), code(key)]
                    for key in likec4_styles._ELEMENT_KEYS
                ),
            ),
            "### Relationship style properties\n\n"
            + table(
                ["Python keyword", "LikeC4 property"],
                (
                    [code(_python_name(key, snake)), code(key)]
                    for key in likec4_styles._RELATIONSHIP_KEYS
                ),
            ),
        ]),
        "likec4-validation": validation_table(LIKEC4_RULES),
    }


def _python_name(key: str, snake_to_camel: Mapping[str, str]) -> str:
    for python_name, camel in snake_to_camel.items():
        if camel == key:
            return python_name
    return key


def _clean_environment() -> None:
    for name in CLI_ENV_VARS:
        os.environ.pop(name, None)


def _flag_type(action: argparse.Action) -> str:
    if action.choices:
        values = ", ".join(code(choice) for choice in action.choices)
        return f"choice ({values})"
    if isinstance(action, argparse._StoreTrueAction):
        return "boolean"
    if action.option_strings[0] in BIN_FLAG_DEFAULTS:
        return "string (path or command)"
    return "string"


def _flag_default(action: argparse.Action) -> str:
    flag = action.option_strings[0]
    if flag in BIN_FLAG_DEFAULTS:
        return code(BIN_FLAG_DEFAULTS[flag])
    if isinstance(action, argparse._StoreTrueAction):
        return "False"
    if action.default is None:
        return "None"
    return code(action.default)


def _subparser(name: str) -> argparse.ArgumentParser:
    parser = build_parser()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action.choices[name]
    raise LookupError(name)


def cli_flag_table(
    command: str, prefix: str | None = None, group: str | None = None
) -> str:
    """Return a table of CLI flags of a command.

    Flags are selected by ``--{prefix}-*`` or by the title of the argparse
    argument group they are declared in.
    """
    _clean_environment()
    parser = _subparser(command)
    if group is not None:
        actions = [
            action
            for candidate in parser._action_groups
            if candidate.title == group
            for action in candidate._group_actions
        ]
    else:
        actions = parser._actions
    rows = []
    for action in actions:
        flags = [
            f
            for f in action.option_strings
            if prefix is None or f.startswith(prefix)
        ]
        if not flags:
            continue
        rows.append([
            code(flags[0]),
            _flag_type(action),
            " ".join((action.help or "").split()),
            _flag_default(action),
        ])
    return table(["Name", "Type", "Description", "Default"], rows)


def cli_regions() -> dict[str, str]:
    return {
        "plantuml-render-options": cli_flag_table(
            "render", group="PlantUML options"
        ),
        "structurizr-render-options": cli_flag_table(
            "render", "--structurizr-"
        ),
        "kroki-export-options": cli_flag_table("export", group="Kroki options"),
        "plantuml-export-options": cli_flag_table(
            "export", group="PlantUML options"
        ),
        "mermaid-export-options": cli_flag_table(
            "export", group="Mermaid options"
        ),
        "d2-export-options": cli_flag_table("export", group="D2 options"),
        "structurizr-export-options": cli_flag_table(
            "export", "--structurizr-"
        ),
        "likec4-export-options": cli_flag_table("export", "--likec4-"),
    }


def _skeleton(title: str, regions: Iterable[str]) -> str:
    sections = "\n\n".join(region(name, "") for name in regions)
    return f"# {title}\n\n{sections}\n"


def planned_outputs() -> dict[Path, str]:
    """Return the new text of every file the generator touches."""
    outputs: dict[Path, str] = {}

    for path, title, regions in (
        (STRUCTURIZR_REFERENCE, "Structurizr Reference", structurizr_body()),
        (LIKEC4_REFERENCE, "LikeC4 Reference", likec4_body()),
    ):
        text = (
            path.read_text(encoding="utf-8")
            if path.exists()
            else _skeleton(title, regions)
        )
        for name, body in regions.items():
            text = replace_region(text, name, body)
        outputs[path] = text

    for path, names in CASE_PAGES.items():
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for name in names:
            text = replace_region(text, name, case_table(ALL_CASES[name]))
        outputs[path] = text

    text = CLI_DOC.read_text(encoding="utf-8")
    for name, body in cli_regions().items():
        text = replace_region(text, name, body)
    outputs[CLI_DOC] = text
    return outputs


def import_error_class(path: str) -> type[BaseException]:
    """Import ``module:Class`` and return the class."""
    module, name = path.split(":")
    return getattr(importlib.import_module(module), name)


def main() -> int:
    for path, text in planned_outputs().items():
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())

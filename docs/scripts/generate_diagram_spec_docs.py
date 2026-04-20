from __future__ import annotations

import json
import re
from dataclasses import dataclass
from inspect import cleandoc
from pathlib import Path
from typing import Any, Iterable

from c4.converters.json.schemas.renderers.mermaid import MermaidRenderOptionsSchema
from c4.converters.json.schemas.renderers.plantuml import PlantUMLRenderOptionsSchema
from c4.diagrams.core import EnumDescriptionsMixin
from pydantic import BaseModel
from typing_extensions import get_args, get_origin

from c4.converters.json.schemas import DIAGRAMS_SCHEMAS
from c4.converters.json.schemas.diagrams.common import BaseDiagramSchema

Json = dict[str, Any]

SLUG_PAT = re.compile(r"[^a-z0-9_]+")

_CAMEL_TO_SNAKE_RE = re.compile(r"([a-z])([A-Z])")

SPECS_DIR = Path(__file__).parent.parent / "assets" / "specs"
MD_SPECS_DIR = Path(__file__).parent.parent / "converters/json/specs"

TOP_SCHEMA_ORDER = [
    "$schema",
    "$id",
    "title",
    "description",
    "type",
    "properties",
    "required",
    "additionalProperties",
    "examples",
    "defs",
    "$defs",
]

DIAGRAM_ATTRS_ORDER = [
    "type",
    "title",
    "elements",
    "boundaries",
    "relationships",
    "layouts",
    "render_options",
]

DEFINITIONS_ORDER = [
    "Person",
    "PersonExt",
    "System",
    "SystemExt",
    "SystemDb",
    "SystemDbExt",
    "SystemQueue",
    "SystemQueueExt",
    "EnterpriseBoundary",
    "SystemBoundary",
    "Container",
    "ContainerExt",
    "ContainerDb",
    "ContainerDbExt",
    "ContainerQueue",
    "ContainerQueueExt",
    "ContainerBoundary",
    "Component",
    "ComponentExt",
    "ComponentDb",
    "ComponentDbExt",
    "ComponentQueue",
    "ComponentQueueExt",
    "Relationship",
    "RelationshipType",
    "Layout",
    "LayoutType",
    "DiagramElementProperties",
    "Element",
    "Boundary",
    # render options

    "PlantUMLRenderOptionsSchema",
    "BaseStyle",
    "BaseTag",
    "DiagramLayout",
    "SetSketchStyle",
    "ShowFloatingLegend",
    "ShowLegend",
    "ShowPersonSprit",
    "RenderOptionsSchema",
    "MermaidRenderOptionsSchema",
]


def reorder_keys(mapping: Json, preferred_order: list[str]) -> Json:
    """
    Return a shallow copy of mapping with keys ordered deterministically.
    """
    ordered: Json = {
        key: mapping[key] for key in preferred_order if key in mapping
    }
    ordered.update({
        key: value for key, value in mapping.items() if key not in ordered
    })
    return ordered


def reorder_schema_for_model(schema: Json, model: type[BaseModel]) -> Json:
    """
    Reorder schema keys, examples, and properties to match model field order.
    """
    schema_copy: Json = reorder_keys(dict(schema), TOP_SCHEMA_ORDER)

    field_order = list(model.model_fields.keys())

    examples = schema_copy.get("examples")
    if isinstance(examples, list) and examples:
        schema_copy["examples"] = [
            reorder_keys(example, DIAGRAM_ATTRS_ORDER)
            if isinstance(example, dict)
            else example
            for example in examples
        ]

    properties = schema_copy.get("properties")
    if isinstance(properties, dict):
        ordered_props: Json = {}
        for field_name in field_order:
            if field_name in properties:
                ordered_props[field_name] = properties[field_name]
        for prop_name, prop_schema in properties.items():
            if prop_name not in ordered_props:
                ordered_props[prop_name] = prop_schema
        schema_copy["properties"] = ordered_props

    return schema_copy


def collect_model_types(
    model_cls: type[BaseModel],
    use_qualified_names: bool = False,
) -> dict[str, type]:
    """
    Collect all referenced Python types reachable from
    Pydantic model annotations.
    """
    collected: dict[str, type] = {}
    visited: set[type[BaseModel]] = set()

    def type_key(tp: type) -> str:
        if use_qualified_names:
            return f"{tp.__module__}.{tp.__name__}"
        return tp.__name__

    def visit_annotation(annotation: Any) -> None:
        if annotation is None or annotation is type(None):
            return

        origin = get_origin(annotation)
        args = get_args(annotation)

        if origin is not None:
            if isinstance(origin, type):
                collected[type_key(origin)] = origin
            for arg in args:
                visit_annotation(arg)
            return

        if not isinstance(annotation, type):
            return

        collected[type_key(annotation)] = annotation

        if issubclass(annotation, BaseModel) and annotation not in visited:
            visited.add(annotation)
            for field in annotation.model_fields.values():
                visit_annotation(field.annotation)

    visit_annotation(model_cls)
    return collected


def camel_to_snake(name: str) -> str:
    """Convert CamelCase into snake_case."""
    return _CAMEL_TO_SNAKE_RE.sub(r"\1_\2", name).lower()


def slug(text: str) -> str:
    """Build a URL-friendly slug (anchors) from text."""
    normalized = text.strip().lower()
    normalized = SLUG_PAT.sub("-", normalized)
    return re.sub(r"-+", "-", normalized).strip("-")


def md_escape(text: str) -> str:
    """Escape Markdown table separators inside cell content."""
    return text.replace("|", "\\|")


def resolve_ref_name(schema_node: Json) -> str | None:
    """Return local $ref name for '#/...', otherwise None."""
    ref_value = schema_node.get("$ref")
    if isinstance(ref_value, str) and ref_value.startswith("#/"):
        return ref_value.split("/")[-1]
    return None


def is_enum_schema(schema_node: Json) -> bool:
    """Check whether the schema node represents an enum."""
    return isinstance(schema_node, dict) and "enum" in schema_node


def allows_null(schema_node: Json) -> bool:
    """Detect if schema allows null via type or anyOf."""
    node_type = schema_node.get("type")
    if node_type == "null":
        return True
    if isinstance(node_type, list) and "null" in node_type:
        return True

    for option in schema_union_options(schema_node):
        if option.get("type") == "null":
            return True
    return False


def schema_union_options(schema_node: Json) -> list[Json]:
    """Return anyOf options as dicts only."""
    any_of = schema_node.get("anyOf")
    if isinstance(any_of, list):
        return [option for option in any_of if isinstance(option, dict)]
    return []


def schema_union_oneof_options(schema_node: Json) -> list[Json]:
    """Return oneOf options as dicts only."""
    one_of = schema_node.get("oneOf")
    if isinstance(one_of, list):
        return [option for option in one_of if isinstance(option, dict)]
    return []


def array_variant(schema_node: Json) -> Json | None:
    """
    Return the array schema for 'array' or 'anyOf[array,null]' forms.
    """
    if schema_node.get("type") == "array":
        return schema_node

    for option in schema_union_options(schema_node):
        if option.get("type") == "array":
            return option
    return None


def object_variant(schema_node: Json) -> Json | None:
    """
    Return object-related schema for object, ref,
    or anyOf[object/ref,null] forms.
    """
    if "$ref" in schema_node:
        return schema_node
    if schema_node.get("type") == "object":
        return schema_node

    for option in schema_union_options(schema_node):
        if option.get("type") == "object" or "$ref" in option:
            return option
    return None


def unique_in_order(values: Iterable[str]) -> list[str]:
    """De-dupe while preserving order."""
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        if value not in seen:
            unique_values.append(value)
            seen.add(value)
    return unique_values


def anyof_ref_names(schema_node: Json) -> list[str]:
    """Extract unique local $ref names from anyOf."""
    ref_names: list[str] = []
    for option in schema_union_options(schema_node):
        ref_name = resolve_ref_name(option)
        if ref_name:
            ref_names.append(ref_name)
    return unique_in_order(ref_names)


def oneof_ref_names(schema_node: Json) -> list[str]:
    """Extract unique local $ref names from oneOf."""
    ref_names: list[str] = []
    for option in schema_union_oneof_options(schema_node):
        ref_name = resolve_ref_name(option)
        if ref_name:
            ref_names.append(ref_name)
    return unique_in_order(ref_names)


def default_repr(schema_node: Json, omit_null: bool) -> str | None:
    """Format const/default/null-as-default for table rendering."""
    if "const" in schema_node:
        value = schema_node["const"]
    elif "default" in schema_node:
        value = schema_node["default"]
    elif allows_null(schema_node):
        value = None
    else:
        return ""

    if value is None:
        return None if omit_null else "`null`"
    if isinstance(value, bool):
        return "`true`" if value else "`false`"
    if isinstance(value, (int, float)):
        return f"`{value}`"
    if isinstance(value, str):
        return f"`{value}`" if value else '`""`'
    return f"`{json.dumps(value, ensure_ascii=False)}`"


def primitive_union_repr(
    schema_node: Json,
) -> str:
    """Render primitive types/unions like `string` | `null` (supports anyOf)."""
    if "anyOf" in schema_node:
        parts: list[str] = []
        for option in schema_union_options(schema_node):
            if "$ref" in option:
                ref_name = resolve_ref_name(option)
                if ref_name:
                    parts.append(f"`{ref_name}`")
                continue

            option_type = option.get("type")
            if isinstance(option_type, str):
                parts.append(f"`{option_type}`")
            elif isinstance(option_type, list):
                parts.extend([f"`{t}`" for t in option_type])

        uniq_parts = unique_in_order(parts)
        union = " \\| ".join(uniq_parts) if uniq_parts else "`object`"
        return f"<span style=\"white-space: nowrap;\">{union}</span>"

    node_type = schema_node.get("type")
    if isinstance(node_type, list):
        return " \\| ".join(f"`{t}`" for t in node_type)
    if isinstance(node_type, str):
        return f"`{node_type}`"
    if "enum" in schema_node:
        return "`string`"
    return "`object`"


@dataclass(frozen=True)
class TypeLinkContext:
    """Render linked code types like array[Name] and Name anchors."""

    anchor: str
    label: str

    def render_array(self) -> str:
        return f'<code>array[<a href="#{self.anchor}">{self.label}</a>]</code>'

    def render_object(self) -> str:
        return f'<code><a href="#{self.anchor}">{self.label}</a></code>'

    def render_enum(self) -> str:
        return f'<code><a href="#{self.anchor}">{self.label}</a></code>'


def sort_by_preferred(items: list[str], preferred: list[str]) -> list[str]:
    def sort_key(item: str) -> tuple[int, str]:
        return preferred.index(item) if item in preferred else 999, item

    return sorted(items, key=sort_key)


class DiagramSpecDocsGenerator:
    """Generate JSON schemas and MkDocs Material markdown specs for diagrams."""

    def __init__(
        self,
        spec_path: Path,
        md_path: Path,
        diagram_schema: type[BaseDiagramSchema],
    ) -> None:
        self.spec_path = spec_path
        self.md_path = md_path
        self.diagram_schema = diagram_schema
        self.diagram_cls = diagram_schema.__diagram_class__

        self.diagram_spec = self._get_diagram_spec(diagram_schema)
        self.defs: Json = self._get_defs(self.diagram_spec)
        self.plantuml_render_options_defs: Json = self._get_defs(
            self._get_diagram_spec(PlantUMLRenderOptionsSchema)
        )
        self.mermaid_render_options_defs: Json = self._get_defs(
            self._get_diagram_spec(MermaidRenderOptionsSchema)
        )

        self.def_type_map = self._get_def_type_map(
            diagram_schema, self.defs
        )

    @staticmethod
    def _get_defs(diagram_spec: Json) -> Json:
        return diagram_spec.get("$defs", {}) or {}

    @staticmethod
    def _get_diagram_spec(
        diagram_schema: type[BaseDiagramSchema],
    ) -> Json:
        raw_schema = diagram_schema.model_json_schema()
        return reorder_schema_for_model(
            raw_schema, model=diagram_schema
        )

    @staticmethod
    def _get_def_type_map(
        diagram_schema: type[BaseDiagramSchema],
        defs: Json,
    ) -> dict[str, type]:
        model_types = collect_model_types(diagram_schema)

        return {
            type_name: type_obj
            for type_name, type_obj in model_types.items()
            if type_name in defs
        }


    def generate(self) -> None:
        """Write JSON schema and markdown documentation to disk."""
        self.spec_path.write_text(
            json.dumps(self.diagram_spec, indent=4),
            encoding="utf-8",
        )

        markdown = self._render_markdown()
        self.md_path.write_text(markdown, encoding="utf-8")

    def _render_markdown(self) -> str:
        """Build a full Markdown document."""

        source_link = f"../../../assets/specs/{self.spec_path.name}"

        diagram_class_repr = (
            f"[{self.diagram_cls.__name__}]"
            f"[{self.diagram_cls.__module__}.{self.diagram_cls.__name__}]"
        )
        title = self.diagram_spec.get("title", self.spec_path.stem)

        lines: list[str] = [
            f"# {title} Spec",
            "",
            f"> **Source:** [{self.spec_path.name}]({source_link})",
            "",
            "",
            f"This schema describes the {diagram_class_repr} spec.",
            "",
            "## Properties",
            "",
            self._render_properties_table(self.diagram_spec),
            "",
        ]

        lines.extend(self._render_examples_block(self.diagram_spec))
        lines.extend(self._render_diagram_components())

        plantuml_render_options_defs = [
            "PlantUMLRenderOptionsSchema",
            *self.plantuml_render_options_defs.keys(),
        ]

        mermaid_render_options_defs = [
            "MermaidRenderOptionsSchema",
            *self.mermaid_render_options_defs.keys(),
        ]

        render_options_defs = [
            "RenderOptionsSchema",
            *plantuml_render_options_defs,
            *mermaid_render_options_defs,
        ]

        lines.extend(["## Definitions", "", ""])
        lines.extend(self._render_note_on_aliases())
        lines.extend(self._render_definitions(exclude=render_options_defs))
        lines.extend(self._render_definitions(include=["RenderOptionsSchema"]))

        lines.extend(["", "", "## PlantUML Render Options", "", ""])
        lines.extend(self._render_definitions(include=plantuml_render_options_defs))

        lines.extend(["", "", "## Mermaid Render Options", "", ""])
        lines.extend(self._render_definitions(include=mermaid_render_options_defs))

        return "\n".join(lines).rstrip() + "\n"

    @staticmethod
    def _get_min_and_advanced_examples(schema: Json) -> tuple[Json, Json]:
        """Return (minimal, advanced) examples from schema."""
        examples = schema.get("examples")
        if isinstance(examples, list) and len(examples) == 2:
            first, second = examples
            if isinstance(first, dict) and isinstance(second, dict):
                return first, second

        raise ValueError(
            f"Expected minimal and advanced examples, got {examples}"
        )

    def _render_examples_block(self, schema: Json) -> list[str]:
        """Render collapsible blocks for minimal and advanced examples."""
        min_example, advanced_example = self._get_min_and_advanced_examples(
            schema
        )

        return [
            *self._render_example_block(min_example, title="Minimal example"),
            "",
            "",
            *self._render_example_block(
                advanced_example, title="Advanced example"
            ),
        ]

    @staticmethod
    def _render_example_block(
        example: Json,
        title: str = "Example",
    ) -> list[str]:
        """Render a single collapsible JSON example."""
        example_json = json.dumps(example, indent=2, ensure_ascii=False)
        indented = "\n".join(
            f"    {line}" for line in example_json.splitlines()
        )

        return [
            f'??? abstract "{title}"',
            "",
            "    ```json",
            indented,
            "    ```",
            "",
        ]

    def _render_properties_table(self, obj_schema: Json) -> str:
        """Render a properties table wrapped into a collapsible info block."""
        properties: Json = obj_schema.get("properties", {}) or {}
        required_fields = set(obj_schema.get("required", []) or [])

        lines: list[str] = [
            '???+ info "Properties"',
            "",
            '    <div class="code-nowrap"></div>',
            "    ",
            "    | Field | Type | Description |",
            "    |---|---|---|",
        ]

        property_names = sort_by_preferred(
            list(properties.keys()), preferred=DIAGRAM_ATTRS_ORDER,
        )

        for prop_name in property_names:
            prop_schema = properties.get(prop_name)
            if not isinstance(prop_schema, dict):
                continue

            is_required = prop_name in required_fields
            field_cell = self._render_field_name(prop_name, is_required)

            description_text = (
                prop_schema.get("description", "")
                or prop_schema.get("title", "")
                or ""
            )
            description_text = self._append_default_to_description(
                description_text=description_text,
                prop_schema=prop_schema,
                is_required=is_required,
            )

            type_cell = self._render_type(prop_name, prop_schema)

            lines.append(
                f"    | {field_cell} | {type_cell} | {description_text} |"
            )

        return "\n".join(lines)

    @staticmethod
    def _render_field_name(name: str, is_required: bool) -> str:
        """Render field name cell with required marker."""
        escaped = md_escape(name)

        if is_required:
            return f"**`{escaped}(required)`**"

        return f"`{escaped}`"

    @staticmethod
    def _append_default_to_description(
        description_text: str,
        prop_schema: Json,
        is_required: bool,
    ) -> str:
        """Add default/const info to description in a consistent way."""
        rendered_default = default_repr(prop_schema, omit_null=True)

        if rendered_default and is_required:
            return f"{description_text} Must be exactly {rendered_default}."

        if rendered_default:
            return f"{description_text} Default: {rendered_default}."

        return description_text

    def _render_type(self, prop_name: str, prop_schema: Json) -> str:
        """
        Render type with special links for known collections and $ref defs.
        """
        if prop_name == "elements":
            return TypeLinkContext(
                anchor="elements", label="Element"
            ).render_array()
        if prop_name == "boundaries":
            return TypeLinkContext(
                anchor="boundaries", label="Boundary"
            ).render_array()

        array_schema = array_variant(prop_schema)
        if array_schema is not None:
            return self._render_array_type(array_schema)

        obj_schema = object_variant(prop_schema)
        if obj_schema is not None and "$ref" in obj_schema:
            ref_name = resolve_ref_name(obj_schema)
            if ref_name:
                link = TypeLinkContext(anchor=slug(ref_name), label=ref_name)
                return (
                    link.render_enum()
                    if self._is_enum_def(ref_name)
                    else link.render_object()
                )

        return primitive_union_repr(prop_schema)


    def _render_array_type(self, array_schema: Json) -> str:
        """Render array type including array item $ref / union refs."""
        items_schema = array_schema.get("items", {})
        if not isinstance(items_schema, dict):
            return "<code>array</code>"

        direct_ref = resolve_ref_name(items_schema)
        if direct_ref:
            return TypeLinkContext(
                anchor=slug(direct_ref), label=direct_ref
            ).render_array()

        union_refs = anyof_ref_names(items_schema) or oneof_ref_names(items_schema)
        if union_refs:
            if len(union_refs) == 1:
                only = union_refs[0]
                return TypeLinkContext(
                    anchor=slug(only), label=only
                ).render_array()

            parts = []

            for ref in union_refs:
                if ref in self.defs:
                    link = TypeLinkContext(anchor=slug(ref), label=ref)
                    parts.append(link.render_object())
                else:
                    parts.append(f"`{ref}`")

            union = "\\|".join(parts)

            if len(union) > 50 and len(parts) > 3:
                first, *others = parts
                union = "<br/>&nbsp;\\|".join(others)

                return f"<code>array[<br/>&nbsp;{first}<br/>&nbsp;\\|{union}<br/>]</code>"

            return f"<code>array[{union}]</code>"

        if items_schema.get("type") == "string":
            return "<code>array[string]</code>"

        if items_schema.get("type") == "array":
            nested_items = items_schema.get("items", {})
            if (
                isinstance(nested_items, dict)
                and nested_items.get("type") == "string"
            ):
                return "<code>array[array[string]]</code>"

        return "<code>array</code>"

    def _render_diagram_components(self) -> list[str]:
        """
        Render high-level sections (elements/boundaries/relationships/layouts).
        """
        top_properties: Json = self.diagram_spec.get("properties", {}) or {}

        section_order = [
            ("Elements", "elements"),
            ("Boundaries", "boundaries"),
            ("Relationships", "relationships"),
            ("Layouts", "layouts"),
        ]

        sections: list[str] = []
        for heading, prop_name in section_order:
            prop_schema = top_properties.get(prop_name)
            if not isinstance(prop_schema, dict):
                continue

            variants = self._complex_field_variants(prop_schema)
            if not variants:
                variants = self._fallback_array_item_ref(prop_schema)

            if variants:
                sections.append(self._render_complex_section(heading, variants))

        return sections

    @staticmethod
    def _fallback_array_item_ref(prop_schema: Json) -> list[str]:
        """Fallback to a single items $ref if anyOf is not used."""
        array_schema = array_variant(prop_schema)
        items_schema = array_schema.get("items") if array_schema else None

        if isinstance(items_schema, dict):
            ref_name = resolve_ref_name(items_schema)
            return [ref_name] if ref_name else []

        return []

    @staticmethod
    def _complex_field_variants(prop_schema: Json) -> list[str]:
        """Extract item variants from array items.anyOf as $ref names."""
        array_schema = array_variant(prop_schema)
        if array_schema is None:
            return []

        items_schema = array_schema.get("items", {})
        if not isinstance(items_schema, dict):
            return []

        if "anyOf" in items_schema:
            return anyof_ref_names(items_schema)

        ref_name = resolve_ref_name(items_schema)

        return [ref_name] if ref_name else []

    def _render_complex_section(
        self,
        title: str,
        variants: list[str],
    ) -> str:
        """
        Render a section listing variant definitions and linked enum defs.
        """
        lines: list[str] = [f"### {title}", ""]

        for variant in variants:
            lines.append(f"- [{variant}](#{slug(variant)})")

        enum_defs = self._find_enum_defs_used_by_variants(variants)
        if enum_defs:
            lines.append("")
            for parent_variant, enum_name in enum_defs:
                lines.append(f"- [{parent_variant} types](#{slug(enum_name)})")

        lines.append("")
        return "\n".join(lines)

    def _find_enum_defs_used_by_variants(
        self, variants: list[str]
    ) -> list[tuple[str, str]]:
        """Find enum definitions referenced by the listed object variants."""
        enum_links: list[tuple[str, str]] = []

        for variant in variants:
            variant_schema = self.defs.get(variant)
            if not isinstance(variant_schema, dict):
                continue

            properties = variant_schema.get("properties", {}) or {}
            if not isinstance(properties, dict):
                continue

            for _property_name, property_schema in properties.items():
                if not isinstance(property_schema, dict):
                    continue

                direct_ref = resolve_ref_name(property_schema)
                if direct_ref and self._is_enum_def(direct_ref):
                    enum_links.append((variant, direct_ref))

                for option in schema_union_options(property_schema):
                    option_ref = resolve_ref_name(option)
                    if option_ref and self._is_enum_def(option_ref):
                        enum_links.append((variant, option_ref))

        enum_links = [(parent, enum_name) for parent, enum_name in enum_links]
        deduped: list[tuple[str, str]] = []
        seen_enum_names: set[str] = set()
        for parent, enum_name in enum_links:
            if enum_name not in seen_enum_names:
                deduped.append((parent, enum_name))
                seen_enum_names.add(enum_name)
        return deduped

    def _is_enum_def(self, def_name: str) -> bool:
        """Check whether a $defs entry is an enum."""
        def_schema = self.defs.get(def_name)
        return isinstance(def_schema, dict) and is_enum_schema(def_schema)

    @staticmethod
    def _render_note_on_aliases() -> list[str]:
        """Render a reusable note about labels and aliases."""
        return [
            '???+ warning "About **labels** and **aliases**"',
            "",
            "    `label` is a display name for the element.",
            "    ",
            "    `alias` is a unique identifier used for referencing elements ",
            "    in relationships and layouts.",
            "    If omitted, it is generated automatically.",
            "    ",
            "    ",
            "    You can also use `label` for referencing elements in relationships "
            "    and layouts, but each `label` must be **unique** within the diagram.",
            "",
            "",
            "<br/>",
            "",
        ]

    def _render_definitions(
        self,
        include: list[str] | None = None,
        exclude: list[str] | None = None,
    ) -> list[str]:
        """Render all definitions as subsections."""
        names = sort_by_preferred(list(self.defs.keys()), DEFINITIONS_ORDER)

        out: list[str] = []
        for name in names:
            if include and name not in include:
                continue

            if exclude and name in exclude:
                continue

            def_schema = self.defs.get(name)
            if not isinstance(def_schema, dict):
                continue

            if is_enum_schema(def_schema):
                out.append(self._render_enum_def(name, def_schema))
            else:
                out.append(self._render_object_def(name, def_schema))

        return out

    def _render_enum_def(self, name: str, schema: Json) -> str:
        """Render an enum definition section."""
        lines: list[str] = [f"### {name}", ""]
        description = schema.get("description", "") or ""
        if description:
            lines.extend([description, ""])

        values = schema.get("enum", []) or []
        if isinstance(values, list):
            values = sorted(values)
        else:
            values = []

        enum_type = self.def_type_map.get(name)
        descriptions: dict[Any, str] = {}
        if enum_type and issubclass(enum_type, EnumDescriptionsMixin):
            descriptions = enum_type.get_descriptions()  # type: ignore[attr-defined]

        if descriptions:
            lines.extend([
                '???+ info "Items"',
                "",
                '    <div class="code-nowrap"></div>',
                "    ",
                "    | Type | Description |",
                "    |---|---|",
            ])
            for val in values:
                item_desc = descriptions[val]
                lines.append(f"    | `{val!s}` | {item_desc} |")
        else:
            for val in values:
                item_desc = descriptions.get(val)
                if item_desc:
                    lines.append(f"- `{val!s}` - {item_desc}")
                else:
                    lines.append(f"- `{md_escape(str(val))}`")

        lines.append("")
        return "\n".join(lines)

    def _render_object_def(self, name: str, schema: Json) -> str:
        """Render an object definition section."""
        lines: list[str] = [f"### {name}", ""]

        model_type = self.def_type_map.get(name)
        if model_type and model_type.__doc__:
            doc = cleandoc(model_type.__doc__)
            if doc:
                lines.extend([doc, ""])

        description = schema.get("description", "") or ""
        if description:
            lines.extend([description, ""])

        lines.append(self._render_properties_table(schema))
        lines.append("")
        return "\n".join(lines)


def generate(
    spec_path: Path, md_path: Path, diagram_schema: type[BaseDiagramSchema]
) -> None:
    """Generate docs for a single diagram schema."""
    generator = DiagramSpecDocsGenerator(
        spec_path=spec_path,
        md_path=md_path,
        diagram_schema=diagram_schema,
    )
    generator.generate()


def main() -> None:
    """Generate docs for all registered diagram schemas."""
    for diagram_schema in DIAGRAMS_SCHEMAS:
        diagram_cls = diagram_schema.__diagram_class__
        diagram_name = camel_to_snake(diagram_cls.__name__)

        spec_path = SPECS_DIR / f"{diagram_name}.json"
        md_path = MD_SPECS_DIR / f"{diagram_name}.md"

        generate(
            spec_path=spec_path,
            md_path=md_path,
            diagram_schema=diagram_schema,
        )


if __name__ == "__main__":
    main()

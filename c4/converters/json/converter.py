from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import IO, Annotated, Any, cast

from pydantic import Field, TypeAdapter, ValidationError

from c4.converters.exceptions import (
    ConversionError,
    DiagramJSONSchemaParsingError,
    DiagramJSONSchemaValidationError,
    ElementResolutionConflictError,
    ElementResolutionError,
)
from c4.converters.json.schemas import (
    ComponentDiagramSchema,
    ContainerDiagramSchema,
    DeploymentDiagramSchema,
    DynamicDiagramSchema,
    SystemContextDiagramSchema,
    SystemLandscapeDiagramSchema,
)
from c4.converters.json.schemas.diagrams.common import (
    BoundaryBase,
    ElementBase,
    RelationshipSchema,
)
from c4.diagrams.core import Boundary, Diagram, Element
from c4.renderers import RenderOptions

AnyDiagramSchema = Annotated[
    (
        SystemContextDiagramSchema
        | SystemLandscapeDiagramSchema
        | ContainerDiagramSchema
        | ComponentDiagramSchema
        | DeploymentDiagramSchema
        | DynamicDiagramSchema
    ),
    Field(discriminator="type"),
]

DiagramSchemaAdapter: TypeAdapter = TypeAdapter(AnyDiagramSchema)


def _format_validation_error_loc(loc: Iterable[Any]) -> str:
    parts = ["root"]

    for item in loc:
        if isinstance(item, int):
            parts[-1] = f"{parts[-1]}[{item}]"
        else:
            parts.append(str(item))

    return "->".join(parts)


def format_validation_error(exc: ValidationError) -> str:
    """Format a pydantic validation error into a human-readable string."""
    lines: list[str] = []
    errors = exc.errors()

    for error in errors:
        error_type = error["type"]
        loc = error.get("loc", ())
        msg = error["msg"]

        if error_type == "union_tag_invalid" and not loc:
            lines.append(msg)
            continue

        path = _format_validation_error_loc(loc)
        lines.append(f"{path}: {msg}")

    return "\n".join(lines)


class JSONToDiagramConverter:
    """Convert a validated JSON diagram schema into a diagram object."""

    _diagram_schema: AnyDiagramSchema

    def __init__(self, data: Mapping[str, Any]) -> None:
        """
        Initialize the converter from raw JSON-compatible mapping data.

        Args:
            data: Parsed diagram payload that matches the expected JSON
                schema structure.
        """
        try:
            self._diagram_schema = DiagramSchemaAdapter.validate_python(data)
        except ValidationError as exc:
            message = format_validation_error(exc)

            raise DiagramJSONSchemaValidationError(message) from None

        diagram = self._diagram_schema.__diagram_class__(
            title=self._diagram_schema.title,
        )

        self._diagram = cast(Diagram, diagram)

    def _add_base_elements(self) -> None:
        """Add dynamic diagram base elements after main content creation."""
        base_elements = []
        if isinstance(self._diagram_schema, DynamicDiagramSchema):
            base_elements = self._diagram_schema.relationships

        for base_element_schema in base_elements:
            if isinstance(base_element_schema, RelationshipSchema):
                self._add_relationship(base_element_schema)
            else:
                base_element_schema.to_diagram_element()

    def _add_boundary(self, boundary_schema: BoundaryBase) -> None:
        """Create a boundary and populate its nested content."""
        boundary = cast(Boundary, boundary_schema.to_diagram_element())

        with boundary:
            self._add_elements(boundary_schema)
            self._add_boundaries(boundary_schema)
            self._add_relationships(boundary_schema)

    def _add_boundaries(self, parent: AnyDiagramSchema | BoundaryBase) -> None:
        """Add all boundaries declared on the given parent schema."""
        boundaries = getattr(parent, "boundaries", [])

        for boundary_schema in cast(list[BoundaryBase], boundaries):
            self._add_boundary(boundary_schema)

    def _add_elements(self, parent: AnyDiagramSchema | BoundaryBase) -> None:
        """Add all direct elements declared on the given parent schema."""
        elements = getattr(parent, "elements", [])

        for element_schema in cast(list[ElementBase], elements):
            element_schema.to_diagram_element()

    def _add_layouts(self) -> None:
        """Add layouts using already resolved diagram elements."""
        for layout_schema in self._diagram_schema.layouts:
            layout_schema.to_diagram_element(
                from_element=self._resolve_element(layout_schema.from_),
                to_element=self._resolve_element(layout_schema.to),
            )

    def _add_relationship(
        self,
        relationship_schema: RelationshipSchema,
    ) -> None:
        """Add a relationship between two resolved diagram elements."""
        relationship_schema.to_diagram_element(
            from_element=self._resolve_element(relationship_schema.from_),
            to_element=self._resolve_element(relationship_schema.to),
        )

    def _add_relationships(
        self, parent: AnyDiagramSchema | BoundaryBase
    ) -> None:
        """Add all relationships declared on the given parent schema."""
        for relationship_schema in self._get_relationships(parent):
            self._add_relationship(relationship_schema)

    def _get_relationships(
        self, parent: AnyDiagramSchema | BoundaryBase
    ) -> list[RelationshipSchema]:
        """Return relationships for a parent, excluding dynamic diagrams."""
        if isinstance(parent, DynamicDiagramSchema):
            return []

        relationships = getattr(parent, "relationships", [])

        return cast(list[RelationshipSchema], relationships)

    def _resolve_element(self, alias_or_label: str) -> Element:
        """Resolve an element by alias first, then by unique label."""
        element = self._diagram.get_element_by_alias(alias_or_label)

        if not element:
            elements = self._diagram.get_elements_by_label(alias_or_label)

            if not elements:
                raise ElementResolutionError(alias_or_label)

            if len(elements) > 1:
                raise ElementResolutionConflictError(
                    label=alias_or_label,
                    conflicted_elements=elements,
                )

            element = elements[0]

        return element

    def _set_render_options(self) -> None:
        """Set rendering options for the diagram."""
        render_options_kwargs = {}
        render_options_schema = self._diagram_schema.render_options

        if render_options_schema and render_options_schema.plantuml:
            layout_config = render_options_schema.plantuml.to_layout_config()
            render_options_kwargs["plantuml"] = layout_config

        if render_options_kwargs:
            self._diagram.render_options = RenderOptions(
                **render_options_kwargs,
            )

    def convert(self) -> Diagram:
        """Build the full diagram and return the populated instance."""
        try:
            with self._diagram:
                self._add_elements(self._diagram_schema)
                self._add_boundaries(self._diagram_schema)
                self._add_relationships(self._diagram_schema)
                self._add_layouts()
                self._add_base_elements()
                self._set_render_options()
        except ValueError as exc:
            raise ConversionError(str(exc)) from None

        return self._diagram


def diagram_from_dict(data: Mapping[str, Any]) -> Diagram:
    """Build a Diagram from a Python dict."""
    converter = JSONToDiagramConverter(data)
    return converter.convert()


def diagram_from_json(
    src: str | bytes | Path | IO[str] | IO[bytes],
) -> Diagram:
    """
    Parse JSON into a Diagram.

    Args:
        src: JSON string/bytes, a Path, or a file-like object.

    Raises:
        ValueError: Invalid JSON or invalid structure/schema.
        TypeError: Wrong types in the JSON payload.
    """
    try:
        if isinstance(src, Path):
            raw = src.read_text(encoding="utf-8")
            data = json.loads(raw)
        elif isinstance(src, (str, bytes)):
            data = json.loads(src)
        else:
            data = json.load(src)
    except json.JSONDecodeError as exc:
        raise DiagramJSONSchemaParsingError(str(exc)) from None

    return diagram_from_dict(data)

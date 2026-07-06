from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import IO, Annotated, Any, cast

from pydantic import BaseModel, Field, TypeAdapter, ValidationError

from c4.constants import D2, MERMAID, PLANTUML
from c4.contrib.d2.converters.json.render_options import (
    D2RenderOptionsSchema,
)
from c4.contrib.d2.converters.json.schemas import (
    D2ComponentDiagramSchema,
    D2ContainerDiagramSchema,
    D2DeploymentDiagramSchema,
    D2DynamicDiagramSchema,
    D2SystemContextDiagramSchema,
    D2SystemLandscapeDiagramSchema,
)
from c4.contrib.mermaid.converters.json.render_options import (
    MermaidRenderOptionsSchema,
)
from c4.contrib.mermaid.converters.json.schemas import (
    MermaidComponentDiagramSchema,
    MermaidContainerDiagramSchema,
    MermaidDeploymentDiagramSchema,
    MermaidDynamicDiagramSchema,
    MermaidSystemContextDiagramSchema,
    MermaidSystemLandscapeDiagramSchema,
)
from c4.contrib.plantuml.converters.json.render_options import (
    PlantUMLRenderOptionsSchema,
)
from c4.contrib.plantuml.converters.json.schemas import (
    LayoutSchema,
    PlantUMLComponentDiagramSchema,
    PlantUMLContainerDiagramSchema,
    PlantUMLDeploymentDiagramSchema,
    PlantUMLDynamicDiagramSchema,
    PlantUMLSystemContextDiagramSchema,
    PlantUMLSystemLandscapeDiagramSchema,
)
from c4.converters.exceptions import (
    ConversionError,
    DiagramJSONSchemaParsingError,
    DiagramJSONSchemaValidationError,
    ElementResolutionConflictError,
    ElementResolutionError,
)
from c4.converters.json.schemas.backends import (
    CoreComponentDiagramSchema,
    CoreContainerDiagramSchema,
    CoreDeploymentDiagramSchema,
    CoreDynamicDiagramSchema,
    CoreSystemContextDiagramSchema,
    CoreSystemLandscapeDiagramSchema,
)
from c4.converters.json.schemas.base import BaseSchemaItem
from c4.converters.json.schemas.diagrams.common import (
    BoundaryBase,
    ElementBase,
    RelationshipSchema,
)
from c4.diagrams.core import Boundary, Diagram, Element
from c4.enums import RendererEnum
from c4.renderers import RenderOptions
from c4.renderers.d2.validation import validate_d2_diagram
from c4.renderers.mermaid.validation import validate_mermaid_diagram
from c4.renderers.plantuml.validation import validate_plantuml_diagram

AnyCoreDiagramSchema = Annotated[
    (
        CoreSystemContextDiagramSchema
        | CoreSystemLandscapeDiagramSchema
        | CoreContainerDiagramSchema
        | CoreComponentDiagramSchema
        | CoreDeploymentDiagramSchema
        | CoreDynamicDiagramSchema
    ),
    Field(discriminator="type"),
]
AnyPlantUMLDiagramSchema = Annotated[
    (
        PlantUMLSystemContextDiagramSchema
        | PlantUMLSystemLandscapeDiagramSchema
        | PlantUMLContainerDiagramSchema
        | PlantUMLComponentDiagramSchema
        | PlantUMLDeploymentDiagramSchema
        | PlantUMLDynamicDiagramSchema
    ),
    Field(discriminator="type"),
]
AnyMermaidDiagramSchema = Annotated[
    (
        MermaidSystemContextDiagramSchema
        | MermaidSystemLandscapeDiagramSchema
        | MermaidContainerDiagramSchema
        | MermaidComponentDiagramSchema
        | MermaidDeploymentDiagramSchema
        | MermaidDynamicDiagramSchema
    ),
    Field(discriminator="type"),
]
AnyD2DiagramSchema = Annotated[
    (
        D2SystemContextDiagramSchema
        | D2SystemLandscapeDiagramSchema
        | D2ContainerDiagramSchema
        | D2ComponentDiagramSchema
        | D2DeploymentDiagramSchema
        | D2DynamicDiagramSchema
    ),
    Field(discriminator="type"),
]
AnyDiagramSchema = (
    AnyCoreDiagramSchema
    | AnyPlantUMLDiagramSchema
    | AnyMermaidDiagramSchema
    | AnyD2DiagramSchema
)

CoreDiagramSchemaAdapter: TypeAdapter = TypeAdapter(AnyCoreDiagramSchema)
PlantUMLDiagramSchemaAdapter: TypeAdapter = TypeAdapter(
    AnyPlantUMLDiagramSchema
)
MermaidDiagramSchemaAdapter: TypeAdapter = TypeAdapter(AnyMermaidDiagramSchema)
D2DiagramSchemaAdapter: TypeAdapter = TypeAdapter(AnyD2DiagramSchema)

DiagramSchemaAdapters = {
    None: CoreDiagramSchemaAdapter,
    PLANTUML: PlantUMLDiagramSchemaAdapter,
    MERMAID: MermaidDiagramSchemaAdapter,
    D2: D2DiagramSchemaAdapter,
}


class BackendSchema(BaseModel):
    backend: RendererEnum | None = Field(
        None, description="JSON schema backend."
    )


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
    """
    Convert a validated JSON diagram schema into a diagram object.

    Diagram elements are created within the diagram/boundary context, so they
    will be added to the current diagram/boundary automatically.
    """

    _diagram_schema: AnyDiagramSchema
    backend: RendererEnum | None

    def __init__(self, data: Mapping[str, Any]) -> None:
        """
        Initialize the converter from raw JSON-compatible mapping data.

        Args:
            data: Parsed diagram payload that matches the expected JSON
                schema structure.
        """
        self._diagram_schema, self.backend = self._parse_diagram_schema(data)
        self._diagram = self._diagram_schema.to_diagram()

    @staticmethod
    def parse_diagram_backend(data: Mapping[str, Any]) -> RendererEnum | None:
        """Parse and resolve the diagram backend."""
        try:
            backend_schema = BackendSchema.model_validate(data)
        except ValidationError as exc:
            message = format_validation_error(exc)
            raise DiagramJSONSchemaValidationError(message) from None

        return backend_schema.backend

    def _parse_diagram_schema(
        self,
        data: Mapping[str, Any],
    ) -> tuple[AnyDiagramSchema, RendererEnum | None]:
        """Parse the diagram against the given backend schema."""
        try:
            backend = self.parse_diagram_backend(data)

            schema = DiagramSchemaAdapters[backend].validate_python(data)
            return cast(AnyDiagramSchema, schema), backend
        except ValidationError as exc:
            message = format_validation_error(exc)
            raise DiagramJSONSchemaValidationError(message) from None

    def _add_boundary(self, boundary_schema: BoundaryBase) -> None:
        """
        Create a boundary and populate its nested content.
        """
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
        """
        Add all direct elements declared on the given parent schema.
        """
        elements = getattr(parent, "elements", [])

        for element_schema in cast(list[ElementBase], elements):
            element_schema.to_diagram_element()

    def _add_backend_specific_ordered_items(self) -> None:
        """Add backend-specific ordered diagram items."""
        if self.backend is RendererEnum.PLANTUML:
            self._add_plantuml_layouts()

    def _add_plantuml_layouts(self) -> None:
        """Add layouts using already resolved diagram elements."""
        layouts = getattr(self._diagram_schema, "layouts", [])

        for layout_schema in cast(list[LayoutSchema], layouts):
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
        """Add relationships and relationship-like items declared on parent."""
        relationships = getattr(parent, "relationships", [])

        for item_schema in cast(list[BaseSchemaItem[Any]], relationships):
            if isinstance(item_schema, RelationshipSchema):
                self._add_relationship(item_schema)
            else:
                item_schema.to_diagram_element()

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
        render_options_schema: BaseSchemaItem | None = getattr(
            self._diagram_schema, "render_options", None
        )
        if not render_options_schema:
            return

        render_options: dict[str, Any] = {
            "plantuml": None,
            "mermaid": None,
            "d2": None,
        }

        if isinstance(render_options_schema, PlantUMLRenderOptionsSchema):
            render_options["plantuml"] = (
                render_options_schema.to_render_options()
            )
        elif isinstance(render_options_schema, MermaidRenderOptionsSchema):
            render_options["mermaid"] = (
                render_options_schema.to_render_options()
            )
        elif isinstance(render_options_schema, D2RenderOptionsSchema):
            render_options["d2"] = render_options_schema.to_render_options()

        if any(render_options.values()):
            self._diagram.render_options = RenderOptions(**render_options)

    def _validate_backend_specific_diagram(self) -> None:
        """Run semantic validations that depend on the selected backend."""
        validators = {
            RendererEnum.PLANTUML: validate_plantuml_diagram,
            RendererEnum.MERMAID: validate_mermaid_diagram,
            RendererEnum.D2: validate_d2_diagram,
        }

        if validator := validators.get(self.backend):  # type: ignore[arg-type]
            try:
                validator(self._diagram)
            except ValueError as exc:
                raise DiagramJSONSchemaValidationError(str(exc)) from None

    def convert(self) -> Diagram:
        """Build the full diagram and return the populated instance."""
        try:
            with self._diagram:
                self._add_elements(self._diagram_schema)
                self._add_boundaries(self._diagram_schema)
                self._add_relationships(self._diagram_schema)
                self._add_backend_specific_ordered_items()
                self._set_render_options()
                self._validate_backend_specific_diagram()
        except ValueError as exc:
            raise ConversionError(str(exc)) from None

        return self._diagram


def diagram_from_dict(
    data: Mapping[str, Any],
) -> tuple[Diagram, RendererEnum | None]:
    """Build a diagram from a parsed JSON mapping."""
    converter = JSONToDiagramConverter(data)

    return converter.convert(), converter.backend


def _load_json_data(
    src: str | bytes | Path | IO[str] | IO[bytes],
) -> Any:
    """
    Load JSON-compatible data from a string, path, or file-like object.
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

    return data


def diagram_backend_from_json(
    src: str | bytes | Path | IO[str] | IO[bytes],
) -> RendererEnum | None:
    """
    Parse JSON diagram schema and return its declared backend.

    This validates the payload with the same schema selection logic used by
    full JSON diagram conversion, but does not build diagram relationships.
    """
    data = _load_json_data(src)

    return JSONToDiagramConverter.parse_diagram_backend(data)


def diagram_from_json(
    src: str | bytes | Path | IO[str] | IO[bytes],
) -> tuple[Diagram, RendererEnum | None]:
    """
    Parse JSON into a Diagram.

    Args:
        src: JSON string/bytes, a Path, or a file-like object.

    Raises:
        ValueError: Invalid JSON or invalid structure/schema.
        TypeError: Wrong types in the JSON payload.
    """
    data = _load_json_data(src)

    return diagram_from_dict(data)

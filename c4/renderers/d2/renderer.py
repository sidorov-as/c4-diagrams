from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Generic

from typing_extensions import override

from c4 import (
    ContainerBoundary,
    DiagramFormat,
    EnterpriseBoundary,
    SystemBoundary,
)
from c4.diagrams.component import (
    Component,
    ComponentDb,
    ComponentDbExt,
    ComponentExt,
    ComponentQueue,
    ComponentQueueExt,
)
from c4.diagrams.container import (
    Container,
    ContainerDb,
    ContainerDbExt,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
)
from c4.diagrams.core import (
    BaseDiagramElement,
    Boundary,
    DiagramElementProperties,
    Element,
    Relationship,
    TDiagram,
)
from c4.diagrams.core.enums import RelationshipType
from c4.diagrams.dynamic import DynamicDiagram
from c4.diagrams.system_context import (
    Person,
    PersonExt,
    System,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemQueue,
    SystemQueueExt,
)
from c4.enums import RendererEnum
from c4.exceptions import D2BackendConfigurationError
from c4.renderers.base import (
    IGNORE_FOREIGN,
    BaseRenderer,
    ExtensionValidationModeType,
)
from c4.renderers.d2.backends import BaseD2Backend
from c4.renderers.d2.formatting import (
    D2StringBuilder,
    d2_label,
    d2_markdown_value,
    is_d2_markdown_value,
    quote_d2_string,
)
from c4.renderers.d2.identifiers import D2Identifier, D2IdentifierPolicy
from c4.renderers.d2.options import (
    D2LegendElement,
    D2LegendRel,
    D2RenderOptions,
)
from c4.renderers.d2.validation import (
    D2UnresolvedRelationshipEndpointError,
    validate_d2_diagram,
)

_DATABASE_ELEMENTS = (
    SystemDb,
    SystemDbExt,
    ContainerDb,
    ContainerDbExt,
    ComponentDb,
    ComponentDbExt,
)
_QUEUE_ELEMENTS = (
    SystemQueue,
    SystemQueueExt,
    ContainerQueue,
    ContainerQueueExt,
    ComponentQueue,
    ComponentQueueExt,
)
_EXTERNAL_ELEMENTS = (
    PersonExt,
    SystemExt,
    SystemDbExt,
    SystemQueueExt,
    ContainerExt,
    ContainerDbExt,
    ContainerQueueExt,
    ComponentExt,
    ComponentDbExt,
    ComponentQueueExt,
)
_BIDIRECTIONAL_RELATIONSHIP_TYPES = {
    RelationshipType.BI_REL,
    RelationshipType.BI_REL_NEIGHBOR,
    RelationshipType.BI_REL_D,
    RelationshipType.BI_REL_DOWN,
    RelationshipType.BI_REL_U,
    RelationshipType.BI_REL_UP,
    RelationshipType.BI_REL_L,
    RelationshipType.BI_REL_LEFT,
    RelationshipType.BI_REL_R,
    RelationshipType.BI_REL_RIGHT,
}

_D2_EXTENSION_KEY = "d2"
_D2_ATTRIBUTE_KEYS = (
    "shape",
    "icon",
    "near",
    "tooltip",
    "link",
    "direction",
)
_PRESET_CLASSES = {
    "c4_person": (
        ("style.fill", "#f5f1ff"),
        ("style.stroke", "#6f4bb2"),
        ("style.font-color", "#211436"),
    ),
    "c4_external": (
        ("style.fill", "#f7f7f7"),
        ("style.stroke", "#767676"),
        ("style.stroke-dash", "5"),
    ),
    "c4_database": (
        ("style.fill", "#edf7ff"),
        ("style.stroke", "#2d6f9f"),
    ),
    "c4_queue": (
        ("style.fill", "#fff6e5"),
        ("style.stroke", "#9b6500"),
    ),
}
_STYLE_KEY_RENAMES = {
    "fill_pattern": "fill-pattern",
    "stroke_width": "stroke-width",
    "stroke_dash": "stroke-dash",
    "border_radius": "border-radius",
    "three_d": "3d",
    "double_border": "double-border",
    "font_size": "font-size",
    "font_color": "font-color",
    "text_transform": "text-transform",
}
_C4_TYPE_NAMES = (
    (Person, "Person"),
    (SystemDb, "Software System"),
    (SystemQueue, "Software System"),
    (System, "Software System"),
    (ContainerDb, "Container"),
    (ContainerQueue, "Container"),
    (Container, "Container"),
    (ComponentDb, "Component"),
    (ComponentQueue, "Component"),
    (Component, "Component"),
    (EnterpriseBoundary, "Enterprise"),
    (SystemBoundary, "System"),
    (ContainerBoundary, "Container"),
    (Boundary, "Boundary"),
)


class D2Renderer(BaseRenderer[TDiagram], Generic[TDiagram]):
    """A renderer for converting a Diagram object into D2 syntax."""

    renderer_type: RendererEnum = RendererEnum.D2

    def __init__(
        self,
        render_options: D2RenderOptions | None = None,
        backend: BaseD2Backend | None = None,
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            render_options: Render options that control D2 text rendering.
            backend: Optional D2 backend used for image rendering.
            extension_validation_mode: Policy for foreign backend extensions.
        """
        super().__init__(extension_validation_mode=extension_validation_mode)
        self._render_options = render_options or D2RenderOptions()
        self._d2_backend = backend
        self._identifiers: dict[str, D2Identifier] = {}
        self._relationship_index = 0

    @override
    def validate(self, diagram: TDiagram) -> None:
        """Validate D2-specific rendering constraints."""
        validate_d2_diagram(
            diagram,
            extension_validation_mode=self._extension_validation_mode,
        )

    def _get_render_options(self, diagram: TDiagram) -> D2RenderOptions:
        render_options = self._render_options
        if diagram.render_options and diagram.render_options.d2:
            render_options = diagram.render_options.d2

        return render_options

    @override
    def render(self, diagram: TDiagram) -> str:
        """
        Render the given Diagram into D2 format.

        Args:
            diagram: The diagram to render.

        Returns:
            A D2-formatted string representing the diagram.
        """
        render_options = self._get_render_options(diagram)

        original_render_options = self._render_options
        self._render_options = render_options

        builder = D2StringBuilder()

        try:
            self.validate(diagram)
            self._identifiers = D2IdentifierPolicy(strict=True).build(
                diagram,
                self,
            )
            self._relationship_index = 0

            self._render_header(builder, diagram)
            self._render_legend(builder)
            self._render_preset_classes(builder, diagram)

            for item in self.iter_render_items(diagram):
                self._render_item(builder, item)

            return f"{builder.get_result()}\n"
        finally:
            self._render_options = original_render_options

    def _render_header(
        self,
        builder: D2StringBuilder,
        diagram: TDiagram,
    ) -> None:
        if self._render_options.direction is not None:
            builder.add(f"direction: {self._render_options.direction}")

        if diagram.title:
            self._render_title(builder, diagram.title)

        if self._render_options.sequence_diagram and isinstance(
            diagram, DynamicDiagram
        ):
            builder.add("shape: sequence_diagram")

        if self._render_options.theme is not None:
            builder.add(f"theme: {self._render_options.theme}")

    def _render_title(self, builder: D2StringBuilder, title: str) -> None:
        title_value = d2_markdown_value(f"# {title}")
        title_near = self._render_options.title_near

        if title_near is None:
            builder.add(f"{D2IdentifierPolicy.TITLE_IDENTIFIER}: {title_value}")
            return

        builder.add(f"{D2IdentifierPolicy.TITLE_IDENTIFIER}: {title_value} {{")
        with builder.indent():
            builder.add(f"near: {title_near}")
        builder.add("}")

    def _render_legend(self, builder: D2StringBuilder) -> None:
        legend = self._render_options.legend
        if legend is None:
            return

        endpoint_hides: list[tuple[str, str]] = []
        hidden_endpoints: set[tuple[str, str]] = set()

        with builder.block("vars"):
            builder.add(f"d2-legend: {quote_d2_string(legend.label)} {{")
            with builder.indent():
                for index, item in enumerate(legend.items, start=1):
                    identifier = item.alias or f"legend_{index}"

                    if isinstance(item, D2LegendElement):
                        self._render_legend_element(
                            builder,
                            item,
                            identifier,
                        )
                        continue

                    self._render_legend_relationship(
                        builder,
                        item,
                        identifier,
                        endpoint_hides,
                        hidden_endpoints,
                    )

                for _, line in endpoint_hides:
                    builder.add(line)

            builder.add("}")

    def _render_legend_element(
        self,
        builder: D2StringBuilder,
        item: D2LegendElement,
        identifier: str,
    ) -> None:
        with builder.block(identifier):
            builder.add(f"label: {quote_d2_string(item.label)}")
            if item.shape is not None:
                shape = self._format_d2_attribute(item, "shape")
                builder.add(f"shape: {shape}")

            if item.icon is not None:
                icon = self._format_d2_attribute(item, "icon")
                builder.add(f"icon: {icon}")

            for name, value in self._d2_style_attributes(item.style):
                builder.add(f"{name}: {value}")

            if item.classes is not None:
                builder.add(f"class: {self._format_d2_classes(item.classes)}")

    def _render_legend_relationship(
        self,
        builder: D2StringBuilder,
        item: D2LegendRel,
        identifier: str,
        endpoint_hides: list[tuple[str, str]],
        hidden_endpoints: set[tuple[str, str]],
    ) -> None:
        has_explicit_endpoints = (
            item.source is not None and item.target is not None
        )
        source = (
            item.source if item.source is not None else f"{identifier}_source"
        )
        target = (
            item.target if item.target is not None else f"{identifier}_target"
        )
        hide_endpoints = item.hide_endpoints

        if hide_endpoints is None:
            hide_endpoints = not has_explicit_endpoints

        connector = "<->" if item.bidirectional else "->"

        with builder.block(f"{source} {connector} {target}"):
            builder.add(f"label: {quote_d2_string(item.label)}")
            for name, value in self._d2_style_attributes(item.style):
                builder.add(f"{name}: {value}")
            if item.classes is not None:
                builder.add(f"class: {self._format_d2_classes(item.classes)}")

        if not hide_endpoints:
            return

        for endpoint in (source, target):
            key = (endpoint, "style.opacity")
            if key in hidden_endpoints:
                continue

            hidden_endpoints.add(key)
            endpoint_hides.append((endpoint, f"{endpoint}.style.opacity: 0"))

    def _render_preset_classes(
        self,
        builder: D2StringBuilder,
        diagram: TDiagram,
    ) -> None:
        class_names = self._used_preset_classes(diagram)
        if not class_names:
            return

        with builder.block("classes"):
            for class_name in class_names:
                with builder.block(class_name):
                    for name, value in _PRESET_CLASSES[class_name]:
                        builder.add(f"{name}: {quote_d2_string(value)}")

    def _used_preset_classes(self, diagram: TDiagram) -> list[str]:
        class_names: set[str] = set()

        for item in self.iter_render_items(diagram):
            self._collect_preset_classes(item, class_names)

        return [  # pragma: no branch
            class_name
            for class_name in _PRESET_CLASSES
            if class_name in class_names
        ]

    def _collect_preset_classes(
        self,
        item: BaseDiagramElement,
        class_names: set[str],
    ) -> None:
        if isinstance(item, Element):
            for class_name in self._element_preset_classes(item):
                class_names.add(class_name)

        if isinstance(item, Boundary):
            for child in self.iter_boundary_render_items(item):
                self._collect_preset_classes(child, class_names)

    def _render_item(
        self,
        builder: D2StringBuilder,
        item: BaseDiagramElement,
        *,
        parent_path: tuple[str, ...] = (),
    ) -> None:
        if isinstance(item, Boundary):
            self._render_boundary(builder, item, parent_path=parent_path)
            return

        if isinstance(item, Element):
            self._render_element(builder, item, parent_path=parent_path)
            return

        if isinstance(item, Relationship):
            self._render_relationship(builder, item, parent_path=parent_path)
            return

        raise TypeError(f"Unsupported D2 render item {item!r}")

    def _render_boundary(
        self,
        builder: D2StringBuilder,
        boundary: Boundary,
        *,
        parent_path: tuple[str, ...],
    ) -> None:
        identifier = self._identifiers[boundary.alias]
        label = self._element_label(boundary)
        attributes = self._boundary_attributes(
            boundary,
            force_default_shape=is_d2_markdown_value(label),
        )

        with builder.block(self._local_identifier(identifier, parent_path)):
            builder.add(f"label: {label}")
            for name, value in attributes:
                builder.add(f"{name}: {value}")

            for item in self.iter_boundary_render_items(boundary):
                self._render_item(
                    builder,
                    item,
                    parent_path=identifier.path,
                )

    def _render_element(
        self,
        builder: D2StringBuilder,
        element: Element,
        *,
        parent_path: tuple[str, ...],
    ) -> None:
        identifier = self._identifiers[element.alias]
        local_identifier = self._local_identifier(identifier, parent_path)
        label = self._element_label(element)
        attributes = self._element_attributes(
            element,
            force_default_shape=is_d2_markdown_value(label),
        )

        if not attributes:
            builder.add(f"{local_identifier}: {label}")
            return

        if is_d2_markdown_value(label):
            builder.add(f"{local_identifier}: {label} {{")
            with builder.indent():
                for name, value in attributes:
                    builder.add(f"{name}: {value}")
            builder.add("}")
            return

        with builder.block(local_identifier):
            builder.add(f"label: {label}")
            for name, value in attributes:
                builder.add(f"{name}: {value}")

    def _element_attributes(
        self,
        element: Element,
        *,
        force_default_shape: bool = False,
    ) -> list[tuple[str, str]]:
        attributes: dict[str, str] = {}
        classes = self._element_preset_classes(element)

        if isinstance(element, Person):
            attributes["shape"] = "c4-person"
        elif isinstance(element, _DATABASE_ELEMENTS):
            attributes["shape"] = "cylinder"
        elif isinstance(element, _QUEUE_ELEMENTS):
            attributes["shape"] = "queue"
        elif force_default_shape:
            attributes["shape"] = "rectangle"

        if classes:
            attributes["class"] = self._format_d2_classes(classes)

        attributes.update(self._d2_attributes(element))

        return list(attributes.items())

    def _boundary_attributes(
        self,
        boundary: Boundary,
        *,
        force_default_shape: bool = False,
    ) -> list[tuple[str, str]]:
        attributes: dict[str, str] = {}

        if force_default_shape:
            attributes["shape"] = "rectangle"

        attributes.update(self._d2_attributes(boundary))

        return list(attributes.items())

    def _element_preset_classes(self, element: Element) -> list[str]:
        classes = []

        if isinstance(element, Person):
            classes.append("c4_person")

        if isinstance(element, _EXTERNAL_ELEMENTS):
            classes.append("c4_external")

        if isinstance(element, _DATABASE_ELEMENTS):
            classes.append("c4_database")

        if isinstance(element, _QUEUE_ELEMENTS):
            classes.append("c4_queue")

        return classes

    def _render_relationship(
        self,
        builder: D2StringBuilder,
        relationship: Relationship,
        *,
        parent_path: tuple[str, ...],
    ) -> None:
        source: Element
        destination: Element
        source, destination = relationship.get_participants()
        source_identifier = self._resolve_relationship_endpoint(
            source.alias,
            parent_path,
            relationship=relationship,
        )
        destination_identifier = self._resolve_relationship_endpoint(
            destination.alias,
            parent_path,
            relationship=relationship,
        )
        label = self._relationship_label(relationship)

        if relationship.relationship_type in _BIDIRECTIONAL_RELATIONSHIP_TYPES:
            if (
                self._render_options.bidirectional_relationships
                == "single_edge"
            ):
                self._add_relationship_edge(
                    builder,
                    source_identifier,
                    destination_identifier,
                    label,
                    self._d2_attributes(relationship),
                    connector="<->",
                )
                return

            self._add_relationship_edge(
                builder,
                source_identifier,
                destination_identifier,
                label,
                self._d2_attributes(relationship),
            )
            self._add_relationship_edge(
                builder,
                destination_identifier,
                source_identifier,
                label,
                self._d2_attributes(relationship),
            )
            return

        self._add_relationship_edge(
            builder,
            source_identifier,
            destination_identifier,
            label,
            self._d2_attributes(relationship),
        )

    def _resolve_relationship_endpoint(
        self,
        alias: str,
        parent_path: tuple[str, ...],
        *,
        relationship: Relationship,
    ) -> str:
        identifier = self._identifiers.get(alias)
        if identifier is not None:
            return self._reference_identifier(identifier, parent_path)

        raise D2UnresolvedRelationshipEndpointError(
            "D2 relationship endpoint is not declared in the diagram: "
            f"{alias!r} for {relationship!r}."
        )

    def _relationship_label(self, relationship: Relationship) -> str | None:
        number_prefix = self._next_relationship_number_prefix()
        if self._relationship_uses_markdown_label(relationship):
            return self._relationship_markdown_label(
                relationship,
                number_prefix=number_prefix,
            )

        label_parts = []
        if relationship.label:
            label_parts.append(f"{number_prefix}{relationship.label}")
        elif number_prefix:
            label_parts.append(number_prefix.rstrip())

        if relationship.technology:
            label_parts.append(f"[{relationship.technology}]")

        if not label_parts:
            return None

        return quote_d2_string("\n".join(label_parts))

    def _next_relationship_number_prefix(self) -> str:
        if not self._render_options.auto_number_relationships:
            return ""

        self._relationship_index += 1
        return f"{self._relationship_index}. "

    def _add_relationship_edge(
        self,
        builder: D2StringBuilder,
        source_identifier: str,
        destination_identifier: str,
        label: str | None,
        attributes: list[tuple[str, str]] | None = None,
        connector: str = "->",
    ) -> None:
        edge_header = (
            f"{source_identifier} {connector} {destination_identifier}"
        )

        if attributes:
            with builder.block(edge_header):
                if label:
                    builder.add(f"label: {label}")
                for name, value in attributes:
                    builder.add(f"{name}: {value}")
            return

        if label:
            builder.add(f"{edge_header}: {label}")
            return

        builder.add(edge_header)

    def _has_renderable_properties(
        self,
        item: BaseDiagramElement,
    ) -> bool:
        return self._render_options.include_properties and bool(item.properties)

    def _element_label(self, element: Element) -> str:
        if self._element_uses_markdown_label(element):
            return self._element_markdown_label(element)

        return d2_label(
            element.label,
            element.technology,
            include_technology=self._render_options.include_technology,
        )

    def _element_uses_markdown_label(self, element: Element) -> bool:
        return bool(element.description) or self._has_renderable_properties(
            element
        )

    def _element_markdown_label(self, element: Element) -> str:
        lines = [f"## {element.label}"]
        label_metadata = self._element_label_metadata(element)
        if label_metadata:
            lines.extend(["", label_metadata])

        if element.description:
            lines.extend(["", str(element.description)])

        if self._has_renderable_properties(element):
            lines.extend(["", self._format_property_table(element.properties)])

        return d2_markdown_value("\n".join(lines))

    def _element_label_metadata(self, element: Element) -> str | None:
        type_label = (
            self._element_type_label(element)
            if self._render_options.include_type_label
            else None
        )
        technology = (
            element.technology
            if self._render_options.include_technology
            else None
        )

        if type_label and technology:
            return f"[{type_label}: {technology}]"

        if type_label:
            return f"[{type_label}]"

        if technology:
            return f"[{technology}]"

        return None

    def _element_type_label(self, element: Element) -> str:
        for element_type, label in _C4_TYPE_NAMES:
            if isinstance(element, element_type):
                return label

        return element.__class__.__name__

    def _relationship_uses_markdown_label(
        self,
        relationship: Relationship,
    ) -> bool:
        return bool(
            relationship.description
        ) or self._has_renderable_properties(relationship)

    def _relationship_markdown_label(
        self,
        relationship: Relationship,
        *,
        number_prefix: str = "",
    ) -> str:
        lines = []

        if relationship.label:
            lines.append(f"**{number_prefix}{relationship.label}**")
        elif number_prefix:
            lines.append(f"**{number_prefix.rstrip()}**")

        if relationship.description:
            if lines:
                lines.append("")
            lines.append(str(relationship.description))

        if self._has_renderable_properties(relationship):
            if lines:
                lines.append("")
            lines.append(self._format_property_table(relationship.properties))

        return d2_markdown_value("\n".join(lines))

    def _format_property_table(
        self,
        properties: DiagramElementProperties,
    ) -> str:
        rows = []

        if properties.show_header:
            rows.append(self._format_markdown_table_row(properties.header))
            rows.append(
                self._format_markdown_table_row(
                    "---" for _ in properties.header
                )
            )
        elif properties.properties:
            column_count = len(properties.properties[0])
            rows.append(
                self._format_markdown_table_row("" for _ in range(column_count))
            )
            rows.append(
                self._format_markdown_table_row(
                    "---" for _ in range(column_count)
                )
            )

        rows.extend(
            self._format_markdown_table_row(row)
            for row in properties.properties
        )

        return "\n".join(rows)

    def _format_markdown_table_row(self, values: Any) -> str:
        cells = [self._format_markdown_table_cell(value) for value in values]
        return f"| {' | '.join(cells)} |"

    def _format_markdown_table_cell(self, value: Any) -> str:
        return (
            str(value)
            .replace("\\", "\\\\")
            .replace("|", "\\|")
            .replace("\r\n", "<br>")
            .replace("\n", "<br>")
            .replace("\r", "<br>")
        )

    def _d2_attributes(
        self,
        item: BaseDiagramElement,
    ) -> list[tuple[str, str]]:
        if not item.extensions:
            return []

        extension = item.extensions.get(_D2_EXTENSION_KEY)
        if not isinstance(extension, Mapping):
            return []

        attributes: list[tuple[str, str]] = []

        for name in _D2_ATTRIBUTE_KEYS:
            if name in extension:
                value = extension[name]
                if value is not None:
                    attributes.append((
                        name,
                        self._format_d2_attribute_value(value, name=name),
                    ))

        style = extension.get("style")
        if isinstance(style, Mapping):
            attributes.extend(self._d2_style_attributes(style))

        classes = extension.get("classes")
        if isinstance(classes, list):
            attributes.append(("class", self._format_d2_classes(classes)))

        return attributes

    def _d2_style_attributes(
        self,
        style: Mapping[str, Any] | None,
    ) -> list[tuple[str, str]]:
        if not isinstance(style, Mapping):
            return []

        attributes: list[tuple[str, str]] = []
        for name, value in style.items():
            if value is None:
                continue

            style_name = _STYLE_KEY_RENAMES.get(
                str(name),
                str(name).replace("_", "-"),
            )
            attributes.append((
                f"style.{style_name}",
                self._format_d2_attribute_value(
                    value,
                    name=f"style.{style_name}",
                ),
            ))

        return attributes

    def _format_d2_attribute_value(self, value: Any, *, name: str) -> str:
        if isinstance(value, bool):
            return str(value).lower()

        if isinstance(value, (int, float)):
            return str(value)

        if name in {"shape", "direction", "near"}:
            return str(value)

        return quote_d2_string(str(value))

    def _format_d2_attribute(self, item: Any, name: str) -> str:
        return self._format_d2_attribute_value(
            value=getattr(item, name), name=name
        )

    def _format_d2_classes(self, classes: list[str]) -> str:
        values = "; ".join(
            quote_d2_string(class_name) for class_name in classes
        )
        return f"[{values}]"

    def _local_identifier(
        self,
        identifier: D2Identifier,
        parent_path: tuple[str, ...],
    ) -> str:
        """Return a D2 path relative to the current parent block."""
        if parent_path and identifier.path[: len(parent_path)] == parent_path:
            return ".".join(identifier.path[len(parent_path) :])

        return identifier.d2_path

    def _reference_identifier(
        self,
        identifier: D2Identifier,
        parent_path: tuple[str, ...],
    ) -> str:
        if self._render_options.fully_qualified_relationships:
            return identifier.d2_path

        if parent_path and identifier.path[: len(parent_path)] == parent_path:
            return ".".join(identifier.path[len(parent_path) :])

        return identifier.d2_path

    @override
    def render_bytes(
        self,
        diagram: TDiagram,
        *,
        format: DiagramFormat,
    ) -> bytes:
        """
        Render a Diagram and return raw bytes.

        This method first converts the Diagram into D2 source text
        and then delegates the actual rendering to the
        configured D2 backend.

        Args:
            diagram: The diagram instance to render.
            format: Output format of the rendered diagram.

        Returns:
            The rendered diagram content as raw bytes.

        Raises:
            D2BackendConfigurationError: If no D2 backend is
                configured for this renderer.
            D2Error: If the underlying D2 backend fails to
                render the diagram.
        """
        if not self._d2_backend:
            raise D2BackendConfigurationError(
                "D2 image export requires a configured backend. "
                "Use LocalD2Backend or configure CLI export with --d2."
            )

        diagram_source = self.render(diagram)
        render_options = self._get_render_options(diagram)

        return self._d2_backend.to_bytes(
            diagram=diagram_source,
            format=format,
            render_options=render_options,
        )

    @override
    def render_file(
        self,
        diagram: TDiagram,
        output_path: str | Path,
        *,
        format: DiagramFormat,
        overwrite: bool = True,
    ) -> Path:
        """
        Render a Diagram and write the result to a file.

        This method first converts the Diagram into D2 source text
        and then delegates file generation to the
        configured D2 backend.

        Args:
            diagram: The diagram instance to render.
            output_path: Path where the rendered diagram should be written.
            format: Output format of the rendered diagram.
            overwrite: Whether to overwrite the output file if it already
                exists.

        Returns:
            Path to the written output file.

        Raises:
            D2BackendConfigurationError: If no D2 backend is
                configured for this renderer.
            FileExistsError: If the output file exists and ``overwrite`` is
                set to ``False``.
            D2Error: If the underlying D2 backend fails to
                render or write the diagram.
        """
        if not self._d2_backend:
            raise D2BackendConfigurationError(
                "D2 image export requires a configured backend. "
                "Use LocalD2Backend or configure CLI export with --d2."
            )

        diagram_source = self.render(diagram)
        render_options = self._get_render_options(diagram)

        return self._d2_backend.to_file(
            diagram=diagram_source,
            output_path=output_path,
            format=format,
            overwrite=overwrite,
            render_options=render_options,
        )

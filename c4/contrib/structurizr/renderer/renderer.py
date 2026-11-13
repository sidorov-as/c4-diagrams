from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from typing_extensions import override

from c4.contrib.structurizr.renderer.backends import BaseStructurizrBackend
from c4.contrib.structurizr.renderer.builder import (
    StructurizrWorkspaceBuilder,
)
from c4.contrib.structurizr.renderer.dsl import (
    auto_layout_directive,
    ordered_style_properties,
    properties_block,
    style_value,
    tags_directive,
)
from c4.contrib.structurizr.renderer.errors import (
    StructurizrBackendConfigurationError,
)
from c4.contrib.structurizr.renderer.formatting import (
    StructurizrStringBuilder,
    quote_structurizr_string,
)
from c4.contrib.structurizr.renderer.identifiers import (
    StructurizrIdentifierRegistry,
)
from c4.contrib.structurizr.renderer.models import (
    StructurizrElementModel,
    StructurizrRelationshipModel,
    StructurizrViewModel,
)
from c4.contrib.structurizr.renderer.options import StructurizrRenderOptions
from c4.contrib.structurizr.renderer.styles import (
    StructurizrStyleModel,
    StructurizrStylesModel,
)
from c4.contrib.structurizr.renderer.validation import (
    StructurizrWorkspaceValidator,
)
from c4.enums import DiagramFormat, RendererEnum
from c4.renderers.base import (
    IGNORE_FOREIGN,
    BaseRenderer,
    ExtensionValidationModeType,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.structurizr import Workspace

_VIEW_TYPE_TO_DSL = {
    "systemLandscape": "systemLandscape",
    "systemContext": "systemContext",
    "container": "container",
    "component": "component",
    "dynamic": "dynamic",
    "deployment": "deployment",
}

# Structurizr DSL has a technology slot only on these element types.
_TECHNOLOGY_ELEMENT_TYPES = {
    "container",
    "component",
    "deploymentNode",
    "infrastructureNode",
}

_SCOPED_VIEW_TYPES = {
    "systemContext",
    "container",
    "component",
}
_OPTIONALLY_SCOPED_VIEW_TYPES = {
    "dynamic",
}


class StructurizrRenderer(BaseRenderer["Workspace"]):
    """A renderer for converting a Structurizr workspace into DSL."""

    renderer_type: RendererEnum = RendererEnum.STRUCTURIZR

    def __init__(
        self,
        render_options: StructurizrRenderOptions | None = None,
        backend: BaseStructurizrBackend | None = None,
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        """Initialize a Structurizr renderer.

        Args:
            render_options: Default Structurizr render configuration.
            backend: Optional backend used for binary and file rendering.
            extension_validation_mode: Handling mode for foreign extensions.
        """
        super().__init__(extension_validation_mode=extension_validation_mode)
        self._render_options = render_options or StructurizrRenderOptions()
        self._backend = backend
        self._identifier_registry = StructurizrIdentifierRegistry()
        self._last_workspace_builder: StructurizrWorkspaceBuilder | None = None

    @override
    def validate(self, diagram: Workspace) -> None:
        """Validate Structurizr-specific rendering constraints.

        Args:
            diagram: Workspace to validate.
        """
        StructurizrWorkspaceValidator(diagram).validate()

    @override
    def render(self, diagram: Workspace) -> str:
        """Render a Structurizr workspace into Structurizr DSL.

        Args:
            diagram: Workspace to render.
        """
        self.validate(diagram)
        workspace_builder = self._build_workspace(diagram)

        self._last_workspace_builder = workspace_builder
        result = self._render_workspace(workspace_builder)

        return f"{result}\n"

    def _build_workspace(
        self,
        diagram: Workspace,
    ) -> StructurizrWorkspaceBuilder:
        """Build the private workspace model for a Structurizr workspace."""
        self._identifier_registry = StructurizrIdentifierRegistry()
        # Workspace owns the declaration order. Its private core inventory
        # supports fluent authoring only; it is not a renderer input.
        for element in (
            *diagram.model.people,
            *diagram.model.software_systems,
            *diagram.model.containers,
            *diagram.model.components,
            *diagram.model.deployment_nodes,
            *diagram.model.software_system_instances,
            *diagram.model.container_instances,
        ):
            self._identifier_registry.register_alias(element.alias)

        identifiers = self._identifier_registry.identifiers
        render_options = self._render_options
        if diagram.render_options:
            render_options = diagram.render_options

        builder = StructurizrWorkspaceBuilder(name=diagram.name or "Workspace")
        return builder.build(
            workspace=diagram,
            identifiers=identifiers,
            auto_layout=render_options.auto_layout,
            style_preset=render_options.style_preset,
            next_relationship_id=self._identifier_registry.next_relationship_id,
        )

    def _render_workspace(
        self,
        workspace_builder: StructurizrWorkspaceBuilder,
    ) -> str:
        """Render the built workspace model as Structurizr DSL text."""
        workspace = workspace_builder.workspace
        builder = StructurizrStringBuilder()

        with builder.block(
            f"workspace {quote_structurizr_string(workspace.name)}"
        ):
            if workspace.description is not None:
                builder.add(
                    f"description "
                    f"{quote_structurizr_string(workspace.description)}"
                )

            properties_block(builder, workspace.properties)

            with builder.block("model"):
                self._render_elements(
                    builder,
                    (*workspace.people, *workspace.software_systems),
                )

                for environment, nodes in workspace.deployment_environments:
                    with builder.block(
                        "deploymentEnvironment "
                        f"{quote_structurizr_string(environment)}"
                    ):
                        for element in nodes:
                            self._render_element(builder, element)

                for relationship in workspace.relationships:
                    self._render_relationship(builder, relationship)

            with builder.block("views"):
                for view in workspace.views:
                    self._render_view(builder, view)

                if workspace.theme is not None:
                    self._render_theme(builder, workspace.theme)

                self._render_styles(builder, workspace.styles)

        return builder.get_result()

    def _render_element(
        self,
        builder: StructurizrStringBuilder,
        element: StructurizrElementModel,
    ) -> None:
        """Render one element, recursing into its nested children."""
        if element.element_type in {
            "containerInstance",
            "softwareSystemInstance",
        }:
            self._render_instance(builder, element)
            return

        parts = [
            f"{element.id} = {element.element_type}",
            quote_structurizr_string(element.name),
        ]
        has_technology = (
            element.technology is not None
            and element.element_type in _TECHNOLOGY_ELEMENT_TYPES
        )

        if element.description is not None:
            parts.append(quote_structurizr_string(element.description))
        elif has_technology:
            parts.append(quote_structurizr_string(""))

        if has_technology and element.technology is not None:
            parts.append(quote_structurizr_string(element.technology))

        directives = self._metadata_directives(
            tags=element.tags,
            url=element.url,
        )
        if (
            not directives
            and not element.properties
            and not element.children
            and not element.infrastructure_nodes
            and not element.software_system_instances
            and not element.container_instances
        ):
            builder.add(" ".join(parts))
            return

        with builder.block(" ".join(parts)):
            for directive in directives:
                builder.add(directive)

            properties_block(builder, element.properties)
            self._render_elements(builder, element.children)
            self._render_elements(builder, element.infrastructure_nodes)

            for instance in element.software_system_instances:
                self._render_element(builder, instance)
            for instance in element.container_instances:
                self._render_element(builder, instance)

    def _render_elements(
        self,
        builder: StructurizrStringBuilder,
        elements: (
            tuple[StructurizrElementModel, ...] | list[StructurizrElementModel]
        ),
    ) -> None:
        """Render each element in an ordered collection."""
        for element in elements:
            self._render_element(builder, element)

    def _render_instance(
        self,
        builder: StructurizrStringBuilder,
        element: StructurizrElementModel,
    ) -> None:
        """Render a software-system or container deployment instance."""
        if element.instance_of_id is None:  # pragma: no cover
            return

        header = (
            f"{element.id} = {element.element_type} {element.instance_of_id}"
        )
        directives = self._metadata_directives(
            tags=element.tags,
            url=element.url,
        )
        if (
            element.description is None
            and not directives
            and not element.properties
        ):
            builder.add(header)
            return

        with builder.block(header):
            if element.description is not None:
                builder.add(
                    f"description "
                    f"{quote_structurizr_string(element.description)}"
                )

            for directive in directives:
                builder.add(directive)

            properties_block(builder, element.properties)

    def _render_relationship(
        self,
        builder: StructurizrStringBuilder,
        relationship: StructurizrRelationshipModel,
    ) -> None:
        """Render a model-level relationship declaration."""
        parts = [
            relationship.source_id,
            "->",
            relationship.destination_id,
        ]

        if relationship.description is not None:
            parts.append(quote_structurizr_string(relationship.description))
        if relationship.technology is not None:
            parts.append(quote_structurizr_string(relationship.technology))

        directives = self._metadata_directives(
            tags=relationship.tags,
            url=relationship.url,
        )
        if not directives and not relationship.properties:
            builder.add(" ".join(parts))
            return

        with builder.block(" ".join(parts)):
            for directive in directives:
                builder.add(directive)

            properties_block(builder, relationship.properties)

    def _view_header(self, view: StructurizrViewModel) -> str:
        """Return the DSL header line for a declared view."""
        view_type = _VIEW_TYPE_TO_DSL.get(view.type, view.type)
        if view.type == "deployment":
            scope_id = view.scope_id or "*"
            return (
                f"{view_type} {scope_id} "
                f"{quote_structurizr_string(view.environment or '')} "
                f"{quote_structurizr_string(view.key)}"
            )

        if view.type == "dynamic":
            scope_id = view.scope_id or "*"
            return (
                f"{view_type} {scope_id} {quote_structurizr_string(view.key)}"
            )

        if (
            view.type in _SCOPED_VIEW_TYPES | _OPTIONALLY_SCOPED_VIEW_TYPES
            and view.scope_id is not None
        ):
            return (
                f"{view_type} {view.scope_id} "
                f"{quote_structurizr_string(view.key)}"
            )
        return f"{view_type} {quote_structurizr_string(view.key)}"

    def _render_view_selectors(
        self,
        builder: StructurizrStringBuilder,
        view: StructurizrViewModel,
    ) -> None:
        """Render a view's include/exclude selector directives."""
        is_dynamic_view = view.type == "dynamic"
        if view.include:
            for selector in view.include:
                builder.add(f"include {selector}")
        elif not view.exclude and not is_dynamic_view:
            builder.add("include *")

        for selector in view.exclude:
            builder.add(f"exclude {selector}")

    def _render_view(
        self,
        builder: StructurizrStringBuilder,
        view: StructurizrViewModel,
    ) -> None:
        """Render a declared view's header and body."""
        with builder.block(self._view_header(view)):
            if view.title is not None:
                builder.add(f"title {quote_structurizr_string(view.title)}")
            if view.description is not None:
                builder.add(
                    f"description {quote_structurizr_string(view.description)}"
                )

            view_tags = tags_directive(view.tags)
            if view_tags is not None:
                builder.add(view_tags)

            properties_block(builder, view.properties)
            self._render_view_selectors(builder, view)

            for relationship in view.relationships:
                builder.add(self._dynamic_relationship(relationship))

            if view.animation:
                with builder.block("animation"):
                    for step in view.animation:
                        builder.add(" ".join(step))

            if view.auto_layout is not None:
                builder.add(auto_layout_directive(view.auto_layout))

    def _dynamic_relationship(
        self,
        relationship: StructurizrRelationshipModel,
    ) -> str:
        """Return a dynamic-view relationship line, DSL-quoted."""
        parts = [
            relationship.source_id,
            "->",
            relationship.destination_id,
        ]

        if relationship.description is not None:
            parts.append(quote_structurizr_string(relationship.description))
        elif relationship.technology is not None:
            parts.append(quote_structurizr_string(""))

        if relationship.technology is not None:
            parts.append(quote_structurizr_string(relationship.technology))

        return " ".join(parts)

    def _render_styles(
        self,
        builder: StructurizrStringBuilder,
        styles: StructurizrStylesModel,
    ) -> None:
        """Render the workspace's element and relationship style blocks."""
        if styles.is_empty:
            return

        with builder.block("styles"):
            for style in styles.elements:
                self._render_style(builder, "element", style)
            for style in styles.relationships:
                self._render_style(builder, "relationship", style)

    def _render_theme(
        self,
        builder: StructurizrStringBuilder,
        theme: str,
    ) -> None:
        """Render the workspace's theme directive."""
        builder.add(f"theme {style_value(theme)}")

    def _render_style(
        self,
        builder: StructurizrStringBuilder,
        style_type: str,
        style: StructurizrStyleModel,
    ) -> None:
        """Render one element or relationship style declaration."""
        properties = dict(style.properties)
        if style_type == "relationship":
            properties = _relationship_style_properties(properties)

        with builder.block(
            f"{style_type} {quote_structurizr_string(style.tag)}"
        ):
            for key in ordered_style_properties(properties):
                builder.add(f"{key} {style_value(properties[key])}")

    def _metadata_directives(
        self,
        *,
        tags: tuple[str, ...],
        url: str | None,
    ) -> list[str]:
        """Return the `tags`/`url` metadata directive lines for an item."""
        directives: list[str] = []
        if tags_directive(tags) is not None:
            directives.append(tags_directive(tags) or "")

        if url is not None:
            directives.append(f"url {quote_structurizr_string(url)}")

        return directives

    @override
    def render_bytes(
        self,
        diagram: Workspace,
        *,
        format: DiagramFormat,
    ) -> bytes:
        """Render a Diagram and export it through the optional backend."""
        if self._backend is None:
            raise StructurizrBackendConfigurationError(
                "Structurizr byte export requires a configured backend. "
                "Configure Structurizr export with a backend such as "
                "KrokiStructurizrBackend."
            )

        return self._backend.to_bytes(
            self.render(diagram),
            format=format,
            render_options=self._render_options,
        )

    @override
    def render_file(
        self,
        diagram: Workspace,
        output_path: Path,
        *,
        format: DiagramFormat,
        overwrite: bool = True,
    ) -> Path:
        """Render a Diagram and write exported output through the backend."""
        if self._backend is None:
            raise StructurizrBackendConfigurationError(
                "Structurizr file export requires a configured backend. "
                "Configure Structurizr export with a backend such as "
                "KrokiStructurizrBackend."
            )

        return self._backend.to_file(
            self.render(diagram),
            output_path,
            format=format,
            overwrite=overwrite,
            render_options=self._render_options,
        )


def _relationship_style_properties(
    properties: dict[str, object],
) -> dict[str, object]:
    """
    Normalize shared style metadata for Structurizr relationship DSL.

    Element styles use ``border`` for solid/dashed/dotted borders, while
    relationship styles use ``style`` for line shape. The public metadata
    schema is currently shared, so relationship rendering translates it here.
    """
    border = properties.pop("border", None)
    if border is not None:
        properties["style"] = str(border).lower()

    return properties

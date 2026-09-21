from __future__ import annotations

import keyword
import re
from collections.abc import Mapping
from typing import Any, TypeAlias, cast

from c4.contrib.structurizr import (
    Container,
    DeploymentNode,
    InfrastructureNode,
    SoftwareSystem,
    StructurizrElement,
    Workspace,
)
from c4.contrib.structurizr.converters.json.schemas import (
    StructurizrAutoLayoutSchema,
    StructurizrComponentViewSchema,
    StructurizrContainerInstanceSchema,
    StructurizrContainerViewSchema,
    StructurizrDeploymentNodeSchema,
    StructurizrDeploymentViewSchema,
    StructurizrDynamicViewSchema,
    StructurizrElementSchema,
    StructurizrInfrastructureNodeSchema,
    StructurizrSelectorSchema,
    StructurizrSoftwareSystemInstanceSchema,
    StructurizrSystemContextViewSchema,
    StructurizrSystemLandscapeViewSchema,
    StructurizrViewSchema,
    StructurizrWorkspaceSchema,
)
from c4.contrib.structurizr.renderer import AutoLayout, StructurizrRenderOptions
from c4.enums import RendererEnum

_DeploymentNodeSchema: TypeAlias = (
    StructurizrDeploymentNodeSchema | StructurizrInfrastructureNodeSchema
)
_ElementRegistrationSchema: TypeAlias = (
    StructurizrElementSchema
    | StructurizrSoftwareSystemInstanceSchema
    | StructurizrContainerInstanceSchema
)


class JSONToStructurizrWorkspaceConverter:
    """Build a typed Structurizr :class:`Workspace` from its JSON schema."""

    def __init__(self, schema: StructurizrWorkspaceSchema) -> None:
        self.schema = schema
        self._elements: dict[str, StructurizrElement] = {}
        self._aliases: dict[str, str] = {}

    def convert(self) -> Workspace:
        """Create the workspace, model inventory, and views in that order."""
        workspace = self._create_workspace()
        self._add_model(workspace)
        self._add_views(workspace)
        return workspace

    def _create_workspace(self) -> Workspace:
        render_options = self._render_options()
        workspace = Workspace(
            self.schema.name,
            description=self.schema.description,
            theme=self.schema.theme,
            render_options=render_options,
        )
        workspace.properties.update(self.schema.properties or {})

        if self.schema.styles:
            for style in self.schema.styles.elements:
                workspace.styles.element(style.target, **style.properties)
            for style in self.schema.styles.relationships:
                workspace.styles.relationship(style.target, **style.properties)

        return workspace

    def _render_options(self) -> StructurizrRenderOptions | None:
        options = self.schema.render_options
        if options is None:
            return None

        return StructurizrRenderOptions(
            auto_layout=(
                self._auto_layout(options.auto_layout)
                if options.auto_layout is not None
                else None
            ),
            style_preset=options.style_preset,
        )

    def _add_model(self, workspace: Workspace) -> None:
        with workspace.model as model:
            for person in self.schema.model.people:
                self._register(
                    person,
                    model.Person(
                        person.name,
                        description=person.description,
                        alias=self._alias(person.id),
                        tags=person.tags,
                        properties=person.properties,
                        url=person.url,
                    ),
                )

            for system_schema in self.schema.model.software_systems:
                system = model.SoftwareSystem(
                    system_schema.name,
                    description=system_schema.description,
                    alias=self._alias(system_schema.id),
                    tags=system_schema.tags,
                    properties=system_schema.properties,
                    url=system_schema.url,
                )
                self._register(system_schema, system)
                for container_schema in system_schema.containers:
                    container = model.Container(
                        container_schema.name,
                        description=container_schema.description,
                        technology=container_schema.technology,
                        alias=self._alias(container_schema.id),
                        owner=system,
                        tags=container_schema.tags,
                        properties=container_schema.properties,
                        url=container_schema.url,
                    )
                    self._register(container_schema, container)
                    for component_schema in container_schema.components:
                        component = model.Component(
                            component_schema.name,
                            description=component_schema.description,
                            technology=component_schema.technology,
                            alias=self._alias(component_schema.id),
                            owner=container,
                            tags=component_schema.tags,
                            properties=component_schema.properties,
                            url=component_schema.url,
                        )
                        self._register(component_schema, component)

            deployment = self.schema.model.deployment
            for environment in deployment.environments if deployment else ():
                for node in environment.deployment_nodes:
                    self._add_deployment_node(
                        model,
                        node,
                        environment.name,
                        None,
                    )

            for relationship in self.schema.model.relationships:
                created = self._element(relationship.from_).uses(
                    self._element(relationship.to),
                    relationship.description,
                    technology=relationship.technology,
                    tags=relationship.tags,
                    properties=relationship.properties,
                    url=relationship.url,
                )
                if relationship.style:
                    created.style = dict(relationship.style)

    def _add_deployment_node(
        self,
        model: Any,
        schema: _DeploymentNodeSchema,
        environment: str,
        parent: DeploymentNode | InfrastructureNode | None,
    ) -> None:
        factory = (
            model.DeploymentNode
            if isinstance(schema, StructurizrDeploymentNodeSchema)
            else model.InfrastructureNode
        )

        kwargs: dict[str, Any] = {
            "description": schema.description,
            "technology": schema.technology,
            "alias": self._alias(schema.id),
            "tags": schema.tags,
            "properties": schema.properties,
            "url": schema.url,
            "style": schema.style,
        }

        if parent is None:
            kwargs["environment"] = environment
        else:
            kwargs["parent"] = parent

        node = factory(schema.name, **kwargs)
        self._register(schema, node)

        for child in schema.deployment_nodes:
            self._add_deployment_node(model, child, environment, node)
        for infrastructure_node in schema.infrastructure_nodes:
            self._add_deployment_node(
                model,
                infrastructure_node,
                environment,
                node,
            )

        if isinstance(schema, StructurizrDeploymentNodeSchema):
            for instance in schema.software_system_instances:
                instance_kwargs = self._instance_kwargs(instance)
                created = node.SoftwareSystemInstance(
                    self._element(instance.software_system),
                    alias=self._alias(instance.id),
                    **instance_kwargs,
                )
                self._register(instance, created)
            for container_instance in schema.container_instances:
                instance_kwargs = self._instance_kwargs(container_instance)
                created = node.ContainerInstance(
                    self._element(container_instance.container),
                    alias=self._alias(container_instance.id),
                    **instance_kwargs,
                )
                self._register(container_instance, created)

    def _add_views(self, workspace: Workspace) -> None:
        for schema in self.schema.views.items:
            options = self._view_options(schema)
            if isinstance(schema, StructurizrSystemLandscapeViewSchema):
                workspace.views.SystemLandscapeView(**options)
            elif isinstance(schema, StructurizrSystemContextViewSchema):
                self._add_system_context_view(workspace, schema, options)
            elif isinstance(schema, StructurizrContainerViewSchema):
                self._add_container_view(workspace, schema, options)
            elif isinstance(schema, StructurizrComponentViewSchema):
                self._add_component_view(workspace, schema, options)
            elif isinstance(schema, StructurizrDynamicViewSchema):
                self._add_dynamic_view(workspace, schema, options)
            elif isinstance(schema, StructurizrDeploymentViewSchema):
                self._add_deployment_view(workspace, schema, options)

    def _add_system_context_view(
        self,
        workspace: Workspace,
        schema: StructurizrSystemContextViewSchema,
        options: dict[str, Any],
    ) -> None:
        workspace.views.SystemContextView(
            cast(SoftwareSystem, self._element(schema.scope)),
            **options,
        )

    def _add_container_view(
        self,
        workspace: Workspace,
        schema: StructurizrContainerViewSchema,
        options: dict[str, Any],
    ) -> None:
        workspace.views.ContainerView(
            cast(SoftwareSystem, self._element(schema.scope)),
            **options,
        )

    def _add_component_view(
        self,
        workspace: Workspace,
        schema: StructurizrComponentViewSchema,
        options: dict[str, Any],
    ) -> None:
        workspace.views.ComponentView(
            cast(Container, self._element(schema.scope)),
            **options,
        )

    def _add_dynamic_view(
        self,
        workspace: Workspace,
        schema: StructurizrDynamicViewSchema,
        options: dict[str, Any],
    ) -> None:
        view = workspace.views.DynamicView(
            self._element(schema.scope) if schema.scope else None,
            **options,
        )

        for step in schema.steps:
            view.step(
                self._element(step.from_),
                self._element(step.to),
                step.description,
                technology=step.technology,
                tags=step.tags,
                properties=step.properties,
                url=step.url,
                style=step.style,
            )

    def _add_deployment_view(
        self,
        workspace: Workspace,
        schema: StructurizrDeploymentViewSchema,
        options: dict[str, Any],
    ) -> None:
        workspace.views.DeploymentView(
            self._element(schema.scope) if schema.scope else None,
            environment=schema.environment,
            **options,
        )

    def _view_options(self, schema: StructurizrViewSchema) -> dict[str, Any]:
        return {
            "key": schema.key,
            "title": schema.title,
            "description": schema.description,
            "include": [self._selector(value) for value in schema.include],
            "exclude": [self._selector(value) for value in schema.exclude],
            "tags": schema.tags,
            "properties": schema.properties,
            "auto_layout": self._auto_layout(schema.auto_layout),
            "animation": [
                [self._selector(value) for value in step]
                for step in schema.animation
            ],
        }

    @staticmethod
    def _auto_layout(
        schema: StructurizrAutoLayoutSchema | None,
    ) -> AutoLayout | None:
        if schema is None:
            return None

        return AutoLayout(
            rank_direction=schema.rank_direction,
            implementation=schema.implementation,
            rank_separation=schema.rank_separation,
            node_separation=schema.node_separation,
        )

    def _selector(self, value: str | StructurizrSelectorSchema) -> object:
        if isinstance(value, StructurizrSelectorSchema):
            return self._element(value.id)

        return value

    @staticmethod
    def _instance_kwargs(instance: Any) -> dict[str, Any]:
        return {
            "description": instance.description,
            "tags": instance.tags,
            "properties": instance.properties,
            "url": instance.url,
            "style": instance.style,
        }

    def _register(
        self,
        schema: _ElementRegistrationSchema,
        element: StructurizrElement,
    ) -> None:
        if schema.style:
            element.style(**schema.style)

        self._elements[schema.id] = element

    def _element(self, element_id: str) -> StructurizrElement:
        try:
            return self._elements[element_id]
        except KeyError as exc:
            raise ValueError(
                f"Unknown Structurizr element reference {element_id!r}"
            ) from exc

    def _alias(self, reference: str) -> str:
        """Map an opaque JSON reference to a unique DSL-safe alias."""
        existing = self._aliases.get(reference)
        if existing is not None:
            return existing

        base = re.sub(r"\W", "_", reference)
        if not base or base[0].isdigit():
            base = f"element_{base}"
        if keyword.iskeyword(base):
            base = f"element_{base}"

        candidate = base
        suffix = 2
        while candidate in self._aliases.values():
            candidate = f"{base}_{suffix}"
            suffix += 1

        self._aliases[reference] = candidate
        return candidate


def workspace_from_dict(
    data: Mapping[str, Any],
) -> tuple[Workspace, RendererEnum]:
    """Convert a Structurizr workspace JSON mapping and infer its renderer."""
    schema = StructurizrWorkspaceSchema.model_validate(data)
    workspace = JSONToStructurizrWorkspaceConverter(schema).convert()
    return (
        workspace,
        RendererEnum.STRUCTURIZR,
    )

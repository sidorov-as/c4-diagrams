from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from c4.contrib.likec4 import (
    Between,
    Children,
    DeploymentInstance,
    DeploymentNode,
    Descendants,
    Element,
    Incoming,
    InOut,
    Link,
    Outgoing,
    Project,
    RawPredicate,
    Where,
    Wildcard,
)
from c4.contrib.likec4.converters.json.schemas import (
    LikeC4AutoLayoutRuleSchema,
    LikeC4BetweenSchema,
    LikeC4ChildrenSchema,
    LikeC4DeploymentNodeSchema,
    LikeC4DeploymentViewSchema,
    LikeC4DescendantsSchema,
    LikeC4DynamicViewSchema,
    LikeC4ElementRefSchema,
    LikeC4ElementSchema,
    LikeC4ElementViewSchema,
    LikeC4ExcludeRuleSchema,
    LikeC4IncludeRuleSchema,
    LikeC4IncomingSchema,
    LikeC4InOutSchema,
    LikeC4LinkSchema,
    LikeC4OutgoingSchema,
    LikeC4ProjectSchema,
    LikeC4RawPredicateSchema,
    LikeC4StyleRuleSchema,
    LikeC4WhereSchema,
    LikeC4WildcardSchema,
)
from c4.enums import RendererEnum

_Item = Element | DeploymentNode | DeploymentInstance


class JSONToLikeC4ProjectConverter:
    """Build a typed LikeC4 :class:`Project` from its JSON schema."""

    def __init__(self, schema: LikeC4ProjectSchema) -> None:
        self.schema = schema
        self._elements: dict[str, Element] = {}
        self._deployment: dict[str, DeploymentNode | DeploymentInstance] = {}

    def convert(self) -> Project:
        """Create specification, model, deployment and views in that order."""
        options = self.schema.render_options
        project = Project(
            self.schema.name,
            view_key=options.view_key if options else None,
        )
        self._add_specification(project)
        self._add_model(project)
        self._add_deployment(project)
        self._add_views(project)
        return project

    def _add_specification(self, project: Project) -> None:
        spec = project.specification
        source = self.schema.specification
        for kind in source.elements:
            spec.element(**self._kind_kwargs(kind))

        for kind in source.deployment_nodes:
            spec.deployment_node(**self._kind_kwargs(kind))

        for relationship in source.relationships:
            spec.relationship(
                relationship.name,
                technology=relationship.technology,
                description=relationship.description,
                **relationship.style,
            )

        for tag in source.tags:
            spec.tag(tag.name, tag.color)

        for color in source.colors:
            spec.color(color.name, color.value)

    @staticmethod
    def _kind_kwargs(kind: Any) -> dict[str, Any]:
        return {
            "name": kind.name,
            "title": kind.title,
            "technology": kind.technology,
            "description": kind.description,
            "notation": kind.notation,
            "tags": kind.tags,
            **kind.style,
        }

    def _add_model(self, project: Project) -> None:
        model = project.model
        for schema in self.schema.model.elements:
            self._add_element(project, schema, None)

        for relationship in self.schema.model.relationships:
            model.relate(
                self._elements[relationship.from_],
                self._elements[relationship.to],
                relationship.title,
                description=relationship.description,
                technology=relationship.technology,
                kind=relationship.kind,
                bidirectional=relationship.bidirectional,
                tags=relationship.tags,
                metadata=relationship.metadata,
                links=self._links(relationship.links),
                navigate_to=relationship.navigate_to,
                **relationship.style,
            )

    def _add_element(
        self,
        project: Project,
        schema: LikeC4ElementSchema,
        parent: Element | None,
    ) -> None:
        element = project.model.element(
            schema.kind,
            schema.title,
            parent=parent,
            alias=schema.alias,
            summary=schema.summary,
            description=schema.description,
            technology=schema.technology,
            tags=schema.tags,
            icon=schema.icon,
            metadata=schema.metadata,
            links=self._links(schema.links),
            **schema.style,
        )
        self._elements[schema.id] = element
        for child in schema.elements:
            self._add_element(project, child, element)

    def _add_deployment(self, project: Project) -> None:
        deployment = project.deployment
        for schema in self.schema.deployment.nodes:
            self._add_node(project, schema, None)

        for relationship in self.schema.deployment.relationships:
            deployment.relate(
                self._deployment[relationship.from_],
                self._deployment[relationship.to],
                relationship.title,
                description=relationship.description,
                technology=relationship.technology,
                kind=relationship.kind,
                bidirectional=relationship.bidirectional,
                tags=relationship.tags,
                metadata=relationship.metadata,
                links=self._links(relationship.links),
                **relationship.style,
            )

    def _add_node(
        self,
        project: Project,
        schema: LikeC4DeploymentNodeSchema,
        parent: DeploymentNode | None,
    ) -> None:
        node = project.deployment.node(
            schema.kind,
            schema.title,
            parent=parent,
            alias=schema.alias,
            description=schema.description,
            technology=schema.technology,
            tags=schema.tags,
            metadata=schema.metadata,
            links=self._links(schema.links),
            **schema.style,
        )
        self._deployment[schema.id] = node

        for child in schema.nodes:
            self._add_node(project, child, node)

        for instance_schema in schema.instances:
            instance = project.deployment.instance(
                self._elements[instance_schema.element],
                instance_schema.name,
                parent=node,
                title=instance_schema.title,
                description=instance_schema.description,
                technology=instance_schema.technology,
                tags=instance_schema.tags,
                metadata=instance_schema.metadata,
                links=self._links(instance_schema.links),
                **instance_schema.style,
            )
            if instance_schema.id is not None:
                self._deployment[instance_schema.id] = instance

    def _add_views(self, project: Project) -> None:
        for schema in self.schema.views.items:
            if isinstance(schema, LikeC4ElementViewSchema):
                self._add_element_view(project, schema)
            elif isinstance(schema, LikeC4DeploymentViewSchema):
                self._add_deployment_view(project, schema)
            else:
                self._add_dynamic_view(project, schema)

    def _view_kwargs(self, schema: Any) -> dict[str, Any]:
        return {
            "description": schema.description,
            "tags": schema.tags,
            "links": self._links(schema.links),
        }

    def _add_element_view(
        self, project: Project, schema: LikeC4ElementViewSchema
    ) -> None:
        view = project.views.element_view(
            schema.key,
            schema.title,
            of=self._elements[schema.of] if schema.of else None,
            **self._view_kwargs(schema),
        )
        self._add_rules(view, schema.rules, self._elements)

    def _add_deployment_view(
        self, project: Project, schema: LikeC4DeploymentViewSchema
    ) -> None:
        view = project.views.deployment_view(
            schema.key, schema.title, **self._view_kwargs(schema)
        )
        self._add_rules(view, schema.rules, self._deployment)

    def _add_dynamic_view(
        self, project: Project, schema: LikeC4DynamicViewSchema
    ) -> None:
        view = project.views.dynamic_view(
            schema.key,
            schema.title,
            variant=schema.variant,
            **self._view_kwargs(schema),
        )

        for step in schema.steps:
            add = view.back if step.backward else view.step
            add(
                self._elements[step.from_],
                self._elements[step.to],
                step.title,
                description=step.description,
                technology=step.technology,
                notes=step.notes,
                navigate_to=step.navigate_to,
                color=step.color,
            )

    def _add_rules(
        self, view: Any, rules: list[Any], registry: Mapping[str, _Item]
    ) -> None:
        for rule in rules:
            if isinstance(rule, LikeC4IncludeRuleSchema):
                items = self._items(rule.items, registry)
                if rule.navigate_to is not None:
                    view.include(*items, navigate_to=rule.navigate_to)
                else:
                    view.include(*items)
            elif isinstance(rule, LikeC4ExcludeRuleSchema):
                view.exclude(*self._items(rule.items, registry))
            elif isinstance(rule, LikeC4StyleRuleSchema):
                view.style(
                    *self._items(rule.targets, registry), **rule.properties
                )
            elif isinstance(rule, LikeC4AutoLayoutRuleSchema):
                view.auto_layout(rule.direction, rule.rank_sep, rule.node_sep)

    def _items(
        self, items: list[Any], registry: Mapping[str, _Item]
    ) -> list[Any]:
        return [self._item(item, registry) for item in items]

    def _item(  # noqa: C901
        self, item: Any, registry: Mapping[str, _Item]
    ) -> Any:
        if isinstance(item, LikeC4WildcardSchema):
            return Wildcard()
        if isinstance(item, LikeC4ElementRefSchema):
            return registry[item.id]
        if isinstance(item, LikeC4ChildrenSchema):
            return Children(registry[item.of])
        if isinstance(item, LikeC4DescendantsSchema):
            return Descendants(registry[item.of])
        if isinstance(item, LikeC4RawPredicateSchema):
            return RawPredicate(item.text)
        if isinstance(item, LikeC4WhereSchema):
            return Where(
                self._item(item.item, registry), tag=item.tag, kind=item.kind
            )
        if isinstance(item, LikeC4BetweenSchema):
            return Between(
                self._item(item.source, registry),
                self._item(item.target, registry),
                item.both,
            )
        if isinstance(item, LikeC4IncomingSchema):
            return Incoming(self._item(item.item, registry))
        if isinstance(item, LikeC4OutgoingSchema):
            return Outgoing(self._item(item.item, registry))
        if isinstance(item, LikeC4InOutSchema):
            return InOut(self._item(item.item, registry))
        raise TypeError(  # pragma: no cover - the schema is a closed union
            f"Unsupported predicate schema: {type(item).__name__}"
        )

    @staticmethod
    def _links(links: list[LikeC4LinkSchema]) -> list[Link]:
        return [Link(link.url, link.title) for link in links]


def project_from_dict(
    data: Mapping[str, Any],
) -> tuple[Project, RendererEnum]:
    """Convert a LikeC4 project JSON mapping and infer its renderer."""
    schema = LikeC4ProjectSchema.model_validate(data)
    return JSONToLikeC4ProjectConverter(schema).convert(), RendererEnum.LIKEC4


__all__ = ("JSONToLikeC4ProjectConverter", "project_from_dict")

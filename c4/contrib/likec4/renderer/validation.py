from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from c4.contrib.likec4._metadata import Link
from c4.contrib.likec4._styles import THEME_COLORS
from c4.contrib.likec4._views import (
    RELATIONSHIP_PREDICATES,
    Between,
    Children,
    Descendants,
    ExcludeRule,
    IncludeRule,
    Incoming,
    InOut,
    Outgoing,
    RawPredicate,
    StyleRule,
    Where,
    Wildcard,
)
from c4.contrib.likec4.renderer.errors import (
    LikeC4ValidationError,
    missing_endpoint_error,
    parent_child_relationship_error,
    undeclared_error,
)
from c4.contrib.likec4.workspace import (
    DeploymentInstance,
    DeploymentNode,
    DeploymentRelationship,
    DeploymentView,
    DynamicView,
    Element,
    ElementView,
    Project,
    Relationship,
)

_LINK_RE = re.compile(
    r"[A-Za-z][A-Za-z0-9+.-]*:\S+|\.{1,2}/\S*|@\S+",
)


def _element_label(element: Element) -> str:
    return f'Element "{element.name}" (kind "{element.kind}")'


def _node_label(node: DeploymentNode) -> str:
    return f'Deployment node "{node.name}" (kind "{node.kind}")'


def _instance_label(instance: DeploymentInstance) -> str:
    return (
        f'Instance "{instance.name}" of element "{instance.element.name}" '
        f'in node "{instance.parent.name}"'
    )


def _ends_label(source: Any, target: Any) -> str:
    return f'Relationship "{source.name}" -> "{target.name}"'


class LikeC4ProjectValidator:
    """Validate ownership, declarations and references of a project."""

    def __init__(self, project: Project) -> None:
        """Index a project's members."""
        if not isinstance(project, Project):
            raise LikeC4ValidationError(
                "LikeC4 rendering accepts only "
                "c4.contrib.likec4.Project instances."
            )

        self.project = project
        self.spec = project.specification
        self.elements: set[Element] = set(project.model.elements)
        self.nodes: set[DeploymentNode] = set(project.deployment.nodes)
        self.instances: set[DeploymentInstance] = set(
            project.deployment.instances
        )
        self.views = project.views.all

    def validate(self) -> None:
        """Run every project check in a fixed order."""
        self._check_specification()
        self._check_elements()
        self._check_relationships()
        self._check_deployment()
        self._check_views()

    def _check_tags(self, owner: str, tags: Iterable[str]) -> None:
        for tag in tags:
            if tag not in self.spec.tags:
                raise undeclared_error(owner=owner, what="tag", name=tag)

    def _check_style(self, owner: str, style: Mapping[str, Any]) -> None:
        for key in ("color", "iconColor"):
            if key in style:
                self._check_color(owner, style[key])

    def _check_color(self, owner: str, color: str | None) -> None:
        if (
            color is not None
            and color not in THEME_COLORS
            and color not in self.spec.colors
        ):
            raise undeclared_error(owner=owner, what="color", name=color)

    @staticmethod
    def _check_links(owner: str, links: Iterable[Link]) -> None:
        for link in links:
            if _LINK_RE.fullmatch(link.url) is None:
                raise LikeC4ValidationError(
                    f'{owner}: link "{link.url}" must have a scheme '
                    '(https://...), start with "./" or "../", or be an '
                    "@alias, and must not contain whitespace."
                )

    def _view_keys(self, *types: type) -> set[str]:
        return {v.key for v in self.views if isinstance(v, types)}

    def _check_specification(self) -> None:
        kinds: Iterable[Any] = (
            *self.spec.element_kinds.values(),
            *self.spec.deployment_kinds.values(),
        )

        for kind in kinds:
            owner = f'Kind "{kind.name}"'
            self._check_tags(owner, kind.tags)
            self._check_style(owner, kind.style)

        for rel_kind in self.spec.relationship_kinds.values():
            self._check_style(
                f'Relationship kind "{rel_kind.name}"', rel_kind.style
            )

        for tag in self.spec.tags.values():
            self._check_color(f'Tag "{tag.name}"', tag.color)

    def _check_elements(self) -> None:
        for element in self.project.model.elements:
            owner = _element_label(element)
            if element.kind not in self.spec.element_kinds:
                raise undeclared_error(
                    owner=owner, what="element kind", name=element.kind
                )

            self._check_tags(owner, element.tags)
            self._check_style(owner, element.style)
            self._check_links(owner, element.links)

    def _check_relationships(self) -> None:
        for rel in self.project.model.relationships:
            self._check_relationship(rel)

    def _check_relationship(self, rel: Relationship) -> None:
        owner = _ends_label(rel.source, rel.target)
        for side, end in (("source", rel.source), ("target", rel.target)):
            if end not in self.elements:
                raise missing_endpoint_error(
                    owner=owner, side=side, endpoint=end.name
                )

        if rel.source in rel.target.ancestors() or (
            rel.target in rel.source.ancestors()
        ):
            raise parent_child_relationship_error(
                source=rel.source.name, target=rel.target.name
            )

        if rel.kind is not None and rel.kind not in (
            self.spec.relationship_kinds
        ):
            raise undeclared_error(
                owner=owner, what="relationship kind", name=rel.kind
            )

        self._check_tags(owner, rel.tags)
        self._check_style(owner, rel.style)
        self._check_links(owner, rel.links)

        if rel.navigate_to is not None and rel.navigate_to not in (
            self._view_keys(DynamicView)
        ):
            raise LikeC4ValidationError(
                f'{owner}: navigateTo "{rel.navigate_to}" must name a '
                "dynamic view of the project."
            )

    def _check_deployment(self) -> None:
        deployment = self.project.deployment
        for node in deployment.nodes:
            owner = _node_label(node)
            if node.kind not in self.spec.deployment_kinds:
                raise undeclared_error(
                    owner=owner, what="deployment node kind", name=node.kind
                )

            self._check_tags(owner, node.tags)
            self._check_style(owner, node.style)
            self._check_links(owner, node.links)
            self._check_instances(node)

        for rel in deployment.relationships:
            self._check_deployment_relationship(rel)

    def _check_instances(self, node: DeploymentNode) -> None:
        anonymous: set[Element] = set()
        for instance in node.instances:
            owner = _instance_label(instance)
            if instance.element not in self.elements:
                raise LikeC4ValidationError(
                    f"{owner}: the instantiated element is not in the "
                    "project model."
                )

            if instance.alias is None:
                if instance.element in anonymous:
                    raise LikeC4ValidationError(
                        f"{owner}: node holds several unnamed instances of "
                        "the same element; give each a name."
                    )

                anonymous.add(instance.element)

            self._check_tags(owner, instance.tags)
            self._check_style(owner, instance.style)
            self._check_links(owner, instance.links)

    def _check_deployment_relationship(
        self, rel: DeploymentRelationship
    ) -> None:
        owner = _ends_label(rel.source, rel.target)
        members = self.nodes | self.instances
        for side, end in (("source", rel.source), ("target", rel.target)):
            if end not in members:
                raise missing_endpoint_error(
                    owner=owner, side=side, endpoint=end.name
                )

        if self._deployment_ancestors(rel.source, rel.target):
            raise parent_child_relationship_error(
                source=rel.source.name, target=rel.target.name
            )

        if rel.kind is not None and rel.kind not in (
            self.spec.relationship_kinds
        ):
            raise undeclared_error(
                owner=owner, what="relationship kind", name=rel.kind
            )

        self._check_tags(owner, rel.tags)
        self._check_style(owner, rel.style)
        self._check_links(owner, rel.links)

    @staticmethod
    def _deployment_chain(
        end: DeploymentNode | DeploymentInstance,
    ) -> list[Any]:
        node = end.parent
        chain: list[Any] = []

        while node is not None:
            chain.append(node)
            node = node.parent

        return chain

    def _deployment_ancestors(
        self,
        source: DeploymentNode | DeploymentInstance,
        target: DeploymentNode | DeploymentInstance,
    ) -> bool:
        return source in self._deployment_chain(target) or (
            target in self._deployment_chain(source)
        )

    def _check_views(self) -> None:
        seen: set[str] = set()
        for view in self.views:
            if view.key in seen:
                raise LikeC4ValidationError(
                    f'View "{view.key}": the key is used by more than one '
                    "view; keys must be unique across all view types."
                )

            seen.add(view.key)

        for view in self.views:
            owner = f'View "{view.key}"'
            self._check_tags(owner, view.tags)
            self._check_links(owner, view.links)

            if isinstance(view, DynamicView):
                self._check_dynamic_view(view)
                continue

            if (
                isinstance(view, ElementView)
                and view.scope is not None
                and view.scope not in self.elements
            ):
                raise LikeC4ValidationError(
                    f'{owner}: scope element "{view.scope.name}" '
                    "is not in the project model."
                )

            self._check_rules(view)

    def _check_rules(self, view: ElementView | DeploymentView) -> None:
        owner = f'View "{view.key}"'
        deployment = isinstance(view, DeploymentView)

        for rule in view.rules:
            if isinstance(rule, IncludeRule):
                self._check_items(owner, rule.items, deployment)
                if rule.navigate_to is not None and rule.navigate_to not in (
                    self._view_keys(ElementView, DeploymentView, DynamicView)
                ):
                    raise LikeC4ValidationError(
                        f'{owner}: navigateTo "{rule.navigate_to}" does not '
                        "name a view of the project."
                    )

            elif isinstance(rule, ExcludeRule):
                self._check_items(owner, rule.items, deployment)
            elif isinstance(rule, StyleRule):
                if any(
                    isinstance(item, RELATIONSHIP_PREDICATES)
                    for item in rule.targets
                ):
                    raise LikeC4ValidationError(
                        f"{owner}: a style rule cannot target a relationship "
                        "predicate."
                    )
                self._check_items(owner, rule.targets, deployment)
                self._check_style(owner, dict(rule.properties))

    def _check_items(
        self, owner: str, items: Iterable[Any], deployment: bool
    ) -> None:
        for item in items:
            if isinstance(item, (Wildcard, RawPredicate)):
                continue

            if isinstance(item, Where):
                if item.tag is not None:
                    self._check_tags(owner, [item.tag])
                kinds = (
                    self.spec.deployment_kinds
                    if deployment
                    else self.spec.element_kinds
                )
                if item.kind is not None and item.kind not in kinds:
                    raise undeclared_error(
                        owner=owner, what="kind", name=item.kind
                    )

                self._check_items(owner, [item.item], deployment)
            elif isinstance(item, Between):
                self._check_items(owner, [item.source, item.target], deployment)
            elif isinstance(item, (Incoming, Outgoing, InOut)):
                self._check_items(owner, [item.item], deployment)
            elif isinstance(item, (Children, Descendants)):
                self._check_reference(owner, item.element, deployment)
            else:
                self._check_reference(owner, item, deployment)

    def _check_reference(self, owner: str, ref: Any, deployment: bool) -> None:
        members: set[Any] = (
            self.nodes | self.instances if deployment else self.elements
        )
        if not isinstance(ref, (Element, DeploymentNode, DeploymentInstance)):
            raise LikeC4ValidationError(
                f"{owner}: {ref!r} is not a model element or deployment "
                "node; use RawPredicate for free-form predicates."
            )

        if ref not in members:
            where = "deployment" if deployment else "model"
            raise LikeC4ValidationError(
                f'{owner}: reference "{getattr(ref, "name", ref)}" does not '
                f"resolve to a member of the project {where}."
            )

    def _check_dynamic_view(self, view: DynamicView) -> None:
        dynamic_keys = self._view_keys(DynamicView)
        for index, step in enumerate(view.steps, start=1):
            owner = f'Step {index} of dynamic view "{view.key}"'
            for end in (step.source, step.target):
                if end not in self.elements:
                    raise LikeC4ValidationError(
                        f'{owner}: element "{end.name}" is not in the '
                        "project model."
                    )

            self._check_color(owner, step.color)
            if step.navigate_to is not None and (
                step.navigate_to not in dynamic_keys
            ):
                raise LikeC4ValidationError(
                    f'{owner}: navigateTo "{step.navigate_to}" must name a '
                    "dynamic view of the project."
                )

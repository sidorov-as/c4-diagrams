from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from typing_extensions import override

from c4.contrib.likec4._views import (
    RELATIONSHIP_PREDICATES,
    AutoLayoutRule,
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
from c4.contrib.likec4.renderer.backends import BaseLikeC4Backend
from c4.contrib.likec4.renderer.dsl import (
    block,
    link_lines,
    metadata_block,
    style_block,
    style_value,
    tags_line,
)
from c4.contrib.likec4.renderer.errors import LikeC4BackendConfigurationError
from c4.contrib.likec4.renderer.formatting import (
    quote_likec4_markdown,
    quote_likec4_string,
)
from c4.contrib.likec4.renderer.identifiers import (
    LikeC4Identifier,
    LikeC4IdentifierRegistry,
)
from c4.contrib.likec4.renderer.validation import LikeC4ProjectValidator
from c4.contrib.likec4.workspace import (
    DeploymentInstance,
    DeploymentNode,
    DeploymentRelationship,
    DeploymentView,
    DynamicStep,
    DynamicView,
    Element,
    ElementKind,
    ElementView,
    Project,
    Relationship,
    RelationshipKind,
)
from c4.enums import DiagramFormat, RendererEnum
from c4.renderers.base import (
    IGNORE_FOREIGN,
    BaseRenderer,
    ExtensionValidationModeType,
)

if TYPE_CHECKING:  # pragma: no cover
    from c4.contrib.likec4.workspace.views import _View

_SIMPLE_ITEMS = (Wildcard, Children, Descendants)


def _string(label: str, value: str | None) -> list[str]:
    return [f"{label} {quote_likec4_string(value)}"] if value else []


def _markdown(label: str, value: str | None) -> list[str]:
    return [f"{label} {quote_likec4_markdown(value)}"] if value else []


class LikeC4Renderer(BaseRenderer["Project"]):
    """A renderer for converting a LikeC4 project into ``.c4`` DSL."""

    renderer_type: RendererEnum = RendererEnum.LIKEC4

    def __init__(
        self,
        backend: BaseLikeC4Backend | None = None,
        view_key: str | None = None,
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        """Initialize a LikeC4 renderer.

        Args:
            backend: Optional backend used for image rendering.
            view_key: Key of the view to export as an image. Defaults to the
                project's ``view_key``, then to its only view.
            extension_validation_mode: Handling mode for foreign extensions.
        """
        super().__init__(extension_validation_mode=extension_validation_mode)
        self._backend = backend
        self._view_key = view_key
        self._model_ids: dict[Element, LikeC4Identifier] = {}
        self._deployment_ids: dict[
            DeploymentNode | DeploymentInstance, LikeC4Identifier
        ] = {}

    @override
    def validate(self, diagram: Project) -> None:
        """Validate LikeC4-specific rendering constraints.

        Args:
            diagram: Project to validate.
        """
        LikeC4ProjectValidator(diagram).validate()

    @override
    def render(self, diagram: Project) -> str:
        """Render a LikeC4 project into LikeC4 DSL.

        Args:
            diagram: Project to render.
        """
        self.validate(diagram)
        self._assign_identifiers(diagram)

        sections = [
            self._specification(diagram),
            self._model(diagram),
            self._deployment(diagram),
            self._views(diagram),
        ]
        text = "\n\n".join("\n".join(lines) for lines in sections if lines)
        return f"{text}\n"

    def _assign_identifiers(self, project: Project) -> None:
        registry = LikeC4IdentifierRegistry()
        self._model_ids = {}
        self._deployment_ids = {}

        for element in project.model.elements:
            parent = self._model_ids[element.parent] if element.parent else None
            self._model_ids[element] = registry.register(
                element.alias or element.title or element.kind,
                parent_fqn=parent.fqn if parent else None,
            )

        for node in project.deployment.nodes:
            parent_id = (
                self._deployment_ids[node.parent] if node.parent else None
            )
            self._deployment_ids[node] = registry.register(
                node.alias or node.title or node.kind,
                parent_fqn=parent_id.fqn if parent_id else None,
                namespace="deployment",
            )

        # Instances come second: an anonymous instance gets its identifier
        # implicitly from its element, so a node of the same name wins.
        for instance in project.deployment.instances:
            implied = self._model_ids[instance.element].identifier
            self._deployment_ids[instance] = registry.register(
                instance.alias or implied,
                parent_fqn=self._deployment_ids[instance.parent].fqn,
                namespace="deployment",
            )

    def _ref(self, item: Any, deployment: bool) -> str:
        if deployment:
            return self._deployment_ids[item].fqn

        return self._model_ids[item].fqn

    def _specification(self, project: Project) -> list[str]:
        spec = project.specification
        body: list[str] = [
            f"color {c.name} {c.value}" for c in spec.colors.values()
        ]

        for kind in spec.element_kinds.values():
            body += self._element_kind("element", kind)

        for rel_kind in spec.relationship_kinds.values():
            body += self._relationship_kind(rel_kind)

        for tag in spec.tags.values():
            body += block(
                f"tag {tag.name}", [f"color {tag.color}"] if tag.color else []
            )

        for kind in spec.deployment_kinds.values():
            body += self._element_kind("deploymentNode", kind)

        return block("specification", body) if body else []

    @staticmethod
    def _element_kind(keyword: str, kind: ElementKind) -> list[str]:
        body = [
            *tags_line(kind.tags),
            *_string("title", kind.title),
            *_string("technology", kind.technology),
            *_markdown("description", kind.description),
            *_string("notation", kind.notation),
            *style_block(kind.style),
        ]
        return block(f"{keyword} {kind.name}", body)

    @staticmethod
    def _relationship_kind(kind: RelationshipKind) -> list[str]:
        body = [
            *_string("technology", kind.technology),
            *_markdown("description", kind.description),
            # Relationship kinds take style properties directly, with no
            # ``style`` block (checked against LikeC4 1.60.0).
            *[f"{key} {style_value(key, v)}" for key, v in kind.style.items()],
        ]
        return block(f"relationship {kind.name}", body)

    def _model(self, project: Project) -> list[str]:
        body: list[str] = []
        for element in project.model.roots:
            body += self._element(element)

        for rel in project.model.relationships:
            body += self._relationship(rel)

        return block("model", body) if body else []

    def _element(self, element: Element) -> list[str]:
        ident = self._model_ids[element].identifier
        header = f"{ident} = {element.kind}"

        if element.title:
            header += f" {quote_likec4_string(element.title)}"

        body = [
            *tags_line(element.tags),
            *_string("summary", element.summary),
            *_markdown("description", element.description),
            *_string("technology", element.technology),
            *([f"icon {element.icon}"] if element.icon else []),
            *style_block(element.style),
            *metadata_block(element.metadata),
            *link_lines(element.links),
        ]

        for child in element.children:
            body += self._element(child)

        return block(header, body, collapse=not element.children)

    def _relationship(self, rel: Relationship) -> list[str]:
        header = (
            f"{self._ref(rel.source, False)} "
            f"{self._arrow(rel.kind, rel.bidirectional)} "
            f"{self._ref(rel.target, False)}"
        )

        if rel.title:
            header += f" {quote_likec4_string(rel.title)}"

        body = [
            *tags_line(rel.tags),
            *_string("technology", rel.technology),
            *_markdown("description", rel.description),
            *metadata_block(rel.metadata),
            *link_lines(rel.links),
            *([f"navigateTo {rel.navigate_to}"] if rel.navigate_to else []),
            *style_block(rel.style),
        ]
        return block(header, body)

    @staticmethod
    def _arrow(kind: str | None, bidirectional: bool) -> str:
        head = "<->" if bidirectional else "->"
        return f"-[{kind}]{head}" if kind else head

    def _deployment(self, project: Project) -> list[str]:
        body: list[str] = []
        for node in project.deployment.roots:
            body += self._node(node)

        for rel in project.deployment.relationships:
            body += self._deployment_relationship(rel)

        return block("deployment", body) if body else []

    def _node(self, node: DeploymentNode) -> list[str]:
        ident = self._deployment_ids[node].identifier
        header = f"{ident} = {node.kind}"

        if node.title:
            header += f" {quote_likec4_string(node.title)}"

        body = [
            *tags_line(node.tags),
            *_markdown("description", node.description),
            *_string("technology", node.technology),
            *style_block(node.style),
            *metadata_block(node.metadata),
            *link_lines(node.links),
        ]

        for instance in node.instances:
            body += self._instance(instance)

        for child in node.children:
            body += self._node(child)

        return block(header, body, collapse=not node.children)

    def _instance(self, instance: DeploymentInstance) -> list[str]:
        ident = self._deployment_ids[instance].identifier
        element = self._model_ids[instance.element]
        header = f"instanceOf {element.fqn}"

        if instance.alias is not None or ident != element.identifier:
            header = f"{ident} = {header}"

        body = [
            *tags_line(instance.tags),
            *_string("title", instance.title),
            *_markdown("description", instance.description),
            *_string("technology", instance.technology),
            *style_block(instance.style),
            *metadata_block(instance.metadata),
            *link_lines(instance.links),
        ]
        return block(header, body)

    def _deployment_relationship(
        self, rel: DeploymentRelationship
    ) -> list[str]:
        header = (
            f"{self._ref(rel.source, True)} "
            f"{self._arrow(rel.kind, rel.bidirectional)} "
            f"{self._ref(rel.target, True)}"
        )

        if rel.title:
            header += f" {quote_likec4_string(rel.title)}"

        body = [
            *tags_line(rel.tags),
            *_string("technology", rel.technology),
            *_markdown("description", rel.description),
            *metadata_block(rel.metadata),
            *link_lines(rel.links),
            *style_block(rel.style),
        ]
        return block(header, body)

    def _views(self, project: Project) -> list[str]:
        body: list[str] = []

        for view in project.views.all:
            if isinstance(view, ElementView):
                body += self._predicate_view(view, False)
            elif isinstance(view, DeploymentView):
                body += self._predicate_view(view, True)
            else:
                body += self._dynamic_view(view)

        return block("views", body) if body else []

    @staticmethod
    def _view_properties(view: _View) -> list[str]:
        return [
            *tags_line(view.tags),
            *_string("title", view.title),
            *_markdown("description", view.description),
            *link_lines(view.links),
        ]

    def _predicate_view(
        self, view: ElementView | DeploymentView, deployment: bool
    ) -> list[str]:
        header = "deployment view" if deployment else "view"
        header += f" {view.key}"
        if isinstance(view, ElementView) and view.scope is not None:
            header += f" of {self._ref(view.scope, False)}"

        body = self._view_properties(view)
        for rule in view.rules:
            if isinstance(rule, IncludeRule):
                suffix = (
                    f" with {{ navigateTo {rule.navigate_to} }}"
                    if rule.navigate_to
                    else ""
                )
                body += self._predicate_lines(
                    "include", rule.items, deployment, suffix
                )
            elif isinstance(rule, ExcludeRule):
                body += self._predicate_lines("exclude", rule.items, deployment)
            elif isinstance(rule, StyleRule):
                targets = ", ".join(
                    self._item(item, deployment) for item in rule.targets
                )
                props = [
                    f"{key} {style_value(key, value)}"
                    for key, value in rule.properties
                ]
                body += block(f"style {targets}", props)
            elif isinstance(rule, AutoLayoutRule):
                parts = [
                    str(part)
                    for part in (rule.direction, rule.rank_sep, rule.node_sep)
                    if part is not None
                ]
                body.append("autoLayout " + " ".join(parts))

        return block(header, body, braces_if_empty=True)

    def _predicate_lines(
        self,
        keyword: str,
        items: Sequence[Any],
        deployment: bool,
        suffix: str = "",
    ) -> list[str]:
        """Group plain items in one line; complex items get their own."""
        lines: list[str] = []
        simple: list[str] = []

        def flush() -> None:
            if simple:
                lines.append(f"{keyword} {', '.join(simple)}{suffix}")
                simple.clear()

        for item in items:
            if isinstance(
                item, (*RELATIONSHIP_PREDICATES, Where, RawPredicate)
            ):
                flush()
                lines.append(
                    f"{keyword} {self._item(item, deployment)}{suffix}"
                )
            else:
                simple.append(self._item(item, deployment))

        flush()
        return lines

    def _item(self, item: Any, deployment: bool) -> str:  # noqa: C901
        if isinstance(item, Wildcard):
            return "*"
        if isinstance(item, Children):
            return f"{self._ref(item.element, deployment)}.*"
        if isinstance(item, Descendants):
            return f"{self._ref(item.element, deployment)}.**"
        if isinstance(item, RawPredicate):
            return item.text
        if isinstance(item, Where):
            conditions = []
            if item.tag is not None:
                conditions.append(f"tag is #{item.tag}")
            if item.kind is not None:
                conditions.append(f"kind is {item.kind}")
            return f"{self._item(item.item, deployment)} where " + " and ".join(
                conditions
            )
        if isinstance(item, Between):
            arrow = "<->" if item.both else "->"
            source = self._item(item.source, deployment)
            return f"{source} {arrow} {self._item(item.target, deployment)}"
        if isinstance(item, Incoming):
            return f"-> {self._item(item.item, deployment)}"
        if isinstance(item, Outgoing):
            return f"{self._item(item.item, deployment)} ->"
        if isinstance(item, InOut):
            return f"-> {self._item(item.item, deployment)} ->"
        return self._ref(item, deployment)

    def _dynamic_view(self, view: DynamicView) -> list[str]:
        body = self._view_properties(view)
        if view.variant != "diagram":
            body.append(f"variant {view.variant}")

        for step in view.steps:
            body += self._step(step)

        for rule in view.rules:
            if isinstance(rule, AutoLayoutRule):
                parts = [
                    str(part)
                    for part in (rule.direction, rule.rank_sep, rule.node_sep)
                    if part is not None
                ]
                body.append("autoLayout " + " ".join(parts))

        return block(f"dynamic view {view.key}", body, braces_if_empty=True)

    def _step(self, step: DynamicStep) -> list[str]:
        arrow = "<-" if step.backward else "->"
        header = (
            f"{self._ref(step.source, False)} {arrow} "
            f"{self._ref(step.target, False)}"
        )
        if step.title:
            header += f" {quote_likec4_string(step.title)}"

        body = [
            *_markdown("description", step.description),
            *_string("technology", step.technology),
            *_markdown("notes", step.notes),
            *([f"navigateTo {step.navigate_to}"] if step.navigate_to else []),
            *([f"color {step.color}"] if step.color else []),
        ]
        return block(header, body)

    @override
    def render_bytes(
        self,
        diagram: Project,
        *,
        format: DiagramFormat,
    ) -> bytes:
        """Render a project and export it through the backend."""
        backend = self._require_backend("byte")
        return backend.to_bytes(
            self.render(diagram),
            format=format,
            view_key=self._resolve_view_key(diagram),
        )

    @override
    def render_file(
        self,
        diagram: Project,
        output_path: Path,
        *,
        format: DiagramFormat,
        overwrite: bool = True,
    ) -> Path:
        """Render a project and write the exported image through the backend."""
        backend = self._require_backend("file")
        return backend.to_file(
            self.render(diagram),
            output_path,
            format=format,
            overwrite=overwrite,
            view_key=self._resolve_view_key(diagram),
        )

    def _resolve_view_key(self, diagram: Project) -> str:
        """Return the configured view key or the project's only view."""
        view_key = self._view_key or diagram.view_key
        if view_key is not None:
            return view_key

        views = diagram.views.all
        if len(views) == 1:
            return views[0].key

        raise LikeC4BackendConfigurationError(
            "LikeC4 image export needs a view key: the project has "
            f"{len(views)} views. Pass view_key (--likec4-view-key)."
        )

    def _require_backend(self, kind: str) -> BaseLikeC4Backend:
        if self._backend is None:
            raise LikeC4BackendConfigurationError(
                f"LikeC4 {kind} export requires a configured backend. "
                "Configure LikeC4 export with a backend such as "
                "LocalLikeC4Backend."
            )
        return self._backend

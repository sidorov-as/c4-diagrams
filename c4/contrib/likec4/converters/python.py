from __future__ import annotations

import keyword
import re
from collections.abc import Mapping
from typing import Any

from c4.contrib.likec4 import (
    Between,
    Children,
    DeploymentInstance,
    DeploymentNode,
    DeploymentView,
    Descendants,
    DynamicView,
    Element,
    ElementView,
    Incoming,
    InOut,
    Link,
    Outgoing,
    Project,
    RawPredicate,
    Where,
    Wildcard,
)
from c4.contrib.likec4._views import (
    AutoLayoutRule,
    ExcludeRule,
    IncludeRule,
    StyleRule,
)

MAX_LINE_LENGTH = 79
_RESERVED_NAMES = frozenset({
    "Between",
    "Children",
    "Descendants",
    "InOut",
    "Incoming",
    "Outgoing",
    "Project",
    "RawPredicate",
    "Rel",
    "Where",
    "Wildcard",
    "deployment",
    "model",
    "project",
    "spec",
    "views",
})
_PREDICATE_NAMES = {
    Between: "Between",
    Children: "Children",
    Descendants: "Descendants",
    InOut: "InOut",
    Incoming: "Incoming",
    Outgoing: "Outgoing",
    RawPredicate: "RawPredicate",
    Where: "Where",
    Wildcard: "Wildcard",
}


class _Code(str):
    """A generated Python expression which must not be quoted."""


def _rule_items(rule: Any) -> tuple[Any, ...]:
    """Return the predicate items of an include, exclude or style rule."""
    if isinstance(rule, (IncludeRule, ExcludeRule)):
        return rule.items

    if isinstance(rule, StyleRule):
        return rule.targets

    return ()


def _collect_instances(item: Any, found: set[int]) -> None:
    """Add the ids of every deployment instance used inside ``item``."""
    if isinstance(item, DeploymentInstance):
        found.add(id(item))
    elif isinstance(item, (Children, Descendants)):
        _collect_instances(item.element, found)
    elif isinstance(item, Where):
        _collect_instances(item.item, found)
    elif isinstance(item, Between):
        _collect_instances(item.source, found)
        _collect_instances(item.target, found)
    elif isinstance(item, (Incoming, Outgoing, InOut)):
        _collect_instances(item.item, found)


class ProjectPythonCodegen:
    """Generate executable public LikeC4 authoring code from a project."""

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._variables: dict[int, str] = {}
        self._used: set[str] = set(_RESERVED_NAMES)
        self._imports: set[str] = set()
        self._referenced_instances: set[int] = set()

    def generate(self, project: Project) -> str:
        """Return executable code that recreates ``project``."""
        self._lines = []
        self._variables = {}
        self._used = set(_RESERVED_NAMES)
        self._imports = {"Project"}
        self._referenced_instances = self._find_referenced_instances(project)

        self._render_project(project)
        self._render_specification(project)
        self._render_model(project)
        self._render_deployment(project)
        self._render_views(project)

        header = self._render_imports()
        body = "\n".join(self._lines).rstrip("\n")
        return f"{header}\n\n\n{body}\n"

    def _render_imports(self) -> str:
        names = sorted(self._imports)
        line = f"from c4.contrib.likec4 import {', '.join(names)}"
        if len(line) <= MAX_LINE_LENGTH:
            return line

        body = "".join(f"    {name},\n" for name in names)
        return f"from c4.contrib.likec4 import (\n{body})"

    def _render_project(self, project: Project) -> None:
        arguments: list[object] = []
        kwargs: dict[str, object] = {}
        if project.name is not None:
            arguments.append(project.name)

        if project.view_key is not None:
            kwargs["view_key"] = project.view_key

        self._call("project = Project", arguments, kwargs)

    def _render_specification(self, project: Project) -> None:
        spec = project.specification
        if not (
            spec.colors
            or spec.element_kinds
            or spec.relationship_kinds
            or spec.tags
            or spec.deployment_kinds
        ):
            return

        self._add("")
        self._add("spec = project.specification")

        for color in spec.colors.values():
            self._call("spec.color", [color.name, color.value])

        for kind in spec.element_kinds.values():
            self._call("spec.element", [kind.name], self._kind_kwargs(kind))

        for relationship in spec.relationship_kinds.values():
            self._call(
                "spec.relationship",
                [relationship.name],
                {
                    **self._present(
                        technology=relationship.technology,
                        description=relationship.description,
                    ),
                    **relationship.style,
                },
            )

        for tag in spec.tags.values():
            self._call("spec.tag", [tag.name], self._present(color=tag.color))

        for kind in spec.deployment_kinds.values():
            self._call(
                "spec.deployment_node", [kind.name], self._kind_kwargs(kind)
            )

    def _kind_kwargs(self, kind: Any) -> dict[str, object]:
        return {
            **self._present(
                title=kind.title,
                technology=kind.technology,
                description=kind.description,
                notation=kind.notation,
                tags=list(kind.tags) or None,
            ),
            **kind.style,
        }

    def _render_model(self, project: Project) -> None:
        model = project.model
        if not model.elements:
            return

        self._add("")
        self._add("model = project.model")

        for element in model.elements:
            self._render_element(element)

        if model.relationships:
            self._add("")

        for relationship in model.relationships:
            self._render_relationship(
                relationship,
                self._present(navigate_to=relationship.navigate_to),
            )

    def _render_element(self, element: Element) -> None:
        variable = self._variable(element, element.alias or element.title)
        style = dict(element.style)
        icon_style = style.pop("icon", None)
        kwargs: dict[str, object] = {}
        if element.parent is not None:
            kwargs["parent"] = _Code(self._name(element.parent))

        kwargs.update(
            self._present(
                alias=element.alias,
                summary=element.summary,
                description=element.description,
                technology=element.technology,
                tags=list(element.tags) or None,
                icon=element.icon,
                metadata=self._metadata(element.metadata),
                links=self._links(element.links),
            )
        )
        kwargs.update(style)
        arguments = self._with_title([element.kind], element.title)
        self._call(f"{variable} = model.element", arguments, kwargs)

        if icon_style is not None:
            self._call(f"{variable}.set_style", [], {"icon": icon_style})

    def _render_deployment(self, project: Project) -> None:
        deployment = project.deployment
        if not deployment.nodes:
            return

        self._add("")
        self._add("deployment = project.deployment")

        for node in deployment.nodes:
            self._render_node(node)

        if deployment.instances:
            self._add("")

        for instance in deployment.instances:
            self._render_instance(instance)

        if deployment.relationships:
            self._add("")

        for relationship in deployment.relationships:
            self._render_relationship(relationship, {})

    def _render_node(self, node: DeploymentNode) -> None:
        variable = self._variable(node, node.alias or node.title)
        kwargs: dict[str, object] = {}
        if node.parent is not None:
            kwargs["parent"] = _Code(self._name(node.parent))

        kwargs.update(
            self._present(
                alias=node.alias,
                description=node.description,
                technology=node.technology,
                tags=list(node.tags) or None,
                metadata=self._metadata(node.metadata),
                links=self._links(node.links),
            )
        )
        kwargs.update(node.style)

        self._call(
            f"{variable} = deployment.node",
            self._with_title([node.kind], node.title),
            kwargs,
        )

    def _render_instance(self, instance: DeploymentInstance) -> None:
        arguments: list[object] = [_Code(self._name(instance.element))]
        if instance.alias is not None:
            arguments.append(instance.alias)

        kwargs = {
            **self._present(
                title=instance.title,
                description=instance.description,
                technology=instance.technology,
                tags=list(instance.tags) or None,
                metadata=self._metadata(instance.metadata),
                links=self._links(instance.links),
            ),
            **instance.style,
        }

        prefix = f"{self._name(instance.parent)}.instance"
        if id(instance) in self._referenced_instances:
            variable = self._variable(
                instance,
                instance.alias or f"{self._name(instance.element)}_instance",
            )
            prefix = f"{variable} = {prefix}"

        self._call(prefix, arguments, kwargs)

    def _render_views(self, project: Project) -> None:
        if not project.views.all:
            return

        self._add("")
        self._add("views = project.views")

        for view in project.views.all:
            self._add("")
            variable = self._variable(view, view.key)
            if isinstance(view, ElementView):
                self._render_element_view(variable, view)
            elif isinstance(view, DeploymentView):
                self._render_deployment_view(variable, view)
            elif isinstance(view, DynamicView):
                self._render_dynamic_view(variable, view)
            else:
                raise TypeError(
                    "Unsupported LikeC4 view for Python conversion: "
                    f"{type(view)!r}"
                )

    def _view_kwargs(self, view: Any) -> dict[str, object]:
        return self._present(
            description=view.description,
            tags=list(view.tags) or None,
            links=self._links(view.links),
        )

    def _render_element_view(self, variable: str, view: ElementView) -> None:
        kwargs: dict[str, object] = {}
        if view.scope is not None:
            kwargs["of"] = _Code(self._name(view.scope))

        kwargs.update(self._view_kwargs(view))
        self._call(
            f"{variable} = views.element_view",
            self._with_title([view.key], view.title),
            kwargs,
        )
        self._render_rules(variable, view.rules)

    def _render_deployment_view(
        self, variable: str, view: DeploymentView
    ) -> None:
        self._call(
            f"{variable} = views.deployment_view",
            self._with_title([view.key], view.title),
            self._view_kwargs(view),
        )
        self._render_rules(variable, view.rules)

    def _render_dynamic_view(self, variable: str, view: DynamicView) -> None:
        kwargs: dict[str, object] = {}
        if view.variant != "diagram":
            kwargs["variant"] = view.variant

        kwargs.update(self._view_kwargs(view))
        self._call(
            f"{variable} = views.dynamic_view",
            self._with_title([view.key], view.title),
            kwargs,
        )

        for step in view.steps:
            self._call(
                f"{variable}.{'back' if step.backward else 'step'}",
                self._with_title(
                    [
                        _Code(self._name(step.source)),
                        _Code(self._name(step.target)),
                    ],
                    step.title,
                ),
                self._present(
                    description=step.description,
                    technology=step.technology,
                    notes=step.notes,
                    navigate_to=step.navigate_to,
                    color=step.color,
                ),
            )

    def _render_rules(self, variable: str, rules: list[Any]) -> None:
        for rule in rules:
            if isinstance(rule, IncludeRule):
                self._call(
                    f"{variable}.include",
                    [self._item(item) for item in rule.items],
                    self._present(navigate_to=rule.navigate_to),
                )
            elif isinstance(rule, ExcludeRule):
                self._call(
                    f"{variable}.exclude",
                    [self._item(item) for item in rule.items],
                )
            elif isinstance(rule, StyleRule):
                self._call(
                    f"{variable}.style",
                    [self._item(item) for item in rule.targets],
                    dict(rule.properties),
                )
            elif isinstance(rule, AutoLayoutRule):
                arguments: list[object] = [rule.direction]
                if rule.rank_sep is not None:
                    arguments.append(rule.rank_sep)
                if rule.node_sep is not None:
                    arguments.append(rule.node_sep)
                self._call(f"{variable}.auto_layout", arguments)
            else:  # pragma: no cover - rules are built by the views API
                raise TypeError(f"Unsupported LikeC4 view rule: {type(rule)!r}")

    def _item(self, item: Any) -> _Code:
        """Render a view predicate item as a Python expression."""
        if isinstance(item, (Element, DeploymentNode, DeploymentInstance)):
            return _Code(self._name(item))

        name = _PREDICATE_NAMES.get(type(item))
        if name is None:
            raise TypeError(
                f"Unsupported LikeC4 predicate item: {type(item)!r}"
            )

        self._imports.add(name)
        if isinstance(item, Wildcard):
            return _Code("Wildcard()")
        if isinstance(item, (Children, Descendants)):
            return _Code(f"{name}({self._item(item.element)})")
        if isinstance(item, RawPredicate):
            return _Code(f"RawPredicate({item.text!r})")
        if isinstance(item, Where):
            parts = [str(self._item(item.item))]
            parts.extend(
                f"{key}={value!r}"
                for key, value in self._present(
                    tag=item.tag, kind=item.kind
                ).items()
            )
            return _Code(f"Where({', '.join(parts)})")
        if isinstance(item, (Incoming, Outgoing, InOut)):
            return _Code(f"{name}({self._item(item.item)})")

        parts = [str(self._item(side)) for side in (item.source, item.target)]
        if item.both:
            parts.append("both=True")

        return _Code(f"Between({', '.join(parts)})")

    def _render_relationship(
        self, relationship: Any, extra: Mapping[str, object]
    ) -> None:
        """Write ``source >> Rel(...) >> target``, or ``source >> target``."""
        source = self._name(relationship.source)
        target = self._name(relationship.target)
        arguments = self._with_title([], relationship.title)
        kwargs = {
            **self._relationship_kwargs(relationship),
            **extra,
            **relationship.style,
        }

        if not arguments and not kwargs:
            self._add(f"{source} >> {target}")
            return

        self._imports.add("Rel")
        self._call(
            f"{source} >> Rel", arguments, kwargs, suffix=f" >> {target}"
        )

    def _relationship_kwargs(self, relationship: Any) -> dict[str, object]:
        kwargs = self._present(
            description=relationship.description,
            technology=relationship.technology,
            kind=relationship.kind,
        )
        if relationship.bidirectional:
            kwargs["bidirectional"] = True

        kwargs.update(
            self._present(
                tags=list(relationship.tags) or None,
                metadata=self._metadata(relationship.metadata),
                links=self._links(relationship.links),
            )
        )
        return kwargs

    @staticmethod
    def _present(**values: object) -> dict[str, object]:
        return {
            key: value for key, value in values.items() if value is not None
        }

    @staticmethod
    def _with_title(arguments: list[object], title: str | None) -> list[object]:
        return [*arguments, title] if title is not None else arguments

    @staticmethod
    def _metadata(metadata: Mapping[str, Any]) -> dict[str, Any] | None:
        if not metadata:
            return None

        return {
            key: list(value) if isinstance(value, tuple) else value
            for key, value in metadata.items()
        }

    @staticmethod
    def _links(links: tuple[Link, ...]) -> list[Any] | None:
        if not links:
            return None

        return [
            link.url if link.title is None else (link.url, link.title)
            for link in links
        ]

    @staticmethod
    def _find_referenced_instances(project: Project) -> set[int]:
        """Return ids of the instances used as relationship ends or items."""
        referenced = {
            id(end)
            for relationship in project.deployment.relationships
            for end in (relationship.source, relationship.target)
            if isinstance(end, DeploymentInstance)
        }
        for view in project.views.all:
            if isinstance(view, DeploymentView):
                for rule in view.rules:
                    for item in _rule_items(rule):
                        _collect_instances(item, referenced)

        return referenced

    def _name(self, obj: object) -> str:
        try:
            return self._variables[id(obj)]
        except KeyError as exc:  # pragma: no cover - ordering invariant
            raise ValueError(f"{obj!r} is used before it is declared") from exc

    def _variable(self, obj: object, hint: str | None) -> str:
        stem = re.sub(r"\W", "_", (hint or "item").strip()).strip("_").lower()
        if not stem or stem[0].isdigit():
            stem = f"item_{stem}".rstrip("_")

        if keyword.iskeyword(stem):
            stem = f"{stem}_"

        if not stem.isidentifier():
            stem = "item"

        separator = "" if stem.endswith("_") else "_"
        candidate, suffix = stem, 2
        while candidate in self._used:
            candidate, suffix = f"{stem}{separator}{suffix}", suffix + 1

        self._used.add(candidate)
        self._variables[id(obj)] = candidate
        return candidate

    def _call(
        self,
        prefix: str,
        arguments: list[object],
        kwargs: Mapping[str, object] | None = None,
        suffix: str = "",
    ) -> None:
        values = [self._literal(value) for value in arguments]
        values.extend(
            f"{name}={self._literal(value)}"
            for name, value in (kwargs or {}).items()
        )

        line = f"{prefix}({', '.join(values)}){suffix}"
        if len(line) <= MAX_LINE_LENGTH or not values:
            self._add(line)
            return

        self._add(f"{prefix}(")

        for value in values:
            self._add(f"    {value},")

        self._add(f"){suffix}")

    @staticmethod
    def _literal(value: object) -> str:
        return str(value) if isinstance(value, _Code) else repr(value)

    def _add(self, line: str) -> None:
        self._lines.append(line)


def project_to_python_code(project: Project) -> str:
    """Generate executable public LikeC4 code that recreates a project."""
    return ProjectPythonCodegen().generate(project)


__all__ = ("ProjectPythonCodegen", "project_to_python_code")

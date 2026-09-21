from __future__ import annotations

import keyword
from collections.abc import Iterator, Mapping
from pprint import pformat
from typing import Any

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import (
    AutoLayout,
    StructurizrRenderOptions,
)
from c4.contrib.structurizr.workspace import (
    ComponentView,
    ContainerView,
    DeploymentView,
    DynamicView,
    SystemContextView,
    SystemLandscapeView,
)


class _Code(str):
    """A generated Python expression which must not be quoted."""


class WorkspacePythonCodegen:
    """Generate executable public Structurizr DSL from a workspace."""

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._variables: dict[str, str] = {}
        self._used_variables: set[str] = set()

    def generate(self, workspace: Workspace) -> str:
        """Return executable public DSL that recreates ``workspace``."""
        self._lines, self._variables, self._used_variables = [], {}, set()
        self._render_imports(workspace)
        self._render_workspace(workspace)
        return "\n".join(self._lines) + "\n"

    def _render_imports(self, workspace: Workspace) -> None:
        if any(
            self._relationship_uses_rel(relationship)
            for relationship in workspace.model.relationships
        ):
            self._lines.append(
                "from c4.contrib.structurizr import Rel, Workspace"
            )
        else:
            self._lines.append("from c4.contrib.structurizr import Workspace")

        if self._structurizr_options(workspace) is not None:
            self._lines.append(
                "from c4.contrib.structurizr.renderer import "
                "StructurizrRenderOptions"
            )
        if self._uses_auto_layout(workspace):
            self._lines.append(
                "from c4.contrib.structurizr.renderer import AutoLayout"
            )

        self._lines.extend(["", ""])

    def _render_workspace(self, workspace: Workspace) -> None:
        self._render_workspace_definition(workspace)
        self._render_workspace_properties_and_styles(workspace)

        if (
            workspace.properties
            or workspace.element_styles
            or workspace.relationship_styles
        ):
            self._add("")

        self._render_workspace_model(workspace)

        self._add("")
        self._render_views(workspace)

    def _render_workspace_definition(self, workspace: Workspace) -> None:
        kwargs: dict[str, object] = {}
        if workspace.description is not None:
            kwargs["description"] = workspace.description

        if workspace.theme is not None:
            kwargs["theme"] = workspace.theme

        if options := self._structurizr_options(workspace):
            kwargs["render_options"] = self._render_options(options)

        self._add_call("workspace = Workspace", [workspace.name], kwargs)

    def _render_workspace_properties_and_styles(
        self, workspace: Workspace
    ) -> None:
        for key, value in workspace.properties.items():
            self._add(f"workspace.set_property({key!r}, {value!r})")

        for style in workspace.element_styles:
            self._add_call(
                "workspace.styles.element", [style.tag], dict(style.properties)
            )

        for style in workspace.relationship_styles:
            self._add_call(
                "workspace.styles.relationship",
                [style.tag],
                dict(style.properties),
            )

    def _render_workspace_model(self, workspace: Workspace) -> None:
        self._add("with workspace.model as model:")
        start = len(self._lines)

        for element in self._iter_model_items(workspace):
            self._render_model_element(element, indent="    ")

        self._render_instances(workspace, indent="    ")

        for relationship in workspace.model.relationships:
            self._render_relationship(relationship, indent="    ")

        if len(self._lines) == start:
            self._add("    pass")

    def _render_model_element(self, element: Any, *, indent: str) -> None:
        variable = self._variable(element.alias)
        kwargs = self._element_kwargs(element)
        factories = {
            "Person": "model.Person",
            "SoftwareSystem": "model.SoftwareSystem",
            "Container": "model.Container",
            "Component": "model.Component",
            "InfrastructureNode": "model.InfrastructureNode",
            "DeploymentNode": "model.DeploymentNode",
        }

        try:
            factory = factories[type(element).__name__]
        except KeyError as exc:
            raise TypeError(
                "Unsupported Structurizr model element for Python conversion: "
                f"{type(element)!r}"
            ) from exc

        if type(element).__name__ in {"Container", "Component"}:
            kwargs["owner"] = self._code_variable(element.parent.alias)
        elif type(element).__name__ in {"InfrastructureNode", "DeploymentNode"}:
            self._node_kwargs(element, kwargs)

        self._add_call(
            f"{indent}{variable} = {factory}", [element.name], kwargs
        )

    @staticmethod
    def _element_kwargs(element: Any) -> dict[str, object]:
        kwargs: dict[str, object] = {"alias": element.alias}
        if element.description is not None:
            kwargs["description"] = element.description
        if element.technology is not None:
            kwargs["technology"] = element.technology
        if element.tags:
            kwargs["tags"] = list(element.tags)
        if element.properties:
            kwargs["properties"] = dict(element.properties)
        if element.url is not None:
            kwargs["url"] = element.url
        if element.style_properties:
            kwargs["style"] = dict(element.style_properties)
        return kwargs

    def _node_kwargs(self, node: Any, kwargs: dict[str, object]) -> None:
        if node.parent is None:
            kwargs["environment"] = node.environment
        else:
            kwargs["parent"] = self._code_variable(node.parent.alias)

    def _render_instances(self, workspace: Workspace, *, indent: str) -> None:
        emitted = False

        for instance in (
            *workspace.model.software_system_instances,
            *workspace.model.container_instances,
        ):
            node = instance.parent_node
            variable = self._variable(instance.alias)
            kwargs = self._element_kwargs(instance)
            kwargs.pop("technology", None)
            factory = (
                "SoftwareSystemInstance"
                if instance.__class__.__name__ == "SoftwareSystemInstance"
                else "ContainerInstance"
            )
            self._add_call(
                f"{indent}{variable} = "
                f"{self._code_variable(node.alias)}.{factory}",
                [self._code_variable(instance.model_element.alias)],
                kwargs,
            )
            emitted = True

        if emitted:
            self._add("")

    @staticmethod
    def _relationship_kwargs(relationship: Any) -> dict[str, object]:
        kwargs: dict[str, object] = {}
        if relationship.technology is not None:
            kwargs["technology"] = relationship.technology
        if relationship.tags:
            kwargs["tags"] = list(relationship.tags)
        if relationship.properties:
            kwargs["properties"] = dict(relationship.properties)
        if relationship.url is not None:
            kwargs["url"] = relationship.url
        if relationship.style:
            kwargs["style"] = dict(relationship.style)
        return kwargs

    @classmethod
    def _relationship_uses_rel(cls, relationship: Any) -> bool:
        return relationship.description is not None or bool(
            cls._relationship_kwargs(relationship)
        )

    def _render_relationship(self, relationship: Any, *, indent: str) -> None:
        source = self._variables[relationship.source.alias]
        destination = self._code_variable(relationship.destination.alias)
        if not self._relationship_uses_rel(relationship):
            self._add(f"{indent}{source} >> {destination}")
            return

        arguments = (
            []
            if relationship.description is None
            else [relationship.description]
        )
        values = [self._literal(value) for value in arguments]
        values.extend(
            f"{name}={self._literal(value)}"
            for name, value in self._relationship_kwargs(relationship).items()
        )

        self._add(
            f"{indent}{source} >> Rel({', '.join(values)}) >> {destination}"
        )

    def _render_views(self, workspace: Workspace) -> None:
        for view in workspace.views:
            kwargs = self._view_kwargs(view)
            if isinstance(view, SystemLandscapeView):
                self._render_system_landscape_view(kwargs)
            elif isinstance(
                view, (SystemContextView, ContainerView, ComponentView)
            ):
                self._render_scoped_view(view, kwargs)
            elif isinstance(view, DynamicView):
                self._render_dynamic_view(view, kwargs)
            elif isinstance(view, DeploymentView):
                self._render_deployment_view(view, kwargs)
            else:
                raise TypeError(
                    "Unsupported Structurizr view for Python conversion: "
                    f"{type(view)!r}"
                )
            self._add("")

    def _render_system_landscape_view(
        self, kwargs: Mapping[str, object]
    ) -> None:
        self._add_call("workspace.views.SystemLandscapeView", [], kwargs)

    def _render_scoped_view(
        self, view: Any, kwargs: Mapping[str, object]
    ) -> None:
        name = type(view).__name__
        scope = view.scope_target
        if scope is None:  # pragma: no cover - validated view invariant
            raise TypeError(f"{name} requires a scope.")

        self._add_call(
            f"workspace.views.{name}",
            [self._code_variable(scope.alias)],
            kwargs,
        )

    def _render_dynamic_view(
        self, view: DynamicView, kwargs: Mapping[str, object]
    ) -> None:
        variable = self._variable(view.key or "dynamic_view")
        self._add_call(
            f"{variable} = workspace.views.DynamicView",
            self._scope_arguments(view),
            kwargs,
        )

        for step in view.steps:
            self._add_call(
                f"{variable}.step",
                [
                    self._code_variable(step.source.alias),
                    self._code_variable(step.destination.alias),
                    *([] if step.description is None else [step.description]),
                ],
                self._step_kwargs(step),
            )

    def _render_deployment_view(
        self, view: DeploymentView, kwargs: dict[str, object]
    ) -> None:
        kwargs["environment"] = view.environment
        self._add_call(
            "workspace.views.DeploymentView",
            self._scope_arguments(view),
            kwargs,
        )

    def _scope_arguments(self, view: Any) -> list[object]:
        if view.scope_target is None:
            return []

        return [self._code_variable(view.scope_target.alias)]

    @staticmethod
    def _step_kwargs(step: Any) -> dict[str, object]:
        candidates = {
            "technology": step.technology,
            "tags": list(step.tags) if step.tags else None,
            "properties": dict(step.properties) if step.properties else None,
            "url": step.url,
            "style": dict(step.style) if step.style else None,
        }
        return {
            key: value for key, value in candidates.items() if value is not None
        }

    def _view_kwargs(self, view: Any) -> dict[str, object]:
        kwargs: dict[str, object] = {}
        for name, value in (
            ("key", view.key),
            ("title", view.title),
            ("description", view.description),
            ("tags", list(view.tags) if view.tags else None),
            (
                "properties",
                dict(view.properties) if view.properties else None,
            ),
        ):
            if value is not None:
                kwargs[name] = value

        if view.include_selectors:
            kwargs["include"] = self._selectors(view.include_selectors)
        if view.exclude_selectors:
            kwargs["exclude"] = self._selectors(view.exclude_selectors)
        if view.auto_layout is not None:
            kwargs["auto_layout"] = self._render_auto_layout(view.auto_layout)
        if view.animation:
            kwargs["animation"] = [
                self._selectors(step) for step in view.animation
            ]
        return kwargs

    def _selectors(self, selectors: tuple[str, ...]) -> _Code:
        return _Code(
            "["
            + ", ".join(
                self._variables.get(value, repr(value)) for value in selectors
            )
            + "]"
        )

    @staticmethod
    def _structurizr_options(
        workspace: Workspace,
    ) -> StructurizrRenderOptions | None:
        return workspace.render_options

    def _render_options(self, options: StructurizrRenderOptions) -> _Code:
        parts = []
        if options.auto_layout is not None:
            parts.append(
                f"auto_layout={self._render_auto_layout(options.auto_layout)}"
            )

        if options.style_preset is not None:
            parts.append(f"style_preset={options.style_preset!r}")

        return _Code("StructurizrRenderOptions(" + ", ".join(parts) + ")")

    @staticmethod
    def _render_auto_layout(auto_layout: AutoLayout) -> _Code:
        parts = [f"rank_direction={auto_layout.rank_direction!r}"]
        for name in ("implementation", "rank_separation", "node_separation"):
            if (value := getattr(auto_layout, name)) is not None:
                parts.append(f"{name}={value!r}")

        return _Code(f"AutoLayout({', '.join(parts)})")

    def _uses_auto_layout(self, workspace: Workspace) -> bool:
        options = self._structurizr_options(workspace)
        return bool(
            (options and options.auto_layout is not None)
            or any(view.auto_layout is not None for view in workspace.views)
        )

    def _variable(self, alias: str) -> str:
        if alias in self._variables:
            return self._variables[alias]

        stem = "".join(
            char if char.isalnum() or char == "_" else "_" for char in alias
        )

        if not stem or stem[0].isdigit():
            stem = f"element_{stem}"
        if keyword.iskeyword(stem):
            stem = f"{stem}_"

        candidate, suffix = stem, 2
        while candidate in self._used_variables:
            candidate, suffix = f"{stem}_{suffix}", suffix + 1

        self._used_variables.add(candidate)
        self._variables[alias] = candidate
        return candidate

    def _code_variable(self, alias: str) -> _Code:
        return _Code(self._variables[alias])

    @staticmethod
    def _iter_model_items(workspace: Workspace) -> Iterator[Any]:
        yield from (
            *workspace.model.people,
            *workspace.model.software_systems,
            *workspace.model.containers,
            *workspace.model.components,
            *workspace.model.deployment_nodes,
        )

    def _add_call(
        self, prefix: str, arguments: list[object], kwargs: Mapping[str, object]
    ) -> None:
        values = [self._literal(value) for value in arguments]
        values.extend(
            f"{name}={self._literal(value)}" for name, value in kwargs.items()
        )
        self._add(f"{prefix}({', '.join(values)})")

    @classmethod
    def _literal(cls, value: object) -> str:
        if isinstance(value, _Code):
            return str(value)

        if isinstance(value, list) and any(
            isinstance(item, (_Code, list)) for item in value
        ):
            return f"[{', '.join(cls._literal(item) for item in value)}]"

        return pformat(value, sort_dicts=False)

    def _add(self, line: str) -> None:
        self._lines.append(line)


def workspace_to_python_code(workspace: Workspace) -> str:
    """Generate executable public Structurizr DSL that recreates a workspace."""
    return WorkspacePythonCodegen().generate(workspace)


__all__ = ("WorkspacePythonCodegen", "workspace_to_python_code")

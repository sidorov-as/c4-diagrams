import ast
from dataclasses import asdict, dataclass, fields, is_dataclass
from inspect import Parameter, signature
from typing import Any

from c4.renderers.plantuml.layout_options import (
    BaseStyle,
    BaseTag,
    BoundaryStyle,
    BoundaryTag,
    ComponentTag,
    ContainerBoundaryStyle,
    ContainerTag,
    DiagramLayout,
    ElementStyle,
    ElementTag,
    EnterpriseBoundaryStyle,
    ExternalComponentTag,
    ExternalContainerTag,
    ExternalPersonTag,
    ExternalSystemTag,
    LayoutConfig,
    LayoutOptions,
    NodeTag,
    PersonTag,
    RelStyle,
    RelTag,
    SystemBoundaryStyle,
    SystemTag,
)

_BOOL_CALLS: tuple[tuple[str, str], ...] = (
    ("hide_stereotype", "hide_stereotype"),
    ("hide_person_sprite", "hide_person_sprite"),
    ("show_person_portrait", "show_person_portrait"),
    ("show_person_outline", "show_person_outline"),
    ("without_property_header", "without_property_header"),
)

_TAG_METHODS: dict[type[BaseTag], str] = {
    ExternalSystemTag: "add_external_system_tag",
    SystemTag: "add_system_tag",
    ExternalContainerTag: "add_external_container_tag",
    ContainerTag: "add_container_tag",
    ExternalComponentTag: "add_external_component_tag",
    ComponentTag: "add_component_tag",
    BoundaryTag: "add_boundary_tag",
    NodeTag: "add_node_tag",
    ElementTag: "add_element_tag",
    ExternalPersonTag: "add_external_person_tag",
    PersonTag: "add_person_tag",
    RelTag: "add_rel_tag",
}

_STYLE_METHODS: dict[type[BaseStyle], str] = {
    RelStyle: "update_rel_style",
    EnterpriseBoundaryStyle: "update_enterprise_boundary_style",
    SystemBoundaryStyle: "update_system_boundary_style",
    ContainerBoundaryStyle: "update_container_boundary_style",
    BoundaryStyle: "update_boundary_style",
    ElementStyle: "update_element_style",
}


_layout_options = LayoutOptions()


_SHOW_LEGEND_DEFAULTS = LayoutOptions().legend_defaults
_SHOW_FLOATING_LEGEND_DEFAULTS = _layout_options.floating_legend_defaults
_SET_SKETCH_STYLE_DEFAULTS = LayoutOptions().sketch_style_defaults
_SHOW_PERSON_SPRITE_DEFAULTS = LayoutOptions().person_sprite_defaults

LAYOUT_OPTIONS_VARIABLE_NAME = "plantuml_layout_options"


def _resolve_method(mapping: dict[type[Any], str], obj: Any) -> str:
    for cls in type(obj).mro():
        if cls in mapping:
            return mapping[cls]
    raise KeyError(type(obj))


@dataclass
class ChainCall:
    method: str
    args: list[ast.expr]
    keywords: list[ast.keyword]


@dataclass
class _MethodSignature:
    ordered_args: list[tuple[str, Any]]
    is_single_arg: bool
    is_single_kwonly_arg: bool


class MethodCallFormatter:
    def __init__(
        self,
        max_line: int = 79,
        owner_cls: type[Any] | None = None,
    ) -> None:
        self._max_line = max_line
        self._indent = " " * 4
        self._nested_indent = " " * 8
        self._owner_cls = owner_cls

    @staticmethod
    def _inspect_signature(
        cls: type[Any],
        method_name: str,
        kwargs: dict[str, Any],
    ) -> _MethodSignature:
        """
        Order kwargs in the same order as the method signature.

        Unknown kwargs (not present in the signature) are appended at the end,
        preserving their original insertion order.
        """
        method = getattr(cls, method_name)
        sig = signature(method)

        param_order: list[str] = []
        kwonly_params: list[Parameter] = []
        for param in sig.parameters.values():
            if param.name not in {"self", "cls"}:
                param_order.append(param.name)

            if param.kind is Parameter.KEYWORD_ONLY:
                kwonly_params.append(param)

        is_single_arg = len(param_order) == 1
        is_single_kwonly_arg = is_single_arg and len(kwonly_params) == 1

        ordered: list[tuple[str, Any]] = []
        seen: set[str] = set()

        for name in param_order:
            if name in kwargs:
                ordered.append((name, kwargs[name]))
                seen.add(name)

        for name, value in kwargs.items():
            if name not in seen:
                ordered.append((name, value))

        return _MethodSignature(
            ordered_args=ordered,
            is_single_arg=is_single_arg,
            is_single_kwonly_arg=is_single_kwonly_arg,
        )

    def format_call(
        self,
        method_name: str,
        call_args: dict[str, Any] | None = None,
    ) -> str:
        """
        Format a chained method call.

        Notes:
            - Arguments are rendered using `repr()` to keep
              output valid Python.
        """
        call_args = call_args or {}

        items: list[tuple[str, Any]] = list(call_args.items())
        is_single_arg = False
        is_single_kwonly_arg = False

        if self._owner_cls is not None and call_args:
            sig = self._inspect_signature(
                self._owner_cls, method_name, call_args
            )
            items = sig.ordered_args
            is_single_arg = sig.is_single_arg
            is_single_kwonly_arg = sig.is_single_kwonly_arg

        if not items:
            args_repr = ""
        elif is_single_arg and not is_single_kwonly_arg:
            _, value = items[0]
            args_repr = repr(value)
        else:
            args_repr = ", ".join(f"{arg}={value!r}" for arg, value in items)

        return f".{method_name}({args_repr})"

    def format_chain_call(self, code: str) -> str:
        if len(code) <= self._max_line:
            return code.strip()

        tree = ast.parse(code)

        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Assign):
            raise ValueError("Expected a single module-level assignment.")

        assign = tree.body[0]
        if len(assign.targets) != 1 or not isinstance(
            assign.targets[0], ast.Name
        ):
            raise ValueError("Expected simple `name = expr` assignment.")

        lhs = assign.targets[0].id
        base, chain = self._extract_chain(assign.value)

        lines: list[str] = [f"{lhs} = (", f"{self._indent}{self._expr(base)}"]

        for call in chain:
            lines.extend(self._render_chained_call(call))

        lines.append(")")
        return "\n".join(lines)

    def _extract_chain(
        self, expr: ast.expr
    ) -> tuple[ast.expr, list[ChainCall]]:
        chain: list[ChainCall] = []
        cur: ast.expr = expr

        while isinstance(cur, ast.Call) and isinstance(cur.func, ast.Attribute):
            chain.append(
                ChainCall(
                    method=cur.func.attr,
                    args=list(cur.args),
                    keywords=list(cur.keywords),
                )
            )
            cur = cur.func.value  # move "left" in the chain

        chain.reverse()
        return cur, chain

    def _render_chained_call(self, call: ChainCall) -> list[str]:
        if not call.args and not call.keywords:
            return [f"{self._indent}.{call.method}()"]

        lines: list[str] = [f"{self._indent}.{call.method}("]

        for arg in call.args:
            lines.append(f"{self._nested_indent}{self._expr(arg)},")

        for kw in call.keywords:
            if kw.arg is None:
                lines.append(f"{self._nested_indent}**{self._expr(kw.value)},")
            else:
                lines.append(
                    f"{self._nested_indent}{kw.arg}={self._expr(kw.value)},"
                )

        lines.append(f"{self._indent})")
        return lines

    @staticmethod
    def _expr(node: ast.AST) -> str:
        return ast.unparse(node)


class LayoutOptionsCodegen:
    """
    Render a :class:`~c4.renderers.plantuml.layout_options.LayoutConfig`
    instance into Python code that builds the same configuration using
    the fluent :class:`~c4.renderers.plantuml.layout_options.LayoutOptions`
    API.

    Output is intended to be human-readable and stable:
    - Skips default/empty values where possible.
    - Preserves tag/style ordering from the input config.
    - Can render either a single-line expression or a multi-line chained call.
      (Single-line mode is used only for trivially small configs.)

    Example:
        LayoutConfig(layout_with_legend=True, layout_as_sketch=True)

        >>> layout_options = (
        >>>     LayoutOptions()
        >>>     .layout_with_legend()
        >>>     .layout_landscape()
        >>> )
    """

    def __init__(
        self,
        variable_name: str = LAYOUT_OPTIONS_VARIABLE_NAME,
    ) -> None:
        self._variable_name = variable_name
        self._method_call_formatter = MethodCallFormatter(
            owner_cls=LayoutOptions,
        )

    def generate(self, config: LayoutConfig) -> str:
        """
        Convert `config` into Python source code that constructs the same
        layout options using chained ``LayoutOptions`` method calls.

        Args:
            config: Final layout configuration produced
                by `LayoutOptions.build()`.

        Returns:
            A string containing valid Python code (one assignment statement)
            that assigns a `LayoutOptions` expression to `layout_options`.
        """
        chained_calls = self._render_chained_calls(config)

        layout_options = (
            f"{self._variable_name} = LayoutOptions(){chained_calls}"
        )

        return self._method_call_formatter.format_chain_call(layout_options)

    def _render_chained_calls(
        self,
        config: LayoutConfig,
    ) -> str:
        parts = [
            *self._render_layout_with_legend(config),
            *self._render_layout_as_sketch(config),
            *self._render_set_sketch_style(config),
            *self._render_show_legend(config),
            *self._render_show_floating_legend(config),
            *self._render_legend_title(config),
            *self._render_bool_calls(config),
            *self._render_show_person_sprite(config),
            *self._render_tags(config),
            *self._render_styles(config),
            *self._render_build(),
        ]

        return "".join(parts)

    def _render_layout_with_legend(
        self,
        config: LayoutConfig,
    ) -> list[str]:
        parts: list[str] = []

        layout_with_legend_consumed = False
        if config.layout is not None:
            method = self._layout_method_name(config.layout)
            if config.layout_with_legend:
                parts.append(self._format_call(method, {"with_legend": True}))
                layout_with_legend_consumed = True
            else:
                parts.append(self._format_call(method))

        if config.layout_with_legend and not layout_with_legend_consumed:
            parts.append(self._format_call("layout_with_legend"))

        return parts

    def _render_layout_as_sketch(self, config: LayoutConfig) -> list[str]:
        parts = []

        if config.layout_as_sketch:
            parts.append(self._format_call("layout_as_sketch"))

        return parts

    @staticmethod
    def _layout_method_name(layout: DiagramLayout) -> str:
        if layout == DiagramLayout.LAYOUT_TOP_DOWN:
            return "layout_top_down"
        if layout == DiagramLayout.LAYOUT_LEFT_RIGHT:
            return "layout_left_right"
        if layout == DiagramLayout.LAYOUT_LANDSCAPE:
            return "layout_landscape"

        raise ValueError(f"Unsupported DiagramLayout: {layout!r}")

    def _render_set_sketch_style(
        self,
        config: LayoutConfig,
    ) -> list[str]:
        parts = []

        if config.set_sketch_style:
            method_call = self._call_with_filtered_kwargs(
                "set_sketch_style",
                config.set_sketch_style,
                defaults=_SET_SKETCH_STYLE_DEFAULTS,
            )

            parts.extend(method_call.splitlines())

        return parts

    def _render_show_legend(self, config: LayoutConfig) -> list[str]:
        parts = []

        if config.show_legend is not None:
            method_call = self._call_from_optional_dataclass(
                "show_legend",
                config.show_legend,
                none_means_default=_SHOW_LEGEND_DEFAULTS,
            )

            parts.extend(method_call.splitlines())
        return parts

    def _render_show_floating_legend(
        self,
        config: LayoutConfig,
    ) -> list[str]:
        parts = []

        if config.show_floating_legend is not None:
            # LayoutOptions.show_floating_legend defaults:
            # alias=None, hide_stereotype=True, details="Small"
            method_call = self._call_from_optional_dataclass(
                "show_floating_legend",
                config.show_floating_legend,
                none_means_default=_SHOW_FLOATING_LEGEND_DEFAULTS,
            )

            parts.extend(method_call.splitlines())

        return parts

    def _render_legend_title(
        self,
        config: LayoutConfig,
    ) -> list[str]:
        parts = []

        if config.legend_title is not None:
            method_call = self._format_call(
                "update_legend_title",
                {"new_title": config.legend_title},
            )

            parts.extend(method_call.splitlines())

        return parts

    def _render_show_person_sprite(
        self,
        config: LayoutConfig,
    ) -> list[str]:
        parts = []

        if config.show_person_sprite is not None:
            method_call = self._call_from_optional_dataclass(
                "show_person_sprite",
                config.show_person_sprite,
                none_means_default=_SHOW_PERSON_SPRITE_DEFAULTS,
            )

            parts.extend(method_call.splitlines())

        return parts

    def _render_tags(self, config: LayoutConfig) -> list[str]:
        parts = []

        for tag in config.tags:
            method_call = self._tag_to_call(tag)

            parts.extend(method_call.splitlines())

        return parts

    def _render_styles(self, config: LayoutConfig) -> list[str]:
        parts = []

        for style in config.styles:
            method_call = self._style_to_call(style)

            parts.extend(method_call.splitlines())

        return parts

    def _format_call(
        self,
        method_name: str,
        call_args: dict[str, Any] | None = None,
    ) -> str:
        """
        Format a method call.

        Notes:
            - Arguments are rendered using `repr()` to keep
              output valid Python.
        """
        return self._method_call_formatter.format_call(method_name, call_args)

    def _call_with_filtered_kwargs(
        self,
        method_name: str,
        obj: Any,
        *,
        defaults: dict[str, Any],
    ) -> str:
        if not is_dataclass(obj):
            raise TypeError(
                f"Expected dataclass for {method_name}, got {type(obj)!r}"
            )

        kwargs: dict[str, Any] = {}

        for arg, value in asdict(obj).items():  # type: ignore[arg-type]
            if value != defaults[arg]:
                kwargs[arg] = value

        return self._format_call(method_name, kwargs)

    def _call_from_optional_dataclass(
        self,
        method_name: str,
        obj: Any,
        *,
        none_means_default: dict[str, Any],
    ) -> str:
        """
        Render calls for dataclasses where `None` means "use builder default".

        This matches how your builder currently works:
        - The presence of `config.show_legend` indicates the
          feature is enabled.
        - Fields inside may be `None` because the builder did not store them
          (meaning "use LayoutOptions default").

        Only arguments that differ from the builder defaults are emitted.
        """
        if not is_dataclass(obj):
            raise TypeError(
                f"Expected dataclass for {method_name}, got {type(obj)!r}"
            )

        raw: dict[str, Any] = {
            field.name: getattr(obj, field.name) for field in fields(obj)
        }

        kwargs: dict[str, Any] = {}

        for arg, value in raw.items():
            default_value = none_means_default.get(arg)
            effective = default_value if value is None else value
            if effective != default_value:
                kwargs[arg] = effective

        return self._format_call(method_name, kwargs)

    def _tag_to_call(self, tag: BaseTag) -> str:
        """
        Map tag dataclass type -> corresponding LayoutOptions.add_*_tag call.
        Filters out empty-string defaults to keep output clean.
        """
        try:
            method_name = _resolve_method(_TAG_METHODS, tag)
        except KeyError:
            raise TypeError(f"Unsupported tag type: {type(tag)!r}") from None

        base_tag_kwargs = {
            "tag_stereo": tag.tag_stereo,
            "legend_text": tag.legend_text,
            "legend_sprite": tag.legend_sprite,
            "sprite": tag.sprite,
        }

        # common element-like tags share the same shape
        element_kwargs = {
            **base_tag_kwargs,
            "bg_color": getattr(tag, "bg_color", None),
            "font_color": getattr(tag, "font_color", None),
            "border_color": getattr(tag, "border_color", None),
            "shadowing": getattr(tag, "shadowing", None),
            "shape": getattr(tag, "shape", None),
            "border_style": getattr(tag, "border_style", None),
            "border_thickness": getattr(tag, "border_thickness", None),
        }

        if isinstance(tag, RelTag):
            tag_kwargs = {
                **base_tag_kwargs,
                "text_color": tag.text_color,
                "line_color": tag.line_color,
                "line_style": tag.line_style,
                "line_thickness": tag.line_thickness,
                "technology": tag.technology,
            }
        elif isinstance(tag, (PersonTag, SystemTag)):
            tag_kwargs = {
                **element_kwargs,
                "type_": getattr(tag, "type_", None),
            }
        else:
            tag_kwargs = {
                **element_kwargs,
                "technology": getattr(tag, "technology", None),
            }

        kwargs = self._filtered_kwargs(
            tag_kwargs,
            drop_values={"", None},
            keep={"tag_stereo"},
        )

        return self._format_call(method_name, kwargs)

    def _style_to_call(self, style: BaseStyle) -> str:
        try:
            method_name = _resolve_method(_STYLE_METHODS, style)
        except KeyError:
            raise TypeError(
                f"Unsupported style type: {type(style)!r}"
            ) from None

        if isinstance(style, RelStyle):
            kwargs = self._filtered_kwargs(
                {
                    "text_color": style.text_color,
                    "line_color": style.line_color,
                },
                drop_values={"", None},
                keep=set(),
            )
        else:
            kwargs = self._style_element_kwargs(style)

        return self._format_call(method_name, kwargs)

    def _style_element_kwargs(self, style: Any) -> dict[str, Any]:
        base = {
            "element_name": style.element_name,
            "bg_color": style.bg_color,
            "font_color": style.font_color,
            "border_color": style.border_color,
            "shadowing": style.shadowing,
            "shape": style.shape,
            "sprite": style.sprite,
            "technology": style.technology,
            "legend_text": style.legend_text,
            "legend_sprite": style.legend_sprite,
            "border_style": style.border_style,
            "border_thickness": style.border_thickness,
        }

        # boundary styles have type_
        if hasattr(style, "type_"):
            base["type_"] = style.type_

        return self._filtered_kwargs(
            base,
            drop_values={"", None},
            keep={"element_name"},
        )

    def _render_bool_calls(self, config: LayoutConfig) -> list[str]:
        parts = []

        for attr, method in _BOOL_CALLS:
            if getattr(config, attr):
                method_call = self._format_call(method)

                parts.extend(method_call.splitlines())

        return parts

    def _render_build(self) -> list[str]:
        method_call = self._format_call("build")

        return method_call.splitlines()

    @staticmethod
    def _filtered_kwargs(
        kwargs: dict[str, Any],
        *,
        drop_values: set[Any],
        keep: set[str],
    ) -> dict[str, Any]:
        """
        Drop values like ""/None unless key is in 'keep'.
        """
        out: dict[str, Any] = {}
        for key, value in kwargs.items():
            if key in keep:
                out[key] = value
                continue

            if value in drop_values:
                continue

            out[key] = value

        return out

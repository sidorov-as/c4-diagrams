from dataclasses import asdict, fields, is_dataclass
from typing import Any

from c4.converters.python.formatters import MethodCallFormatter
from c4.renderers.plantuml.options import (
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
    NodeTag,
    PersonTag,
    PlantUMLRenderOptions,
    PlantUMLRenderOptionsBuilder,
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


_render_options_builder = PlantUMLRenderOptionsBuilder()


_SHOW_LEGEND_DEFAULTS = _render_options_builder.legend_defaults
_SHOW_FLOATING_LEGEND_DEFAULTS = (
    _render_options_builder.floating_legend_defaults
)
_SET_SKETCH_STYLE_DEFAULTS = _render_options_builder.sketch_style_defaults
_SHOW_PERSON_SPRITE_DEFAULTS = _render_options_builder.person_sprite_defaults

RENDER_OPTIONS_VARIABLE_NAME = "plantuml_render_options"


def _resolve_method(mapping: dict[type[Any], str], obj: Any) -> str:
    for cls in type(obj).mro():
        if cls in mapping:
            return mapping[cls]
    raise KeyError(type(obj))


class PlantUMLRenderOptionsCodegen:
    """
    Render a :class:`~c4.renderers.plantuml.options.PlantUMLRenderOptions`
    instance into Python code that builds the same configuration using
    the fluent
    :class:`~c4.renderers.plantuml.options.PlantUMLRenderOptionsBuilder` API.

    Output is intended to be human-readable and stable:
    - Skips default/empty values where possible.
    - Preserves tag/style ordering from the input options.
    - Can render either a single-line expression or a multi-line chained call.
      (Single-line mode is used only for trivially small configs.)

    Example:
        PlantUMLRenderOptions(layout_with_legend=True, layout_as_sketch=True)

        >>> render_options_builder = (
        >>>     PlantUMLRenderOptionsBuilder()
        >>>     .layout_with_legend()
        >>>     .layout_landscape()
        >>> )
    """

    def __init__(
        self,
        variable_name: str = RENDER_OPTIONS_VARIABLE_NAME,
    ) -> None:
        self._variable_name = variable_name
        self._method_call_formatter = MethodCallFormatter(
            owner_cls=PlantUMLRenderOptionsBuilder,
        )

    def generate(self, options: PlantUMLRenderOptions) -> str:
        """
        Convert `options` into Python source code that constructs the same
        render options using chained
        `PlantUMLRenderOptionsBuilder` method calls.

        Args:
            options: Final layout configuration produced
                by `PlantUMLRenderOptionsBuilder.build()`.

        Returns:
            A string containing valid Python code (one assignment statement)
            that assigns a `PlantUMLRenderOptionsBuilder` expression
            to `plantuml_render_options`.
        """
        chained_calls = self._render_chained_calls(options)
        builder_call = f"PlantUMLRenderOptionsBuilder(){chained_calls}"

        render_options = f"{self._variable_name} = {builder_call}"

        return self._method_call_formatter.format_chain_call(render_options)

    def _render_chained_calls(
        self,
        options: PlantUMLRenderOptions,
    ) -> str:
        parts = [
            *self._render_includes(options),
            *self._render_layout_with_legend(options),
            *self._render_layout_as_sketch(options),
            *self._render_set_sketch_style(options),
            *self._render_show_legend(options),
            *self._render_show_floating_legend(options),
            *self._render_legend_title(options),
            *self._render_bool_calls(options),
            *self._render_show_person_sprite(options),
            *self._render_tags(options),
            *self._render_styles(options),
            *self._render_build(),
        ]

        return "".join(parts)

    def _render_includes(
        self,
        options: PlantUMLRenderOptions,
    ) -> list[str]:
        parts: list[str] = []

        if options.includes:
            parts.append(
                self._format_call("add_includes", call_args=options.includes)
            )

        return parts

    def _render_layout_with_legend(
        self,
        options: PlantUMLRenderOptions,
    ) -> list[str]:
        parts: list[str] = []

        layout_with_legend_consumed = False
        if options.layout is not None:
            method = self._layout_method_name(options.layout)
            if options.layout_with_legend:
                parts.append(
                    self._format_call(method, call_kwargs={"with_legend": True})
                )
                layout_with_legend_consumed = True
            else:
                parts.append(self._format_call(method))

        if options.layout_with_legend and not layout_with_legend_consumed:
            parts.append(self._format_call("layout_with_legend"))

        return parts

    def _render_layout_as_sketch(
        self, options: PlantUMLRenderOptions
    ) -> list[str]:
        parts = []

        if options.layout_as_sketch:
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
        options: PlantUMLRenderOptions,
    ) -> list[str]:
        parts = []

        if options.set_sketch_style:
            method_call = self._call_with_filtered_kwargs(
                "set_sketch_style",
                options.set_sketch_style,
                defaults=_SET_SKETCH_STYLE_DEFAULTS,
            )

            parts.extend(method_call.splitlines())

        return parts

    def _render_show_legend(self, options: PlantUMLRenderOptions) -> list[str]:
        parts = []

        if options.show_legend is not None:
            method_call = self._call_from_optional_dataclass(
                "show_legend",
                options.show_legend,
                none_means_default=_SHOW_LEGEND_DEFAULTS,
            )

            parts.extend(method_call.splitlines())
        return parts

    def _render_show_floating_legend(
        self,
        options: PlantUMLRenderOptions,
    ) -> list[str]:
        parts = []

        if options.show_floating_legend is not None:
            # PlantUMLRenderOptionsBuilder.show_floating_legend defaults:
            # alias=None, hide_stereotype=True, details="Small"
            method_call = self._call_from_optional_dataclass(
                "show_floating_legend",
                options.show_floating_legend,
                none_means_default=_SHOW_FLOATING_LEGEND_DEFAULTS,
            )

            parts.extend(method_call.splitlines())

        return parts

    def _render_legend_title(
        self,
        options: PlantUMLRenderOptions,
    ) -> list[str]:
        parts = []

        if options.legend_title is not None:
            method_call = self._format_call(
                "update_legend_title",
                call_kwargs={"new_title": options.legend_title},
            )

            parts.extend(method_call.splitlines())

        return parts

    def _render_show_person_sprite(
        self,
        options: PlantUMLRenderOptions,
    ) -> list[str]:
        parts = []

        if options.show_person_sprite is not None:
            method_call = self._call_from_optional_dataclass(
                "show_person_sprite",
                options.show_person_sprite,
                none_means_default=_SHOW_PERSON_SPRITE_DEFAULTS,
            )

            parts.extend(method_call.splitlines())

        return parts

    def _render_tags(self, options: PlantUMLRenderOptions) -> list[str]:
        parts = []

        for tag in options.tags:
            method_call = self._tag_to_call(tag)

            parts.extend(method_call.splitlines())

        return parts

    def _render_styles(self, options: PlantUMLRenderOptions) -> list[str]:
        parts = []

        for style in options.styles:
            method_call = self._style_to_call(style)

            parts.extend(method_call.splitlines())

        return parts

    def _format_call(
        self,
        method_name: str,
        call_args: tuple[Any, ...] | list[Any] | None = None,
        call_kwargs: dict[str, Any] | None = None,
    ) -> str:
        """
        Format a method call.

        Notes:
            - Arguments are rendered using `repr()` to keep
              output valid Python.
        """
        return self._method_call_formatter.format_call(
            method_name, call_args, call_kwargs
        )

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

        return self._format_call(method_name, call_kwargs=kwargs)

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
        - The presence of `options.show_legend` indicates the
          feature is enabled.
        - Fields inside may be `None` because the builder did not store them
          (meaning "use PlantUMLRenderOptionsBuilder default").

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

        return self._format_call(method_name, call_kwargs=kwargs)

    def _tag_to_call(self, tag: BaseTag) -> str:
        """
        Map tag dataclass type -> corresponding
        PlantUMLRenderOptionsBuilder.add_*_tag call.

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

        return self._format_call(method_name, call_kwargs=kwargs)

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

        return self._format_call(method_name, call_kwargs=kwargs)

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

    def _render_bool_calls(self, options: PlantUMLRenderOptions) -> list[str]:
        parts = []

        for attr, method in _BOOL_CALLS:
            if getattr(options, attr):
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

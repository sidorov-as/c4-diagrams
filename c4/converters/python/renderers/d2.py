from dataclasses import asdict
from typing import Any

from c4.converters.python.formatters import MethodCallFormatter
from c4.renderers import D2RenderOptions, D2RenderOptionsBuilder

RENDER_OPTIONS_VARIABLE_NAME = "d2_render_options"

_OPTION_METHOD_PARAMS = {
    "direction": "direction",
    "layout": "layout",
    "theme": "theme",
    "title_near": "position",
    "sequence_diagram": "enabled",
    "auto_number_relationships": "enabled",
    "include_type_label": "enabled",
    "include_technology": "enabled",
    "include_properties": "enabled",
    "bidirectional_relationships": "strategy",
    "fully_qualified_relationships": "enabled",
}


class D2RenderOptionsCodegen:
    """Render D2 render options as builder-based Python code."""

    def __init__(
        self,
        variable_name: str = RENDER_OPTIONS_VARIABLE_NAME,
    ) -> None:
        self._variable_name = variable_name
        self._method_call_formatter = MethodCallFormatter(
            owner_cls=D2RenderOptionsBuilder,
        )

    def generate(self, options: D2RenderOptions) -> str:
        chained_calls = self._render_chained_calls(options)
        builder_call = f"D2RenderOptionsBuilder(){chained_calls}"
        render_options = f"{self._variable_name} = {builder_call}"

        return self._method_call_formatter.format_chain_call(render_options)

    def _render_chained_calls(self, options: D2RenderOptions) -> str:
        parts = [
            *self._render_simple_options(options),
            *self._render_legend(options),
            *self._render_build(),
        ]

        return "".join(parts)

    def _render_simple_options(self, options: D2RenderOptions) -> list[str]:
        defaults = D2RenderOptions()
        parts = []
        for key, value in asdict(options).items():
            if key == "legend" or value == getattr(defaults, key):
                continue

            method_call = self._format_call(
                key,
                call_kwargs={_OPTION_METHOD_PARAMS[key]: value},
            )
            parts.extend(method_call.splitlines())

        return parts

    def _render_legend(self, options: D2RenderOptions) -> list[str]:
        if options.legend is None:
            return []

        method_call = self._format_call(
            "legend", call_kwargs={"legend": options.legend}
        )
        return method_call.splitlines()

    def _format_call(
        self,
        method_name: str,
        call_args: tuple[Any, ...] | list[Any] | None = None,
        call_kwargs: dict[str, Any] | None = None,
    ) -> str:
        return self._method_call_formatter.format_call(
            method_name, call_args, call_kwargs
        )

    def _render_build(self) -> list[str]:
        method_call = self._format_call("build")

        return method_call.splitlines()

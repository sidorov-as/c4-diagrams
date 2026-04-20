from dataclasses import asdict
from typing import Any

from c4.converters.python.formatters import MethodCallFormatter
from c4.renderers import MermaidRenderOptions, MermaidRenderOptionsBuilder
from c4.renderers.mermaid.options import BaseStyle, ElementStyle, RelStyle

RENDER_OPTIONS_VARIABLE_NAME = "mermaid_render_options"


class MermaidRenderOptionsCodegen:
    """
    Render a :class:`~c4.renderers.mermaid.options.MermaidRenderOptions`
    instance into Python code that builds the same configuration using
    the fluent
    :class:`~c4.renderers.mermaid.options.MermaidRenderOptionsBuilder` API.

    Output is intended to be human-readable and stable:
    - Skips default/empty values where possible.
    - Preserves tag/style ordering from the input options.
    - Can render either a single-line expression or a multi-line chained call.
      (Single-line mode is used only for trivially small configs.)

    Example:
        MermaidRenderOptions(
            styles=[
                ElementStyle(
                    element="customer",
                    font_color="red",
                    bg_color="grey",
                    border_color="red",
                )
            ],
            update_layout_config=UpdateLayoutConfig(
                c4_shape_in_row=4,
                c4_boundary_in_row=2,
            )
        )

        >>> render_options_builder = (
        >>>     MermaidRenderOptionsBuilder()
        >>>     .update_layout_config(
        >>>         c4_shape_in_row=4,
        >>>         c4_boundary_in_row=2
        >>>      )
        >>>     .update_element_style(
        >>>          "customer",
        >>>          font_color="red",
        >>>          bg_color="grey",
        >>>          border_color="red",
        >>>      )
        >>> )
    """

    def __init__(
        self,
        variable_name: str = RENDER_OPTIONS_VARIABLE_NAME,
    ) -> None:
        self._variable_name = variable_name
        self._method_call_formatter = MethodCallFormatter(
            owner_cls=MermaidRenderOptionsBuilder,
        )

    def generate(self, options: MermaidRenderOptions) -> str:
        """
        Convert `options` into Python source code that constructs the same
        render options using chained
        `MermaidRenderOptionsBuilder` method calls.

        Args:
            options: Final layout configuration produced
                by `MermaidRenderOptionsBuilder.build()`.

        Returns:
            A string containing valid Python code (one assignment statement)
            that assigns a `MermaidRenderOptionsBuilder` expression
            to `mermaid_render_options`.
        """
        chained_calls = self._render_chained_calls(options)
        builder_call = f"MermaidRenderOptionsBuilder(){chained_calls}"

        render_options = f"{self._variable_name} = {builder_call}"

        return self._method_call_formatter.format_chain_call(render_options)

    def _render_chained_calls(
        self,
        options: MermaidRenderOptions,
    ) -> str:
        parts = [
            *self._render_styles(options),
            *self._render_update_layout_config(options),
            *self._render_build(),
        ]

        return "".join(parts)

    def _render_update_layout_config(
        self,
        options: MermaidRenderOptions,
    ) -> list[str]:
        parts = []

        if options.update_layout_config is not None:
            method_name = "update_layout_config"

            kwargs = self._filtered_kwargs(
                asdict(options.update_layout_config),
                drop_values={"", None},
                keep=set(),
            )

            method_call = self._format_call(method_name, call_kwargs=kwargs)

            parts.extend(method_call.splitlines())

        return parts

    def _render_styles(self, options: MermaidRenderOptions) -> list[str]:
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

    def _style_to_call(self, style: BaseStyle) -> str:
        if isinstance(style, RelStyle):
            method_name = "update_rel_style"
        elif isinstance(style, ElementStyle):
            method_name = "update_element_style"
        else:
            raise TypeError(
                f"Unsupported style type: {type(style)!r}"
            ) from None

        kwargs = self._filtered_kwargs(
            asdict(style),
            drop_values={"", None},
            keep=set(),
        )

        return self._format_call(method_name, call_kwargs=kwargs)

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

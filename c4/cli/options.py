from __future__ import annotations

import argparse
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Literal, TextIO

from c4 import PNG
from c4.cli.exceptions import CLIError
from c4.constants import (
    D2,
    DEFAULT_JAVA_BIN,
    DEFAULT_PLANTUML_BIN,
    DEFAULT_PLANTUML_SERVER_URL,
    DEFAULT_RENDERER,
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    DIAGRAM_FORMATS_BY_RENDERER,
    KNOWN_RENDERERS,
    LOCAL_BACKEND,
    MERMAID,
    PLANTUML,
    PLANTUML_SKINPARAM_DPI_TEMPLATE,
    STRUCTURIZR,
)
from c4.enums import DiagramFormat, RendererEnum
from c4.renderers import BaseRenderer, PlantUMLRenderer
from c4.renderers.plantuml import (
    LocalPlantUMLBackend,
    RemotePlantUMLBackend,
)
from c4.renderers.plantuml.backends import BasePlantUMLBackend


@dataclass
class CLIOptions:
    """
    Base CLI options shared across commands.

    Attributes:
        renderer: Selected renderer backend (e.g. PlantUML, Mermaid).
        target: Diagram target reference string
            (e.g. "module", "module:diagram", "file.py", "file.py:diagram").
    """

    renderer: Literal[
        RendererEnum.PLANTUML,
        RendererEnum.MERMAID,
        RendererEnum.STRUCTURIZR,
        RendererEnum.D2,
    ]
    target: str


@dataclass
class RenderCLIOptions(CLIOptions):
    """
    CLI options for the `render` command.

    Attributes:
        output: Optional output path. If omitted, writes to stdout.
    """

    output: Path | None = None

    @contextmanager
    def open_output(self) -> Iterator[TextIO]:
        """
        Open an output stream for writing UTF-8 text.

        - If output is None, yields sys.stdout (no closing is performed).
        - Otherwise opens the file in text write mode and closes it on exit.
        """
        if self.output is None:
            yield sys.stdout
            return

        out = self.output.open("w", encoding="utf-8")
        try:
            yield out
        finally:
            out.close()


@dataclass
class PlantUMLExportCLIOptions:
    """
    PlantUML-specific export options.

    Attributes:
        plantuml_backend: PlantUML execution mode: "local" or "remote".
        plantuml_server_url: URL of the PlantUML server when using "remote".
        plantuml_bin: Local PlantUML executable path/command.
        plantuml_jar: Local PlantUML JAR path. If provided, it takes precedence
            over plantuml_bin.
        java_bin: Java executable to run the PlantUML JAR.
    """

    plantuml_backend: Literal["local", "remote"] = "local"
    plantuml_server_url: str = DEFAULT_PLANTUML_SERVER_URL
    plantuml_bin: str | None = DEFAULT_PLANTUML_BIN
    plantuml_jar: str | None = None
    java_bin: str | None = DEFAULT_JAVA_BIN
    plantuml_skinparam_dpi: int | None = None

    @property
    def local_backend_kwargs(self) -> dict[str, Any]:
        """
        Keyword arguments for LocalPlantUMLBackend.
        """
        return {
            "plantuml_bin": self.plantuml_bin,
            "plantuml_jar": self.plantuml_jar,
            "java_bin": self.java_bin,
        }

    @property
    def remote_backend_kwargs(self) -> dict[str, Any]:
        """
        Keyword arguments for RemotePlantUMLBackend.
        """
        return {
            "server_url": self.plantuml_server_url,
        }


@dataclass
class ExportCLIOptions(CLIOptions):
    """
    CLI options for the `export` command.

    Attributes:
        renderer_options: Renderer-specific export options (e.g. PlantUML).
        format: Export format (e.g. PNG, SVG). Must be supported
            by the renderer.
        output: Optional output path. If omitted, writes to stdout (bytes).
        timeout: Rendering timeout in seconds.
    """

    renderer_options: PlantUMLExportCLIOptions
    format: DiagramFormat = PNG
    output: Path | None = None
    timeout: float = DEFAULT_RENDERING_TIMEOUT_SECONDS

    @contextmanager
    def open_output(self) -> Iterator[BinaryIO]:
        """
        Open an output stream for writing bytes.

        - If output is None, yields sys.stdout.buffer
            (no closing is performed).
        - Otherwise opens the file in binary write mode and closes it on exit.
        """
        if self.output is None:
            yield sys.stdout.buffer
            return

        out = self.output.open("wb")
        try:
            yield out
        finally:
            out.close()


def _get_renderer_name(args: argparse.Namespace) -> RendererEnum:
    """
    Select renderer name based on CLI args.

    Precedence:
        1) Explicit --renderer
        2) Shorthand renderer flags (--plantuml/--mermaid/--structurizr/--d2)
        3) DEFAULT_RENDERER

    Raises:
        CLIError: If the resolved renderer is unknown.
    """
    if getattr(args, "renderer", None):
        renderer = args.renderer

    elif getattr(args, PLANTUML.value, False):
        renderer = PLANTUML.value
    elif getattr(args, MERMAID.value, False):
        renderer = MERMAID.value
    elif getattr(args, STRUCTURIZR.value, False):
        renderer = STRUCTURIZR.value
    elif getattr(args, D2.value, False):
        renderer = D2.value
    else:
        renderer = DEFAULT_RENDERER

    if renderer not in KNOWN_RENDERERS:
        allowed = ", ".join(sorted(KNOWN_RENDERERS))
        raise CLIError(f"Unknown renderer {renderer!r}. Allowed: {allowed}.")

    return RendererEnum(renderer)


def _validate_output_format(
    renderer: RendererEnum,
    fmt: str | DiagramFormat,
) -> DiagramFormat:
    """
    Validate that an export format is supported by the selected renderer.

    Args:
        renderer: Selected renderer.
        fmt: Format string from CLI (e.g. "png", "svg").

    Returns:
        A ``DiagramFormat`` instance corresponding to ``fmt``.

    Raises:
        CLIError: If the renderer is unknown or the format is unsupported.
    """
    allowed = DIAGRAM_FORMATS_BY_RENDERER.get(renderer)
    if not allowed:
        allowed_renderers = ", ".join(sorted(DIAGRAM_FORMATS_BY_RENDERER))
        raise CLIError(
            f"Renderer {str(renderer)!r} has no registered formats. "
            f"Allowed renderers: {allowed_renderers}."
        )

    if fmt not in allowed:
        allowed_list = ", ".join(sorted(allowed))
        raise CLIError(
            f"--format {fmt!r} is not supported by "
            f"renderer {renderer.value!r}. Allowed: {allowed_list}."
        )

    return DiagramFormat(fmt)


def build_render_cli_options(
    args: argparse.Namespace,
) -> RenderCLIOptions:
    """
    Convert parsed CLI args to RenderCLIOptions.
    """
    cli_options = CLIOptions(
        renderer=_get_renderer_name(args),
        target=args.target,
    )

    return RenderCLIOptions(
        renderer=cli_options.renderer,
        target=cli_options.target,
        output=args.output,
    )


def build_renderer(cli_options: RenderCLIOptions) -> BaseRenderer:
    """
    Build a renderer used by the `render` command.

    Raises:
        CLIError: If the renderer is not supported by the render command.
    """
    renderer = cli_options.renderer

    if renderer == PLANTUML:
        return PlantUMLRenderer()

    raise CLIError(
        f"Renderer {str(renderer)!r} is not supported by the 'render' command."
    )


def _build_plantuml_export_cli_options(
    args: argparse.Namespace,
) -> PlantUMLExportCLIOptions:
    """
    Build PlantUML export options from parsed CLI args.

    Notes:
        If a PlantUML JAR is provided, it takes precedence over plantuml_bin.
    """
    # Prefer explicit args; fall back to defaults via dataclass fields.
    plantuml_bin: str | None = args.plantuml_bin
    plantuml_jar: str | None = args.plantuml_jar

    if plantuml_jar:
        # If plantuml_jar is provided, ignore plantuml_bin
        # to ensure JAR priority
        plantuml_bin = None

    return PlantUMLExportCLIOptions(
        plantuml_backend=args.plantuml_backend,
        plantuml_server_url=args.plantuml_server_url,
        plantuml_bin=plantuml_bin,
        plantuml_jar=plantuml_jar,
        java_bin=args.java_bin,
        plantuml_skinparam_dpi=args.plantuml_skinparam_dpi,
    )


def _build_plantuml_exporter(
    cli_options: ExportCLIOptions,
) -> PlantUMLRenderer:
    """
    Build a PlantUML renderer configured for exporting binary artifacts.

    This function selects and initializes the appropriate PlantUML backend
    (local execution or remote server) based on CLI options, applies rendering
    timeouts, and wires the backend into a PlantUMLRenderer instance.

    Args:
        cli_options: Parsed export CLI options containing PlantUML backend
            configuration, timeout, and renderer-specific settings.

    Returns:
        A PlantUMLRenderer instance configured with the selected backend.

    Notes:
        - When using the local backend, PlantUML can be executed via either
          a native executable or a JAR (with Java), depending on configuration.
        - When using the remote backend, diagrams are rendered by a PlantUML
          server over HTTP.
        - If a skinparam DPI value is configured, it is injected via a PlantUML
          include and affects all output formats (PNG, SVG, etc.).
    """
    renderer_options = cli_options.renderer_options

    backend: BasePlantUMLBackend
    if renderer_options.plantuml_backend == LOCAL_BACKEND:
        backend = LocalPlantUMLBackend(
            timeout_seconds=cli_options.timeout,
            **renderer_options.local_backend_kwargs,
        )
    else:
        backend = RemotePlantUMLBackend(
            timeout_seconds=cli_options.timeout,
            **renderer_options.remote_backend_kwargs,
        )

    includes = []
    if renderer_options.plantuml_skinparam_dpi:
        dpi = PLANTUML_SKINPARAM_DPI_TEMPLATE.format(
            dpi=renderer_options.plantuml_skinparam_dpi
        )

        includes.append(dpi)

    return PlantUMLRenderer(
        includes=includes,
        backend=backend,
    )


def build_export_cli_options(args: argparse.Namespace) -> ExportCLIOptions:
    """
    Convert parsed CLI args to ExportCLIOptions.

    Raises:
        CLIError: If the renderer is unsupported for export or
            the output format is invalid.
    """
    cli_options = CLIOptions(
        renderer=_get_renderer_name(args),
        target=args.target,
    )
    renderer = cli_options.renderer

    if renderer == RendererEnum.PLANTUML:
        renderer_options = _build_plantuml_export_cli_options(args)
    else:
        raise CLIError(
            f"Renderer {renderer.value!r} is not supported by "
            f"the 'export' command."
        )

    return ExportCLIOptions(
        renderer=cli_options.renderer,
        target=cli_options.target,
        format=_validate_output_format(renderer, fmt=args.format),
        timeout=args.timeout,
        output=args.output,
        renderer_options=renderer_options,
    )


def build_exporter(cli_options: ExportCLIOptions) -> BaseRenderer:
    """
    Build a renderer configured for exporting binary artifacts (e.g. PNG).

    For PlantUML, this configures the appropriate backend (local or remote)
    and passes timeout/options through to the backend.

    Raises:
        CLIError: If the renderer is unsupported.
    """
    renderer = cli_options.renderer

    if renderer == PLANTUML:
        return _build_plantuml_exporter(cli_options)

    raise CLIError(f"Unsupported renderer: {renderer.value!r}")

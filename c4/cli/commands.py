from c4.cli.context import CommandContext
from c4.cli.discover import resolve_diagram, resolve_json_diagram
from c4.cli.exceptions import CLIError
from c4.cli.options import (
    ExportCLIOptions,
    RenderCLIOptions,
    build_convert_cli_options,
    build_export_cli_options,
    build_exporter,
    build_render_cli_options,
    build_renderer,
)
from c4.cli.watch import (
    build_watch_child_argv,
    run_with_watch,
    validate_enabled_watch_options,
)
from c4.converters.exceptions import ConversionError
from c4.converters.python.converter import diagram_to_python_code
from c4.enums import DiagramConvertionFormat


def _run_with_watch(
    cli_options: RenderCLIOptions | ExportCLIOptions,
    context: CommandContext,
) -> int:
    watch_options = validate_enabled_watch_options(cli_options)

    return run_with_watch(
        build_watch_child_argv(context.argv),
        watch_options,
        cli_options.output,  # type: ignore[arg-type]
    )


def render_once(cli_options: RenderCLIOptions) -> int:
    """
    Render a diagram to its textual representation.

    Resolves the target diagram, renders it using the configured renderer,
    and writes the resulting source code to stdout or to a file, depending
    on CLI options.
    """
    diagram = resolve_diagram(cli_options.target)
    renderer = build_renderer(cli_options)

    diagram_source = renderer.render(diagram)

    with cli_options.open_output() as out:
        out.write(diagram_source)

    return 0


def handle_render(context: CommandContext) -> int:
    """
    Handle the `render` command.
    """
    args = context.args
    cli_options = build_render_cli_options(args)

    if not cli_options.watch.enabled:
        return render_once(cli_options)

    return _run_with_watch(
        cli_options,
        context,
    )


def export_once(cli_options: ExportCLIOptions) -> int:
    """
    Export a diagram as a rendered artifact.

    Resolves the target diagram, renders it using the configured exporter,
    and writes the resulting binary output (e.g. PNG, SVG) to stdout or to
    a file, depending on CLI options.
    """
    diagram = resolve_diagram(cli_options.target)
    exporter = build_exporter(cli_options)

    diagram_bytes = exporter.render_bytes(
        diagram,
        format=cli_options.format,
    )

    with cli_options.open_output() as out:
        out.write(diagram_bytes)

    return 0


def handle_export(context: CommandContext) -> int:
    """
    Handle the `export` command.
    """
    args = context.args
    cli_options = build_export_cli_options(args)

    if not cli_options.watch.enabled:
        return export_once(cli_options)

    return _run_with_watch(
        cli_options,
        context,
    )


def handle_convert(context: CommandContext) -> int:
    """
    Converts a diagram from one representation to another.
    """
    args = context.args
    cli_options = build_convert_cli_options(args)
    from_format = cli_options.from_format
    to_format = cli_options.to_format

    match from_format, to_format:
        case DiagramConvertionFormat.JSON, DiagramConvertionFormat.PY:
            try:
                diagram, backend = resolve_json_diagram(args.target)
                diagram_source = diagram_to_python_code(diagram, backend)
            except ConversionError as exc:
                raise CLIError(exc.message) from None
        case _:
            raise CLIError(
                f"Unsupported conversion: "
                f"{from_format.value} → {to_format.value}."
            )

    with cli_options.open_output() as out:
        out.write(diagram_source)

    return 0

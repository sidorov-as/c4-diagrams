import argparse

from c4.cli.discover import resolve_diagram
from c4.cli.options import (
    build_export_cli_options,
    build_exporter,
    build_render_cli_options,
    build_renderer,
)


def handle_render(args: argparse.Namespace) -> int:
    """
    Render a diagram to its textual representation.

    This handler resolves the target diagram, renders it using the
    configured renderer, and writes the resulting source code to
    stdout or to a file, depending on CLI options.
    """
    cli_options = build_render_cli_options(args)

    diagram = resolve_diagram(cli_options.target)
    renderer = build_renderer(cli_options)

    diagram_source = renderer.render(diagram)

    with cli_options.open_output() as out:
        out.write(diagram_source)

    return 0


def handle_export(args: argparse.Namespace) -> int:
    """
    Export a diagram as a rendered artifact.

    This handler resolves the target diagram, renders it using the
    configured exporter, and writes the resulting binary output
    (e.g. PNG, SVG) to stdout or to a file, depending on CLI options.
    """
    cli_options = build_export_cli_options(args)

    diagram = resolve_diagram(cli_options.target)
    exporter = build_exporter(cli_options)

    diagram_bytes = exporter.render_bytes(
        diagram,
        format=cli_options.format,
    )

    with cli_options.open_output() as out:
        out.write(diagram_bytes)

    return 0

from __future__ import annotations

import argparse
import os
import shutil
import textwrap
from collections.abc import Callable, Iterable
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, TypeVar

from c4 import PNG, __version__
from c4.cli.commands import handle_convert, handle_export, handle_render
from c4.constants import (
    ALL_DIAGRAM_FORMATS,
    CONVERT_FROM_FORMATS,
    CONVERT_TO_FORMATS,
    DEFAULT_JAVA_BIN,
    DEFAULT_PLANTUML_SERVER_URL,
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    FORMATS_BY_RENDERER_HELP_TEXT,
    JAVA_BIN_ENV_VAR,
    KNOWN_RENDERERS,
    LOCAL_BACKEND,
    MERMAID_BIN_ENV_VAR,
    MERMAID_SCALE_FACTOR_ENV_VAR,
    PLANTUML_BIN_ENV_VAR,
    PLANTUML_JAR_ENV_VAR,
    PLANTUML_SERVER_URL_ENV_VAR,
    PLANTUML_SKINPARAM_DPI_ENV_VAR,
    REMOTE_BACKEND,
    RENDERING_TIMEOUT_SECONDS_ENV_VAR,
)
from c4.enums import ConvertShortcut

if TYPE_CHECKING:  # pragma: no cover
    from argparse import _SubParsersAction


T = TypeVar("T")


class HelpFormatter(argparse.HelpFormatter):
    """
    Help formatter that respects explicit newlines in help text.

    Argparse normally re-wraps help strings and may collapse formatting.
    This formatter wraps each original line separately, allowing to
    structure long help texts with manual line breaks.
    """

    def _split_lines(self, text: str, width: int) -> list[str]:
        """
        Wrap help text while preserving explicit line breaks.

        Empty lines are preserved as paragraph breaks.
        """
        import textwrap

        lines = []
        for line in text.splitlines():
            lines.extend(textwrap.wrap(line.strip(), width))
        return lines


def _exporter_binary_type(value: str, backend: str) -> str:
    """
    Validate a binary executable reference.

    The value may be either a command name available in PATH or a full path.
    """
    resolved = shutil.which(value)
    if not resolved:
        raise argparse.ArgumentTypeError(
            f"{backend} binary {value!r} was not found in PATH or "
            f"is not executable."
        )
    return value


def str2bool(value: str) -> bool:
    if isinstance(value, bool):
        return value
    if value.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif value.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


_plantuml_bin_type = partial(_exporter_binary_type, backend="PlantUML")
_mermaid_bin_type = partial(_exporter_binary_type, backend="Mermaid")


def _plantuml_jar_type(value: str | Path) -> Path:
    """
    Validate a PlantUML JAR file path.

    Returns:
        The resolved Path to the jar.
    """
    path = Path(value)
    if not path.exists():
        raise argparse.ArgumentTypeError(
            f"PlantUML jar file does not exist: {str(value)!r}."
        )
    if not path.is_file():
        raise argparse.ArgumentTypeError(
            f"PlantUML jar path is not a file: {str(value)!r}."
        )
    return path


def _output_file_path(value: str | Path) -> Path:
    """
    Validate and convert a CLI argument to an output file path.

    The path may point to an existing file or a non-existent file that
    will be created later.

    The parent directory must already exist; directories are not created
    implicitly to avoid accidental filesystem changes.

    Args:
        value: Raw path string provided via CLI.

    Returns:
        A Path object representing the output file path.

    Raises:
        argparse.ArgumentTypeError:
            - If the path points to an existing directory.
            - If the parent directory does not exist.
    """
    path = Path(value)

    if path.exists() and path.is_dir():
        raise argparse.ArgumentTypeError(
            f"Output path {value!r} is a directory, expected a file path."
        )

    parent = path.parent
    if parent != Path(".") and not parent.exists():
        raise argparse.ArgumentTypeError(
            f"Directory {str(parent)!r} does not exist."
        )

    return path


def _env_default(
    envvars: Iterable[str],
    *,
    cast: Callable[[str], T] | None = None,
) -> str | T | None:
    """
    Resolve a default value from one or more environment variables.

    Environment variables are checked in the given order. The first variable
    that is set (even if later variables are also set) wins.

    Args:
        envvars:
            Environment variable names to check, in priority order.
        cast:
            Optional callable that converts the env var string value into a
            target type (e.g. ``int``, ``float``). Use this to match the
            ``type=`` used by argparse flags.

    Returns:
        The first matching env var value (converted if ``cast`` is provided),
        or ``None`` if none of the variables are set.

    Raises:
        argparse.ArgumentTypeError:
            If a variable is set but cannot be converted using ``cast``.
    """
    for env in envvars:
        value = os.getenv(env)
        if value:
            if cast:
                try:
                    return cast(value)
                except ValueError as exc:
                    raise argparse.ArgumentTypeError(
                        f"Invalid value for env var {env}: {value!r}"
                    ) from exc

            return value

    return None


def _add_renderer_flags(parser: argparse.ArgumentParser) -> None:
    """
    Add renderer selection flags.

    The options are mutually exclusive: you can either select a renderer by
    name or use a shorthand alias.
    """
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--renderer",
        choices=[choice.value for choice in KNOWN_RENDERERS],
        help="Renderer to use (overrides the diagram's default renderer).",
    )
    group.add_argument(
        "--plantuml",
        action="store_true",
        help="Use PlantUML renderer (alias for --renderer plantuml).",
    )
    group.add_argument(
        "--mermaid",
        action="store_true",
        help="Use Mermaid renderer (alias for --renderer mermaid).",
    )


def _add_plantuml_render_flags(parser: argparse.ArgumentParser) -> None:
    """Add PlantUML-specific flags."""
    group = parser.add_argument_group("PlantUML options")

    group.add_argument(
        "--plantuml-use-new-c4-style",
        action="store_true",
        help="Activates the new C4-PlantUML style.",
    )


def _build_render_parser(
    subparser: _SubParsersAction,
) -> None:
    """
    Register the `render` subcommand.

    This command renders a diagram into text (typically PlantUML/Mermaid source)
    and writes it to stdout by default.
    """
    render_parser = subparser.add_parser(
        "render",
        help="Render a diagram to text output.",
    )
    render_parser.add_argument(
        "target",
        help=(
            "Diagram target: Python file or module (file.py, file.py:diagram, "
            "module.path, module.path:diagram) or a JSON file (file.json)."
        ),
    )
    render_parser.add_argument(
        "-o",
        "--output",
        type=_output_file_path,
        help="Redirect output to a file.",
    )

    _add_renderer_flags(render_parser)
    _add_plantuml_render_flags(render_parser)

    render_parser.set_defaults(func=handle_render)


def _add_plantuml_export_flags(parser: argparse.ArgumentParser) -> None:
    """
    Add PlantUML-specific export flags.

    These flags configure the PlantUML backend (local or server) and the
    underlying execution details (binary vs jar, Java executable, DPI, etc.).
    """
    group = parser.add_argument_group("PlantUML options")

    group.add_argument(
        "--plantuml-backend",
        choices=(LOCAL_BACKEND, REMOTE_BACKEND),
        default=LOCAL_BACKEND,
        help="How to run PlantUML: local execution or remote server.",
    )
    group.add_argument(
        "--plantuml-server-url",
        default=DEFAULT_PLANTUML_SERVER_URL,
        help=(
            f"PlantUML server URL. If not provided, "
            f"the {PLANTUML_SERVER_URL_ENV_VAR} environment variable "
            f"will be used."
        ),
    )

    mex = group.add_mutually_exclusive_group()
    mex.add_argument(
        "--plantuml-bin",
        type=_plantuml_bin_type,
        default=_env_default([PLANTUML_BIN_ENV_VAR]),
        help=(
            "PlantUML executable (command name or full path). "
            f"If not provided, the {PLANTUML_BIN_ENV_VAR} "
            f"environment variable will be used."
        ),
    )
    mex.add_argument(
        "--plantuml-jar",
        type=_plantuml_jar_type,
        default=_env_default([PLANTUML_JAR_ENV_VAR]),
        help=(
            "Path to the PlantUML JAR file (runs via Java). "
            f"If provided, the {PLANTUML_BIN_ENV_VAR} environment variable "
            "is ignored. "
            f"Can also be set via the {PLANTUML_JAR_ENV_VAR} "
            f"environment variable."
        ),
    )

    group.add_argument(
        "--java-bin",
        default=DEFAULT_JAVA_BIN,
        help=(
            "Java executable to use when running PlantUML via JAR. "
            f"If not provided, the {JAVA_BIN_ENV_VAR} "
            f"environment variable will be used."
        ),
    )
    group.add_argument(
        "--plantuml-skinparam-dpi",
        type=int,
        default=_env_default(
            [PLANTUML_SKINPARAM_DPI_ENV_VAR],
            cast=int,
        ),
        help=(
            "Set PlantUML 'skinparam dpi' value to control raster (PNG) "
            "resolution. This option modifies diagram rendering and affects "
            "all output formats. "
            f"Can also be set via the {PLANTUML_SKINPARAM_DPI_ENV_VAR} "
            f"environment variable."
        ),
    )
    group.add_argument(
        "--plantuml-use-new-c4-style",
        action="store_true",
        help="Activates the new C4-PlantUML style.",
    )
    group.add_argument(
        "--plantuml-use-bundled-c4-plantuml",
        type=str2bool,
        default=True,
        help=(
            "Use bundled C4-PlantUML library files instead of fetching them "
            "from remote sources."
        ),
    )


def _add_mermaid_export_flags(parser: argparse.ArgumentParser) -> None:
    """
    Add Mermaid-specific export flags.

    These flags configure the local Mermaid backend and the underlying
    execution details.
    """
    group = parser.add_argument_group("Mermaid options")

    group.add_argument(
        "--mermaid-bin",
        type=_mermaid_bin_type,
        help=(
            "Mermaid executable (command name or full path). "
            f"If not provided, the {MERMAID_BIN_ENV_VAR} "
            f"environment variable will be used."
        ),
    )
    group.add_argument(
        "--mermaid-scale-factor",
        type=int,
        default=_env_default(
            [MERMAID_SCALE_FACTOR_ENV_VAR],
            cast=int,
        ),
        help=(
            "Set Mermaid scale value to control Puppeteer scale factor"
            " (default: 1). Can also be set via the "
            f"{MERMAID_SCALE_FACTOR_ENV_VAR} environment variable."
        ),
    )


def _build_export_parser(
    subparser: _SubParsersAction,
) -> None:
    """
    Register the `export` subcommand.

    This command renders a diagram into a binary artifact (e.g. PNG/SVG),
    depending on the selected renderer and output format.
    """
    export_parser = subparser.add_parser(
        "export",
        help=(
            "Export a diagram to a rendered artifact "
            "(e.g., PNG/SVG, renderer-dependent)."
        ),
    )
    # To support linebreaks in help text
    export_parser.formatter_class = HelpFormatter

    export_parser.add_argument(
        "target",
        help=(
            "Diagram target: Python file or module (file.py, file.py:diagram, "
            "module.path, module.path:diagram) or a JSON file (file.json)."
        ),
    )
    export_parser.add_argument(
        "-o",
        "--output",
        type=_output_file_path,
        help="Redirect output to a file.",
    )
    export_parser.add_argument(
        "-f",
        "--format",
        default=PNG,
        choices=ALL_DIAGRAM_FORMATS,
        help=textwrap.dedent(
            f"""\
            Output format (render-specific). Supported formats:
            {FORMATS_BY_RENDERER_HELP_TEXT}
            """,
        ),
    )
    export_parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_RENDERING_TIMEOUT_SECONDS,
        help=(
            "Render timeout in seconds. "
            f"Can also be set via the {RENDERING_TIMEOUT_SECONDS_ENV_VAR} "
            f"environment variable."
        ),
    )

    _add_renderer_flags(export_parser)
    _add_plantuml_export_flags(export_parser)
    _add_mermaid_export_flags(export_parser)

    export_parser.set_defaults(func=handle_export)


def _build_convert_parser(
    subparser: _SubParsersAction,
) -> None:
    """
    Register the `convert` subcommand.

    This command converts diagrams between supported input and output formats.
    """
    convert_parser = subparser.add_parser(
        "convert",
        help="Convert a diagram from one representation to another.",
    )
    # To support linebreaks in help text
    convert_parser.formatter_class = HelpFormatter

    convert_parser.add_argument(
        "target",
        help="Diagram target.",
    )

    shortcut_group = convert_parser.add_mutually_exclusive_group()
    shortcut_group.add_argument(
        "--json-to-py",
        action="store_const",
        const=ConvertShortcut.JSON_TO_PY,
        dest="mode_shortcut",
        help="Shortcut for --from json --to py.",
    )

    from_group = convert_parser.add_mutually_exclusive_group()
    from_group.add_argument(
        "--from",
        choices=CONVERT_FROM_FORMATS,
        help="Input format.",
    )
    from_group.add_argument(
        "--from-json",
        action="store_true",
        help="Convert from JSON diagram.",
    )

    to_group = convert_parser.add_mutually_exclusive_group()
    to_group.add_argument(
        "--to",
        choices=CONVERT_TO_FORMATS,
        help="Output format.",
    )
    to_group.add_argument(
        "--to-py",
        action="store_true",
        help="Convert to Python DSL.",
    )

    convert_parser.add_argument(
        "-o",
        "--output",
        type=_output_file_path,
        help="Redirect output to a file.",
    )

    convert_parser.set_defaults(func=handle_convert)


def build_parser() -> argparse.ArgumentParser:
    """
    Build the top-level CLI parser for `c4`.

    Returns:
        A fully configured ArgumentParser with subcommands.
    """
    parser = argparse.ArgumentParser(
        prog="c4",
        description="C4 diagrams CLI",
    )
    parser.add_argument(
        "-V", "--version", action="version", version=__version__
    )
    command = parser.add_subparsers(dest="command", required=True)

    _build_render_parser(command)
    _build_export_parser(command)
    _build_convert_parser(command)

    return parser

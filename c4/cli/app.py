from __future__ import annotations

import traceback

from c4.cli.exceptions import CLIError
from c4.cli.parser import build_parser


def main(argv: list[str] | None = None) -> int:
    """The C4 command-line interface."""
    parser = build_parser()

    try:
        args = parser.parse_args(argv)
        return int(args.func(args))
    except CLIError as exc:
        parser.error(exc.message)  # will cause sys.exit(2)
    except BrokenPipeError:
        # E.g. piping should not show a stack trace
        # like this: 'BrokenPipeError: [Errno 32] Broken pipe'
        return 0
    except Exception as exc:
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        return 2


def entrypoint() -> None:
    """
    Console script entry point for the C4 CLI.
    """
    raise SystemExit(main())

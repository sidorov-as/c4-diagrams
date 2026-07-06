from __future__ import annotations

import importlib.util
import subprocess
import sys
import time
import traceback
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Protocol, TypeAlias

from c4.cli.discover import _import_module_or_raise, _parse_target
from c4.cli.exceptions import CLIError

Change: TypeAlias = object
WatchCallable: TypeAlias = Callable[
    ...,
    Iterable[Iterable[tuple[Change, str]]],
]
WATCH_VALUE_FLAGS = frozenset((
    "--watch-delay",
    "--watch-dir",
    "--watch-include",
))
WATCH_BOOL_FLAGS = frozenset(("--watch", "-w"))


@dataclass(frozen=True)
class WatchOptions:
    """
    Configuration for CLI watch mode.
    """

    enabled: bool = False
    delay: float = 0.25
    path: Path | None = None
    dirs: tuple[Path, ...] = ()
    include: tuple[str, ...] = ()


class WatchCLIOptions(Protocol):
    """
    CLI options required to validate enabled watch mode.
    """

    target: str
    watch: WatchOptions
    output: Path | None


def _resolve_file_path(path: Path, target: str) -> Path:
    """
    Resolve a direct file target and reject missing or non-file paths.
    """
    resolved_path = path.resolve()
    if resolved_path.is_file():
        return resolved_path

    raise CLIError(
        f"Could not resolve watch source file from target {target!r}."
    )


def _resolve_module_file(module_name: str) -> Path | None:
    """
    Resolve an importable module name to the file that defines it.
    """
    try:
        spec = importlib.util.find_spec(module_name)
    except ModuleNotFoundError:
        spec = None

    if spec is not None and spec.origin is not None:
        spec_path = Path(spec.origin)
        if spec_path.is_file():
            return spec_path.resolve()

    try:
        module = _import_module_or_raise(module_name)
    except ModuleNotFoundError as exc:
        missing_name = exc.name or ""
        if module_name.startswith(f"{missing_name}."):
            raise CLIError(
                f"Could not import module {module_name!r}. "
                "Make sure it is installed and importable "
                "(check PYTHONPATH / working directory)."
            ) from exc

        raise

    module_file = getattr(module, "__file__", None)
    if not module_file:
        return None

    module_path = Path(module_file)
    if not module_path.is_file():
        return None

    return module_path.resolve()


def resolve_watch_path(target: str) -> Path:
    """
    Resolve a CLI target to the concrete source file watch mode should track.
    """
    parsed_target = _parse_target(target)

    if parsed_target.is_py_file or parsed_target.is_json_file:
        return _resolve_file_path(Path(parsed_target.module_or_file), target)

    file_path = _resolve_module_file(parsed_target.module_or_file)
    if file_path is None:
        raise CLIError(
            f"Could not resolve watch source file from target {target!r}."
        )

    return file_path


def validate_watch_output(enabled: bool, output: Path | None) -> None:
    """
    Validate output requirements for watch mode.
    """
    if enabled and output is None:
        raise CLIError("--watch requires --output.")


def validate_watch_options(watch_options: WatchOptions) -> None:
    """
    Validate watch mode options.
    """
    if not watch_options.enabled:
        return

    if watch_options.delay <= 0:
        raise CLIError("--watch-delay must be greater than 0.")

    for watch_dir in watch_options.dirs:
        resolved_dir = watch_dir.resolve()
        if not resolved_dir.is_dir():
            raise CLIError(
                f"--watch-dir {str(watch_dir)!r} must be an existing directory."
            )

    if watch_options.include and not watch_options.dirs:
        raise CLIError("--watch-include requires at least one --watch-dir.")


def validate_watch_input_output(
    watch_options: WatchOptions,
    output: Path,
) -> None:
    """
    Validate that watch mode does not write over the watched source file.
    """
    if not watch_options.enabled or watch_options.path is None:
        return

    if watch_options.path.resolve() == output.resolve():
        raise CLIError("--watch output must be different from the input file.")


def validate_enabled_watch_options(
    cli_options: WatchCLIOptions,
) -> WatchOptions:
    """
    Validate watch mode and return options with the concrete source path set.
    """
    validate_watch_output(cli_options.watch.enabled, cli_options.output)
    validate_watch_options(cli_options.watch)

    if cli_options.output is None:
        raise CLIError("--watch requires --output.")

    resolved_options = replace(
        cli_options.watch,
        path=resolve_watch_path(cli_options.target),
    )
    validate_watch_input_output(resolved_options, cli_options.output)

    return resolved_options


def _import_watch() -> WatchCallable:
    """
    Import the optional watchfiles watcher.
    """
    try:
        from watchfiles import watch  # type: ignore[import-not-found]
    except ImportError:
        raise CLIError("Install c4-diagrams[watch] to use --watch.") from None
    return watch  # type: ignore[no-any-return]


def build_watch_child_argv(argv: Iterable[str]) -> list[str]:
    """
    Build the one-shot child command argv by removing watch-only flags.
    """
    child_argv: list[str] = []
    skip_next = False

    for arg in argv:
        if skip_next:
            skip_next = False
            continue

        if arg in WATCH_BOOL_FLAGS:
            continue

        if arg in WATCH_VALUE_FLAGS:
            skip_next = True
            continue

        if any(arg.startswith(f"{flag}=") for flag in WATCH_VALUE_FLAGS):
            continue

        child_argv.append(arg)

    return child_argv


def _normalize_watch_path(path: Path) -> Path:
    """
    Return a stable absolute path for watch comparisons.
    """
    try:
        return path.resolve()
    except OSError:
        return path.absolute()


def is_watch_event_relevant(
    events: Iterable[tuple[Change, str]],
    watch_options: WatchOptions,
) -> bool:
    """
    Return whether a watchfiles change batch should trigger a rerun.

    The algorithm first normalizes the primary source path and every extra
    watch directory so all later comparisons use absolute filesystem paths.
    It then scans the event batch in order:

    - A change to the primary source file is always relevant, even when
      include patterns are configured.
    - A change outside every configured watch directory is ignored.
    - A change inside a configured watch directory is relevant immediately
      when no include patterns are configured.
    - When include patterns exist, the changed path is made relative to the
      matching watch directory and tested with ``Path.match`` against each
      pattern. The first matching pattern makes the event batch relevant.

    If no changed path satisfies those rules, the batch is ignored.
    """
    primary_path = (
        _normalize_watch_path(watch_options.path)
        if watch_options.path is not None
        else None
    )
    watch_dirs = tuple(
        _normalize_watch_path(watch_dir) for watch_dir in watch_options.dirs
    )

    for _, changed_path_value in events:
        changed_path = _normalize_watch_path(Path(changed_path_value))

        if primary_path is not None and changed_path == primary_path:
            return True

        for watch_dir in watch_dirs:
            try:
                relative_path = changed_path.relative_to(watch_dir)
            except ValueError:
                continue

            if not watch_options.include:
                return True

            if any(
                relative_path.match(pattern)
                for pattern in watch_options.include
            ):
                return True

    return False


def _run_watch_child(child_argv: list[str]) -> int:
    """
    Run one child CLI invocation and convert unexpected failures to status 1.
    """
    command_name = child_argv[0] if child_argv else "command"

    try:
        return subprocess.run(  # noqa: S603
            [sys.executable, "-m", "c4", *child_argv],
            check=False,
        ).returncode
    except Exception as exc:
        print(f"{command_name} failed:")
        traceback.print_exception(type(exc), exc, exc.__traceback__)
        return 1


def _deduplicate_watch_dirs(paths: Iterable[Path]) -> tuple[Path, ...]:
    """
    Normalize watch directories and preserve only their first occurrence.
    """
    seen: set[Path] = set()
    deduplicated_paths: list[Path] = []

    for path in paths:
        normalized_path = _normalize_watch_path(path)
        if normalized_path in seen:
            continue

        seen.add(normalized_path)
        deduplicated_paths.append(normalized_path)

    return tuple(deduplicated_paths)


def run_with_watch(
    child_argv: list[str],
    watch_options: WatchOptions,
    output: Path,
) -> int:
    """
    Run a child CLI command once, then rerun it for relevant watchfile events.
    """
    watch = _import_watch()

    try:
        initial_status = _run_watch_child(child_argv)

        if watch_options.path is None:
            raise CLIError("--watch requires a resolved source path.")

        validate_watch_input_output(watch_options, output)

        watched_dirs = _deduplicate_watch_dirs((
            watch_options.path.parent,
            *watch_options.dirs,
        ))

        for events in watch(*watched_dirs):
            events = tuple(events)
            if not is_watch_event_relevant(events, watch_options):
                continue

            time.sleep(watch_options.delay)
            _run_watch_child(child_argv)
    except KeyboardInterrupt:
        return 0

    return initial_status

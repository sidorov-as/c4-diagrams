from __future__ import annotations

import builtins
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest
from pytest_mock import MockerFixture

import c4.cli.watch as watch
from c4.cli.exceptions import CLIError
from tests.conftest import MakeTmpPyFile

pytestmark = [pytest.mark.usefixtures("clean_sys_modules")]


def _install_fake_watchfiles(
    mocker: MockerFixture,
    watch_func,
) -> None:
    fake_watchfiles = ModuleType("watchfiles")
    fake_watchfiles.watch = watch_func
    mocker.patch.dict(sys.modules, {"watchfiles": fake_watchfiles})


def test_resolve_watch_path_py_file(tmp_path: Path):
    file_path = tmp_path / "diagram.py"
    file_path.write_text("", encoding="utf-8")

    result = watch.resolve_watch_path(str(file_path))

    assert result == file_path.resolve()


def test_resolve_watch_path_py_file_with_diagram_ref(tmp_path: Path):
    file_path = tmp_path / "diagram.py"
    file_path.write_text("", encoding="utf-8")

    result = watch.resolve_watch_path(f"{file_path}:diagram")

    assert result == file_path.resolve()


def test_resolve_watch_path_json_file(tmp_path: Path):
    file_path = tmp_path / "diagram.json"
    file_path.write_text("{}", encoding="utf-8")

    result = watch.resolve_watch_path(str(file_path))

    assert result == file_path.resolve()


def test_resolve_watch_path_module(make_tmp_py_file: MakeTmpPyFile):
    module_path = make_tmp_py_file("diagram.py")

    result = watch.resolve_watch_path("diagram")

    assert result == module_path.resolve()


def test_resolve_watch_path_module_with_diagram_ref(
    make_tmp_py_file: MakeTmpPyFile,
):
    module_path = make_tmp_py_file("diagram.py")

    result = watch.resolve_watch_path("diagram:diagram")

    assert result == module_path.resolve()


def test_resolve_watch_path_imports_module_when_spec_has_no_file(
    make_tmp_py_file: MakeTmpPyFile,
    mocker: MockerFixture,
):
    module_path = make_tmp_py_file("diagram.py")
    mocker.patch.object(
        watch.importlib.util,
        "find_spec",
        lambda module_name: SimpleNamespace(origin=None),
    )

    result = watch.resolve_watch_path("diagram")

    assert result == module_path.resolve()


def test_resolve_watch_path_imports_module_when_spec_origin_is_directory(
    make_tmp_py_file: MakeTmpPyFile,
    mocker: MockerFixture,
    tmp_path: Path,
):
    module_path = make_tmp_py_file("diagram.py")
    mocker.patch.object(
        watch.importlib.util,
        "find_spec",
        lambda module_name: SimpleNamespace(origin=str(tmp_path)),
    )

    result = watch.resolve_watch_path("diagram")

    assert result == module_path.resolve()


def test_resolve_watch_path_module_without_file_raises(
    mocker: MockerFixture,
):
    mocker.patch.object(
        watch.importlib.util,
        "find_spec",
        lambda module_name: SimpleNamespace(origin=None),
    )
    mocker.patch.object(
        watch,
        "_import_module_or_raise",
        lambda module_name: SimpleNamespace(),
    )
    expected_error = re.escape(
        "Could not resolve watch source file from target 'diagram'."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.resolve_watch_path("diagram")


def test_resolve_watch_path_module_with_non_file_module_file_raises(
    mocker: MockerFixture,
    tmp_path: Path,
):
    mocker.patch.object(
        watch.importlib.util,
        "find_spec",
        lambda module_name: SimpleNamespace(origin=None),
    )
    mocker.patch.object(
        watch,
        "_import_module_or_raise",
        lambda module_name: SimpleNamespace(__file__=str(tmp_path)),
    )
    expected_error = re.escape(
        "Could not resolve watch source file from target 'diagram'."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.resolve_watch_path("diagram")


def test_resolve_watch_path_reraises_top_level_module_not_found(
    mocker: MockerFixture,
):
    mocker.patch.object(
        watch.importlib.util,
        "find_spec",
        lambda module_name: SimpleNamespace(origin=None),
    )

    def raise_module_not_found(module_name):
        raise ModuleNotFoundError(name="dependency")

    mocker.patch.object(
        watch,
        "_import_module_or_raise",
        raise_module_not_found,
    )

    with pytest.raises(ModuleNotFoundError):
        watch.resolve_watch_path("diagram")


def test_resolve_watch_path_missing_file_raises(tmp_path: Path):
    target = str(tmp_path / "missing.py")
    expected_error = re.escape(
        f"Could not resolve watch source file from target {target!r}."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.resolve_watch_path(target)


def test_resolve_watch_path_directory_raises(tmp_path: Path):
    with pytest.raises(CLIError):
        watch.resolve_watch_path(str(tmp_path))


def test_resolve_watch_path_missing_module_raises():
    expected_error = re.escape(
        "Could not import module 'missing_module'. "
        "Make sure it is installed and importable "
        "(check PYTHONPATH / working directory)."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.resolve_watch_path("missing_module")


def test_resolve_watch_path_missing_dotted_module_raises_cli_error():
    expected_error = re.escape(
        "Could not import module 'missing_package.diagram'. "
        "Make sure it is installed and importable "
        "(check PYTHONPATH / working directory)."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.resolve_watch_path("missing_package.diagram")


def test_validate_watch_output_requires_output_when_enabled():
    expected_error = re.escape("--watch requires --output.")

    with pytest.raises(CLIError, match=expected_error):
        watch.validate_watch_output(True, None)


def test_validate_watch_options_invalid_delay_raises():
    watch_options = watch.WatchOptions(enabled=True, delay=0)
    expected_error = re.escape("--watch-delay must be greater than 0.")

    with pytest.raises(CLIError, match=expected_error):
        watch.validate_watch_options(watch_options)


def test_validate_watch_options_missing_watch_dir_raises(tmp_path: Path):
    watch_dir = tmp_path / "missing"
    watch_options = watch.WatchOptions(enabled=True, dirs=(watch_dir,))
    expected_error = re.escape(
        f"--watch-dir {str(watch_dir)!r} must be an existing directory."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.validate_watch_options(watch_options)


def test_validate_watch_options_file_watch_dir_raises(tmp_path: Path):
    watch_dir = tmp_path / "diagram.py"
    watch_dir.write_text("", encoding="utf-8")
    watch_options = watch.WatchOptions(enabled=True, dirs=(watch_dir,))
    expected_error = re.escape(
        f"--watch-dir {str(watch_dir)!r} must be an existing directory."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.validate_watch_options(watch_options)


def test_validate_watch_options_accepts_existing_watch_dirs(tmp_path: Path):
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"
    first_dir.mkdir()
    second_dir.mkdir()
    watch_options = watch.WatchOptions(
        enabled=True,
        dirs=(first_dir, second_dir),
    )

    watch.validate_watch_options(watch_options)


def test_validate_watch_options_include_requires_watch_dir():
    watch_options = watch.WatchOptions(enabled=True, include=("*.py",))
    expected_error = re.escape(
        "--watch-include requires at least one --watch-dir."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.validate_watch_options(watch_options)


def test_validate_watch_options_ignores_disabled_options(tmp_path: Path):
    watch_options = watch.WatchOptions(
        enabled=False,
        delay=0,
        dirs=(tmp_path / "missing",),
        include=("*.py",),
    )

    watch.validate_watch_options(watch_options)


def test_validate_enabled_watch_options_requires_output_after_validation(
    mocker: MockerFixture,
):
    calls: list[str] = []
    mocker.patch.object(
        watch,
        "validate_watch_output",
        lambda enabled, output: calls.append("output"),
    )
    mocker.patch.object(
        watch,
        "validate_watch_options",
        lambda watch_options: calls.append("options"),
    )

    with pytest.raises(CLIError, match=re.escape("--watch requires --output.")):
        watch.validate_enabled_watch_options(
            SimpleNamespace(
                target="diagram.py",
                watch=watch.WatchOptions(enabled=True),
                output=None,
            )
        )

    assert calls == ["output", "options"]


def test_validate_watch_input_output_same_file_raises(tmp_path: Path):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    output_path = tmp_path / "." / "diagram.py"
    watch_options = watch.WatchOptions(
        enabled=True,
        path=watch.resolve_watch_path(str(source_path)),
    )
    expected_error = re.escape(
        "--watch output must be different from the input file."
    )

    with pytest.raises(CLIError, match=expected_error):
        watch.validate_watch_input_output(watch_options, output_path)


def test_validate_watch_input_output_ignored_when_disabled(tmp_path: Path):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    watch_options = watch.WatchOptions(enabled=False, path=source_path)

    watch.validate_watch_input_output(watch_options, source_path)


def test_validate_watch_input_output_ignored_before_path_resolution(
    tmp_path: Path,
):
    output_path = tmp_path / "diagram.py"
    watch_options = watch.WatchOptions(enabled=True)

    watch.validate_watch_input_output(watch_options, output_path)


def test_import_watch_missing_dependency(
    mocker: MockerFixture,
):
    original_import = builtins.__import__
    expected_error = re.escape("Install c4-diagrams[watch] to use --watch.")

    def fake_import(
        name,
        globals_=None,
        locals_=None,
        fromlist=(),
        level=0,
    ):
        if name == "watchfiles":
            raise ImportError("No module named 'watchfiles'")

        return original_import(name, globals_, locals_, fromlist, level)

    mocker.patch.object(builtins, "__import__", fake_import)

    with pytest.raises(CLIError, match=expected_error):
        watch._import_watch()


def test_build_watch_child_argv_removes_watch_only_flags():
    result = watch.build_watch_child_argv([
        "export",
        "diagram.py",
        "--watch",
        "--watch-delay",
        "0.5",
        "--watch-dir=local",
        "--watch-include",
        "*.py",
        "-o",
        "diagram.svg",
        "-w",
    ])

    assert result == ["export", "diagram.py", "-o", "diagram.svg"]


def test_is_watch_event_relevant_matches_primary_source(
    tmp_path: Path,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    watch_options = watch.WatchOptions(
        path=source_path,
        dirs=(tmp_path / "includes",),
        include=("*.puml",),
    )

    result = watch.is_watch_event_relevant(
        [(object(), str(source_path))],
        watch_options,
    )

    assert result is True


def test_is_watch_event_relevant_primary_source_ignores_include_patterns(
    tmp_path: Path,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    watch_options = watch.WatchOptions(
        path=source_path,
        dirs=(tmp_path,),
        include=("*.json",),
    )

    result = watch.is_watch_event_relevant(
        [(object(), str(source_path))],
        watch_options,
    )

    assert result is True


def test_is_watch_event_relevant_matches_include_under_watch_dir(
    tmp_path: Path,
):
    include_dir = tmp_path / "includes"
    changed_path = include_dir / "common" / "base.puml"
    watch_options = watch.WatchOptions(
        path=tmp_path / "diagram.py",
        dirs=(include_dir,),
        include=("**/*.puml",),
    )

    result = watch.is_watch_event_relevant(
        [(object(), str(changed_path))],
        watch_options,
    )

    assert result is True


def test_is_watch_event_relevant_matches_any_file_under_watch_dir_without_include(
    tmp_path: Path,
):
    include_dir = tmp_path / "includes"
    changed_path = include_dir / "common" / "shared.py"
    watch_options = watch.WatchOptions(
        path=tmp_path / "diagram.py",
        dirs=(include_dir,),
    )

    result = watch.is_watch_event_relevant(
        [(object(), str(changed_path))],
        watch_options,
    )

    assert result is True


def test_is_watch_event_relevant_matches_nested_glob_under_watch_dir(
    tmp_path: Path,
):
    include_dir = tmp_path / "includes"
    changed_path = include_dir / "common" / "diagram.py"
    watch_options = watch.WatchOptions(
        path=tmp_path / "diagram.py",
        dirs=(include_dir,),
        include=("**/*.py",),
    )

    result = watch.is_watch_event_relevant(
        [(object(), str(changed_path))],
        watch_options,
    )

    assert result is True


def test_is_watch_event_relevant_ignores_unmatched_watch_dir_change(
    tmp_path: Path,
):
    include_dir = tmp_path / "includes"
    changed_path = include_dir / "base.txt"
    watch_options = watch.WatchOptions(
        path=tmp_path / "diagram.py",
        dirs=(include_dir,),
        include=("*.puml",),
    )

    result = watch.is_watch_event_relevant(
        [(object(), str(changed_path))],
        watch_options,
    )

    assert result is False


def test_is_watch_event_relevant_ignores_unrelated_change(
    tmp_path: Path,
):
    watch_options = watch.WatchOptions(
        path=tmp_path / "diagram.py",
        dirs=(tmp_path / "includes",),
        include=("*.puml",),
    )

    result = watch.is_watch_event_relevant(
        [(object(), str(tmp_path / "other.py"))],
        watch_options,
    )

    assert result is False


def test_is_watch_event_relevant_falls_back_to_absolute_on_resolve_error(
    mocker: MockerFixture,
    tmp_path: Path,
):
    original_resolve = Path.resolve

    def resolve_or_raise(path: Path):
        if path.name == "diagram.py":
            raise OSError("broken")

        return original_resolve(path)

    mocker.patch.object(Path, "resolve", resolve_or_raise)
    source_path = tmp_path / "diagram.py"
    watch_options = watch.WatchOptions(path=source_path)

    result = watch.is_watch_event_relevant(
        [(object(), str(source_path))],
        watch_options,
    )

    assert result is True


def test_run_with_watch_runs_immediately_and_reruns_relevant_events(
    tmp_path: Path,
    mocker: MockerFixture,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    output_path = tmp_path / "diagram.puml"
    child_calls: list[list[str]] = []
    watched_paths = None
    sleep_calls: list[float] = []

    def fake_run(cmd, check):
        child_calls.append(cmd)
        assert check is False
        return subprocess.CompletedProcess(cmd, 0)

    def fake_watch(*paths):
        nonlocal watched_paths
        watched_paths = paths
        yield [(object(), str(source_path))]
        raise KeyboardInterrupt

    _install_fake_watchfiles(mocker, fake_watch)
    mocker.patch.object(watch.subprocess, "run", fake_run)
    mocker.patch.object(watch.time, "sleep", sleep_calls.append)
    watch_options = watch.WatchOptions(
        enabled=True,
        delay=0.5,
        path=source_path,
    )

    result = watch.run_with_watch(
        ["render", str(source_path), "-o", str(output_path)],
        watch_options,
        output_path,
    )

    assert result == 0
    assert child_calls == [
        [
            sys.executable,
            "-m",
            "c4",
            "render",
            str(source_path),
            "-o",
            str(output_path),
        ],
        [
            sys.executable,
            "-m",
            "c4",
            "render",
            str(source_path),
            "-o",
            str(output_path),
        ],
    ]
    assert watched_paths == (tmp_path.resolve(),)
    assert sleep_calls == [0.5]


def test_run_with_watch_deduplicates_watch_directories(
    tmp_path: Path,
    mocker: MockerFixture,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    include_dir = tmp_path / "includes"
    include_dir.mkdir()
    output_path = tmp_path / "diagram.puml"
    watched_paths = None

    def fake_watch(*paths):
        nonlocal watched_paths
        watched_paths = paths
        return iter(())

    _install_fake_watchfiles(mocker, fake_watch)
    mocker.patch.object(
        watch.subprocess,
        "run",
        lambda cmd, check: subprocess.CompletedProcess(cmd, 7),
    )
    watch_options = watch.WatchOptions(
        enabled=True,
        path=source_path,
        dirs=(tmp_path, tmp_path / ".", include_dir),
    )

    result = watch.run_with_watch(
        ["render", str(source_path), "-o", str(output_path)],
        watch_options,
        output_path,
    )

    assert result == 7
    assert watched_paths == (tmp_path.resolve(), include_dir.resolve())


def test_run_with_watch_requires_resolved_source_path(
    mocker: MockerFixture,
    tmp_path: Path,
):
    output_path = tmp_path / "diagram.puml"
    watch_called = False

    def fake_watch(*paths):
        nonlocal watch_called
        watch_called = True
        return iter(())

    _install_fake_watchfiles(mocker, fake_watch)
    mocker.patch.object(
        watch.subprocess,
        "run",
        lambda cmd, check: subprocess.CompletedProcess(cmd, 0),
    )

    with pytest.raises(
        CLIError,
        match=re.escape("--watch requires a resolved source path."),
    ):
        watch.run_with_watch(
            ["render", "diagram.py", "-o", str(output_path)],
            watch.WatchOptions(enabled=True),
            output_path,
        )

    assert watch_called is False


def test_run_with_watch_ignores_irrelevant_events(
    tmp_path: Path,
    mocker: MockerFixture,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    output_path = tmp_path / "diagram.puml"
    child_calls: list[list[str]] = []

    def fake_watch(*paths):
        yield [(object(), str(tmp_path / "other.py"))]
        raise KeyboardInterrupt

    _install_fake_watchfiles(mocker, fake_watch)
    mocker.patch.object(
        watch.subprocess,
        "run",
        lambda cmd, check: (
            child_calls.append(cmd) or subprocess.CompletedProcess(cmd, 0)
        ),
    )
    watch_options = watch.WatchOptions(
        enabled=True,
        path=source_path,
    )

    result = watch.run_with_watch(
        ["render", str(source_path), "-o", str(output_path)],
        watch_options,
        output_path,
    )

    assert result == 0
    assert len(child_calls) == 1


def test_run_with_watch_uses_fresh_child_process_for_helper_file_changes(
    tmp_path: Path,
    mocker: MockerFixture,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    include_dir = tmp_path / "local"
    include_dir.mkdir()
    shared_path = include_dir / "shared.py"
    shared_path.write_text("", encoding="utf-8")
    output_path = tmp_path / "diagram.puml"
    child_calls: list[list[str]] = []

    def fake_run(cmd, check):
        child_calls.append(cmd)
        if len(child_calls) == 1:
            shared_path.write_text("VALUE = 'updated'", encoding="utf-8")

        return subprocess.CompletedProcess(cmd, 0)

    def fake_watch(*paths):
        yield [(object(), str(shared_path))]
        raise KeyboardInterrupt

    _install_fake_watchfiles(mocker, fake_watch)
    mocker.patch.object(watch.subprocess, "run", fake_run)
    mocker.patch.object(watch.time, "sleep", lambda delay: None)
    watch_options = watch.WatchOptions(
        enabled=True,
        path=source_path,
        dirs=(include_dir,),
        include=("*.py",),
    )

    result = watch.run_with_watch(
        ["render", str(source_path), "-o", str(output_path)],
        watch_options,
        output_path,
    )

    assert result == 0
    assert len(child_calls) == 2
    assert shared_path.read_text(encoding="utf-8") == "VALUE = 'updated'"


def test_run_with_watch_handles_keyboard_interrupt_during_initial_action(
    tmp_path: Path,
    mocker: MockerFixture,
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    output_path = tmp_path / "diagram.puml"
    watch_called = False

    def action():
        raise KeyboardInterrupt

    def fake_run(cmd, check):
        action()
        return subprocess.CompletedProcess(cmd, 0)

    def fake_watch(*paths):
        nonlocal watch_called
        watch_called = True
        return iter(())

    _install_fake_watchfiles(mocker, fake_watch)
    mocker.patch.object(watch.subprocess, "run", fake_run)
    watch_options = watch.WatchOptions(
        enabled=True,
        path=source_path,
    )

    result = watch.run_with_watch(
        ["render", str(source_path), "-o", str(output_path)],
        watch_options,
        output_path,
    )

    assert result == 0
    assert watch_called is False


def test_run_with_watch_prints_action_exceptions_and_keeps_watching(
    tmp_path: Path,
    mocker: MockerFixture,
    capsys: pytest.CaptureFixture[str],
):
    source_path = tmp_path / "diagram.py"
    source_path.write_text("", encoding="utf-8")
    output_path = tmp_path / "diagram.puml"
    child_calls = 0

    def fake_run(cmd, check):
        nonlocal child_calls
        child_calls += 1
        if child_calls == 1:
            raise RuntimeError("broken")

        return subprocess.CompletedProcess(cmd, 0)

    def fake_watch(*paths):
        yield [(object(), str(source_path))]
        raise KeyboardInterrupt

    _install_fake_watchfiles(mocker, fake_watch)
    mocker.patch.object(watch.subprocess, "run", fake_run)
    mocker.patch.object(watch.time, "sleep", lambda delay: None)
    watch_options = watch.WatchOptions(
        enabled=True,
        path=source_path,
    )

    result = watch.run_with_watch(
        ["render", str(source_path), "-o", str(output_path)],
        watch_options,
        output_path,
    )

    captured = capsys.readouterr()
    assert result == 0
    assert child_calls == 2
    assert "render failed:" in captured.out
    assert "RuntimeError: broken" in captured.err

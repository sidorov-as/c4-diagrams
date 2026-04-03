import dataclasses
import os
import subprocess
import sys
from asyncio import Protocol
from collections.abc import Iterator
from pathlib import Path

import pytest

pytest_plugins = (
    "pytester",
    "tests.fixtures.converters.json",
)

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
BASE_DIR = SNAPSHOTS_DIR.parent.parent


@pytest.fixture()
def assert_match_snapshot():
    def _assert_equal(
        *,
        snapshot_name: str | None = None,
        snapshot_dir: Path = SNAPSHOTS_DIR,
        snapshot_file: Path | None = None,
        diagram_code: str | None = None,
        diagram_code_file: Path | None = None,
    ) -> None:
        if snapshot_file and snapshot_name:
            raise ValueError(
                "Provide either snapshot_file or snapshot_name, not both"
            )

        if snapshot_name:
            snapshot_file = snapshot_dir / snapshot_name

        if not snapshot_file:
            raise ValueError("You must provide snapshot_file or snapshot_name")

        if not snapshot_file.exists():
            raise AssertionError(
                f"Snapshot {snapshot_file.relative_to(BASE_DIR)} does not exist"
            )

        expected_code = snapshot_file.read_text(encoding="utf-8")

        if diagram_code and diagram_code_file:
            raise ValueError(
                "Provide either diagram_code or diagram_code_file, not both"
            )

        if diagram_code_file:
            if not diagram_code_file.exists():
                raise AssertionError(
                    f"Diagram file {diagram_code_file.relative_to(BASE_DIR)} "
                    f"does not exist"
                )
            diagram_code = diagram_code_file.read_text(encoding="utf-8")

        if diagram_code is None:
            raise ValueError(
                "You must provide diagram_code or diagram_code_file"
            )

        assert diagram_code.strip() == expected_code.strip()

    return _assert_equal


class AssertMatchSnapshot(Protocol):
    def __call__(
        self,
        *,
        snapshot_name: str | None = None,
        snapshot_dir: Path = SNAPSHOTS_DIR,
        snapshot_file: Path | None = None,
        diagram_code: str | None = None,
        diagram_code_file: Path | None = None,
    ) -> None: ...


@pytest.fixture()
def sys_path_tmp(tmp_path: Path) -> Iterator[Path]:
    tmp_path_str = str(tmp_path)

    sys.path.insert(0, tmp_path_str)
    try:
        yield tmp_path
    finally:
        if tmp_path_str in sys.path:
            sys.path.remove(tmp_path_str)


@pytest.fixture()
def clean_sys_modules():
    before = set(sys.modules)

    yield

    after = set(sys.modules)
    created = after - before

    for name in created:
        sys.modules.pop(name, None)


@pytest.fixture()
def make_tmp_py_file(
    sys_path_tmp: Path,
    tmp_path: Path,
):
    created: list[Path] = []

    def _factory(
        relative_path: Path | str,
        content: str = "",
        cleanup: bool = True,
        add_to_sys_path: bool = False,
    ) -> Path:
        _relative_path = Path(relative_path)
        assert not _relative_path.is_absolute(), (
            "Relative path required, got absolute"
        )

        if add_to_sys_path:
            path = sys_path_tmp / _relative_path
        else:
            path = tmp_path / _relative_path

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

        if cleanup:
            created.append(path)

        return path

    yield _factory

    for created_path in reversed(created):
        created_path.unlink(missing_ok=True)


class MakeTmpPyFile(Protocol):
    def __call__(
        self,
        relative_path: Path,
        content: str = "",
        cleanup: bool = True,
        add_to_sys_path: bool = False,
    ) -> Path: ...


@dataclasses.dataclass
class CommandResult:
    stdout: str | bytes
    stderr: str | bytes
    exit_code: int


@pytest.fixture()
def cli(sys_path_tmp: Path):
    def with_args(
        argv: list[str] | None = None,
        cwd: str | Path | None = None,
    ) -> CommandResult:
        argv = argv or []
        cmd = [sys.executable, "-m", "c4", *argv]

        env = dict(os.environ)
        pythonpath = str(sys_path_tmp)
        if env.get("PYTHONPATH"):
            pythonpath = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
        env["PYTHONPATH"] = pythonpath

        run_kwargs = {
            "capture_output": True,
            "text": True,
            "timeout": 60,
            "env": env,
        }
        if cwd:
            run_kwargs["cwd"] = cwd

        res = subprocess.run(cmd, **run_kwargs)  # noqa: S603

        return CommandResult(
            stdout=res.stdout,
            stderr=res.stderr,
            exit_code=res.returncode,
        )

    return with_args


class CLI(Protocol):
    def __call__(
        self,
        argv: list[str] | None = None,
        cwd: str | Path | None = None,
    ) -> CommandResult: ...

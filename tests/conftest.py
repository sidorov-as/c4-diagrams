import sys
from collections.abc import Iterator
from pathlib import Path
from typing import Protocol

import pytest

pytest_plugins = ["pytester"]

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
BASE_DIR = SNAPSHOTS_DIR.parent.parent


@pytest.fixture
def assert_match_snapshot():
    def _assert_equal(
        snapshot: str,
        diagram_code: str,
        snapshot_dir: Path = SNAPSHOTS_DIR,
    ) -> None:
        snapshot_file = snapshot_dir / snapshot
        if not snapshot_file.exists():
            raise AssertionError(
                f"Snapshot {snapshot_file.relative_to(BASE_DIR)} does not exist"
            )

        expected_code = snapshot_file.read_text(encoding="utf-8")

        assert diagram_code == expected_code

    return _assert_equal


class AssertMatchSnapshot(Protocol):
    def __call__(
        self,
        snapshot: str,
        diagram_code: str,
        snapshot_dir: Path = SNAPSHOTS_DIR,
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

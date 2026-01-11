from pathlib import Path
from typing import Protocol

import pytest

SNAPSHOTS_DIR = Path(__file__).parent / "snapshots"
BASE_DIR = SNAPSHOTS_DIR.parent.parent


@pytest.fixture
def assert_match_snapshot():
    def _assert_equal(snapshot: str, diagram_code: str) -> None:
        snapshot_file = SNAPSHOTS_DIR / snapshot
        if not snapshot_file.exists():
            raise AssertionError(
                f"Snapshot {snapshot_file.relative_to(BASE_DIR)} does not exist"
            )

        expected_code = snapshot_file.read_text(encoding="utf-8")

        assert diagram_code == expected_code

    return _assert_equal


class AssertMatchSnapshot(Protocol):
    def __call__(self, snapshot: str, diagram_code: str) -> None: ...

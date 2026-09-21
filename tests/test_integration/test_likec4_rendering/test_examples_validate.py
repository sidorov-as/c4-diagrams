from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).parents[3] / "docs" / "assets" / "examples" / "likec4"
SOURCES = sorted(EXAMPLES.glob("*.c4"))

pytestmark = [
    pytest.mark.likec4,
    pytest.mark.skipif(
        shutil.which("likec4") is None, reason="likec4 is not installed"
    ),
]


def test_examples_are_found():
    assert [path.stem for path in SOURCES] == [
        "extended-customer-support-component-project",
        "project.advanced",
        "project.minimal",
        "tuned-sysops-component-project",
    ]


@pytest.mark.parametrize("source", SOURCES, ids=lambda path: path.stem)
def test_committed_example_is_valid_likec4(source: Path, tmp_path: Path):
    """Run ``likec4 validate`` on each committed example (with layout)."""
    project_dir = tmp_path / source.stem
    project_dir.mkdir()
    shutil.copy(source, project_dir / source.name)

    result = subprocess.run(  # noqa: S603
        ["likec4", "validate", "--json", str(project_dir)],  # noqa: S607
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    report = json.loads(result.stdout)
    assert report["valid"] is True, report.get("errors")
    assert result.returncode == 0

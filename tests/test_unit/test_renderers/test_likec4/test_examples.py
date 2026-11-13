import runpy
from pathlib import Path

import pytest

EXAMPLES = Path(__file__).parents[4] / "docs" / "assets" / "examples" / "likec4"
PYTHON_EXAMPLES = sorted(EXAMPLES.glob("*.py"))


def test_examples_exist():
    assert {path.stem for path in PYTHON_EXAMPLES} == {
        "project.minimal",
        "project.advanced",
    }


@pytest.mark.parametrize("path", PYTHON_EXAMPLES, ids=lambda p: p.stem)
def test_example_renders_to_committed_dsl(path: Path):
    project = runpy.run_path(str(path))["project"]

    expected = path.with_suffix(".c4").read_text(encoding="utf-8")

    assert project.render() == expected

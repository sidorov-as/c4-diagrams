from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[3]
OVERVIEW_DIR = ROOT / "docs" / "assets" / "overview"
PORTABLE_SOURCE = OVERVIEW_DIR / "overview.py"


def _readme_example() -> str:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    block = re.search(r"```python\n# diagram\.py\n(.*?)```", readme, re.DOTALL)
    assert block is not None, "README has no `# diagram.py` example"
    return block.group(1)


def test_readme_example_matches_overview_source() -> None:
    assert (
        _readme_example().strip()
        == PORTABLE_SOURCE.read_text(encoding="utf-8").strip()
    )


def test_portable_overview_source_avoids_backend_helpers() -> None:
    source = PORTABLE_SOURCE.read_text(encoding="utf-8")

    assert "c4.contrib" not in source
    assert not re.search(r"\bRel(Down|Up|Left|Right|Back|Neighbor)\b", source)


def test_home_page_includes_overview_sources() -> None:
    index = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")

    for source in OVERVIEW_DIR.glob("overview*.py"):
        assert f"assets/overview/{source.name}" in index


def test_plantuml_variant_matches_portable_source_with_rel_right() -> None:
    variant = (OVERVIEW_DIR / "overview.plantuml.py").read_text(
        encoding="utf-8"
    )
    portable = PORTABLE_SOURCE.read_text(encoding="utf-8")

    assert (
        variant
        .replace("RelRight", "Rel")
        .replace("from c4.contrib.plantuml import Rel\n", "")
        .replace(
            "from c4 import Person, System,",
            "from c4 import Person, Rel, System,",
        )
        == portable
    )

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from c4.converters.json.converter import diagram_from_dict, diagram_from_json

ROOT = Path(__file__).parents[3]
PAGE = (ROOT / "docs" / "converters" / "json" / "json.md").read_text(
    encoding="utf-8"
)
EXAMPLES = ROOT / "docs" / "assets" / "examples" / "json"

# discriminator shown on the page -> minimal example document
DOCUMENTS = {
    "omitted": EXAMPLES / "core" / "system-context-diagram.minimal.json",
    "plantuml": EXAMPLES / "plantuml" / "system-context-diagram.minimal.json",
    "mermaid": EXAMPLES / "mermaid" / "system-context-diagram.minimal.json",
    "d2": EXAMPLES / "d2" / "system-context-diagram.minimal.json",
    "structurizr": EXAMPLES / "structurizr" / "workspace.minimal.json",
    "likec4": EXAMPLES / "likec4" / "project.minimal.json",
}


def _page_roots() -> dict[str, str]:
    rows = re.findall(
        r"^\|\s*(`?\w+`?)\s*\|\s*([^|]+?)\s*\|", PAGE, re.MULTILINE
    )
    return {
        key.strip("`"): root
        for key, root in rows
        if key.strip("`") in DOCUMENTS
    }


def test_page_lists_every_discriminator() -> None:
    assert set(_page_roots()) == set(DOCUMENTS)


@pytest.mark.parametrize("discriminator", DOCUMENTS)
def test_root_type_matches_page(discriminator: str) -> None:
    data = json.loads(DOCUMENTS[discriminator].read_text(encoding="utf-8"))
    root, _ = diagram_from_dict(data)

    named = _page_roots()[discriminator]
    assert f"`{type(root).__name__}`" in named or type(root).__name__ in named


def test_quick_start_document_loads(tmp_path: Path) -> None:
    section = PAGE.split("## Quick start", 1)[1]
    document = section.split("```json\n", 1)[1].split("```", 1)[0]
    path = tmp_path / "diagram.json"
    path.write_text(document, encoding="utf-8")

    diagram, _ = diagram_from_json(path)

    assert "Uses HTTP API" in diagram.as_plantuml()

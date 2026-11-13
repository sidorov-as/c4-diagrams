from __future__ import annotations

import re
from pathlib import Path

import pytest

import c4.contrib.mermaid as mermaid

PAGE = (
    Path(__file__).parents[3]
    / "docs"
    / "api_docs"
    / "mermaid"
    / "relationships.md"
)
HELPERS = re.findall(
    r"^::: c4\.contrib\.mermaid\.(\w+)",
    PAGE.read_text(encoding="utf-8"),
    re.MULTILINE,
)


def test_relationship_page_lists_helpers() -> None:
    assert HELPERS


@pytest.mark.parametrize("name", HELPERS)
def test_documented_helper_is_exported(name: str) -> None:
    assert hasattr(mermaid, name)

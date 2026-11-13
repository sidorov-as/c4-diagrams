from __future__ import annotations

import ast
import re
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]
SKIP_MARKER = "<!-- skip-syntax -->"
FENCE_OPEN = re.compile(r"^(\s*)(`{3,})\s*(?:python|py)\b[^\n]*$")
INCLUDE = "--8<--"

MARKDOWN_FILES = sorted([
    *(ROOT / "docs").rglob("*.md"),
    ROOT / "README.md",
    ROOT / "CONTRIBUTING.md",
])


def _python_blocks(path: Path) -> list[tuple[int, str]]:
    """Return (line number of the opening fence, source) for each checked block."""
    lines = path.read_text(encoding="utf-8").splitlines()
    blocks: list[tuple[int, str]] = []
    index = 0
    while index < len(lines):
        match = FENCE_OPEN.match(lines[index])
        if match is None:
            index += 1
            continue

        start = index
        closing = re.compile(rf"^\s*{match.group(2)}\s*$")
        index += 1
        body: list[str] = []
        while index < len(lines) and not closing.match(lines[index]):
            body.append(lines[index])
            index += 1
        index += 1

        previous = lines[start - 1].strip() if start > 0 else ""
        if previous == SKIP_MARKER:
            continue

        source = textwrap.dedent(
            "\n".join(line for line in body if INCLUDE not in line)
        )
        if source.strip():
            blocks.append((start + 1, source))
    return blocks


SNIPPETS = [
    pytest.param(path, line, source, id=f"{path.relative_to(ROOT)}:{line}")
    for path in MARKDOWN_FILES
    for line, source in _python_blocks(path)
]


def test_snippets_are_collected() -> None:
    assert SNIPPETS


@pytest.mark.parametrize(("path", "line", "source"), SNIPPETS)
def test_python_block_is_valid_syntax(
    path: Path, line: int, source: str
) -> None:
    try:
        ast.parse(source)
    except SyntaxError as exc:
        pytest.fail(
            f"{path.relative_to(ROOT)}:{line}: {exc.msg} (block line {exc.lineno})"
        )

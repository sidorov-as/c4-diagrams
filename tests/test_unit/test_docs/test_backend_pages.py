from __future__ import annotations

import re
from pathlib import Path

import pytest

from docs.scripts.backend_call_cases import (
    LIKEC4_CASES,
    STRUCTURIZR_CASES,
    Case,
    contains_fragment,
    likec4_render,
    structurizr_render,
)

RENDERERS_DIR = Path(__file__).parents[3] / "docs" / "renderers"
BACKEND_PAGES = sorted([
    *(RENDERERS_DIR / "structurizr").glob("*.md"),
    *(RENDERERS_DIR / "likec4").glob("*.md"),
])
CODE_BLOCK = re.compile(r"^```(\w+)\n(.*?)^```", re.DOTALL | re.MULTILINE)

STRUCTURIZR_ALL = [
    pytest.param(case, id=f"{group}-{index}")
    for group, cases in STRUCTURIZR_CASES.items()
    for index, case in enumerate(cases)
]


LIKEC4_ALL = [
    pytest.param(case, id=f"{group}-{index}")
    for group, cases in LIKEC4_CASES.items()
    for index, case in enumerate(cases)
]


def _blocks(path: Path, language: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [body for lang, body in CODE_BLOCK.findall(text) if lang == language]


@pytest.mark.parametrize("case", STRUCTURIZR_ALL)
def test_structurizr_call_renders_the_dsl_shown_in_the_docs(case: Case):
    assert contains_fragment(structurizr_render(case), case.dsl)


@pytest.mark.parametrize("case", LIKEC4_ALL)
def test_likec4_call_renders_the_dsl_shown_in_the_docs(case: Case):
    assert contains_fragment(likec4_render(case), case.dsl)


def _collapse_styles(dsl: str) -> str:
    """Replace the content of the top-level ``styles`` block with ``...``."""
    lines = dsl.splitlines()
    result: list[str] = []
    skipping = False
    for line in lines:
        if skipping:
            if line == "    }":
                skipping = False
                result.append(line)
            continue
        result.append(line)
        if line == "    styles {":
            skipping = True
            result.append("      ...")
    return "\n".join(result)


def test_structurizr_quickstart_runs_and_matches_the_shown_dsl():
    index = RENDERERS_DIR / "structurizr" / "index.md"
    text = index.read_text(encoding="utf-8")
    quickstart = text[text.index("## Quickstart") :]
    code = CODE_BLOCK.search(quickstart)
    assert code is not None
    namespace: dict[str, object] = {}
    exec(code.group(2), namespace)  # noqa: S102

    shown = CODE_BLOCK.search(text[text.index("<!-- quickstart-output -->") :])
    assert shown is not None
    rendered = namespace["workspace"].render()  # type: ignore[attr-defined]

    assert _collapse_styles(rendered).strip() == shown.group(2).strip()


def test_likec4_quickstart_runs_and_matches_the_shown_source():
    text = (RENDERERS_DIR / "likec4" / "index.md").read_text(encoding="utf-8")
    quickstart = text[text.index("## Quickstart") :]
    code = CODE_BLOCK.search(quickstart)
    assert code is not None
    namespace: dict[str, object] = {}
    exec(code.group(2), namespace)  # noqa: S102

    shown = CODE_BLOCK.search(text[text.index("<!-- quickstart-output -->") :])
    assert shown is not None
    rendered = namespace["project"].render()  # type: ignore[attr-defined]

    assert rendered.strip() == shown.group(2).strip()


def _backend_page(path: Path):
    # Pages that build a local backend need that CLI, so they run in its CI job.
    marks = []
    if path.name == "renderers.md":
        marks.append(getattr(pytest.mark, path.parent.name))
    return pytest.param(
        path, id=path.parent.name + "/" + path.name, marks=marks
    )


@pytest.mark.parametrize("path", [_backend_page(p) for p in BACKEND_PAGES])
def test_self_contained_python_blocks_in_backend_pages_run(
    path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    # Snippets may save files with relative paths; keep them out of the repo.
    monkeypatch.chdir(tmp_path)
    for block in _blocks(path, "python"):
        if block.lstrip().startswith(("from c4", "import c4")):
            exec(compile(block, str(path), "exec"), {})  # noqa: S102


def test_likec4_cheatsheet_specification_matches_the_c4_preset():
    from c4.contrib.likec4 import C4, Project

    text = (RENDERERS_DIR / "likec4" / "c4-cheatsheet.md").read_text(
        encoding="utf-8"
    )
    namespace: dict[str, object] = {}
    exec(  # noqa: S102
        _blocks(RENDERERS_DIR / "likec4" / "c4-cheatsheet.md", "python")[0],
        namespace,
    )
    explicit = namespace["project"].specification  # type: ignore[attr-defined]
    preset = Project("Shop")
    preset.specification.use(C4)

    assert "use(C4)" in text
    assert explicit.element_kinds == preset.specification.element_kinds

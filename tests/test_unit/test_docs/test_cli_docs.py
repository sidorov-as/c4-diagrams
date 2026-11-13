from __future__ import annotations

from pathlib import Path

import pytest

from docs.scripts.generate_backend_reference import _subparser

CLI_DOC = (Path(__file__).parents[3] / "docs" / "cli.md").read_text(
    encoding="utf-8"
)


def _option_strings(command: str) -> list[str]:
    return [
        option
        for action in _subparser(command)._actions
        for option in action.option_strings
    ]


@pytest.mark.parametrize("command", ["render", "export"])
def test_every_option_is_documented(command: str) -> None:
    options = _option_strings(command)
    assert options
    section = CLI_DOC.split(f"### c4 {command}", 1)[1].split("\n### ", 1)[0]
    missing = [option for option in options if f"`{option}`" not in section]
    assert not missing, (
        f"c4 {command} options missing from docs/cli.md: {missing}"
    )


def test_first_example_output_matches_renderer() -> None:
    start = CLI_DOC.index("```python\n# diagram.py\n")
    source = CLI_DOC[start:].split("```python\n", 1)[1].split("```", 1)[0]
    shown = CLI_DOC[start:].split("```puml\n", 1)[1].split("```", 1)[0]

    namespace: dict[str, object] = {}
    exec(compile(source, "docs/cli.md", "exec"), namespace)  # noqa: S102

    assert shown.strip() == namespace["diagram"].as_plantuml().strip()  # type: ignore[attr-defined]

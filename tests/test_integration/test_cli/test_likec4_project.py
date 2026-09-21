import json
import shutil
import stat
import sys
import textwrap
from pathlib import Path

import pytest

from tests.conftest import CLI, MakeTmpPyFile

PROJECT_SOURCE = textwrap.dedent(
    """
    from c4.contrib.likec4 import Project, Wildcard

    project = Project("Shop")
    project.specification.element("system")
    project.model.element("system", "Shop", alias="shop")
    project.views.element_view("index", "Landscape").include(Wildcard())
    project.views.element_view("other", "Other").include(Wildcard())
    """
)

PROJECT_JSON = {
    "backend": "likec4",
    "specification": {"elements": [{"name": "system"}]},
    "model": {
        "elements": [
            {"id": "shop", "alias": "shop", "kind": "system", "title": "Shop"}
        ]
    },
    "views": {
        "items": [
            {
                "type": "element",
                "key": "index",
                "rules": [{"rule": "include", "items": [{"type": "wildcard"}]}],
            }
        ]
    },
}

EXPECTED_DSL_PREFIX = "specification { element system }\n"

# A stand-in for `likec4` that records its arguments and writes the image the
# real CLI would produce, so the CLI wiring is tested without Node/Chromium.
FAKE_LIKEC4 = """\
#!/bin/sh
out=""; view=""; fmt="$2"
while [ $# -gt 0 ]; do
  case "$1" in
    -o) out="$2"; shift ;;
    -f) view="$2"; shift ;;
  esac
  shift
done
mkdir -p "$out"
printf 'fake-image' > "$out/$view.$fmt"
"""


@pytest.fixture
def project_file(make_tmp_py_file: MakeTmpPyFile) -> Path:
    return make_tmp_py_file("project_module.py", PROJECT_SOURCE)


@pytest.fixture
def fake_likec4(tmp_path: Path) -> Path:
    path = tmp_path / "bin" / "likec4"
    path.parent.mkdir()
    path.write_text(FAKE_LIKEC4, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return path


posix_only = pytest.mark.skipif(
    sys.platform == "win32", reason="Uses a POSIX shell script"
)


def test_render_likec4_to_stdout(project_file: Path, cli: CLI):
    result = cli(["render", str(project_file), "--likec4"])

    assert result.exit_code == 0, result.stderr
    assert result.stdout.startswith(EXPECTED_DSL_PREFIX)
    assert not result.stderr


def test_render_likec4_to_file_invokes_no_external_tool(
    project_file: Path, cli: CLI, tmp_path: Path
):
    output = tmp_path / "out.c4"

    result = cli(["render", str(project_file), "--likec4", "-o", str(output)])

    assert result.exit_code == 0, result.stderr
    assert output.read_text(encoding="utf-8").startswith(EXPECTED_DSL_PREFIX)


def test_render_likec4_json_selects_renderer_from_backend(
    cli: CLI, tmp_path: Path
):
    source = tmp_path / "project.json"
    source.write_text(json.dumps(PROJECT_JSON), encoding="utf-8")

    result = cli(["render", str(source)])

    assert result.exit_code == 0, result.stderr
    assert result.stdout.startswith(EXPECTED_DSL_PREFIX)


def test_render_likec4_json_conflicting_renderer_is_rejected(
    cli: CLI, tmp_path: Path
):
    source = tmp_path / "project.json"
    source.write_text(json.dumps(PROJECT_JSON), encoding="utf-8")

    result = cli(["render", str(source), "--d2"])

    assert result.exit_code == 2
    assert "does not match" in result.stderr


def test_render_project_with_other_renderer_fails(project_file: Path, cli: CLI):
    result = cli(["render", str(project_file), "--plantuml"])

    assert result.exit_code == 2
    assert "Cannot render Project" in result.stderr
    assert "requires a c4.diagrams.core.Diagram" in result.stderr


def test_render_other_diagram_with_likec4_fails(
    make_tmp_py_file: MakeTmpPyFile, cli: CLI
):
    module = make_tmp_py_file(
        "diagram_module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            with SystemContextDiagram(title="D") as diagram:
                pass
            """
        ),
    )

    result = cli(["render", str(module), "--likec4"])

    assert result.exit_code == 2
    assert "accepts only c4.contrib.likec4.Project" in result.stderr


def test_convert_likec4_json_to_python(cli: CLI, tmp_path: Path):
    source = tmp_path / "project.json"
    source.write_text(json.dumps(PROJECT_JSON), encoding="utf-8")

    result = cli(["convert", str(source), "--json-to-py"])

    assert result.exit_code == 0, result.stderr
    assert result.stdout.startswith("from c4.contrib.likec4 import ")
    assert "project = Project()" in result.stdout


@posix_only
@pytest.mark.parametrize("fmt", ["png", "jpg"])
def test_export_likec4_uses_the_configured_command(
    project_file: Path, cli: CLI, tmp_path: Path, fake_likec4: Path, fmt: str
):
    output = tmp_path / f"out.{fmt}"

    result = cli([
        "export",
        str(project_file),
        "--likec4",
        "--likec4-bin",
        str(fake_likec4),
        "--likec4-view-key",
        "index",
        "-f",
        fmt,
        "-o",
        str(output),
    ])

    assert result.exit_code == 0, result.stderr
    assert output.read_bytes() == b"fake-image"


@posix_only
def test_export_likec4_needs_a_view_key_with_several_views(
    project_file: Path, cli: CLI, fake_likec4: Path
):
    result = cli([
        "export",
        str(project_file),
        "--likec4",
        "--likec4-bin",
        str(fake_likec4),
    ])

    assert result.exit_code == 2
    assert "needs a view key" in result.stderr


def test_export_likec4_rejects_unsupported_format(project_file: Path, cli: CLI):
    result = cli(["export", str(project_file), "--likec4", "-f", "svg"])

    assert result.exit_code == 2
    assert "not supported by renderer 'likec4'" in result.stderr


def test_export_likec4_reports_missing_binary(project_file: Path, cli: CLI):
    result = cli([
        "export",
        str(project_file),
        "--likec4",
        "--likec4-bin",
        "definitely-not-likec4",
    ])

    assert result.exit_code == 2
    assert "LikeC4 binary 'definitely-not-likec4' was not found" in (
        result.stderr
    )


@pytest.mark.likec4
@pytest.mark.skipif(
    shutil.which("likec4") is None, reason="likec4 is not installed"
)
def test_export_likec4_with_the_real_cli(
    project_file: Path, cli: CLI, tmp_path: Path
):
    output = tmp_path / "out.png"

    result = cli([
        "export",
        str(project_file),
        "--likec4",
        "--likec4-view-key",
        "index",
        "-o",
        str(output),
    ])

    if "Playwright Chromium is not installed" in result.stderr:
        pytest.skip("Playwright Chromium is not installed")
    assert result.exit_code == 0, result.stderr
    assert output.read_bytes().startswith(b"\x89PNG")

import sys
import textwrap
from pathlib import Path

import pytest

from tests.conftest import CLI, AssertMatchSnapshot, MakeTmpPyFile

pytestmark = [pytest.mark.usefixtures("clean_sys_modules")]

SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def test_render__absolute_file_path__success(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli(["render", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success.puml",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_render__module__success(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli(["render", "module", "-o", str(diagram_output)])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success.puml",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_render__absolute_file_path_with_ref__success(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli([
        "render",
        f"{module_path!s}:diagram",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success.puml",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_render__module_with_ref__success(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli(["render", "module:diagram", "-o", str(diagram_output)])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success.puml",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_render__absolute_file_path__diagram_not_found(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram
            """
        ),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        f"c4: error: No Diagram instances found in '{module_path!s}'. "
        f"Define a Diagram at module level or specify one "
        f"explicitly as '<target>:<name>'.\n"
    )

    result = cli(["render", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_render__module__diagram_not_found(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram
            """
        ),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        "c4: error: No Diagram instances found in module 'module'. "
        "Define a Diagram at module level or specify one "
        "explicitly as '<target>:<name>'.\n"
    )

    result = cli(["render", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_render__absolute_file_path_with_ref__diagram_not_found(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            d = SystemContextDiagram("Example")
            """
        ),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        f"c4: error: Diagram reference 'diagram' was not found "
        f"in {str(module_path)!r}.\n"
    )

    result = cli([
        "render",
        f"{module_path!s}:diagram",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_render__module_with_ref__diagram_not_found(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            d = SystemContextDiagram("Example")
            """
        ),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        "c4: error: Diagram reference 'diagram' was not found "
        "in module 'module'.\n"
    )

    result = cli(["render", "module:diagram", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_render__absolute_file_path_with_ref__invalid_ref(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            d = SystemContextDiagram("Example")
            """
        ),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        f"c4: error: Invalid target "
        f"'{module_path!s}:'. "
        f"Expected 'module', 'module:diagram', 'file.py', "
        f"'file.py:diagram' or 'file.json'.\n"
    )

    result = cli([
        "render",
        f"{module_path!s}:",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_render__module_with_ref__invalid_ref(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            d = SystemContextDiagram("Example")
            """
        ),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        "c4: error: Invalid target "
        "'module:'. "
        "Expected 'module', 'module:diagram', 'file.py', "
        "'file.py:diagram' or 'file.json'.\n"
    )

    result = cli(["render", "module:", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_render__absolute_file_path__multiple_diagrams(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram1 = SystemContextDiagram("Example 1")
            diagram2 = SystemContextDiagram("Example 2")
            """
        ),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        f"c4: error: Multiple diagrams found in '{module_path!s}': "
        f"diagram1, diagram2. "
        f"Either ensure the target contains exactly one Diagram, or "
        f"specify one explicitly as '{module_path!s}:<diagram_name>'.\n"
    )

    result = cli(["render", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_render__module__multiple_diagrams(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram1 = SystemContextDiagram("Example 1")
            diagram2 = SystemContextDiagram("Example 2")
            """
        ),
    )
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        "c4: error: Multiple diagrams found in module 'module': "
        "diagram1, diagram2. "
        "Either ensure the target contains exactly one Diagram, or "
        "specify one explicitly as 'module:<diagram_name>'.\n"
    )

    result = cli(["render", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_render__absolute_file_path__file_not_found(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file("module.py")
    module_path.unlink()
    expected_error = (
        "usage: c4 [-h] [-V] {render,export,convert} ...\n"
        f"c4: error: Python file not found: '{module_path!s}'.\n"
    )

    result = cli(["render", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


@pytest.mark.skipif(
    sys.version_info >= (3, 11),
    reason="Different traceback in Python 3.10",
)
def test_render__absolute_file_path__internal_import_error_310(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from not_existing_dependency import boom  # noqa: F401
            """
        ),
    )
    expected_error = textwrap.dedent(
        f"""
              File "{module_path}", line 2, in <module>
                from not_existing_dependency import boom  # noqa: F401
            ModuleNotFoundError: No module named 'not_existing_dependency'
            """
    )

    result = cli(["render", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Different traceback in Python 3.11+",
)
def test_render__absolute_file_path__internal_import_error(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from not_existing_dependency import boom  # noqa: F401
            """
        ),
    )
    expected_error = textwrap.dedent(
        f"""
              File "{module_path}", line 2, in <module>
                from not_existing_dependency import boom  # noqa: F401
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            ModuleNotFoundError: No module named 'not_existing_dependency'
            """
    )

    result = cli(["render", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


@pytest.mark.skipif(
    sys.version_info >= (3, 11),
    reason="Different traceback in Python 3.10",
)
def test_render__module__internal_import_error_310(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from not_existing_dependency import boom  # noqa: F401
            """
        ),
    )
    expected_error = textwrap.dedent(
        f"""
              File "{module_path}", line 2, in <module>
                from not_existing_dependency import boom  # noqa: F401
            ModuleNotFoundError: No module named 'not_existing_dependency'
        """
    )

    result = cli(["render", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Different traceback in Python 3.11+",
)
def test_render__module__internal_import_error(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from not_existing_dependency import boom  # noqa: F401
            """
        ),
    )
    expected_error = textwrap.dedent(
        f"""
              File "{module_path}", line 2, in <module>
                from not_existing_dependency import boom  # noqa: F401
                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
            ModuleNotFoundError: No module named 'not_existing_dependency'
        """
    )

    result = cli(["render", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_render__absolute_file_path__error_during_import(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            raise Exception("boom")
            """
        ),
    )
    expected_error = textwrap.dedent(
        f"""
              File "{module_path}", line 2, in <module>
                raise Exception("boom")
            Exception: boom
        """
    )

    result = cli(["render", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_render__module__error_during_import(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            raise Exception("boom")
            """
        ),
    )
    expected_error = textwrap.dedent(
        f"""
              File "{module_path}", line 2, in <module>
                raise Exception("boom")
            Exception: boom
        """
    )

    result = cli(["render", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_render_to_stdout(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli(["render", str(module_path)])

    assert result.exit_code == 0
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success.puml",
        diagram_code=result.stdout,
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_render_default_renderer_plantuml(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli(["render", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success.puml",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_render_provided_renderer_plantuml(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli([
        "render",
        str(module_path),
        "--renderer",
        "plantuml",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success.puml",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_render_shortcut_renderer_plantuml(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli([
        "render",
        str(module_path),
        "--plantuml",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success.puml",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason="Different traceback in Python 3.13+",
)
def test_render_unknown_renderer(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    module_path = make_tmp_py_file("module.py")
    module_path.unlink()
    expected_error = (
        "c4 render: error: argument --renderer: invalid choice: 'unknown' "
        "(choose from plantuml)"
    )

    result = cli(["render", str(module_path), "--renderer", "unknown"])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_render_mutually_exclusive_renderers(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    module_path = make_tmp_py_file("module.py")
    module_path.unlink()
    expected_error = (
        "c4 render: error: argument --plantuml: not "
        "allowed with argument --renderer\n"
    )

    result = cli([
        "render",
        str(module_path),
        "--renderer",
        "plantuml",
        "--plantuml",
    ])

    assert result.exit_code == 2
    print(result.stdout)
    assert not result.stdout
    assert expected_error in result.stderr


def test_render_output_file_path_is_directory(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
    pytester: pytest.Pytester,
    tmp_path: Path,
):
    diagram_output = tmp_path / "diagram" / "result.txt"
    diagram_output.parent.mkdir()
    output_dir = diagram_output.parent
    module_path = make_tmp_py_file("module.py")
    expected_error = (
        "c4 render: error: argument -o/--output: Output path "
        f"'{output_dir}' is a directory, expected a file path.\n"
    )

    result = cli([
        "render",
        str(module_path),
        "-o",
        str(output_dir),
    ])

    assert result.exit_code == 2
    print(result.stdout)
    assert not result.stdout
    assert expected_error in result.stderr


def test_render_output_file_path_parent_does_not_exist(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
    pytester: pytest.Pytester,
    tmp_path: Path,
):
    diagram_output = tmp_path / "diagram" / "result.txt"
    output_dir = diagram_output.parent
    module_path = make_tmp_py_file("module.py")
    expected_error = (
        "c4 render: error: argument -o/--output: Directory "
        f"'{output_dir}' does not exist.\n"
    )

    result = cli([
        "render",
        str(module_path),
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    print(result.stdout)
    assert not result.stdout
    assert expected_error in result.stderr


def test_render__use_new_c4_style(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.puml"
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = cli([
        "render",
        "module",
        "--plantuml-use-new-c4-style",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot_name="test_render_success_new_c4_style.puml",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )

import sys
import textwrap
from pathlib import Path

import pytest

from tests.conftest import AssertMatchSnapshot, MakeTmpPyFile
from tests.test_integration.test_cli.conftest import CLI

pytestmark = [pytest.mark.usefixtures("clean_sys_modules")]


SNAPSHOT_DIR = Path(__file__).parent / "snapshots"


def test_export__absolute_file_path__success(
    tmp_path: Path,
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    diagram_output = tmp_path / "diagram.txt"
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        str(module_path),
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_export__module__success(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        "module",
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_export__absolute_file_path_with_ref__success(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        f"{module_path!s}:diagram",
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_export__module_with_ref__success(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        "module:diagram",
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_export__absolute_file_path__diagram_not_found(
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

    result = cli(["export", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_export__module__diagram_not_found(
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

    result = cli(["export", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_export__absolute_file_path_with_ref__diagram_not_found(
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
        "export",
        f"{module_path!s}:diagram",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_export__module_with_ref__diagram_not_found(
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

    result = cli(["export", "module:diagram", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_export__absolute_file_path_with_ref__invalid_ref(
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
        "export",
        f"{module_path!s}:",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_export__module_with_ref__invalid_ref(
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

    result = cli(["export", "module:", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_export__absolute_file_path__multiple_diagrams(
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

    result = cli(["export", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_export__module__multiple_diagrams(
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

    result = cli(["export", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


def test_export__absolute_file_path__file_not_found(
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

    result = cli(["export", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert result.stderr == expected_error


@pytest.mark.skipif(
    sys.version_info >= (3, 11),
    reason="Different traceback in Python 3.10",
)
def test_export__absolute_file_path__internal_import_error_310(
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

    result = cli(["export", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Different traceback in Python 3.11+",
)
def test_export__absolute_file_path__internal_import_error(
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

    result = cli(["export", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


@pytest.mark.skipif(
    sys.version_info >= (3, 11),
    reason="Different traceback in Python 3.10",
)
def test_export__module__internal_import_error_310(
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

    result = cli(["export", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


@pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Different traceback in Python 3.11+",
)
def test_export__module__internal_import_error(
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

    result = cli(["export", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_export__absolute_file_path__error_during_import(
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

    result = cli(["export", str(module_path), "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_export__module__error_during_import(
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

    result = cli(["export", "module", "-o", str(diagram_output)])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_to_stdout(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        str(module_path),
        "-f",
        "txt",
        "--timeout",
        "60",
    ])

    assert result.exit_code == 0
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=result.stdout,
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_export_default_renderer_plantuml(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        str(module_path),
        "-f",
        "txt",
        "-o",
        str(diagram_output),
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


def test_export_provided_renderer_plantuml(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        str(module_path),
        "--renderer",
        "plantuml",
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason="Different traceback in Python 3.13+",
)
def test_export_plantuml_invalid_format(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )
    expected_error = (
        "c4 export: error: argument -f/--format: invalid choice: 'unknown' "
        "(choose from eps, latex, png, svg, txt, utxt)\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--plantuml",
        "-f",
        "unknown",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_plantuml_invalid_plantuml_bin(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example") as diagram:
                ...
            """
        ),
    )
    expected_error = (
        "c4 export: error: argument --plantuml-bin: PlantUML binary "
        "'binary-does-not-exist' was not found in PATH "
        "or is not executable.\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--plantuml",
        "--plantuml-bin",
        "binary-does-not-exist",
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_plantuml_plantuml_jar_does_not_exist(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example") as diagram:
                ...
            """
        ),
    )
    expected_error = (
        "c4 export: error: argument --plantuml-jar: PlantUML jar "
        "file does not exist: 'does-not-exist.jar'.\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--plantuml",
        "--plantuml-jar",
        "does-not-exist.jar",
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_plantuml_plantuml_jar_is_not_a_file(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example") as diagram:
                ...
            """
        ),
    )
    expected_error = (
        "c4 export: error: argument --plantuml-jar: PlantUML jar "
        f"path is not a file: '{tmp_path}'.\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--plantuml",
        "--plantuml-jar",
        str(tmp_path),
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_shortcut_renderer_plantuml(
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
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        str(module_path),
        "--plantuml",
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 0
    assert not result.stdout
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=diagram_output.read_text(),
        snapshot_dir=SNAPSHOT_DIR,
    )


@pytest.mark.skipif(
    sys.version_info < (3, 13),
    reason="Different traceback in Python 3.13+",
)
def test_export_unknown_renderer(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    module_path = make_tmp_py_file("module.py")
    module_path.unlink()
    expected_error = (
        "c4 export: error: argument --renderer: invalid choice: 'unknown' "
        "(choose from plantuml)\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--renderer",
        "unknown",
        "-f",
        "txt",
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_mutually_exclusive_renderers(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    module_path = make_tmp_py_file("module.py")
    module_path.unlink()
    expected_error = (
        "c4 export: error: argument --plantuml: not "
        "allowed with argument --renderer\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--renderer",
        "plantuml",
        "--plantuml",
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    print(result.stdout)
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_mutually_exclusive_plantuml_flags(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
    pytester: pytest.Pytester,
):
    module_path = make_tmp_py_file("module.py")
    fake_plantuml_jar = pytester.makefile(".jar", lines=[""])
    expected_error = (
        "c4 export: error: argument --plantuml-jar: not allowed with "
        "argument --plantuml-bin\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--renderer",
        "plantuml",
        "--plantuml-bin",
        "plantuml",
        "--plantuml-jar",
        str(fake_plantuml_jar),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    print(result.stdout)
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_output_file_path_is_directory(
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
        "c4 export: error: argument -o/--output: Output path "
        f"'{output_dir}' is a directory, expected a file path.\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--plantuml",
        "-f",
        "txt",
        "-o",
        str(output_dir),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    print(result.stdout)
    assert not result.stdout
    assert expected_error in result.stderr


def test_export_output_file_path_parent_does_not_exist(
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
        "c4 export: error: argument -o/--output: Directory "
        f"'{output_dir}' does not exist.\n"
    )

    result = cli([
        "export",
        str(module_path),
        "--plantuml",
        "-f",
        "txt",
        "-o",
        str(diagram_output),
        "--timeout",
        "60",
    ])

    assert result.exit_code == 2
    print(result.stdout)
    assert not result.stdout
    assert expected_error in result.stderr


def test_export__use_new_c4_style(
    make_tmp_py_file: MakeTmpPyFile,
    cli: CLI,
    assert_match_snapshot: AssertMatchSnapshot,
):
    module_path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import Person, Rel, System, SystemContextDiagram

            with SystemContextDiagram("Example system context") as diagram:
                user = Person(label="User", description="System user")
                backend = System(label="Backend API", description="Main application backend")

                user >> Rel("Uses HTTP API") >> backend
            """
        ),
    )

    result = cli([
        "export",
        str(module_path),
        "--plantuml-use-new-c4-style",
        "-f",
        "txt",
        "--timeout",
        "60",
    ])

    assert result.exit_code == 0
    assert not result.stderr
    assert_match_snapshot(
        snapshot="test_export_success.txt",
        diagram_code=result.stdout,
        snapshot_dir=SNAPSHOT_DIR,
    )

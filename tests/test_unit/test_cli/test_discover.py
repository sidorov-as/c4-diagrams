import os
import re
import sys
import textwrap
from pathlib import Path
from types import ModuleType

import pytest
from pytest_mock import MockerFixture

import c4.cli.discover as discover
from c4 import Person, SystemContextDiagram
from c4.cli.discover import Target
from c4.cli.exceptions import (
    DiagramNotFoundError,
    ImportFromStringError,
    MissingConverterDependency,
    MultipleDiagramsFoundError,
    TargetParseError,
)
from c4.diagrams.core import Diagram
from tests.conftest import MakeTmpPyFile

pytestmark = [pytest.mark.usefixtures("clean_sys_modules")]


def test__import_module_or_raise_success(
    make_tmp_py_file: MakeTmpPyFile,
):
    module = make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram = SystemContextDiagram("Example")
            """
        ),
    )

    result = discover._import_module_or_raise("diagram")

    assert isinstance(result, ModuleType)
    assert result.__spec__.origin == str(module)
    assert result.__spec__.name == "diagram"
    assert isinstance(result.diagram, SystemContextDiagram)
    assert result.diagram.title == "Example"


def test__import_module_or_raise_import_error_unknown_module():
    expected_error = re.escape(
        "Could not import module 'missing'. "
        "Make sure it is installed and importable "
        "(check PYTHONPATH / working directory)."
    )

    with pytest.raises(ImportFromStringError, match=expected_error):
        discover._import_module_or_raise("missing")


def test__import_module_or_raise_import_error_unknown_submodule(
    make_tmp_py_file: MakeTmpPyFile,
):
    expected_error = re.escape(
        "Could not import module 'missing.module'. "
        "Make sure it is installed and importable "
        "(check PYTHONPATH / working directory)."
    )
    make_tmp_py_file("missing.py")

    with pytest.raises(ImportFromStringError, match=expected_error):
        discover._import_module_or_raise("missing.module")


def test__import_module_or_raise_import_error_unknown_nested_submodule(
    make_tmp_py_file: MakeTmpPyFile,
):
    expected_error = re.escape(
        "No module named 'missing.module'; 'missing' is not a package"
    )
    make_tmp_py_file("missing.py")

    with pytest.raises(ModuleNotFoundError, match=expected_error):
        discover._import_module_or_raise("missing.module.nested")


def test__import_module_or_raise_import_error_internal_error(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            raise Exception("boom")
            """
        ),
    )

    with pytest.raises(Exception, match="boom"):
        discover._import_module_or_raise("diagram")


def test__resolve_dotted_attribute_success():
    class Root:
        class A:
            class B:
                value = 123

        a = A()

    result = discover._resolve_dotted_attribute(Root(), "a.B.value")

    assert result == 123


def test__resolve_dotted_attribute_missing_raises():
    class Root:
        pass

    with pytest.raises(AttributeError):
        discover._resolve_dotted_attribute(Root(), "a.b")


def test__resolve_diagram_ref_success():
    module = ModuleType("m")
    module.diagram = Diagram()
    target = Target(module_or_file="m", object_ref="diagram", is_py_file=False)

    result = discover._resolve_diagram_ref(
        target,
        module,
    )

    assert result is module.diagram


def test__resolve_diagram_ref_no_object_ref_error():
    module = ModuleType("m")
    module.diagram = Diagram()
    target = Target(module_or_file="m", object_ref="", is_py_file=False)

    with pytest.raises(ValueError, match="Diagram reference not provided"):
        discover._resolve_diagram_ref(
            target,
            module,
        )


@pytest.mark.parametrize(
    ("attr_path",),
    [
        ("missing",),
        ("a.b.c",),
    ],
)
def test__resolve_diagram_ref_missing_raises_module(attr_path: str):
    module = ModuleType("m")
    module.diagram = Diagram()
    target = Target(module_or_file="m", object_ref=attr_path, is_py_file=False)
    expected_error = (
        f"Diagram reference '{attr_path}' was not found in module 'm'."
    )

    with pytest.raises(DiagramNotFoundError, match=expected_error):
        discover._resolve_diagram_ref(target, module)


@pytest.mark.parametrize(
    ("attr_path",),
    [
        ("missing",),
        ("a.b.c",),
    ],
)
def test__resolve_diagram_ref_missing_raises_file(attr_path: str):
    module = ModuleType("")
    module.__file__ = "/path/to/diagram.py"
    module.diagram = Diagram()
    target = Target(
        module_or_file="/path/to/diagram.py",
        object_ref=attr_path,
        is_py_file=True,
    )
    expected_error = (
        f"Diagram reference '{attr_path}' was not found "
        f"in '/path/to/diagram.py'."
    )

    with pytest.raises(DiagramNotFoundError, match=expected_error):
        discover._resolve_diagram_ref(target, module)


def test__resolve_diagram_ref_wrong_type_raises_module():
    module = ModuleType("m")
    module.not_diagram = object()
    target = Target(
        module_or_file="m", object_ref="not_diagram", is_py_file=False
    )
    expected_error = (
        "Reference 'not_diagram' in module 'm' must be a "
        "Diagram instance; got object."
    )

    with pytest.raises(ImportFromStringError, match=expected_error):
        discover._resolve_diagram_ref(target, module)


def test__resolve_diagram_ref_wrong_type_raises_file():
    module = ModuleType("")
    module.__file__ = "/path/to/diagram.py"
    module.not_diagram = object()
    target = Target(
        module_or_file="/path/to/diagram.py",
        object_ref="not_diagram",
        is_py_file=True,
    )
    expected_error = (
        "Reference 'not_diagram' in '/path/to/diagram.py' must be a "
        "Diagram instance; got object."
    )

    with pytest.raises(ImportFromStringError, match=expected_error):
        discover._resolve_diagram_ref(target, module)


def test__load_module_from_file_path_not_exists_raises(tmp_path: Path):
    file_path = tmp_path / "missing.py"

    expected_error = re.escape(f"Python file not found: {str(file_path)!r}.")

    with pytest.raises(ImportFromStringError, match=expected_error):
        discover._load_module_from_file(str(file_path))


def test__load_module_from_file_path_is_dir_raises(tmp_path: Path):
    dir_path = tmp_path / "as_dir"
    dir_path.mkdir()

    expected_error = re.escape(f"Path is not a file: {str(dir_path)!r}.")

    with pytest.raises(ImportFromStringError, match=expected_error):
        discover._load_module_from_file(str(dir_path))


def test__load_module_from_file_spec_is_none_raises(
    tmp_path: Path,
    mocker: MockerFixture,
):
    file_path = tmp_path / "m.py"
    file_path.write_text("x = 1\n", encoding="utf-8")
    abs_path = os.path.abspath(str(file_path))
    mocked_spec_from_file_location = mocker.patch(
        "importlib.util.spec_from_file_location",
        autospec=True,
        return_value=None,
    )
    expected_error = re.escape(
        f"Could not load Python file as a module: {abs_path!r}."
    )

    with pytest.raises(ImportFromStringError, match=expected_error):
        discover._load_module_from_file(str(file_path))

    mocked_spec_from_file_location.assert_called_once()


def test__load_module_from_file_module_from_spec_error_raises(
    tmp_path: Path,
    mocker: MockerFixture,
):
    file_path = tmp_path / "m.py"
    file_path.write_text("x = 1\n", encoding="utf-8")
    loader = mocker.Mock()
    loader.exec_module = mocker.Mock()
    spec = mocker.Mock()
    spec.loader = loader
    mocked_spec_from_file_location = mocker.patch(
        "importlib.util.spec_from_file_location",
        autospec=True,
        return_value=spec,
    )
    mocked_module_from_spec = mocker.patch(
        "importlib.util.module_from_spec",
        autospec=True,
        side_effect=RuntimeError("boom"),
    )

    with pytest.raises(RuntimeError, match="boom"):
        discover._load_module_from_file(str(file_path))

    mocked_spec_from_file_location.assert_called_once()
    mocked_module_from_spec.assert_called_once_with(spec)


def test__load_module_from_file_exec_module_error_raises(
    tmp_path: Path,
    mocker: MockerFixture,
):
    file_path = tmp_path / "m.py"
    file_path.write_text("x = 1\n", encoding="utf-8")
    loader = mocker.Mock()
    loader.exec_module.side_effect = RuntimeError("boom")
    spec = mocker.Mock()
    spec.loader = loader
    mocker.patch(
        "importlib.util.spec_from_file_location",
        autospec=True,
        return_value=spec,
    )
    module = ModuleType("_x")
    mocker.patch(
        "importlib.util.module_from_spec",
        autospec=True,
        return_value=module,
    )

    with pytest.raises(RuntimeError, match="boom"):
        discover._load_module_from_file(str(file_path))


def test__load_module_from_file_success_loads_module(tmp_path: Path):
    file_path = tmp_path / "m.py"
    file_path.write_text("value = 123\n", encoding="utf-8")

    module = discover._load_module_from_file(str(file_path))

    assert isinstance(module, ModuleType)
    assert module.value == 123


def test__load_module_from_file_modified_sys_path(tmp_path: Path) -> None:
    """
    Regression test for issue https://github.com/sidorov-as/c4-diagrams/issues/23
    """
    common_c4 = tmp_path / "common_c4" / "__init__.py"
    common_c4.parent.mkdir()
    common_c4.write_text(
        textwrap.dedent(
            """
            from functools import partial

            from c4 import System, Person

            Backend = partial(System, label="Backend")
            User = partial(Person, label="User")
            WebApp = partial(System, label="Web Application")
            """
        )
    )
    file_path = tmp_path / "diagram.py"
    file_path.write_text(
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            from common_c4 import Backend, User, WebApp


            with SystemContextDiagram() as diagram:
                user = User()
                web_app = WebApp()
                backend = Backend()

                user >> "Interacts with" >> web_app
                web_app >> "Sends requests to" >> backend
            """
        )
    )

    module = discover._load_module_from_file(str(file_path))

    assert isinstance(module, ModuleType)
    assert isinstance(module.diagram, SystemContextDiagram)
    assert isinstance(module.user, Person)
    assert module.user.label == "User"


def test__load_module_from_file_loads_related_modules(tmp_path: Path):
    file_path = tmp_path / "diagram.py"
    file_path.write_text("value = 123\n", encoding="utf-8")

    module = discover._load_module_from_file(str(file_path))

    assert isinstance(module, ModuleType)
    assert module.value == 123


def test__list_diagram_globals_filters_and_sorts(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            diagram2 = SystemContextDiagram("Example 2")
            diagram3 = object()  # not a diagram

            with SystemContextDiagram("Example 1") as _diagram1:
                ...
            """
        ),
    )
    module = discover._import_module_or_raise("diagram")

    result = discover._list_diagram_globals(module)

    assert result == ["_diagram1", "diagram2"]


def test__get_single_diagram_from_module_single_returns_instance(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            with SystemContextDiagram("Example") as diagram1:
                ...
            """
        ),
    )
    module = discover._import_module_or_raise("diagram")
    target = Target(module_or_file="diagram", object_ref=None, is_py_file=False)

    result = discover._get_single_diagram_from_module(target, module)

    assert result is module.diagram1


def test__get_single_diagram_from_module_none_raises_module(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram
            """
        ),
    )
    module = discover._import_module_or_raise("diagram")
    target = Target(module_or_file="diagram", object_ref=None, is_py_file=False)
    expected_error = (
        "No Diagram instances found in module 'diagram'. "
        "Define a Diagram at module level or "
        "specify one explicitly as '<target>:<name>'."
    )

    with pytest.raises(DiagramNotFoundError, match=expected_error):
        discover._get_single_diagram_from_module(target, module)


def test__get_single_diagram_from_module_none_raises_file(
    make_tmp_py_file: MakeTmpPyFile,
):
    module_path = make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram
            """
        ),
    )
    module = discover._import_module_or_raise("diagram")
    target = Target(
        module_or_file="diagram.py", object_ref=None, is_py_file=True
    )
    expected_error = (
        f"No Diagram instances found in {str(module_path)!r}. "
        "Define a Diagram at module level or "
        "specify one explicitly as '<target>:<name>'."
    )

    with pytest.raises(DiagramNotFoundError, match=expected_error):
        discover._get_single_diagram_from_module(target, module)


def test__get_single_diagram_from_module_multiple_raises_module(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            with SystemContextDiagram("Example 1") as diagram1:
                ...

            diagram2 = SystemContextDiagram("Example 2")
            """
        ),
    )
    module = discover._import_module_or_raise("diagram")
    target = Target(module_or_file="diagram", object_ref=None, is_py_file=False)
    expected_error = (
        "Multiple diagrams found in module 'diagram': diagram1, diagram2. "
        "Either ensure the target contains exactly one Diagram, "
        "or specify one explicitly as 'diagram:<diagram_name>'."
    )

    with pytest.raises(MultipleDiagramsFoundError, match=expected_error):
        discover._get_single_diagram_from_module(target, module)


def test__get_single_diagram_from_module_multiple_raises_file(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            with SystemContextDiagram("Example 1") as diagram1:
                ...

            diagram2 = SystemContextDiagram("Example 2")
            """
        ),
    )
    module = discover._import_module_or_raise("diagram")
    target = Target(
        module_or_file="diagram.py", object_ref=None, is_py_file=True
    )
    expected_error = (
        "Multiple diagrams found in 'diagram.py': diagram1, diagram2. "
        "Either ensure the target contains exactly one Diagram, "
        "or specify one explicitly as 'diagram.py:<diagram_name>'."
    )

    with pytest.raises(MultipleDiagramsFoundError, match=expected_error):
        discover._get_single_diagram_from_module(target, module)


def test__load_target_module(
    mocker: MockerFixture,
):
    mocked_load_module_from_file = mocker.patch.object(
        discover, "_load_module_from_file"
    )
    mocked_import_module_or_raise = mocker.patch.object(
        discover, "_import_module_or_raise"
    )
    target = Target(module_or_file="diagram", object_ref=None, is_py_file=False)

    result = discover._load_target_module(target)

    assert result == mocked_import_module_or_raise.return_value
    mocked_load_module_from_file.assert_not_called()
    mocked_import_module_or_raise.assert_called_once_with("diagram")


def test__load_target_module_is_file(
    mocker: MockerFixture,
):
    mocked_load_module_from_file = mocker.patch.object(
        discover, "_load_module_from_file"
    )
    mocked_import_module_or_raise = mocker.patch.object(
        discover, "_import_module_or_raise"
    )
    target = Target(
        module_or_file="diagram.py", object_ref=None, is_py_file=True
    )

    result = discover._load_target_module(target)

    assert result == mocked_load_module_from_file.return_value
    mocked_load_module_from_file.assert_called_once_with("diagram.py")
    mocked_import_module_or_raise.assert_not_called()


@pytest.mark.parametrize(
    (
        "raw",
        "expected_module_or_file",
        "expected_object_ref",
        "expected_is_py_file",
        "expected_is_json_file",
    ),
    [
        (
            "python.module",
            "python.module",
            None,
            False,
            False,
        ),
        (
            " python.module ",
            "python.module",
            None,
            False,
            False,
        ),
        (
            "python.module:diagram",
            "python.module",
            "diagram",
            False,
            False,
        ),
        (
            " python.module:diagram ",
            "python.module",
            "diagram",
            False,
            False,
        ),
        (
            "file.py",
            "file.py",
            None,
            True,
            False,
        ),
        (
            " file.py ",
            "file.py",
            None,
            True,
            False,
        ),
        (
            "file.py:a.b.c",
            "file.py",
            "a.b.c",
            True,
            False,
        ),
        (
            " file.py : a.b.c ",
            "file.py",
            "a.b.c",
            True,
            False,
        ),
        (
            "file.json",
            "file.json",
            None,
            False,
            True,
        ),
        (
            " file.json ",
            "file.json",
            None,
            False,
            True,
        ),
    ],
    ids=[
        "module",
        "module_strip",
        "module_with_object_ref",
        "module_with_object_ref_strip",
        "file",
        "file_strip",
        "file_with_object_ref",
        "file_with_object_ref_strip",
        "file_json",
        "file_json_strip",
    ],
)
def test__parse_target_success(
    raw: str,
    expected_module_or_file: str,
    expected_object_ref: str,
    expected_is_py_file: bool,
    expected_is_json_file: bool,
):
    target = discover._parse_target(raw)

    assert target.module_or_file == expected_module_or_file
    assert target.object_ref == expected_object_ref
    assert target.is_py_file == expected_is_py_file
    assert target.is_json_file == expected_is_json_file


@pytest.mark.parametrize(
    ("raw",),
    [
        ("",),
        ("   ",),
        (":x",),
        ("x:",),
        ("x:  ",),
        ("  :  ",),
    ],
    ids=[
        "empty",
        "whitespaces",
        "no_module_or_file",
        "no_object_ref",
        "no_object_ref_whitespace",
        "no_module_and_object_ref",
    ],
)
def test__parse_target_invalid_raises(raw: str):
    with pytest.raises(TargetParseError):
        discover._parse_target(raw)


def test_resolve_diagram_module_target_single_autodetect(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "diagram.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            with SystemContextDiagram("Example") as diagram:
                ...
            """
        ),
    )

    result = discover.resolve_diagram("diagram")

    assert isinstance(result, Diagram)
    assert result.title == "Example"


def test_resolve_diagram_module_target_explicit_ref(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            with SystemContextDiagram("Example") as diagram:
                ...
            """
        ),
    )

    result = discover.resolve_diagram("module:diagram")

    assert isinstance(result, Diagram)
    assert result.title == "Example"


def test_resolve_diagram_module_target_dotted_ref(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            class Nested:
                diagram = SystemContextDiagram("Example")

            nested = Nested()
            """
        ),
    )

    result = discover.resolve_diagram("module:nested.diagram")

    assert isinstance(result, Diagram)
    assert result.title == "Example"


def test_resolve_diagram_module_target_no_diagrams_raises(
    make_tmp_py_file: MakeTmpPyFile,
):
    make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            x = 123
            """
        ),
    )

    with pytest.raises(DiagramNotFoundError):
        discover.resolve_diagram("module")


def test_resolve_diagram_module_target_multiple_diagrams_raises(
    make_tmp_py_file: MakeTmpPyFile,
):
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

    with pytest.raises(MultipleDiagramsFoundError):
        discover.resolve_diagram("module")


def test_resolve_diagram_file_target_single_autodetect(
    make_tmp_py_file: MakeTmpPyFile,
):
    file_path: Path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            with SystemContextDiagram("Example") as diagram:
                ...
            """
        ),
    )

    result = discover.resolve_diagram(file_path)

    assert isinstance(result, Diagram)
    assert result.title == "Example"


def test_resolve_diagram_file_target_explicit_ref(
    make_tmp_py_file: MakeTmpPyFile,
):
    file_path: Path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            from c4 import SystemContextDiagram

            with SystemContextDiagram("Example") as diagram:
                ...
            """
        ),
    )

    result = discover.resolve_diagram(f"{file_path}:diagram")

    assert isinstance(result, Diagram)
    assert result.title == "Example"


def test_resolve_diagram_file_target_missing_file_raises(
    tmp_path: Path,
):
    file_path = tmp_path / "missing.py"

    with pytest.raises(ImportFromStringError):
        discover.resolve_diagram(file_path)


def test_resolve_diagram_file_target_exec_error_raises(
    make_tmp_py_file: MakeTmpPyFile,
):
    file_path: Path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            raise RuntimeError('boom')
            """
        ),
    )

    with pytest.raises(RuntimeError, match="boom"):
        discover.resolve_diagram(file_path)


def test_resolve_diagram_file_target_ref_wrong_type_raises(
    make_tmp_py_file: MakeTmpPyFile,
):
    file_path: Path = make_tmp_py_file(
        "module.py",
        textwrap.dedent(
            """
            diagram = object()
            """
        ),
    )

    with pytest.raises(ImportFromStringError):
        discover.resolve_diagram(f"{file_path}:diagram")


def test_resolve_diagram__json_target(
    tmp_path: Path,
):
    file_path = tmp_path / "diagram.json"
    file_path.write_text(
        """
        {"type": "SystemContextDiagram", "title": "Example"}
        """
    )

    result = discover.resolve_diagram(file_path)

    assert isinstance(result, Diagram)
    assert result.title == "Example"


def test_resolve_diagram__json_target__missing_dependencies(
    mocker: MockerFixture,
    tmp_path: Path,
):
    # to prevent caching in _import_json_converter
    sys.modules.pop("c4.converters.json.converter", None)
    file_path = tmp_path / "diagram.json"
    mocker.patch.dict("sys.modules", {"pydantic": None})

    with pytest.raises(MissingConverterDependency):
        discover.resolve_diagram(file_path)


def test_resolve_diagram__json_target__diagram_file_not_found(
    tmp_path: Path,
):
    file_path = tmp_path / "diagram.json"
    expected_error = f"Diagram file not found: {file_path!s}"

    with pytest.raises(ImportFromStringError, match=expected_error):
        discover.resolve_diagram(file_path)

    assert not file_path.exists()

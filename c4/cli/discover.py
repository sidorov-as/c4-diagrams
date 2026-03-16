from __future__ import annotations

import importlib
import importlib.util
import os
import typing
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import IO, TYPE_CHECKING, Any, Protocol
from uuid import uuid4

from c4.cli.exceptions import (
    DiagramNotFoundError,
    ImportFromStringError,
    MissingConverterDependency,
    MultipleDiagramsFoundError,
    TargetParseError,
)
from c4.diagrams.core import Diagram

if TYPE_CHECKING:  # pragma: no cover

    class DiagramFromJson(Protocol):
        def __call__(
            self, src: str | bytes | Path | IO[str] | IO[bytes]
        ) -> Diagram: ...


@dataclass(frozen=True)
class Target:
    """
    Parsed CLI target in the form:

    - "python.module"
    - "python.module:diagram"
    - "file.py"
    - "file.py:diagram" (or dotted: "file.py:a.b.c")
    - "file.json"

    Attributes:
        module_or_file: Module path ("python.module") or file path ("file.py").
        object_ref: Optional attribute reference (name or dotted path).
        is_py_file: True if the target points to a .py file.
        is_json_file: True if the target points to a .json file.
    """

    module_or_file: str  # "file.json", "file.py" or "python.module"
    object_ref: str | None
    is_py_file: bool = False
    is_json_file: bool = False


def _import_module_or_raise(module_str: str) -> ModuleType:
    """
    Import a module by dotted name.

    This intentionally does not mask ImportError raised *from inside* the
    imported module (e.g., missing dependency), so stack traces remain useful.

    Args:
        module_str: Dotted module path.

    Returns:
        Imported module.

    Raises:
        ImportFromStringError: If the module itself cannot be imported.
        ImportError: If the module is found but fails due to
            an internal ImportError.
    """
    try:
        return importlib.import_module(module_str)
    except ModuleNotFoundError as exc:
        if exc.name != module_str:
            # Import errors are written to stderr.
            raise

        raise ImportFromStringError(
            f"Could not import module {module_str!r}. "
            "Make sure it is installed and importable "
            "(check PYTHONPATH / working directory)."
        ) from exc


def _resolve_dotted_attribute(root: Any, dotted_path: str) -> Any:
    """
    Resolve a dotted attribute path from a root object.

    Example:
        _resolve_dotted_attribute(module, "a.b.c") resolves module.a.b.c.

    Args:
        root: Root object to start from (usually a module).
        dotted_path: Dotted attribute path.

    Returns:
        Resolved attribute value.

    Raises:
        AttributeError: If any segment in the path is missing.
    """
    current = root
    for part in dotted_path.split("."):
        current = getattr(current, part)
    return current


def _resolve_diagram_ref(
    target: Target,
    module: ModuleType,
) -> Diagram:
    """
    Resolve a dotted attribute path inside a module and
    validate it's a Diagram.

    Args:
        target: Parsed target with provided object_ref.
        module: Loaded/imported module.

    Returns:
        Diagram instance.

    Raises:
        DiagramNotFoundError: If the attribute path does not exist.
        ImportFromStringError: If the resolved object is
            not a Diagram instance.
    """
    if not target.object_ref:
        raise ValueError("Diagram reference not provided")

    dotted_path = target.object_ref

    if target.is_py_file:
        module_repr = f"{str(module.__file__)!r}"
    else:
        module_repr = f"module {module.__name__!r}"

    try:
        value = _resolve_dotted_attribute(module, dotted_path)
    except AttributeError as exc:
        raise DiagramNotFoundError(
            f"Diagram reference {dotted_path!r} was not found in {module_repr}."
        ) from exc

    if not isinstance(value, Diagram):
        raise ImportFromStringError(
            f"Reference {dotted_path!r} in {module_repr} must be "
            f"a Diagram instance; got {type(value).__name__}."
        )

    return value


def _load_module_from_file(filepath: str) -> ModuleType:
    """
    Load a Python file as an importable module.

    A unique temporary module name is generated to avoid collisions.

    Args:
        filepath: Path to a Python file.

    Returns:
        Loaded module object.

    Raises:
        ImportFromStringError: If the file does not exist
            or cannot be executed.
    """
    filepath = os.path.abspath(filepath)
    if not os.path.exists(filepath):
        raise ImportFromStringError(f"Python file not found: {filepath!r}.")
    if not os.path.isfile(filepath):
        raise ImportFromStringError(f"Path is not a file: {filepath!r}.")

    suffix = uuid4().hex[:4]
    module_name = f"_c4_file_{suffix}"
    spec = importlib.util.spec_from_file_location(module_name, filepath)
    if spec is None or spec.loader is None:
        raise ImportFromStringError(
            f"Could not load Python file as a module: {filepath!r}."
        )

    # Import errors are written to stderr.
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def _list_diagram_globals(module: ModuleType) -> list[str]:
    """
    List module-level globals that are Diagram instances.

    Args:
        module: Module to inspect.

    Returns:
        Sorted list of names referencing Diagram instances.
    """
    names: list[str] = []
    for name, value in vars(module).items():
        if isinstance(value, Diagram):
            names.append(name)
    return sorted(names)


def _get_single_diagram_from_module(
    target: Target,
    module: ModuleType,
) -> Diagram:
    """
    Auto-detect a single module-level Diagram instance.

    This is used when the target does not specify an explicit
    object reference.

    Args:
        target: Parsed target.
        module: Loaded/imported module.

    Returns:
        The single Diagram instance found at module level.

    Raises:
        DiagramNotFoundError: If no Diagram instances are found.
        MultipleDiagramsFoundError: If more than one
            Diagram instance is found.
    """
    diagram_names = _list_diagram_globals(module)

    if target.is_py_file:
        module_repr = f"{str(module.__file__)!r}"
    else:
        module_repr = f"module {module.__name__!r}"

    if not diagram_names:
        raise DiagramNotFoundError(
            f"No Diagram instances found in {module_repr}. "
            "Define a Diagram at module level or "
            "specify one explicitly as '<target>:<name>'."
        )

    if len(diagram_names) > 1:
        raise MultipleDiagramsFoundError(target, diagram_names)

    diagram = getattr(module, diagram_names[0])

    return typing.cast(Diagram, diagram)


def _load_target_module(target: Target) -> ModuleType:
    """
    Load a module for a parsed target.

    - For file targets: executes the file as a module.
    - For module targets: imports the module by name.

    Args:
        target: Parsed target.

    Returns:
        Loaded/imported module.
    """
    if target.is_py_file:
        return _load_module_from_file(target.module_or_file)

    return _import_module_or_raise(target.module_or_file)


def _parse_target(raw: str | Path) -> Target:
    """
    Parse a raw CLI target string into a Target object.

    Accepted forms:
        - "python.module"
        - "python.module:diagram" (dotted paths allowed)
        - "file.py"
        - "file.py:diagram" (dotted paths allowed)

    Whitespace around parts is ignored.

    Args:
        raw: Raw target string.

    Returns:
        Parsed Target.

    Raises:
        TargetParseError: If the target is empty or malformed.
    """
    raw = str(raw).strip()
    if not raw:
        raise TargetParseError(raw)

    if ":" in raw:
        module_or_file, object_ref = raw.split(":", 1)
        module_or_file = module_or_file.strip()
        object_ref = object_ref.strip()
        if not module_or_file or not object_ref:
            raise TargetParseError(raw)
    else:
        module_or_file, object_ref = raw, None

    return Target(
        module_or_file=module_or_file,
        object_ref=object_ref,
        is_py_file=module_or_file.endswith(".py"),
        is_json_file=module_or_file.endswith(".json"),
    )


def _import_json_converter() -> DiagramFromJson | None:
    try:
        from c4.converters.json.converter import diagram_from_json
    except ImportError:
        return None

    return diagram_from_json


def resolve_diagram(raw_target: str | Path) -> Diagram:
    """
    Resolve a Diagram instance from a CLI target string.

    Behavior:
        - If "<target>:<object_ref>" is provided:
            * Load/import the module and resolve <object_ref> as
              a dotted attribute.
            * Validate that the resolved value is a Diagram instance.
        - If "<object_ref>" is not provided:
            * Load/import the module and auto-detect exactly one
              module-level Diagram.

    Args:
        raw_target: Target string ("file.py", "file.py:diagram",
            "python.module", "python.module:diagram").

    Returns:
        Resolved Diagram instance.

    Raises:
        TargetParseError: If the target string is malformed.
        ImportFromStringError: If the module/file cannot be imported
            or the ref is not a Diagram.
        DiagramNotFoundError: If the requested diagram is missing
            (or no diagrams exist).
        MultipleDiagramsFoundError: If auto-detection finds more than
            one diagram.
        MissingConverterDependency: If converter dependencies
            are not installed.
    """
    target = _parse_target(raw_target)
    if target.is_json_file:
        diagram_from_json = _import_json_converter()
        if diagram_from_json is None:
            raise MissingConverterDependency()

        json_file = Path(raw_target)
        if not json_file.exists():
            raise ImportFromStringError(
                f"Diagram file not found: {json_file!s}."
            )

        return diagram_from_json(Path(raw_target))

    module = _load_target_module(target)

    if target.object_ref:
        return _resolve_diagram_ref(target, module)

    return _get_single_diagram_from_module(target, module)

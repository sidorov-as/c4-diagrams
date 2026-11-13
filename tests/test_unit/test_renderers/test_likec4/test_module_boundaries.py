import ast
import subprocess
import sys
from pathlib import Path

import c4.contrib.likec4 as likec4_package

PACKAGE_DIR = Path(likec4_package.__file__).parent
RENDERER_MODULE = "c4.contrib.likec4.renderer"


def _authoring_modules() -> list[Path]:
    return [
        *sorted((PACKAGE_DIR / "workspace").rglob("*.py")),
        *sorted(PACKAGE_DIR.glob("_*.py")),
    ]


def _module_scope_imports(tree: ast.Module) -> list[str]:
    """Return imported module names, ignoring imports inside functions."""
    names: list[str] = []

    def visit(nodes: list[ast.stmt]) -> None:
        for node in nodes:
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                names.append(base)
                names.extend(f"{base}.{alias.name}" for alias in node.names)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            else:
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, ast.stmt):
                        visit([child])

    visit(tree.body)
    return names


def test_authoring_modules_do_not_import_renderer_at_module_scope():
    offenders = []
    for path in _authoring_modules():
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for name in _module_scope_imports(tree):
            if name == RENDERER_MODULE or name.startswith(
                f"{RENDERER_MODULE}."
            ):
                offenders.append(f"{path.relative_to(PACKAGE_DIR)}: {name}")
    assert not offenders, offenders


def test_package_import_does_not_load_renderer_or_need_node():
    code = (
        "import sys\n"
        "from c4.contrib.likec4 import Project\n"
        f"assert {RENDERER_MODULE!r} not in sys.modules\n"
        "assert not any(m.startswith('playwright') for m in sys.modules)\n"
    )
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-I", "-c", code],
        capture_output=True,
        text=True,
        check=False,
        env={"PATH": ""},
    )
    assert result.returncode == 0, result.stderr

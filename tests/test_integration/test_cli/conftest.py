from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Protocol

import pytest

from tests.conftest import MakeTmpPyFile

SIMPLE_RENDER_DIAGRAM_SOURCE = textwrap.dedent(
    """
    from c4 import SystemContextDiagram

    diagram = SystemContextDiagram("Example")
    """
)

EXPORT_DIAGRAM_SOURCE = textwrap.dedent(
    """
    from c4 import Person, Rel, System, SystemContextDiagram

    with SystemContextDiagram("Example system context") as diagram:
        user = Person(label="User", description="System user")
        backend = System(label="Backend API", description="Main application backend")

        user >> Rel("Uses HTTP API") >> backend
    """
)


class MakeCliDiagram(Protocol):
    def __call__(self, relative_path: str = "diagram.py") -> Path: ...


class MakeFakeWatchfiles(Protocol):
    def __call__(self, changed_filename: str = "diagram.py") -> Path: ...


@pytest.fixture()
def make_simple_render_diagram(
    make_tmp_py_file: MakeTmpPyFile,
) -> MakeCliDiagram:
    def _make_diagram(relative_path: str = "diagram.py") -> Path:
        return make_tmp_py_file(relative_path, SIMPLE_RENDER_DIAGRAM_SOURCE)

    return _make_diagram


@pytest.fixture()
def make_export_diagram(
    make_tmp_py_file: MakeTmpPyFile,
) -> MakeCliDiagram:
    def _make_diagram(relative_path: str = "diagram.py") -> Path:
        return make_tmp_py_file(relative_path, EXPORT_DIAGRAM_SOURCE)

    return _make_diagram


@pytest.fixture()
def make_fake_watchfiles(
    make_tmp_py_file: MakeTmpPyFile,
) -> MakeFakeWatchfiles:
    """
    The fixture creates a real watchfiles.py in the temporary import path, so
    the CLI imports that instead of the external watchfiles package
    during the test.
    """

    def _make_watchfiles(changed_filename: str = "diagram.py") -> Path:
        return make_tmp_py_file(
            "watchfiles.py",
            textwrap.dedent(
                f"""
                from pathlib import Path


                def watch(*paths):
                    for path in paths:
                        changed_path = Path(path) / {changed_filename!r}
                        if changed_path.exists():
                            yield [(object(), str(changed_path))]
                            break
                    raise KeyboardInterrupt
                """
            ),
        )

    return _make_watchfiles

from __future__ import annotations

import typing
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_DIR = PROJECT_ROOT / "docs" / "assets"

_ParametrizeIdsIterable = typing.Iterable[None | str | float | int | bool]
_ParametrizeIdsCallable = typing.Callable[[typing.Any], object | None]
_ParametrizeScopeName = typing.Literal[
    "session", "package", "module", "class", "function"
]


class ParametrizeArgs(typing.TypedDict, total=False):
    argnames: str | list[str] | tuple[str, ...]
    argvalues: typing.Iterable[typing.Any]
    indirect: bool | typing.Sequence[str] | None
    ids: _ParametrizeIdsCallable | _ParametrizeIdsCallable | None
    scope: _ParametrizeScopeName | None

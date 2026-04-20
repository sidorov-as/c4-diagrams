from __future__ import annotations

from enum import Enum, auto
from typing import (
    Final,
    Literal,
    TypeAlias,
    TypeVar,
)

_T = TypeVar("_T")


class _Required(Enum):
    required = auto()


Required: TypeAlias = _T | Literal[_Required.required]
REQUIRED: Final[Literal[_Required.required]] = _Required.required


class _Missing(Enum):
    missing = auto()


Maybe: TypeAlias = _T | Literal[_Missing.missing]
MISSING: Final[Literal[_Missing.missing]] = _Missing.missing

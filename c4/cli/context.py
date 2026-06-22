from __future__ import annotations

import argparse
from dataclasses import dataclass


@dataclass(frozen=True)
class CommandContext:
    args: argparse.Namespace
    argv: tuple[str, ...]

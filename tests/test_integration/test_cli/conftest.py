import dataclasses
import os
import subprocess
import sys
from asyncio import Protocol
from pathlib import Path

import pytest


@dataclasses.dataclass
class CommandResult:
    stdout: str | bytes
    stderr: str | bytes
    exit_code: int


@pytest.fixture()
def cli(sys_path_tmp: Path):
    def with_args(
        argv: list[str] | None = None,
        cwd: str | Path | None = None,
    ) -> CommandResult:
        argv = argv or []
        cmd = [sys.executable, "-m", "c4", *argv]

        env = dict(os.environ)
        pythonpath = str(sys_path_tmp)
        if env.get("PYTHONPATH"):
            pythonpath = f"{pythonpath}{os.pathsep}{env['PYTHONPATH']}"
        env["PYTHONPATH"] = pythonpath

        run_kwargs = {
            "capture_output": True,
            "text": True,
            "timeout": 30,
            "env": env,
        }
        if cwd:
            run_kwargs["cwd"] = cwd

        res = subprocess.run(cmd, **run_kwargs)  # noqa: S603

        return CommandResult(
            stdout=res.stdout,
            stderr=res.stderr,
            exit_code=res.returncode,
        )

    return with_args


class CLI(Protocol):
    def __call__(
        self,
        argv: list[str] | None = None,
        cwd: str | Path | None = None,
    ) -> CommandResult: ...

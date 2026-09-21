from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from pathlib import Path

from c4.constants import (
    DEFAULT_LIKEC4_BIN,
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    LIKEC4_BIN_ENV_VAR,
    RENDERING_TIMEOUT_SECONDS_ENV_VAR,
)
from c4.contrib.likec4.renderer.errors import (
    LikeC4BackendConfigurationError,
    LikeC4LocalRenderingError,
)
from c4.enums import LIKEC4_DIAGRAM_FORMATS, DiagramFormat
from c4.utils import MISSING, Maybe

_CHROMIUM_MARKERS = (
    "Executable doesn't exist",
    "npx playwright install",
)
_SOURCE_FILE_NAME = "workspace.c4"


class BaseLikeC4Backend(ABC):
    """Export LikeC4 DSL text to an image."""

    @abstractmethod
    def to_bytes(
        self,
        source: str,
        *,
        format: DiagramFormat | str,
        view_key: str | None = None,
    ) -> bytes:
        """
        Export LikeC4 DSL source and return the generated image bytes.

        Args:
            source: LikeC4 DSL source to export.
            format: Target diagram format.
            view_key: Key of the view to export.

        Raises:
            LikeC4RenderingError: If rendering fails.
        """
        raise NotImplementedError()  # pragma: no cover

    def to_file(
        self,
        source: str,
        output_path: str | Path,
        *,
        format: DiagramFormat | None,
        overwrite: bool = True,
        view_key: str | None = None,
    ) -> Path:
        """
        Export LikeC4 DSL source and write the generated image.

        Args:
            source: LikeC4 DSL source to export.
            output_path: Destination file path.
            format: Target format; inferred from ``output_path`` when
                omitted.
            overwrite: Whether to replace an existing destination file.
            view_key: Key of the view to export.

        Raises:
            ValueError: If ``format`` is ``None`` and the output path has no
                suffix.
            FileExistsError: If the output exists and ``overwrite`` is false.
            LikeC4RenderingError: If rendering fails.
        """
        output_path = Path(output_path)
        if format is None:
            if not output_path.suffix:
                raise ValueError(
                    "format is None and output_path has no extension."
                )

            format = DiagramFormat(output_path.suffix.lstrip(".").lower())

        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file already exists: {output_path!s}"
            )

        content = self.to_bytes(source, format=format, view_key=view_key)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(content)
        return output_path


class LocalLikeC4Backend(BaseLikeC4Backend):
    """
    Export LikeC4 views using the local ``likec4`` CLI.

    Image export needs Node.js and Playwright Chromium.

    Env vars:
      - LIKEC4_BIN: executable name/path (default: 'likec4')
    """

    def __init__(
        self,
        *,
        likec4_bin: Maybe[str | Sequence[str]] = MISSING,
        timeout_seconds: Maybe[float] = MISSING,
        env: Mapping[str, str] | None = None,
    ) -> None:
        """
        Initialize the backend and check that the CLI is installed.

        Args:
            likec4_bin: Executable name/path or a command prefix such as
                ``["npx", "likec4@1.60.0"]``.
            timeout_seconds: Timeout of one CLI call.
            env: Extra environment variables for the CLI process.

        Raises:
            LikeC4BackendConfigurationError: If the CLI is not found or the
                timeout is not a number.
        """
        self._env = dict(os.environ)
        if env:
            self._env.update(env)

        if likec4_bin is MISSING:
            likec4_bin = self._env.get(LIKEC4_BIN_ENV_VAR, DEFAULT_LIKEC4_BIN)

        self._command: list[str] = (
            [likec4_bin]
            if isinstance(likec4_bin, str)
            else [str(part) for part in likec4_bin]
        )

        if timeout_seconds is MISSING:
            timeout_seconds = self._env.get(  # type: ignore[assignment]
                RENDERING_TIMEOUT_SECONDS_ENV_VAR,
                DEFAULT_RENDERING_TIMEOUT_SECONDS,
            )
        try:
            self._timeout_seconds = float(timeout_seconds)  # type: ignore[arg-type]
        except ValueError as exc:
            raise LikeC4BackendConfigurationError(
                f"Invalid timeout: {timeout_seconds!r} "
                f"(expected a number of seconds)."
            ) from exc

        self._resolve_binary()

    def to_bytes(
        self,
        source: str,
        *,
        format: DiagramFormat | str,
        view_key: str | None = None,
    ) -> bytes:
        """
        Export one view of LikeC4 DSL source to PNG or JPG.

        Args:
            source: LikeC4 DSL source to export.
            format: ``'png'`` or ``'jpg'``.
            view_key: Key of the view to export.

        Returns:
            Rendered image content as raw bytes.

        Raises:
            ValueError: If the format is not supported.
            LikeC4BackendConfigurationError: If ``view_key`` is missing, or
                Chromium is not installed.
            LikeC4LocalRenderingError: If the CLI fails or produces no file.
        """
        diagram_format = self._check_format(format)
        if not view_key:
            raise LikeC4BackendConfigurationError(
                "LikeC4 image export needs a view key: pass view_key "
                "(--likec4-view-key) to choose the view to export."
            )

        with tempfile.TemporaryDirectory(prefix="likec4-gen-") as tmp:
            tmp_dir = Path(tmp)
            input_dir = tmp_dir / "src"
            output_dir = tmp_dir / "out"
            input_dir.mkdir()
            (input_dir / _SOURCE_FILE_NAME).write_text(source, encoding="utf-8")

            output_path = output_dir / f"{view_key}.{diagram_format.value}"
            cmd = [
                *self._command,
                "export",
                diagram_format.value,
                "--flat",
                "-o",
                str(output_dir),
                "-f",
                view_key,
                str(input_dir),
            ]

            try:
                res = subprocess.run(  # noqa: S603
                    cmd,
                    cwd=str(tmp_dir),
                    capture_output=True,
                    text=True,
                    timeout=self._timeout_seconds,
                    env=self._env,
                )
            except subprocess.TimeoutExpired as exc:
                raise LikeC4LocalRenderingError(
                    f"LikeC4 export timed out after "
                    f"{self._timeout_seconds:g} seconds."
                ) from exc

            output = "\n".join(
                part.strip() for part in (res.stderr, res.stdout) if part
            )
            if res.returncode != 0:
                if any(marker in output for marker in _CHROMIUM_MARKERS):
                    raise LikeC4BackendConfigurationError(
                        "Playwright Chromium is not installed. "
                        "Install it with: npx playwright install chromium"
                    )

                raise LikeC4LocalRenderingError(output or "LikeC4 failed.")

            if not output_path.exists():
                raise LikeC4LocalRenderingError(
                    f"View {view_key!r} was not exported; "
                    f"check that the view exists. {output}".strip()
                )

            return output_path.read_bytes()

    @staticmethod
    def _check_format(format: DiagramFormat | str) -> DiagramFormat:
        try:
            diagram_format = DiagramFormat(format)
        except ValueError:
            diagram_format = None

        if diagram_format not in LIKEC4_DIAGRAM_FORMATS:
            supported = ", ".join(
                sorted(item.value for item in LIKEC4_DIAGRAM_FORMATS)
            )
            raise ValueError(
                f"Unsupported LikeC4 format: {format!r}. "
                f"Supported formats: {supported}."
            )
        return diagram_format

    def _resolve_binary(self) -> None:
        if not self._command or not shutil.which(self._command[0]):
            raise LikeC4BackendConfigurationError(
                "LikeC4 is not available. "
                f"Tried {self._command[:1]!r} in PATH. "
                "Install it with `npm install -g likec4`, or configure it "
                f"with the {LIKEC4_BIN_ENV_VAR} environment variable "
                "or likec4_bin."
            )

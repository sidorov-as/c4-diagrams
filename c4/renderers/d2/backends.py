from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from pathlib import Path

from c4 import PNG, DiagramFormat
from c4.constants import (
    D2_BIN_ENV_VAR,
    DEFAULT_D2_BIN,
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    RENDERING_TIMEOUT_SECONDS_ENV_VAR,
)
from c4.enums import D2_DIAGRAM_FORMATS
from c4.exceptions import (
    D2BackendConfigurationError,
    D2LocalRenderingError,
)
from c4.renderers.d2.options import D2Layout, D2RenderOptions
from c4.utils import MISSING, Maybe


class BaseD2Backend(ABC):
    """
    Generate D2 diagrams from plain text.

    A generator takes D2 diagram source text and produces image bytes
    (or writes them to a file).
    """

    @abstractmethod
    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = PNG,
        render_options: D2RenderOptions | None = None,
    ) -> bytes:
        """
        Generate a D2 diagram and return the generated image as bytes.

        Args:
            diagram: D2 diagram source text.
            format: Output image format, such as ``'svg'``, ``'png'``,
                or ``'pdf'``.
            render_options: Optional D2 render options used by backends that
                support renderer-controlled export flags.

        Returns:
            Rendered image content as raw bytes.

        Raises:
            D2RenderingError: If rendering fails.
        """
        raise NotImplementedError()  # pragma: no cover

    def to_file(
        self,
        diagram: str,
        output_path: str | Path,
        *,
        format: DiagramFormat | None = PNG,
        overwrite: bool = True,
        render_options: D2RenderOptions | None = None,
    ) -> Path:
        """
        Generate a D2 diagram and write the generated image to a file.

        Args:
            diagram: D2 diagram source text.
            output_path: Path where the rendered image should be written.
            format: Output image format. If ``None``, the format is inferred
                from ``output_path`` suffix.
            overwrite: Whether to overwrite the output file if it already
                exists.
            render_options: Optional D2 render options used by backends that
                support renderer-controlled export flags.

        Returns:
            Path to the written output file.
        """
        output_path = Path(output_path)

        if format is None:
            if not output_path.suffix:
                raise ValueError(
                    "format is None and output_path has no extension."
                )
            format = output_path.suffix.lstrip(".").lower()  # type: ignore[assignment]

        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file already exists: {output_path!s}"
            )

        content = self.to_bytes(
            diagram,
            format=format,  # type: ignore[arg-type]
            render_options=render_options,
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(content)
        return output_path

    def _ensure_format_supported(
        self,
        format: DiagramFormat,
    ) -> None:
        if format not in D2_DIAGRAM_FORMATS:
            raise ValueError(
                f"{format.value!r} format is not supported by D2 renderer."
            )


class LocalD2Backend(BaseD2Backend):
    """
    Generate D2 diagrams using the local D2 executable.

    Env vars:
      - D2_BIN: executable name/path (default: 'd2')
    """

    _d2_bin: str | None

    def __init__(
        self,
        *,
        d2_bin: Maybe[str | None] = MISSING,
        timeout_seconds: Maybe[float] = MISSING,
        d2_args: Sequence[str] = (),
        layout: D2Layout | None = None,
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._env = dict(os.environ)
        if env:
            self._env.update(env)

        if d2_bin is MISSING:
            self._d2_bin = self._env.get(D2_BIN_ENV_VAR, DEFAULT_D2_BIN)
        else:
            self._d2_bin = d2_bin

        self._d2_args = list(d2_args)
        if layout is not None:
            D2RenderOptions(layout=layout)
        self._layout = layout

        if timeout_seconds is MISSING:
            timeout_seconds = self._env.get(  # type: ignore[assignment]
                RENDERING_TIMEOUT_SECONDS_ENV_VAR,
                DEFAULT_RENDERING_TIMEOUT_SECONDS,
            )

        try:
            self._timeout_seconds = float(timeout_seconds)  # type: ignore[arg-type]
        except ValueError as exc:
            source = (
                "timeout_seconds argument"
                if timeout_seconds is not MISSING
                else f"environment variable {RENDERING_TIMEOUT_SECONDS_ENV_VAR}"
            )

            raise D2BackendConfigurationError(
                f"Invalid timeout from {source}: {timeout_seconds!r} "
                f"(expected a number of seconds)."
            ) from exc

        self._resolve_backend()

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.SVG,
        render_options: D2RenderOptions | None = None,
    ) -> bytes:
        """
        Generate a D2 diagram using the local D2 binary
        and return the generated image as bytes.

        Args:
            diagram: D2 diagram source text.
            format: Output image format, such as ``'svg'``, ``'png'``,
                or ``'pdf'``.
            render_options: Optional D2 render options used to configure
                the local D2 CLI invocation.

        Returns:
            Rendered image content as raw bytes.

        Raises:
            D2RenderingError: If rendering fails.
        """
        self._ensure_format_supported(format)

        with tempfile.TemporaryDirectory(prefix="d2-gen-") as tmp:
            tmp_dir = Path(tmp)
            input_path = tmp_dir / "diagram.d2"
            input_path.write_text(diagram, encoding="utf-8")

            output_path = input_path.with_suffix(f".{format.value}")
            cmd = self._build_cmd(
                input_path=input_path,
                output_path=output_path,
                render_options=render_options,
            )

            res = subprocess.run(  # noqa: S603
                cmd,
                cwd=str(tmp_dir),
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
                env=self._env,
            )
            if res.returncode != 0:
                stderr = (res.stderr or "").strip()
                stdout = (res.stdout or "").strip()
                raise D2LocalRenderingError(stderr or stdout or "D2 failed.")

            if not output_path.exists():
                raise D2LocalRenderingError(
                    f"Expected output was not generated: {output_path.name}"
                )

            return output_path.read_bytes()

    def _resolve_backend(self) -> None:
        binary_found = self._d2_bin and shutil.which(self._d2_bin)

        if not binary_found:
            raise D2BackendConfigurationError(
                "D2 is not available. "
                f"Tried binary {self._d2_bin!r} in PATH. "
                "Configure D2 by setting the D2_BIN environment variable, "
                "or by passing d2_bin."
            )

    def _build_cmd(
        self,
        *,
        input_path: Path,
        output_path: Path,
        render_options: D2RenderOptions | None = None,
    ) -> list[str]:
        cmd = [
            self._d2_bin,
            str(input_path),
            str(output_path),
            *self._d2_args,
        ]

        layout = self._layout
        if layout is None and render_options is not None:
            layout = render_options.layout

        if layout is not None:
            cmd.append(f"--layout={layout}")

        return cmd  # type: ignore[return-value]

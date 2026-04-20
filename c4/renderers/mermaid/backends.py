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
    DEFAULT_MERMAID_BIN,
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    MERMAID_BIN_ENV_VAR,
    RENDERING_TIMEOUT_SECONDS_ENV_VAR,
)
from c4.enums import MERMAID_DIAGRAM_FORMATS
from c4.exceptions import (
    MermaidBackendConfigurationError,
    MermaidLocalRenderingError,
)
from c4.utils import MISSING, Maybe


class BaseMermaidBackend(ABC):
    """
    Generate Mermaid diagrams from plain text.

    A generator takes a Mermaid diagram text and produces image bytes
    (or writes them to a file).
    """

    @abstractmethod
    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = PNG,
    ) -> bytes:
        """
        Generate a Mermaid diagram and return the generated image as bytes.

        Args:
            diagram: Mermaid diagram source text.
            format: Output image format (for example, ``'svg'`` or ``'png'``).

        Returns:
            Rendered image content as raw bytes.

        Raises:
            MermaidRenderingError: If rendering fails.
        """
        raise NotImplementedError()  # pragma: no cover

    def to_file(
        self,
        diagram: str,
        output_path: str | Path,
        *,
        format: DiagramFormat | None = PNG,
        overwrite: bool = True,
    ) -> Path:
        """
        Generate a Mermaid diagram and write the generated image to a file.

        Args:
            diagram: Mermaid diagram source text.
            output_path: Path where the rendered image should be written.
            format: Output image format. If ``None``, the format is
                inferred from ``output_path`` suffix.
            overwrite: Whether to overwrite the output file if
                it already exists.

        Returns:
            Path to the written output file.

        Raises:
            ValueError: If ``format`` is ``None`` and the output path
                has no suffix.
            FileExistsError: If the output file exists
                and ``overwrite`` is ``False``.
            MermaidRenderingError: If rendering fails.
        """
        output_path = Path(output_path)

        if format is None:
            if not output_path.suffix:
                raise ValueError(
                    "format is None and output_path has no extension."
                )
            format = output_path.suffix.lstrip(".").lower()  # type: ignore[assignment]

        output_path = Path(output_path)

        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"Output file already exists: {output_path!s}"
            )

        content = self.to_bytes(diagram, format=format)  # type: ignore[arg-type]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(content)
        return output_path

    def _ensure_format_supported(
        self,
        format: DiagramFormat,
    ) -> None:
        if format not in MERMAID_DIAGRAM_FORMATS:
            raise ValueError(
                f"{format.value!r} format is not supported by Mermaid renderer."
            )


class LocalMermaidBackend(BaseMermaidBackend):
    """
    Generate Mermaid diagrams using local mermaid-cli.

    Env vars:
      - MERMAID_BIN: executable name/path (default: 'mmdc')
    """

    _mermaid_bin: str | None

    def __init__(
        self,
        *,
        mermaid_bin: Maybe[str | None] = MISSING,
        timeout_seconds: Maybe[float] = MISSING,
        mermaid_args: Sequence[str] = (),
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._env = dict(os.environ)
        if env:
            self._env.update(env)

        if mermaid_bin is MISSING:
            self._mermaid_bin = self._env.get(
                MERMAID_BIN_ENV_VAR, DEFAULT_MERMAID_BIN
            )
        else:
            self._mermaid_bin = mermaid_bin

        self._mermaid_args = list(mermaid_args)

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

            raise MermaidBackendConfigurationError(
                f"Invalid timeout from {source}: {timeout_seconds!r} "
                f"(expected a number of seconds)."
            ) from exc

        self._resolve_backend()

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.SVG,
    ) -> bytes:
        """
        Generate a Mermaid diagram using local Mermaid binary
        and return the generated image as bytes.

        Args:
            diagram: Mermaid diagram source text.
            format: Output image format (for example, ``'svg'`` or ``'png'``).

        Returns:
            Rendered image content as raw bytes.

        Raises:
            MermaidLocalRenderingError: If rendering fails.
            MermaidBackendConfigurationError: If the required Mermaid backend
                                              is not available.
        """
        self._ensure_format_supported(format)

        with tempfile.TemporaryDirectory(prefix="Mermaid-gen-") as tmp:
            tmp_dir = Path(tmp)
            input_path = tmp_dir / "diagram.mmd"
            input_path.write_text(diagram, encoding="utf-8")

            ext = format.value
            output_path = input_path.with_suffix(f".{ext}")
            cmd = self._build_cmd(
                input_path=input_path, output_path=output_path
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
                raise MermaidLocalRenderingError(
                    stderr or stdout or "Mermaid failed."
                )

            if not output_path.exists():
                raise MermaidLocalRenderingError(
                    f"Expected output was not generated: {output_path.name}"
                )

            return output_path.read_bytes()

    def _resolve_backend(self) -> None:
        binary_found = self._mermaid_bin and shutil.which(self._mermaid_bin)

        if not binary_found:
            raise MermaidBackendConfigurationError(
                "Mermaid is not available. "
                f"Tried binary {self._mermaid_bin!r} in PATH. "
                "Configure Mermaid by setting the MERMAID_BIN "
                "environment variable, or by passing mermaid_bin."
            )

    def _build_cmd(
        self,
        *,
        input_path: Path,
        output_path: Path,
    ) -> list[str]:
        return [
            self._mermaid_bin,  # type: ignore[list-item]
            "-i",
            str(input_path),
            "-o",
            str(output_path),
            *self._mermaid_args,
        ]

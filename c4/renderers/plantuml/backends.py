from __future__ import annotations

import base64
import os
import shutil
import subprocess
import tempfile
import zlib
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from contextlib import suppress
from pathlib import Path
from string import ascii_lowercase, ascii_uppercase, digits
from typing import Literal
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from c4.compat.strenum import StrEnum
from c4.exceptions import (
    PlantUMLBackendConfigurationError,
    PlantUMLLocalRenderingError,
    PlantUMLRemoteRenderingError,
)


class DiagramFormat(StrEnum):
    EPS = "eps"
    LATEX = "latex"
    SVG = "svg"
    PNG = "png"
    TXT = "txt"
    UTXT = "utxt"


DEFAULT_PLANTUML_SERVER_URL = "https://www.plantuml.com/plantuml"

BASE64_TO_PLANTUML = {
    ord(b): b2.encode()
    for b, b2 in zip(
        ascii_uppercase + ascii_lowercase + digits + "+/=",
        digits + ascii_uppercase + ascii_lowercase + "-_=",
    )
}


class BasePlantUMLBackend(ABC):
    """
    Generate PlantUML diagrams from plain text.

    A generator takes a PlantUML diagram text and produces image bytes
    (or writes them to a file).
    """

    @abstractmethod
    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.SVG,
    ) -> bytes:
        """
        Generate a PlantUML diagram and return the generated image as bytes.

        Args:
            diagram: PlantUML diagram source text.
            format: Output image format (for example, ``'svg'`` or ``'png'``).

        Returns:
            Rendered image content as raw bytes.

        Raises:
            PlantUMLRenderingError: If rendering fails.
            FileNotFoundError: If the required PlantUML backend is
                not available.
        """
        raise NotImplementedError()

    def to_file(
        self,
        diagram: str,
        output_path: Path,
        *,
        format: DiagramFormat | None = None,
        overwrite: bool = True,
    ) -> Path:
        """
        Generate a PlantUML diagram and write the generated image to a file.

        Args:
            diagram: PlantUML diagram source text.
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
            PlantUMLRenderingError: If rendering fails.
            FileNotFoundError: If the required PlantUML backend is
                not available.
        """
        if format is None:
            if not output_path.suffix:
                raise ValueError(
                    "format is None and output_path has no suffix (e.g. .svg)."
                )
            format = output_path.suffix.lstrip(".").lower()  # type: ignore[assignment]

        if output_path.exists() and not overwrite:
            raise FileExistsError(f"Output exists: {output_path}")

        content = self.to_bytes(diagram, format=format)  # type: ignore[arg-type]
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(content)
        return output_path


class RemotePlantUMLBackend(BasePlantUMLBackend):
    """
    Generate PlantUML diagrams using PlantUML server.

    Env vars:
      - PLANTUML_SERVER_URL: PlantUML server path
                            (default: 'https://www.plantuml.com/plantuml')
    """

    _server_url: str

    def __init__(
        self,
        *,
        server_url: str | None = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        server_url = server_url or os.getenv(
            "PLANTUML_SERVER_URL", DEFAULT_PLANTUML_SERVER_URL
        )
        self._server_url = (
            server_url[:-1] if server_url.endswith("/") else server_url  # type: ignore[index, union-attr, assignment]
        )
        self._timeout_seconds = timeout_seconds

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.SVG,
    ) -> bytes:
        """
        Generate a PlantUML diagram using PlantUML server and
        return the generated image as bytes.

        Args:
            diagram: PlantUML diagram source text.
            format: Output image format (for example, ``'svg'`` or ``'png'``).

        Returns:
            Rendered image content as raw bytes.

        Raises:
            PlantUMLRemoteRenderingError: If rendering fails.
        """
        encoded = self._encode_text_diagram(diagram).decode("utf-8")
        url = f"{self._server_url}/{format}/{encoded}"
        request = Request(url, method="GET")  # noqa: S310

        try:
            with urlopen(request, timeout=self._timeout_seconds) as resp:  # noqa: S310
                return resp.read()  # type: ignore[no-any-return]
        except HTTPError as exc:
            body = b""
            with suppress(Exception):
                body = exc.read() or b""

            body_preview = body[:200].decode("utf-8", errors="replace")
            raise PlantUMLRemoteRenderingError(
                f"PlantUML server render failed: "
                f"HTTP {exc.code} {exc.reason}. "
                f"Body: {body_preview!r}"
            ) from exc
        except URLError as exc:
            raise PlantUMLRemoteRenderingError(
                f"PlantUML server render failed: {exc.reason!r}"
            ) from exc

    def _encode_text_diagram(self, text_diagram: str) -> bytes:
        """
        Encode text diagram with zlib/plantuml specific base64 encoding.

        Steps:
        - UTF-8 encode
        - deflate compress (zlib)
        - strip zlib header (2 bytes) and checksum (4 bytes)
        - base64 encode
        - translate into PlantUML alphabet

        See: https://plantuml.com/text-encoding
        """
        utf_encoded = text_diagram.encode("utf-8")
        compressed = zlib.compress(utf_encoded)
        compressed = compressed[2:-4]  # strip zlib header + adler32
        b64_encoded = base64.b64encode(compressed)
        return b"".join(BASE64_TO_PLANTUML[b] for b in b64_encoded)


class LocalPlantUMLBackend(BasePlantUMLBackend):
    """
    Generate PlantUML diagrams using local PlantUML binary or jar.

    Env vars:
      - PLANTUML_BIN: executable name/path (default: 'plantuml')
      - PLANTUML_JAR: path to plantuml.jar
    """

    _plantuml_bin: str
    _java_bin: str

    def __init__(
        self,
        *,
        backend: Literal["binary", "jar"] = "binary",
        plantuml_bin: str | None = None,
        plantuml_jar: Path | None = None,
        java_bin: str = "java",
        timeout_seconds: float = 30.0,
        plantuml_args: Sequence[str] = (),
        java_args: Sequence[str] = (),
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._backend = backend
        self._plantuml_bin = plantuml_bin or os.getenv(  # type: ignore[assignment]
            "PLANTUML_BIN", "plantuml"
        )

        jar_env = os.getenv("PLANTUML_JAR")
        self._plantuml_jar = plantuml_jar or (
            Path(jar_env) if jar_env else None
        )
        self._plantuml_args = list(plantuml_args)

        self._java_bin = java_bin
        self._java_args = list(java_args)

        self._env = dict(os.environ)
        if env:
            self._env.update(env)

        self._timeout_seconds = timeout_seconds

        self._validate_backend_available()

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = DiagramFormat.SVG,
    ) -> bytes:
        """
        Generate a PlantUML diagram using local PlantUML binary or jar
        and return the generated image as bytes.

        Args:
            diagram: PlantUML diagram source text.
            format: Output image format (for example, ``'svg'`` or ``'png'``).

        Returns:
            Rendered image content as raw bytes.

        Raises:
            PlantUMLLocalRenderingError: If rendering fails.
            PlantUMLBackendConfigurationError: If the required PlantUML backend
                                               is not available.
        """
        with tempfile.TemporaryDirectory(prefix="plantuml-gen-") as tmp:
            tmp_dir = Path(tmp)
            input_path = tmp_dir / "diagram.puml"
            input_path.write_text(diagram, encoding="utf-8")

            out_path = input_path.with_suffix(f".{format}")
            cmd = self._build_cmd(input_path=input_path, format=format)

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
                raise PlantUMLLocalRenderingError(
                    stderr or stdout or "PlantUML failed."
                )

            if not out_path.exists():
                raise FileNotFoundError(
                    f"Expected output was not generated: {out_path.name}"
                )

            return out_path.read_bytes()

    def _validate_backend_available(self) -> None:
        if self._backend == "binary":
            if not shutil.which(self._plantuml_bin):
                raise PlantUMLBackendConfigurationError(
                    "PlantUML binary not found. Install it or set PLANTUML_BIN."
                )
        elif self._backend == "jar":
            if not (self._plantuml_jar and self._plantuml_jar.exists()):
                raise PlantUMLBackendConfigurationError(
                    "PlantUML jar not found. Set PLANTUML_JAR "
                    "or pass plantuml_jar."
                )
        else:
            raise PlantUMLBackendConfigurationError(
                f"Unknown backend: {self._backend!r}"
            )

    def _build_cmd(
        self,
        *,
        input_path: Path,
        format: DiagramFormat,
    ) -> list[str]:
        tflag = f"-t{format}"
        if self._backend == "jar":
            return [
                self._java_bin,
                *self._java_args,
                "-jar",
                str(self._plantuml_jar),
                tflag,
                *self._plantuml_args,
                input_path.name,
            ]

        return [
            self._plantuml_bin,
            tflag,
            *self._plantuml_args,
            input_path.name,
        ]

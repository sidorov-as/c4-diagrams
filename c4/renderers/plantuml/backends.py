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
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from c4 import PNG, DiagramFormat
from c4.constants import (
    DEFAULT_JAVA_BIN,
    DEFAULT_PLANTUML_BIN,
    DEFAULT_PLANTUML_SERVER_URL,
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    JAVA_BIN_ENV_VAR,
    PLANTUML_BIN_ENV_VAR,
    PLANTUML_JAR_ENV_VAR,
    PLANTUML_SERVER_URL_ENV_VAR,
    RENDERING_TIMEOUT_SECONDS_ENV_VAR,
)
from c4.enums import PLANTUML_DIAGRAM_FORMATS
from c4.exceptions import (
    PlantUMLBackendConfigurationError,
    PlantUMLLocalRenderingError,
    PlantUMLRemoteRenderingError,
)

BASE64_TO_PLANTUML = {
    ord(b): b2.encode()
    for b, b2 in zip(
        ascii_uppercase + ascii_lowercase + digits + "+/=",
        digits + ascii_uppercase + ascii_lowercase + "-_=",
        strict=True,
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
        format: DiagramFormat = PNG,
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
        output_path: str | Path,
        *,
        format: DiagramFormat | None = PNG,
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
        if format not in PLANTUML_DIAGRAM_FORMATS:
            raise ValueError(
                f"{format.value!r} format is not supported "
                f"by PlantUML renderer."
            )


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
        timeout_seconds: float = DEFAULT_RENDERING_TIMEOUT_SECONDS,
    ) -> None:
        server_url = server_url or os.getenv(
            PLANTUML_SERVER_URL_ENV_VAR, DEFAULT_PLANTUML_SERVER_URL
        )
        self._server_url = (
            server_url[:-1] if server_url.endswith("/") else server_url  # type: ignore[index, union-attr, assignment]
        )
        _timeout_seconds = os.getenv(
            RENDERING_TIMEOUT_SECONDS_ENV_VAR, timeout_seconds
        )
        self._timeout_seconds = float(_timeout_seconds)

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat = PNG,
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
        self._ensure_format_supported(format)

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


class _Empty: ...  # pragma: no cover


empty = _Empty()


class LocalPlantUMLBackend(BasePlantUMLBackend):
    """
    Generate PlantUML diagrams using local PlantUML binary or jar.

    Env vars:
      - PLANTUML_BIN: executable name/path (default: 'plantuml')
      - PLANTUML_JAR: path to plantuml.jar
    """

    _plantuml_bin: str | None
    _plantuml_jar: Path | None

    def __init__(
        self,
        *,
        plantuml_bin: str | None | _Empty = empty,
        plantuml_jar: Path | None | _Empty = empty,
        java_bin: str | None = None,
        timeout_seconds: float = DEFAULT_RENDERING_TIMEOUT_SECONDS,
        plantuml_args: Sequence[str] = (),
        java_args: Sequence[str] = (),
        env: Mapping[str, str] | None = None,
    ) -> None:
        self._env = dict(os.environ)
        if env:
            self._env.update(env)

        if plantuml_bin is empty:
            self._plantuml_bin = self._env.get(
                PLANTUML_BIN_ENV_VAR, DEFAULT_PLANTUML_BIN
            )
        else:
            self._plantuml_bin = plantuml_bin  # type: ignore[assignment]

        self._plantuml_args = list(plantuml_args)

        if plantuml_jar is empty:
            jar_env = self._env.get(PLANTUML_JAR_ENV_VAR)
            self._plantuml_jar = Path(jar_env) if jar_env else None
        else:
            self._plantuml_jar = plantuml_jar  # type: ignore[assignment]

        self._java_bin = java_bin or self._env.get(
            JAVA_BIN_ENV_VAR, DEFAULT_JAVA_BIN
        )
        self._java_args = list(java_args)

        timeout_env = self._env.get(
            RENDERING_TIMEOUT_SECONDS_ENV_VAR,
            timeout_seconds,
        )
        try:
            self._timeout_seconds = float(timeout_env)
        except ValueError as exc:
            raise PlantUMLBackendConfigurationError(
                f"Invalid {RENDERING_TIMEOUT_SECONDS_ENV_VAR}={timeout_env!r}:"
                f" expected a number of seconds."
            ) from exc

        _timeout_seconds = os.getenv(
            RENDERING_TIMEOUT_SECONDS_ENV_VAR, timeout_seconds
        )
        self._timeout_seconds = timeout_seconds

        self._resolve_backend()

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

            output_path = self._build_output_path(input_path, format)
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

            if not output_path.exists():
                raise PlantUMLLocalRenderingError(
                    f"Expected output was not generated: {output_path.name}"
                )

            return output_path.read_bytes()

    def _build_output_path(
        self,
        input_path: Path,
        format: DiagramFormat,
    ) -> Path:
        """
        Build the output file path for a rendered diagram.

        The output path is derived from the input path by replacing its suffix
        with an extension corresponding to the requested diagram format.

        Special case:
            For ``DiagramFormat.TXT``, the extension is prefixed with ``"a"``
            (e.g. ``.atxt``) to avoid collisions with source files or to
            distinguish generated textual artifacts from inputs.

        Args:
            input_path:
                Path to the input file used as the base for naming the output.
            format:
                Target diagram output format.

        Returns:
            A new ``Path`` with the updated file extension.
        """
        ext = format.value
        if format == DiagramFormat.TXT:
            ext = f"a{format.value}"

        out_path = input_path.with_suffix(f".{ext}")

        return out_path

    def _resolve_backend(self) -> None:
        binary_found = self._plantuml_bin and shutil.which(self._plantuml_bin)
        jar_found = self._plantuml_jar and self._plantuml_jar.exists()

        if binary_found:
            self._use_jar = False
            return

        if jar_found:
            self._use_jar = True
            return

        raise PlantUMLBackendConfigurationError(
            "PlantUML is not available. "
            f"Tried binary {self._plantuml_bin!r} in PATH and "
            f"jar {self._plantuml_jar!r}. "
            "Configure PlantUML by setting the PLANTUML_BIN or PLANTUML_JAR "
            "environment variables, or by passing plantuml_bin / plantuml_jar."
        )

    def _build_cmd(
        self,
        *,
        input_path: Path,
        format: DiagramFormat,
    ) -> list[str]:
        self._ensure_format_supported(format)

        tflag = f"-t{format}"

        if self._use_jar:
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
            self._plantuml_bin,  # type: ignore[list-item]
            tflag,
            *self._plantuml_args,
            input_path.name,
        ]

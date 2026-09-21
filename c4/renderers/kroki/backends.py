from __future__ import annotations

import base64
import os
import zlib
from collections.abc import Mapping
from contextlib import suppress
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from c4 import PNG, DiagramFormat
from c4.constants import (
    DEFAULT_KROKI_SERVER_URL,
    DEFAULT_RENDERING_TIMEOUT_SECONDS,
    KROKI_SERVER_URL_ENV_VAR,
    RENDERING_TIMEOUT_SECONDS_ENV_VAR,
)
from c4.exceptions import KrokiRemoteRenderingError

DEFAULT_KROKI_HEADERS = {
    "User-Agent": "c4-diagrams",
    "Accept": "*/*",
}


class KrokiBackend:
    """
    Generate diagrams using a Kroki server.

    Kroki uses regular zlib compression followed by URL-safe base64 for GET
    URLs. This is intentionally different from PlantUML server encoding.
    """

    def __init__(
        self,
        *,
        server_url: str | None = None,
        diagram_type: str = "plantuml",
        timeout_seconds: float = DEFAULT_RENDERING_TIMEOUT_SECONDS,
        use_post: bool = False,
        diagram_options: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        resolved_server_url = (
            server_url
            or os.getenv(
                KROKI_SERVER_URL_ENV_VAR,
                DEFAULT_KROKI_SERVER_URL,
            )
            or DEFAULT_KROKI_SERVER_URL
        )
        self._server_url = resolved_server_url.rstrip("/")
        self._diagram_type = self._normalize_path_part(
            diagram_type,
            name="diagram_type",
        )
        self._use_post = use_post
        self._diagram_options = dict(diagram_options or {})
        self._headers = {
            **DEFAULT_KROKI_HEADERS,
            **dict(headers or {}),
        }

        timeout = os.getenv(
            RENDERING_TIMEOUT_SECONDS_ENV_VAR,
            timeout_seconds,
        )
        self._timeout_seconds = float(timeout)

    def to_bytes(
        self,
        diagram: str,
        *,
        format: DiagramFormat | str = PNG,  # noqa: A002
        diagram_type: str | None = None,
        diagram_options: Mapping[str, str] | None = None,
    ) -> bytes:
        """Render a text diagram with Kroki and return response bytes."""
        diagram_type_value = self._normalize_path_part(
            diagram_type or self._diagram_type,
            name="diagram_type",
        )
        format_value = self._format_value(format)
        options = self._merged_diagram_options(diagram_options)

        if self._use_post:
            request = self._build_post_request(
                diagram=diagram,
                diagram_type=diagram_type_value,
                format=format_value,
                diagram_options=options,
            )
        else:
            request = self._build_get_request(
                diagram=diagram,
                diagram_type=diagram_type_value,
                format=format_value,
                diagram_options=options,
            )

        try:
            with urlopen(request, timeout=self._timeout_seconds) as resp:  # noqa: S310
                return resp.read()  # type: ignore[no-any-return]
        except HTTPError as exc:
            body = b""
            with suppress(Exception):
                body = exc.read() or b""

            body_preview = body[:200].decode("utf-8", errors="replace")
            raise KrokiRemoteRenderingError(
                f"Kroki render failed: HTTP {exc.code} {exc.reason}. "
                f"Body: {body_preview!r}"
            ) from exc
        except URLError as exc:
            raise KrokiRemoteRenderingError(
                f"Kroki render failed: {exc.reason!r}"
            ) from exc

    def _build_get_request(
        self,
        *,
        diagram: str,
        diagram_type: str,
        format: str,  # noqa: A002
        diagram_options: Mapping[str, str],
    ) -> Request:
        encoded = self._encode_text_diagram(diagram)
        url = f"{self._server_url}/{diagram_type}/{format}/{encoded}"
        url = self._add_query_params(url, diagram_options)
        return Request(url, headers=self._headers, method="GET")  # noqa: S310

    def _build_post_request(
        self,
        *,
        diagram: str,
        diagram_type: str,
        format: str,  # noqa: A002
        diagram_options: Mapping[str, str],
    ) -> Request:
        url = f"{self._server_url}/{diagram_type}/{format}"
        headers = {
            "Content-Type": "text/plain; charset=utf-8",
            **self._headers,
        }

        for name, value in diagram_options.items():
            headers[f"Kroki-Diagram-Options-{name}"] = value

        return Request(  # noqa: S310
            url,
            data=diagram.encode("utf-8"),
            headers=headers,
            method="POST",
        )

    def _encode_text_diagram(self, text_diagram: str) -> str:
        compressed = zlib.compress(text_diagram.encode("utf-8"), 9)
        return base64.urlsafe_b64encode(compressed).decode("ascii")

    def _format_value(self, format: DiagramFormat | str) -> str:  # noqa: A002
        value = getattr(format, "value", format)
        return self._normalize_path_part(str(value), name="format")

    def _normalize_path_part(self, value: str, *, name: str) -> str:
        normalized = value.strip().lower()
        if (
            not normalized
            or "/" in normalized
            or "?" in normalized
            or "#" in normalized
        ):
            raise ValueError(f"Invalid Kroki {name}: {value!r}")
        return normalized

    def _merged_diagram_options(
        self,
        diagram_options: Mapping[str, str] | None,
    ) -> dict[str, str]:
        options = dict(self._diagram_options)
        if diagram_options:
            options.update(diagram_options)
        return options

    def _add_query_params(
        self,
        url: str,
        query_params: Mapping[str, str],
    ) -> str:
        if not query_params:
            return url
        return f"{url}?{urlencode(query_params)}"

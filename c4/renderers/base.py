from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING, Generic

from c4 import DiagramFormat
from c4.diagrams.core import ExtensionValidationModeType
from c4.diagrams.core.diagram import TDiagram
from c4.enums import IGNORE_FOREIGN, ExtensionValidationMode, RendererEnum

if TYPE_CHECKING:  # pragma: no cover
    from c4.diagrams.core import BaseDiagramElement, Boundary


class IndentedStringBuilder:
    """Utility class for building text with indented lines."""

    def __init__(self, level: int = 0, indent: str = "    "):
        """
        Initialize the builder.

        Args:
            level: Initial indentation level (default is 0).
            indent: String used for one indent unit (default is 4 spaces).
        """
        self._level: int = level
        self._indent: str = indent
        self._lines: list[str] = []

    def add(
        self,
        *lines: str,
        blank_line_after: bool = False,
        ignore_empty_lines: bool = True,
        indent: bool = True,
    ) -> None:
        """
        Add one or more lines with the current indentation level applied.

        Args:
            *lines: One or more lines of text to add.
            blank_line_after: Whether to insert a blank line after the last
                added line.
            ignore_empty_lines: Whether to ignore empty lines or not.
            indent: Whether to add indentation to lines or not.
        """
        for line in lines:
            if not line and ignore_empty_lines:
                continue

            if indent:
                self._lines.append(f"{self._indent * self._level}{line}")
            else:
                self._lines.append(line)

        if blank_line_after:
            self.add_blank_line()

    def add_blank_line(self, check_duplicates: bool = True) -> None:
        """
        Add a blank line to the output, optionally skipping duplicates.

        Args:
            check_duplicates (bool): If True, avoids adding a blank line if
                the last line is already blank. Defaults to True.
        """
        if check_duplicates and self._lines:
            last_line = self._lines[-1]

            if last_line.endswith("\n") or not last_line.strip():
                return

        self._lines.append("")

    @property
    def lines(self) -> list[str]:
        """
        Returns a copy of the collected lines.
        """
        return list(self._lines)

    @contextmanager
    def indent(self) -> Iterator[int]:
        """
        Context manager for increasing indentation level temporarily.
        """
        self._level += 1
        try:
            yield self._level
        finally:
            self.dedent()

    def dedent(self) -> None:
        """
        Decrease the indentation level by one.
        """
        self._level -= 1

    def reset(self) -> None:
        """
        Clear all accumulated lines.
        """
        self._lines = []

    def get_result(self) -> str:
        """
        Join all accumulated lines into a single string.

        Returns:
            str: The final formatted string with line breaks.
        """
        return "\n".join(self._lines)


class BaseRenderer(ABC, Generic[TDiagram]):
    """
    Abstract base class for all diagram renderers.

    This class defines the interface and common structure for rendering
    a `Diagram` object into a textual representation.

    Subclasses must implement the `render` method to convert the diagram into
    a specific format (e.g., PlantUML, Mermaid, etc.).
    """

    renderer_type: RendererEnum

    def __init__(
        self,
        extension_validation_mode: ExtensionValidationModeType = IGNORE_FOREIGN,
    ) -> None:
        """
        Initialize the renderer.

        Args:
            extension_validation_mode: How strictly renderer-specific
                extension data is validated before rendering.
        """
        self._extension_validation_mode = ExtensionValidationMode(
            extension_validation_mode
        )

    def iter_render_items(
        self,
        diagram: TDiagram,
    ) -> Iterator[BaseDiagramElement]:
        """Return this renderer's top-level declaration render stream."""
        yield from diagram.ordered_elements

    def iter_boundary_render_items(
        self,
        boundary: Boundary,
    ) -> Iterator[BaseDiagramElement]:
        """Return this renderer's declaration stream inside a boundary."""
        yield from boundary.ordered_elements

    def validate(self, diagram: TDiagram) -> None:
        """Validate that this renderer can faithfully render the diagram."""
        raise NotImplementedError(  # pragma: no cover
            "Renderer class requires .validate() to be implemented"
        )

    @abstractmethod
    def render(self, diagram: TDiagram) -> str:
        """
        Render the provided Diagram into a textual format.

        Args:
            diagram: The diagram object to be rendered.

        Returns:
            A string containing the formatted diagram in the target syntax.
        """
        raise NotImplementedError(  # pragma: no cover
            "Renderer class requires .render() to be implemented"
        )

    @abstractmethod
    def render_bytes(
        self,
        diagram: TDiagram,
        *,
        format: DiagramFormat,
    ) -> bytes:
        """
        Render a Diagram and return the result as raw bytes.

        Concrete renderers may delegate conversion of their textual source to
        a local or remote backend.

        Args:
            diagram: The diagram instance to render.
            format: Output format of the rendered diagram.

        Returns:
            The rendered diagram content as raw bytes.
        """
        raise NotImplementedError(  # pragma: no cover
            "Renderer class requires .render_bytes() to be implemented"
        )

    @abstractmethod
    def render_file(
        self,
        diagram: TDiagram,
        output_path: Path,
        *,
        format: DiagramFormat,
        overwrite: bool = True,
    ) -> Path:
        """
        Render a Diagram and write the result to a file.


        Args:
            diagram: The diagram instance to render.
            output_path: Path where the rendered diagram should be written.
            format: Output format of the rendered diagram.
            overwrite: Whether to overwrite the output file if it already
                exists.

        Returns:
            Path to the written output file.
        """
        raise NotImplementedError(  # pragma: no cover
            "Renderer class requires .render_file() to be implemented"
        )

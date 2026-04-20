from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, ClassVar, Generic, TypeVar

from c4.diagrams.core import MISSING


@dataclass(frozen=True)
class Argument:
    """
    Represents a single argument in a macro call.

    Attributes:
        name: The argument name (e.g. 'label', 'type').
        source: The name of the attribute or data key to pull from
            the diagram element. If None, defaults to the value of `name`.
        format: Optional function used to format the value
            before rendering (e.g., quoting or escaping).
        forced_keyword: If True, this argument will always be rendered
            as a keyword argument (e.g., `$name=value`).
    """

    name: str
    source: str | None = None
    format: Callable[[Any], str] | None = None
    forced_keyword: bool = False

    @classmethod
    def keyword(
        cls,
        name: str,
        source: str | None = None,
        format: Callable[[Any], str] | None = None,  # noqa: A002
    ) -> Argument:
        return cls(
            name=name,
            source=source,
            format=format,
            forced_keyword=True,
        )


def compose(*funcs: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """
    Compose functions left-to-right.

    Example:
        formatter = compose(str, str.lower, quote)
        formatter(True) == '"true"'
    """

    def composed(value: Any) -> Any:
        for func in funcs:
            value = func(value)
        return value

    return composed


def escape(value: str) -> str:
    r"""
    Escape newline and quote characters.

    Replaces all `\n` characters with `\\n` and `"` with `\"`.
    """
    return value.replace("\n", "\\n").replace('"', '\\"')


def quote(value: str) -> str:
    """
    Wrap a string in double quotes without escaping.
    """
    return f'"{value}"'


def str_or_empty(value: str | None) -> str:
    """
    Return the string value or an empty string if the input is falsy.
    """
    if value is None:
        return ""

    return str(value)


def join_and_quote(sep: str) -> Callable[[Any], str]:
    """
    Create a formatter that joins strings with a separator and
    wraps the result in quotes.
    """

    def formatter(items: list[str]) -> str:
        return quote(f"{sep}".join(items))

    return formatter


def macro_call(value: str) -> str:
    """
    Formats the given string as a PlantUML macro call.
    """
    return f"{value}()"


bool_to_quoted_lower_or_empty: Callable[[Any], str] = compose(
    str_or_empty,
    str.lower,
    quote,
)
quote_and_lower: Callable[[Any], str] = compose(quote, str.lower)
force_str: Callable[[Any], str] = compose(str)
quote_and_escape: Callable[[Any], str] = compose(escape, quote)


_TDiagramElement = TypeVar("_TDiagramElement")


class BaseMacro(Generic[_TDiagramElement]):
    """
    Base class for rendering macros from diagram elements.

    Subclasses must define `macro` and `args`. The class can be used to render
    any diagram element into its corresponding macro syntax.

    Attributes:
        macro: The name of the macro (e.g. "Person", "Rel").
        args: Ordered list of macro arguments.
    """

    macro: ClassVar[str | None] = None
    args: ClassVar[list[Argument]] = []
    keyword_arg_prefix: ClassVar[str] = "$"

    def __init__(self, diagram_element: _TDiagramElement) -> None:
        """
        Initializes the macro wrapper for the given diagram element.

        Args:
            diagram_element: The element to render.
        """
        self._diagram_element = diagram_element

    def get_data(self) -> dict[str, Any]:
        """
        Returns a dictionary of macro args and values from the element.

        Subclasses must override this to extract values from their element.
        """
        if not self.args:
            return {}

        raise NotImplementedError(
            f"{self.__class__.__name__}.get_data() must be overridden "
            f"when 'args' are defined"
        )

    def get_macro(self) -> str | None:
        """
        Returns the name of the macro.

        Can be overridden to provide dynamic macro name resolution.
        """
        return getattr(self, "macro", None)

    def check_macro(self) -> str:
        """
        Returns the macro name or raises if it is missing.
        """
        macro = self.get_macro()

        if not macro:
            raise AttributeError(
                f"Attribute `macro` not provided for {self.__class__.__name__}"
            )

        return macro

    def render(self) -> str:
        """
        Renders the element as a macro call.

        Returns:
            Rendered macro string.
        """
        macro = self.check_macro()
        data = self.get_data()

        parts = []
        forced_keyword = False
        args = self.args or []

        if args and not data:
            raise ValueError(
                f"Cannot render macro for element "
                f"{self._diagram_element!r}: "
                f"arguments are defined ({[arg.name for arg in args]}), but "
                f"no input data was provided."
            )

        for arg in args:
            name = arg.source or arg.name

            value = data.get(name, MISSING)

            if value is None or value is MISSING:
                forced_keyword = True
                continue

            if arg.format:
                value = arg.format(value)

            if forced_keyword or arg.forced_keyword:
                parts.append(f"{self.keyword_arg_prefix}{arg.name}={value}")
                forced_keyword = True
            else:
                parts.append(f"{value}")

        return f"{macro}({', '.join(parts)})"

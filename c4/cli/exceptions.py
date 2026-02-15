from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from c4.cli.discover import Target


class CLIError(Exception):
    """
    Base class for all CLI-related errors.

    These errors are intended to be shown directly to the user
    without a full traceback.
    """

    def __init__(self, message: str) -> None:
        self.message = message

        super().__init__(message)


class TargetParseError(CLIError):
    """
    Raised when a CLI target string cannot be parsed.

    Examples of valid targets:
        - 'python.module'
        - 'python.module:diagram'
        - 'file.py'
        - 'file.py:diagram'
    """

    def __init__(self, raw: str) -> None:
        super().__init__(
            f"Invalid target {raw!r}. "
            f"Expected 'module', 'module:diagram', 'file.py', "
            f"or 'file.py:diagram'."
        )


class DiagramNotFoundError(CLIError):
    """
    Raised when a requested Diagram cannot be found.

    This may happen if:
        - The specified diagram name does not exist.
        - No Diagram instances exist in the target module.
    """

    pass


class MultipleDiagramsFoundError(CLIError):
    """
    Raised when multiple Diagram instances are found but no
    explicit diagram name was provided.

    In this case, the user must specify which diagram to use.
    """

    def __init__(self, target: Target, names: list[str]) -> None:
        self.target = target
        self.names = names

        if target.is_file:
            module_repr = f"{target.module_or_file!r}"
        else:
            module_repr = f"module {target.module_or_file!r}"

        diagrams = ", ".join(names)

        super().__init__(
            f"Multiple diagrams found in {module_repr}: {diagrams}. "
            f"Either ensure the target contains exactly one Diagram, "
            f"or specify one explicitly as "
            f"'{target.module_or_file}:<diagram_name>'."
        )


class ImportFromStringError(CLIError):
    """
    Raised when a module, file, or attribute cannot be imported
    or does not resolve to a valid Diagram instance.
    """

    pass

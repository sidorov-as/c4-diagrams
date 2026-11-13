from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from c4.cli.discover import Target
    from c4.enums import RendererEnum


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
        - 'file.json'
    """

    def __init__(self, raw: str) -> None:
        super().__init__(
            f"Invalid target {raw!r}. "
            f"Expected 'module', 'module:diagram', 'file.py', "
            f"'file.py:diagram' or 'file.json'."
        )


class RenderTargetNotFoundError(CLIError):
    """
    Raised when a requested Diagram cannot be found.

    This may happen if:
        - The specified diagram name does not exist.
        - No render targets exist in the target module.
    """

    pass


class MultipleRenderTargetsFoundError(CLIError):
    """
    Raised when multiple render targets are found but no explicit target name
    was provided.

    In this case, the user must specify which render target to use.
    """

    def __init__(self, target: Target, names: list[str]) -> None:
        self.target = target
        self.names = names

        if target.is_py_file:
            module_repr = f"{target.module_or_file!r}"
        else:
            module_repr = f"module {target.module_or_file!r}"

        targets = ", ".join(names)

        super().__init__(
            f"Multiple render targets found in {module_repr}: {targets}. "
            "Either ensure the target contains exactly one render target, "
            f"or specify one explicitly as "
            f"'{target.module_or_file}:<target_name>'."
        )


class ImportFromStringError(CLIError):
    """
    Raised when a module, file, or attribute cannot be imported
    or does not resolve to a valid render target.
    """

    pass


class RendererBackendMismatchError(CLIError):
    """
    Raised when a JSON diagram backend conflicts with a requested renderer.
    """

    def __init__(
        self,
        *,
        backend: RendererEnum,
        renderer: RendererEnum,
    ) -> None:
        super().__init__(
            f"JSON diagram backend {backend.value!r} does not match "
            f"selected renderer {renderer.value!r}."
        )


class MissingConverterDependency(CLIError):
    """
    Raised when converter cannot be imported due to missing dependencies.
    """

    def __init__(self) -> None:
        super().__init__(
            "Converter dependency is not installed, "
            "run `pip install c4-diagrams[converters]`"
        )

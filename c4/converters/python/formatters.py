import ast
from dataclasses import dataclass
from inspect import Parameter, signature
from typing import Any


@dataclass
class ChainCall:
    method: str
    args: list[ast.expr]
    keywords: list[ast.keyword]


@dataclass
class _MethodSignature:
    ordered_kwargs: list[tuple[str, Any]]
    render_single_as_positional: bool


class MethodCallFormatter:
    def __init__(
        self,
        max_line: int = 79,
        owner_cls: type[Any] | None = None,
    ) -> None:
        self._max_line = max_line
        self._indent = " " * 4
        self._nested_indent = " " * 8
        self._owner_cls = owner_cls

    @staticmethod
    def _inspect_signature(
        cls: type[Any],
        method_name: str,
        kwargs: dict[str, Any],
        positional_args: tuple[Any, ...],
    ) -> _MethodSignature:
        """
        Order kwargs according to the method signature.

        Unknown kwargs are appended at the end, preserving insertion order.

        If the method has exactly one non-self parameter and it is positional
        (not keyword-only), then a single provided kwarg for that parameter
        may be rendered as positional.
        """
        method = getattr(cls, method_name)
        sig = signature(method)

        params = [
            param
            for param in sig.parameters.values()
            if param.name not in {"self", "cls"}
        ]

        ordered_kwargs: list[tuple[str, Any]] = []
        seen: set[str] = set()

        for param in params:
            if param.name in kwargs:
                ordered_kwargs.append((param.name, kwargs[param.name]))
                seen.add(param.name)

        for name, value in kwargs.items():
            if name not in seen:
                ordered_kwargs.append((name, value))

        render_single_as_positional = False
        if len(params) == 1 and not positional_args and len(kwargs) == 1:
            param = params[0]
            if param.kind in (
                Parameter.POSITIONAL_ONLY,
                Parameter.POSITIONAL_OR_KEYWORD,
            ):
                render_single_as_positional = param.name in kwargs

        return _MethodSignature(
            ordered_kwargs=ordered_kwargs,
            render_single_as_positional=render_single_as_positional,
        )

    def format_call(
        self,
        method_name: str,
        call_args: tuple[Any, ...] | list[Any] | None = None,
        call_kwargs: dict[str, Any] | None = None,
    ) -> str:
        """
        Format a chained method call.

        Notes:
            - Arguments are rendered using `repr()` to keep output valid Python.
            - Positional args are rendered before keyword args.
            - If the method accepts exactly one positional parameter, a single
              supplied kwarg for that parameter is rendered positionally.
        """
        call_args = tuple(call_args or ())
        call_kwargs = call_kwargs or {}

        kwargs_items = list(call_kwargs.items())
        render_single_as_positional = False

        if self._owner_cls is not None:
            sig = self._inspect_signature(
                self._owner_cls,
                method_name,
                call_kwargs,
                call_args,
            )
            kwargs_items = sig.ordered_kwargs
            render_single_as_positional = sig.render_single_as_positional

        parts: list[str] = [repr(arg) for arg in call_args]

        if render_single_as_positional:
            _, value = kwargs_items[0]
            parts.append(repr(value))
        else:
            parts.extend(f"{name}={value!r}" for name, value in kwargs_items)

        return f".{method_name}({', '.join(parts)})"

    def format_chain_call(self, code: str) -> str:
        if len(code) <= self._max_line:
            return code.strip()

        tree = ast.parse(code)

        if len(tree.body) != 1 or not isinstance(tree.body[0], ast.Assign):
            raise ValueError("Expected a single module-level assignment.")

        assign = tree.body[0]
        if len(assign.targets) != 1 or not isinstance(
            assign.targets[0], ast.Name
        ):
            raise ValueError("Expected simple `name = expr` assignment.")

        lhs = assign.targets[0].id
        base, chain = self._extract_chain(assign.value)

        lines: list[str] = [f"{lhs} = (", f"{self._indent}{self._expr(base)}"]

        for call in chain:
            lines.extend(self._render_chained_call(call))

        lines.append(")")
        return "\n".join(lines)

    def _extract_chain(
        self, expr: ast.expr
    ) -> tuple[ast.expr, list[ChainCall]]:
        chain: list[ChainCall] = []
        cur: ast.expr = expr

        while isinstance(cur, ast.Call) and isinstance(cur.func, ast.Attribute):
            chain.append(
                ChainCall(
                    method=cur.func.attr,
                    args=list(cur.args),
                    keywords=list(cur.keywords),
                )
            )
            cur = cur.func.value

        chain.reverse()
        return cur, chain

    def _render_chained_call(self, call: ChainCall) -> list[str]:
        if not call.args and not call.keywords:
            return [f"{self._indent}.{call.method}()"]

        lines: list[str] = [f"{self._indent}.{call.method}("]

        for arg in call.args:
            lines.append(f"{self._nested_indent}{self._expr(arg)},")

        for kw in call.keywords:
            if kw.arg is None:
                lines.append(f"{self._nested_indent}**{self._expr(kw.value)},")
            else:
                lines.append(
                    f"{self._nested_indent}{kw.arg}={self._expr(kw.value)},"
                )

        lines.append(f"{self._indent})")
        return lines

    @staticmethod
    def _expr(node: ast.AST) -> str:
        return ast.unparse(node)

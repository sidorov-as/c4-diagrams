from __future__ import annotations

import ast
from typing import Any

import pytest

from c4.converters.python.renderers.plantuml import (
    ChainCall,
    MethodCallFormatter,
)


class Owner:
    def m(self, a: Any, b: Any, c: Any) -> None:  # pragma: no cover
        raise RuntimeError

    def defaults(
        self,
        a: Any | None = None,
        b: Any | None = None,
    ) -> None:  # pragma: no cover
        raise RuntimeError

    def single(self, a: Any) -> None:  # pragma: no cover
        raise RuntimeError

    def single_kwonly(self, *, a: Any) -> None:  # pragma: no cover
        raise RuntimeError

    @classmethod
    def cm(cls, x: Any, y: Any) -> None:  # pragma: no cover
        raise RuntimeError

    def no_args(self) -> None:
        raise RuntimeError


def test_method_call_formatter__inspect_signature__many_params():
    kwargs = {"c": 3, "a": 1, "x": 9, "b": 2}

    result = MethodCallFormatter._inspect_signature(
        Owner,
        "m",
        kwargs,
    )

    assert result.ordered_args == [("a", 1), ("b", 2), ("c", 3), ("x", 9)]
    assert result.is_single_arg is False
    assert result.is_single_kwonly_arg is False


def test_method_call_formatter__inspect_signature__no_params():
    result = MethodCallFormatter._inspect_signature(Owner, "no_args", {})

    assert result.ordered_args == []
    assert result.is_single_arg is False
    assert result.is_single_kwonly_arg is False


def test_method_call_formatter__inspect_signature__one_param():
    result = MethodCallFormatter._inspect_signature(Owner, "single", {"a": 1})

    assert result.ordered_args == [("a", 1)]
    assert result.is_single_arg is True
    assert result.is_single_kwonly_arg is False


def test_method_call_formatter__inspect_signature__defaults():
    result = MethodCallFormatter._inspect_signature(Owner, "defaults", {"a": 1})

    assert result.ordered_args == [("a", 1)]
    assert result.is_single_arg is False
    assert result.is_single_kwonly_arg is False


def test_method_call_formatter__inspect_signature__defaults_no_args():
    result = MethodCallFormatter._inspect_signature(Owner, "defaults", {})

    assert result.ordered_args == []
    assert result.is_single_arg is False
    assert result.is_single_kwonly_arg is False


def test_method_call_formatter__inspect_signature__one_kwonly_param():
    result = MethodCallFormatter._inspect_signature(
        Owner, "single_kwonly", {"a": 1}
    )

    assert result.ordered_args == [("a", 1)]
    assert result.is_single_arg is True
    assert result.is_single_kwonly_arg is True


def test_method_call_formatter__format_call_empty_args():
    formatter = MethodCallFormatter()

    result = formatter.format_call("m")

    assert result == ".m()"


def test_method_call_formatter__format_call_renders_kwargs():
    formatter = MethodCallFormatter()

    result = formatter.format_call("m", {"a": 1, "b": "x"})

    assert result == ".m(a=1, b='x')"


def test_method_call_formatter__format_call_orders_kwargs_with_owner_cls():
    formatter = MethodCallFormatter(owner_cls=Owner)
    call_args = {"c": 3, "a": 1, "b": 2}

    result = formatter.format_call("m", call_args)

    assert result == ".m(a=1, b=2, c=3)"


@pytest.mark.parametrize(
    ("method_name", "kwargs", "expected"),
    [
        (
            "m",
            {"c": 3, "a": 1, "b": 2},
            [("a", 1), ("b", 2), ("c", 3)],
        ),
        (
            "m",
            {"b": 2, "unknown": 9, "a": 1},
            [("a", 1), ("b", 2), ("unknown", 9)],
        ),
        (
            "cm",
            {"y": "Y", "x": "X"},
            [("x", "X"), ("y", "Y")],
        ),
        (
            "cm",
            {"unknown": 0, "y": "Y"},
            [("y", "Y"), ("unknown", 0)],
        ),
    ],
)
def test_method_call_formatter_inspect_signature__orders_kwargs(
    method_name: str,
    kwargs: dict[str, Any],
    expected: list[tuple[str, Any]],
):
    cls = Owner

    result = MethodCallFormatter._inspect_signature(
        cls=cls,
        method_name=method_name,
        kwargs=kwargs,
    )

    assert result.ordered_args == expected


@pytest.mark.parametrize(
    ("call_args", "expected"),
    [
        (None, ".foo()"),
        ({}, ".foo()"),
    ],
)
def test_method_call_formatter__format_call__no_args(
    call_args: dict[str, Any] | None,
    expected: str,
):
    formatter = MethodCallFormatter()

    result = formatter.format_call("foo", call_args)

    assert result == expected


def test_method_call_formatter__format_call__renders_kwargs_with_repr():
    formatter = MethodCallFormatter()

    result = formatter.format_call("m", {"a": "x", "b": 2})

    assert result == ".m(a='x', b=2)"


def test_method_call_formatter__format_call__renders_single_arg():
    formatter = MethodCallFormatter(owner_cls=Owner)

    result = formatter.format_call("single", {"a": "x"})

    assert result == ".single('x')"


def test_method_call_formatter__format_call__orders_kwargs_by_signature():
    formatter = MethodCallFormatter(owner_cls=Owner)

    result = formatter.format_call("m", {"c": 3, "a": 1, "b": 2})

    assert result == ".m(a=1, b=2, c=3)"


def test_method_call_formatter__format_call__unknown_kwargs_order():
    formatter = MethodCallFormatter(owner_cls=Owner)

    result = formatter.format_call("m", {"b": 2, "z": 9, "a": 1, "y": 8})

    assert result == ".m(a=1, b=2, z=9, y=8)"


def test_method_call_formatter__format_chain_call__stripped():
    formatter = MethodCallFormatter()
    code = "  x = 1  "

    result = formatter.format_chain_call(code)

    assert result == "x = 1"


def test_method_call_formatter__format_chain_call__non_single_assign_raises():
    formatter = MethodCallFormatter(max_line=1)
    code = "a = 1\nb = 2"

    with pytest.raises(ValueError, match="single module-level assignment"):
        formatter.format_chain_call(code)


def test_method_call_formatter__format_chain_call__non_simple_target_raises():
    formatter = MethodCallFormatter(max_line=1)
    code = "a, b = 1, 2"

    with pytest.raises(ValueError, match="Expected simple `name = expr`"):
        formatter.format_chain_call(code)


def test_method_call_formatter__extract_chain__returns_base_and_calls():
    formatter = MethodCallFormatter(max_line=79)
    expr = ast.parse("x().a(1).b(y=2)").body[0].value  # type: ignore[attr-defined]

    base, chain = formatter._extract_chain(expr)

    assert ast.unparse(base) == "x()"
    assert [c.method for c in chain] == ["a", "b"]
    assert [ast.unparse(a) for a in chain[0].args] == ["1"]
    assert [(k.arg, ast.unparse(k.value)) for k in chain[1].keywords] == [
        ("y", "2")
    ]


def test_method_call_formatter__render_chained_call__renders_args_kwargs():
    formatter = MethodCallFormatter(max_line=79)
    call = ChainCall(
        method="m",
        args=[ast.parse("1").body[0].value],  # type: ignore[attr-defined]
        keywords=[
            ast.keyword(
                arg="x",
                value=ast.parse("2").body[0].value,  # type: ignore[attr-defined]
            ),
            ast.keyword(
                arg=None,
                value=ast.parse("extra").body[0].value,  # type: ignore[attr-defined]
            ),
        ],
    )

    lines = formatter._render_chained_call(call)

    assert lines == [
        "    .m(",
        "        1,",
        "        x=2,",
        "        **extra,",
        "    )",
    ]


def test_method_call_formatter__format_chain_call__formats_long_chain_call():
    formatter = MethodCallFormatter(max_line=1)
    code = "out = Base().a(1, x=2, **extra).b('t')"

    result = formatter.format_chain_call(code)

    assert result == "\n".join([
        "out = (",
        "    Base()",
        "    .a(",
        "        1,",
        "        x=2,",
        "        **extra,",
        "    )",
        "    .b(",
        "        't',",
        "    )",
        ")",
    ])


def test_method_call_formatter__format_chain_call__fits_max_line():
    formatter = MethodCallFormatter(max_line=79)
    code = "out = Base().a(1, x=2, **extra).b('t')"

    result = formatter.format_chain_call(code)

    assert result == code

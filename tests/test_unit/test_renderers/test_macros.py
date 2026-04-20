import re
from typing import Any, ClassVar

import pytest

from c4.diagrams.core import Diagram, Element
from c4.renderers.macros import (
    Argument,
    BaseMacro,
    force_str,
    macro_call,
    quote,
    quote_and_escape,
    quote_and_lower,
    str_or_empty,
)


@pytest.fixture()
def diagram():
    with Diagram() as _diagram:
        yield _diagram


class MacroWithArgsAndNoData(BaseMacro):
    macro = "example"
    args: ClassVar[list[Argument]] = [
        Argument(name="arg1"),
    ]

    def get_data(self) -> dict[str, Any]:
        return {}


class MacroWithArgsAndData(BaseMacro):
    macro = "example"
    args: ClassVar[list[Argument]] = [
        Argument(name="arg1"),
        Argument(name="arg2", source="argument2", format=quote),
        Argument(name="arg3", format=quote_and_lower),
        Argument(name="arg4", format=quote),
        Argument(name="arg5", forced_keyword=True, format=quote),
        Argument(name="arg6", format=quote),
    ]

    def get_data(self) -> dict[str, Any]:
        return {
            "arg1": "arg1",
            "argument2": "Arg2 value",
            "arg3": "Arg3 value",
            "arg4": "Arg4 value",
            "arg5": "Arg5 value",
            "arg6": "Arg6 value",
        }


class MacroForceKeyword(MacroWithArgsAndData):
    def get_data(self) -> dict[str, Any]:
        return {
            "arg1": "arg1",
            "argument2": "Arg2 value",
            "arg4": "Arg4 value",
            "arg5": "Arg5 value",
            "arg6": "Arg6 value",
            "arg7": "Arg7 value",
        }


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("a", '"a"'),
        ('a"b', '"a\\"b"'),
        ("a\nb", '"a\\nb"'),
        ('a"\n"b', '"a\\"\\n\\"b"'),
    ],
)
def test_quote_and_escape(value: str, expected: str):
    result = quote_and_escape(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", ""),
        (None, ""),
        (True, "True"),
        (False, "False"),
    ],
)
def test_str_or_empty(value: str, expected: str):
    result = str_or_empty(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", '""'),
        ("a", '"a"'),
        ('a"b', '"a"b"'),
        ("a\nb", '"a\nb"'),
        ("  spaced  ", '"  spaced  "'),
    ],
)
def test_quote(value: str, expected: str):
    result = quote(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("", '""'),
        ("A", '"a"'),
        ("AbC", '"abc"'),
        ("A B", '"a b"'),
        ('A"b', '"a"b"'),
    ],
)
def test_quote_and_lower(value: str, expected: str):
    result = quote_and_lower(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("x", "x"),
        ("", ""),
        (0, "0"),
        (1, "1"),
        (True, "True"),
        (False, "False"),
        (None, "None"),
        (["a", 1], "['a', 1]"),
        ({"a": 1}, "{'a': 1}"),
    ],
)
def test_force_str(value: str, expected: str):
    result = force_str(value)

    assert result == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Rel", "Rel()"),
        ("", "()"),
        ("  X  ", "  X  ()"),
        ("My_Macro", "My_Macro()"),
    ],
)
def test_macro_call(value: str, expected: str):
    result = macro_call(value)

    assert result == expected


def test_base_macro_check_macro():
    class TestMacro(BaseMacro[...]):
        macro = "example"

    macro = TestMacro(...)

    result = macro.check_macro()

    assert result == "example"


def test_base_macro_get_macro():
    class TestMacro(BaseMacro[...]):
        macro = "example"

    macro = TestMacro(...)

    result = macro.get_macro()

    assert result == "example"


def test_base_macro_get_macro_not_provided():
    class TestMacro(BaseMacro[...]): ...

    macro = TestMacro(...)

    result = macro.get_macro()

    assert result is None


def test_base_macro_check_macro_not_provided_error():
    class TestMacro(BaseMacro[...]): ...

    macro = TestMacro(...)
    expected_error = "Attribute `macro` not provided for TestMacro"

    with pytest.raises(AttributeError, match=expected_error):
        macro.check_macro()


def test_base_macro_get_data_no_args():
    class TestMacro(BaseMacro[...]): ...

    macro = TestMacro(...)

    result = macro.get_data()

    assert result == {}


def test_base_macro_get_data_not_implemented_error():
    class TestMacro(BaseMacro[...]):
        macro = "example"
        args: ClassVar[list[Argument]] = [
            Argument(name="arg1"),
        ]

    macro = TestMacro(...)
    expected_error = re.escape(
        "TestMacro.get_data() must be overridden when 'args' are defined"
    )

    with pytest.raises(NotImplementedError, match=expected_error):
        macro.get_data()


@pytest.mark.usefixtures("diagram")
def test_macro_render_args_and_no_data_error():
    element = Element(label="example")
    macro = MacroWithArgsAndNoData(element)
    expected_error = re.escape(
        f"Cannot render macro for element "
        f"{element!r}: "
        f"arguments are defined (['arg1']), but "
        f"no input data was provided."
    )

    with pytest.raises(ValueError, match=expected_error):
        macro.render()

    def get_data(self) -> dict[str, Any]:
        return {
            "arg1": "arg1",
            "argument2": "Arg2 value",
            "arg3": "Arg3 value",
            "arg4": "Arg4 value",
            "arg5": "Arg5 value",
            "arg6": "Arg6 value",
        }


@pytest.mark.usefixtures("diagram")
def test_base_macro_render():
    element = Element(label="example")
    macro = MacroWithArgsAndData(element)
    expected_result = (
        'example(arg1, "Arg2 value", "arg3 value", "Arg4 value", '
        '$arg5="Arg5 value", $arg6="Arg6 value")'
    )

    result = macro.render()

    assert result == expected_result


@pytest.mark.usefixtures("diagram")
def test_base_macro_render_force_keyword():
    element = Element(label="example")
    macro = MacroForceKeyword(element)
    expected_result = (
        'example(arg1, "Arg2 value", $arg4="Arg4 value", '
        '$arg5="Arg5 value", $arg6="Arg6 value")'
    )

    result = macro.render()

    assert result == expected_result

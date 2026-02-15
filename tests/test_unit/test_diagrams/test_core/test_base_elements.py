import re

import pytest

from c4.diagrams.core import (
    BaseDiagramElement,
    BaseIndex,
    Diagram,
    Index,
    LastIndex,
    SetIndex,
    increment,
    set_index,
)


@pytest.mark.parametrize(
    ("obj", "expected"),
    [
        (LastIndex(), "LastIndex()"),
        (Index(), "Index()"),
        (Index(3), "Index(3)"),
        (SetIndex(7), "SetIndex(7)"),
    ],
)
def test_index_str_without_prefix_or_suffix(
    obj: BaseIndex,
    expected: str,
) -> None:
    result = str(obj)
    assert result == expected


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        ("1+" + LastIndex(), "1+LastIndex()"),
        ("2+" + Index(), "2+Index()"),
        ("1-" + Index(3), "1-Index(3)"),
        ("3+" + SetIndex(7), "3+SetIndex(7)"),
        (LastIndex() + "-1", "LastIndex()-1"),
        (Index() + "-1", "Index()-1"),
        (Index(3) + "-1", "Index(3)-1"),
        (SetIndex(7) + "-1", "SetIndex(7)-1"),
        ("2+" + Index(3) + "-1", "2+Index(3)-1"),
    ],
)
def test_index_str_with_prefix_and_or_suffix(
    expr: BaseIndex,
    expected: str,
) -> None:
    result = str(expr)
    assert result == expected


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (LastIndex() + 1, "LastIndex()+1"),
        (Index() + 1, "Index()+1"),
        (Index(3) + 1, "Index(3)+1"),
        (SetIndex(7) + 1, "SetIndex(7)+1"),
        (Index() - 2, "Index()-2"),
        (Index(3) - 2, "Index(3)-2"),
        (SetIndex(7) - 2, "SetIndex(7)-2"),
        (Index() + 1 - 2 + 3, "Index()+1-2+3"),
        ("2+" + Index(3) + 1 + "-1", "2+Index(3)+1-1"),
        ("P" + Index() + 0, "PIndex()+0"),
    ],
)
def test_index_str_with_arithmetic_operations(
    expr: BaseIndex,
    expected: str,
) -> None:
    result = str(expr)
    assert result == expected


@pytest.mark.parametrize("index_class", [BaseIndex, Index, LastIndex, SetIndex])
def test_index_add_rejects_empty_string(
    index_class: type[BaseIndex],
) -> None:
    idx = index_class() if index_class is not SetIndex else SetIndex(0)
    expected_error = re.escape(
        f"{index_class.__name__}.__add__() requires non-empty string"
    )

    with pytest.raises(TypeError, match=expected_error):
        idx + ""  # type: ignore[operator]


@pytest.mark.parametrize(
    ("other",),
    [
        (None,),
        ([],),
        ({},),
        ((),),
        (0.5,),
        (object(),),
    ],
)
@pytest.mark.parametrize("index_class", [BaseIndex, Index, LastIndex, SetIndex])
def test_index_add_rejects_invalid_type(
    other: object,
    index_class: type[BaseIndex],
) -> None:
    idx = index_class() if index_class is not SetIndex else SetIndex(0)
    expected_error = re.escape(
        f"{index_class.__name__}.__add__() requires str or int, got {other!r}"
    )

    with pytest.raises(TypeError, match=expected_error):
        idx + other  # type: ignore[operator]


@pytest.mark.parametrize(
    ("other",),
    [
        (None,),
        (0,),
        ([],),
        ({},),
        ((),),
        ("",),
    ],
)
@pytest.mark.parametrize("index_class", [BaseIndex, Index, LastIndex, SetIndex])
def test_index_radd_rejects_non_empty_string_requirement(
    other: object,
    index_class: type[BaseIndex],
) -> None:
    idx = index_class() if index_class is not SetIndex else SetIndex(0)
    expected_error = re.escape(
        f"{index_class.__name__}.__add__() requires non-empty string"
    )

    with pytest.raises(TypeError, match=expected_error):
        other + idx  # type: ignore[operator]


@pytest.mark.parametrize(
    ("other",),
    [
        (None,),
        ("1",),
        (0.5,),
        ([],),
        ({},),
        ((),),
        (object(),),
    ],
)
@pytest.mark.parametrize("index_class", [BaseIndex, Index, LastIndex, SetIndex])
def test_index_sub_rejects_non_int(
    other: object,
    index_class: type[BaseIndex],
) -> None:
    idx = index_class() if index_class is not SetIndex else SetIndex(0)
    expected_error = re.escape(
        f"{index_class.__name__}.__sub__() requires int, got {other!r}"
    )

    with pytest.raises(TypeError, match=expected_error):
        idx - other  # type: ignore[operator]


@pytest.mark.parametrize("index_class", [BaseIndex, Index, LastIndex])
def test_index_add_rejects_setting_suffix_twice(
    index_class: type[BaseIndex],
) -> None:
    idx = index_class()
    idx = idx + "-1"
    expected_error = re.escape(
        f"Operation not allowed. "
        f"Use a new {index_class.__name__}() instance instead"
    )

    with pytest.raises(ValueError, match=expected_error):
        idx + "-2"


def test_set_index_add_rejects_setting_suffix_twice() -> None:
    idx = SetIndex(0)
    idx = idx + "-1"
    expected_error = re.escape(
        "Operation not allowed. Use a new SetIndex() instance instead"
    )

    with pytest.raises(ValueError, match=expected_error):
        idx + "-2"


@pytest.mark.parametrize("index_class", [BaseIndex, Index, LastIndex])
def test_index_radd_rejects_setting_prefix_twice(
    index_class: type[BaseIndex],
) -> None:
    idx = index_class()
    idx = "1+" + idx
    expected_error = re.escape(
        f"Operation not allowed. "
        f"Use a new {index_class.__name__}() instance instead"
    )

    with pytest.raises(ValueError, match=expected_error):
        "2+" + idx


def test_set_index_radd_rejects_setting_prefix_twice() -> None:
    idx = SetIndex(0)
    idx = "1+" + idx
    expected_error = re.escape(
        "Operation not allowed. Use a new SetIndex() instance instead"
    )

    with pytest.raises(ValueError, match=expected_error):
        "2+" + idx


@pytest.mark.parametrize(
    ("index", "expected_signature"),
    [
        (BaseIndex(), ""),
        (Index(), ""),
        (Index(offset=1), "1"),
        (LastIndex(), ""),
        (SetIndex(5), "5"),
    ],
)
def test_index_get_signature(
    index: BaseIndex,
    expected_signature: str,
) -> None:
    assert index.get_signature() == expected_signature


def test_create_increment_outside_the_diagram_context():
    expected_error = "Element must be created within a diagram context"

    with pytest.raises(ValueError, match=expected_error):
        increment()


def test_increment_adds_itself_to_diagram():
    with Diagram() as diagram:
        inc = increment()

    assert diagram.base_elements == [inc]
    assert inc.offset == 1


def test_increment_with_offset():
    with Diagram() as diagram:
        inc = increment(5)

    assert diagram.base_elements == [inc]
    assert inc.offset == 5


def test_create_set_index_outside_the_diagram_context():
    expected_error = "Element must be created within a diagram context"

    with pytest.raises(ValueError, match=expected_error):
        set_index(0)


def test_set_index_adds_itself_to_diagram():
    with Diagram() as diagram:
        inc = set_index(1)

    assert diagram.base_elements == [inc]
    assert inc.new_index == 1


def test_create_base_diagram_element_outside_the_diagram_context():
    expected_error = "Element must be created within a diagram context"

    with pytest.raises(ValueError, match=expected_error):
        BaseDiagramElement()


def test_base_diagram_element_adds_itself_to_diagram():
    with Diagram() as diagram:
        base_element = BaseDiagramElement()

    assert diagram.base_elements == [base_element]


def test_base_diagram_element_add_property(diagram: Diagram):
    base_element = BaseDiagramElement()
    show_header_before = base_element.properties.show_header
    header_before = base_element.properties.header
    properties_before = list(base_element.properties.properties)

    base_element.add_property("Property Name", "Property Value")

    assert show_header_before is True
    assert base_element.properties.show_header is True
    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]
    assert properties_before == []
    assert base_element.properties.properties == [
        ["Property Name", "Property Value"]
    ]


def test_base_diagram_element_add_property_header_len_mismatch_error(
    diagram: Diagram,
):
    base_element = BaseDiagramElement()
    show_header_before = base_element.properties.show_header
    header_before = base_element.properties.header
    properties_before = list(base_element.properties.properties)
    expected_error = "The number of values does not match the header length"

    with pytest.raises(ValueError, match=expected_error):
        base_element.add_property("Property Name")

    assert show_header_before is True
    assert base_element.properties.show_header is True
    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]
    assert properties_before == []
    assert base_element.properties.properties == []


def test_base_diagram_element_add_properties(diagram: Diagram):
    base_element = BaseDiagramElement()
    show_header_before = base_element.properties.show_header
    header_before = base_element.properties.header
    base_element.add_property("Property 1", "Property 1 Value")
    properties_before = list(base_element.properties.properties)

    base_element.add_property("Property 2", "Property 2 Value")

    assert show_header_before is True
    assert base_element.properties.show_header is True
    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]
    assert properties_before == [["Property 1", "Property 1 Value"]]
    assert base_element.properties.properties == [
        ["Property 1", "Property 1 Value"],
        ["Property 2", "Property 2 Value"],
    ]


def test_base_diagram_element_without_property_header(diagram: Diagram):
    base_element = BaseDiagramElement()

    base_element.without_property_header()

    assert base_element.properties.show_header is False


def test_base_diagram_element_set_property_header(diagram: Diagram):
    base_element = BaseDiagramElement()
    header_before = base_element.properties.header

    base_element.set_property_header("Key", "Value")

    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Key", "Value"]


def test_base_diagram_element_set_property_header_error(diagram: Diagram):
    base_element = BaseDiagramElement()
    header_before = base_element.properties.header
    base_element.add_property("Property 1", "Property 1 Value")
    expected_error = re.escape(
        "Cannot change header after properties have been added. "
        "Set the header before calling add_property()."
    )

    with pytest.raises(ValueError, match=expected_error):
        base_element.set_property_header("Key", "Value")

    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]


def test_base_diagram_element_set_empty_property_header_error(diagram: Diagram):
    base_element = BaseDiagramElement()
    header_before = base_element.properties.header
    expected_error = "The header cannot be empty"

    with pytest.raises(ValueError, match=expected_error):
        base_element.set_property_header()

    assert header_before == ["Property", "Value"]
    assert base_element.properties.header == ["Property", "Value"]

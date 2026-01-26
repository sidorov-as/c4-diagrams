from c4.diagrams.core import EmptyStr, Required, empty, not_provided


def test_empty_str_repr():
    empty_str = EmptyStr()

    assert repr(empty_str) == "<EmptyStr>"
    assert empty_str == ""


def test_empty_comparison():
    alias = empty

    assert alias is empty


def test_required_repr():
    required = Required()

    assert repr(required) == "<Required>"
    assert required == ""


def test_not_provided_comparison():
    alias = not_provided

    assert alias is not_provided

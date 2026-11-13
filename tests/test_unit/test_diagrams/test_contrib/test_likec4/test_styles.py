import pytest

from c4.contrib.likec4._styles import parse_element_style


def test_opacity_rejects_bool():
    with pytest.raises(TypeError, match="not a bool"):
        parse_element_style(opacity=True)


@pytest.mark.parametrize("value", ["abc", None, "5.5%"])
def test_opacity_rejects_non_integer(value):
    with pytest.raises(ValueError, match="integer percentage"):
        parse_element_style(opacity=value)


def test_opacity_accepts_percent_string():
    assert parse_element_style(opacity="40%") == {"opacity": 40}


def test_multiple_must_be_bool():
    with pytest.raises(TypeError, match="multiple must be a bool"):
        parse_element_style(multiple="yes")


@pytest.mark.parametrize("value", ["", 3])
def test_icon_must_be_non_empty_string(value):
    with pytest.raises(TypeError, match="icon must be a non-empty string"):
        parse_element_style(icon=value)

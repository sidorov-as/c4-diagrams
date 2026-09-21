import pytest

from c4.contrib.likec4.renderer import (
    escape_likec4_markdown,
    escape_likec4_string,
    quote_likec4_markdown,
    quote_likec4_string,
)


def test_string_escapes_quotes_and_backslashes():
    assert escape_likec4_string('a"b\\c') == 'a\\"b\\\\c'
    assert quote_likec4_string('say "hi"') == '"say \\"hi\\""'


def test_markdown_escapes_link_syntax():
    assert escape_likec4_markdown("see [[cloud.api]]") == (
        "see \\[\\[cloud.api]]"
    )
    assert escape_likec4_markdown("[single]") == "[single]"


@pytest.mark.parametrize(
    ("text", "quoted"),
    [
        ("plain", "'''plain'''"),
        ("[[a.b]]", "'''\\\\[\\\\[a.b]]'''"),
        ("it's", "'''it\\'s'''"),
        ("back\\slash", "'''back\\\\slash'''"),
    ],
)
def test_markdown_quoting(text, quoted):
    assert quote_likec4_markdown(text) == quoted

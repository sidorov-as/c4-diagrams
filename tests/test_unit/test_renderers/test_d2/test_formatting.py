from c4.renderers.d2.formatting import (
    D2StringBuilder,
    d2_label,
    d2_markdown_value,
    escape_d2_string,
    is_d2_markdown_value,
    quote_d2_string,
)


def test_escape_d2_string_escapes_quotes_newlines_and_backslashes():
    value = 'Customer says "hi"\nPath: C:\\tmp'

    assert escape_d2_string(value) == (
        'Customer says \\"hi\\"\\nPath: C:\\\\tmp'
    )


def test_escape_d2_string_escapes_control_characters():
    value = "first\rsecond\tthird"

    assert escape_d2_string(value) == "first\\rsecond\\tthird"


def test_quote_d2_string_wraps_escaped_text():
    assert quote_d2_string('API: "v1"') == '"API: \\"v1\\""'


def test_d2_label_keeps_punctuation():
    assert d2_label("Payments API: v1.0!") == '"Payments API: v1.0!"'


def test_d2_label_adds_technology_as_multiline_label():
    assert d2_label("Payments API", "Python/FastAPI") == (
        '"Payments API\\n[Python/FastAPI]"'
    )


def test_d2_label_can_omit_technology():
    assert (
        d2_label(
            "Payments API",
            "Python/FastAPI",
            include_technology=False,
        )
        == '"Payments API"'
    )


def test_d2_markdown_value_formats_raw_markdown_block():
    result = d2_markdown_value("## API\n\n| Property | Value |")

    assert result == "\n".join([
        "||md",
        "  ## API",
        "",
        "  | Property | Value |",
        "||",
    ])
    assert is_d2_markdown_value(result)


def test_d2_string_builder_indents_multiline_values():
    builder = D2StringBuilder()

    with builder.block("api"):
        builder.add(f"label: {d2_markdown_value('## API')}")

    assert builder.get_result() == "\n".join([
        "api: {",
        "  label: ||md",
        "    ## API",
        "  ||",
        "}",
    ])


def test_d2_string_builder_adds_indented_lines_and_nested_blocks():
    builder = D2StringBuilder()

    builder.add("direction: right")
    with builder.block("store"):
        builder.add('label: "Store"')
        with builder.block("api"):
            builder.add('label: "API"')
    builder.add("customer -> store.api")

    assert builder.get_result() == "\n".join([
        "direction: right",
        "store: {",
        '  label: "Store"',
        "  api: {",
        '    label: "API"',
        "  }",
        "}",
        "customer -> store.api",
    ])


def test_d2_string_builder_preserves_blank_lines():
    builder = D2StringBuilder()

    builder.add("first")
    builder.add()
    builder.add("second")

    assert builder.lines == ["first", "", "second"]

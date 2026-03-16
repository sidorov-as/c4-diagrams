import pytest

from c4.diagrams.core import AliasGenerator


@pytest.fixture
def alias_generator() -> AliasGenerator:
    return AliasGenerator()


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("My Label", "my_label"),
        ("My-Label", "my_label"),
        ("My Label-Here", "my_label_here"),
        ("MiXeD CaSe", "mixed_case"),
        ("a b-c d", "a_b_c_d"),
    ],
)
def test_alias_generator__normalize(label: str, expected: str):
    result = AliasGenerator._normalize(label)

    assert result == expected


def test_alias_generator__generate__returns_explicit_alias(
    alias_generator: AliasGenerator,
):
    result = alias_generator.generate(label="Anything", alias="custom")

    assert result == "custom"


def test_alias_generator__generate__raises_on_duplicate_explicit_alias(
    alias_generator: AliasGenerator,
):
    alias_generator.generate(label="Anything", alias="custom")

    with pytest.raises(ValueError, match=r"Alias 'custom' already exists\."):
        alias_generator.generate(label="Something else", alias="custom")


def test_alias_generator__generate__auto_alias_returns_base_first_time(
    alias_generator: AliasGenerator,
):
    result = alias_generator.generate(label="My Label")

    assert result == "my_label"


@pytest.mark.parametrize(
    ("calls", "expected"),
    [
        (2, "my_label_1"),
        (3, "my_label_2"),
        (4, "my_label_3"),
    ],
)
def test_alias_generator__generate__auto_alias_increments_counter(
    alias_generator: AliasGenerator,
    calls: int,
    expected: str,
):
    for _ in range(calls - 1):
        alias_generator.generate(label="My Label")

    result = alias_generator.generate(label="My Label")

    assert result == expected


def test_alias_generator__generate__explicit_alias_inc_auto_alias(
    alias_generator: AliasGenerator,
):
    alias_generator.generate(label="My Label")
    alias_generator.generate(label="Anything", alias="my_label_1")

    result = alias_generator.generate(label="My Label")

    assert result == "my_label_2"


def test_alias_generator__generate__explicit_alias_does_not_affect_for_label(
    alias_generator: AliasGenerator,
):
    alias_generator.generate(label="Anything", alias="custom")

    result = alias_generator.generate(label="My Label")

    assert result == "my_label"


def test_alias_generator__generate__raises_when_alias_equals_used_auto_alias(
    alias_generator: AliasGenerator,
):
    alias_generator.generate(label="My Label")

    with pytest.raises(ValueError, match=r"Alias 'my_label' already exists\."):
        alias_generator.generate(label="Anything", alias="my_label")

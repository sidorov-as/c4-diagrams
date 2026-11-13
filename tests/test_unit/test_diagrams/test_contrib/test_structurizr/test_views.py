from __future__ import annotations

import pytest

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr._views import (
    RawSelector,
    ViewTag,
    dsl_literal,
    normalize_animation,
    normalize_view_selectors,
    view_selector,
)


def test_view_selectors__normalize_literals_tags_and_native_elements():
    system = Workspace().model.SoftwareSystem("Payments", alias="payments")

    assert normalize_view_selectors(system) == ("payments",)
    assert normalize_view_selectors([
        system,
        RawSelector("*"),
        ViewTag("Tier 1"),
    ]) == (
        "payments",
        "*",
        'element.tag=="Tier 1"',
    )
    assert dsl_literal("Public") == "Public"
    assert dsl_literal('Line\n"Break"') == '"Line\\n\\"Break\\""'


def test_normalize_animation__accepts_single_selector_or_grouped_steps():
    system = Workspace().model.SoftwareSystem("Payments", alias="payments")

    assert normalize_animation(system) == (("payments",),)
    assert normalize_animation([["customer", system], "database"]) == (
        ("customer", "payments"),
        ("database",),
    )


def test_view_selector__rejects_unsupported_values():
    with pytest.raises(
        TypeError, match="Unsupported Structurizr view selector"
    ):
        view_selector(object())

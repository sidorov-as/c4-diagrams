from __future__ import annotations

import pytest

from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr._metadata import normalize_structurizr_tags


def test_native_metadata__dedupes_tags_and_merges_properties_and_styles():
    system = Workspace().model.SoftwareSystem("Payments")

    system.tag("Critical", "Critical", "Tier 1").tag("Critical")
    system.property("owner", "platform").property("tier", 1)
    system.style(background="#123456").style(color="#ffffff")

    assert system.tags == ("Critical", "Tier 1")
    assert system.properties == {"owner": "platform", "tier": 1}
    assert system.style_properties == {
        "background": "#123456",
        "color": "#ffffff",
    }


def test_native_metadata__empty_mutations_keep_empty_direct_values():
    system = Workspace().model.SoftwareSystem("Payments")

    system.tag().style()

    assert system.tags == ()
    assert system.properties == {}
    assert system.style_properties == {}
    assert system.url is None


def test_normalize_structurizr_tags__rejects_invalid_values():
    for tags in ("Critical", {"Critical"}, ["Critical", object()]):
        with pytest.raises(TypeError, match="list\\[str\\] or None"):
            normalize_structurizr_tags(tags)

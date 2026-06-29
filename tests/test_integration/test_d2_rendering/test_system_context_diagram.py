from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    Person,
    Rel,
    System,
    SystemContextDiagram,
    SystemDbExt,
    SystemQueue,
)

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_system_context_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with SystemContextDiagram(title="Internet Banking Context") as diagram:
        customer = Person("Customer", alias="customer")
        banking = System("Internet Banking", alias="banking")
        audit = SystemDbExt("Audit Store", alias="audit_store")
        events = SystemQueue("Domain Events", alias="domain_events")

        customer >> Rel("Uses", technology="HTTPS") >> banking
        banking >> Rel("Writes audit events", technology="JSON") >> audit
        banking >> "Publishes" >> events

    assert_match_snapshot(
        snapshot_name="d2/system_context_diagram.d2",
        diagram_code=diagram.as_d2(),
    )

from __future__ import annotations

from typing import TYPE_CHECKING

from c4 import (
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    System,
    SystemExt,
    SystemLandscapeDiagram,
)

if TYPE_CHECKING:  # pragma: no cover
    from tests.conftest import AssertMatchSnapshot


def test_render_system_landscape_diagram(
    assert_match_snapshot: AssertMatchSnapshot,
):
    with SystemLandscapeDiagram(title="Big Bank Landscape") as diagram:
        customer = Person(
            "Personal Banking Customer",
            "A customer of the bank.",
            alias="customer",
        )

        with EnterpriseBoundary("Big Bank", alias="big_bank"):
            banking = System(
                "Internet Banking System",
                "Allows customers to view account information.",
                alias="banking",
            )
            support = PersonExt(
                "Customer Support",
                "External support team.",
                alias="support",
            )

        email = SystemExt(
            "Email System",
            "External email service.",
            alias="email",
        )

        customer >> Rel("Uses", technology="HTTPS") >> banking
        support >> "Helps with" >> banking
        banking >> "Sends email using" >> email

    assert_match_snapshot(
        snapshot_name="d2/system_landscape_diagram.d2",
        diagram_code=diagram.as_d2(),
    )

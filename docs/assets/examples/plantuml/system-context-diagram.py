from c4 import (
    EnterpriseBoundary,
    LayD,
    LayR,
    Person,
    PersonExt,
    Rel,
    System,
    SystemContextDiagram,
    SystemExt,
)
from c4.renderers import RenderOptions
from c4.renderers.plantuml import LayoutOptions

with SystemContextDiagram(title="Retail Platform") as diagram:
    customer = Person(
        "Customer",
        "Places orders through the storefront.",
        tags=["Primary"],
        alias="customer",
    )
    support_agent = PersonExt(
        "Support Agent",
        "Handles issues in an external CRM.",
        tags=["External"],
        alias="support_agent",
    )
    payment_gateway = SystemExt(
        "Payment Gateway",
        "Processes card payments.",
        tags=["External"],
        alias="payment_gateway",
    )
    crm_platform = SystemExt(
        "CRM Platform",
        "External CRM used by support agents.",
        tags=["External"],
        alias="crm_platform",
    )
    with EnterpriseBoundary(
        "Acme Corp",
        "Internal systems owned by Acme.",
        tags=["Enterprise"],
        alias="acme_enterprise",
    ):
        retail_platform = System(
            "Retail Platform",
            "Core platform for catalog, checkout, and order management.",
            tags=["Core"],
            link="https://retail.example.com",
            alias="retail_platform",
        )

    (
        customer
        >> Rel(
            "Browses and places orders",
            technology="HTTPS",
            tags=["Synchronous"],
        )
        >> retail_platform
    )
    (
        retail_platform
        >> Rel("Charges card", technology="REST API", tags=["Synchronous"])
        >> payment_gateway
    )
    (
        support_agent
        >> Rel("Manages customer issues", technology="Web UI", tags=["Manual"])
        >> crm_platform
    )
    LayR(customer, retail_platform)
    LayR(retail_platform, payment_gateway)
    LayD(support_agent, crm_platform)


plantuml_layout_options = (
    LayoutOptions()
    .layout_left_right(
        with_legend=True,
    )
    .show_legend(
        hide_stereotype=False,
        details="Normal",
    )
    .update_legend_title(
        "System Context",
    )
    .add_person_tag(
        tag_stereo="Primary",
        shadowing=False,
        sprite="person",
        legend_text="Primary user",
    )
    .add_external_person_tag(
        tag_stereo="External",
        shadowing=False,
        sprite="person",
        legend_text="External person",
    )
    .add_system_tag(
        tag_stereo="Core",
        shadowing=False,
        sprite="server",
        legend_text="Core internal system",
    )
    .add_external_system_tag(
        tag_stereo="External",
        shadowing=False,
        sprite="cloud",
        legend_text="External dependency",
    )
    .add_boundary_tag(
        tag_stereo="Enterprise",
        shadowing=False,
        legend_text="Enterprise boundary",
    )
    .add_rel_tag(
        tag_stereo="Synchronous",
        legend_text="Synchronous integration",
    )
    .add_rel_tag(
        tag_stereo="Manual",
        legend_text="Manual interaction",
    )
    .build()
)

render_options = RenderOptions(
    plantuml=plantuml_layout_options,
)

diagram.render_options = render_options

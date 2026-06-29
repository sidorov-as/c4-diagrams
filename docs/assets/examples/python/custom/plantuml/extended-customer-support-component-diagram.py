from __future__ import annotations

from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentExt,
    ComponentQueue,
    Person,
    Rel,
)
from c4.renderers import (
    PlantUMLRenderOptionsBuilder,
)


def plantuml_attrs(tag: str) -> dict[str, object]:
    return {"plantuml": {"tags": [tag]}}


def plantuml_rel(tag: str) -> dict[str, object]:
    return {"plantuml": {"tags": [tag]}}


with ComponentDiagram(
    title="Customer Support System - Extended Component View",
) as diagram:
    admin_api = Component(
        "Admin API",
        "User management and reference-data management.",
        technology="Container Service",
        alias="admin_api",
        **plantuml_attrs("Backend"),
    )
    admin_portal = Component(
        "Admin Portal",
        "Manages system users and reference data.",
        technology="Single-page Application",
        alias="admin_portal",
        **plantuml_attrs("Frontend"),
    )
    administrator = Person(
        "Administrator",
        "Internal user with administrative access.",
        alias="administrator",
        **plantuml_attrs("User"),
    )
    analytics_api = Component(
        "Analytics API",
        "Ticket status reports, survey analysis and performance reports.",
        technology="Container Service",
        alias="analytics_api",
        **plantuml_attrs("Backend"),
    )
    api_gateway = Component(
        "API Gateway",
        "Performs access control, security checks and request routing.",
        technology="Container Service",
        alias="api_gateway",
        **plantuml_attrs("Gateway"),
    )
    auth0 = ComponentExt(
        "Auth0",
        "External identity provider for authentication.",
        technology="OIDC/OAuth2",
        alias="auth0",
        **plantuml_attrs("External"),
    )
    billing_api = Component(
        "Billing API",
        "Billing management and financial reports.",
        technology="Container Service",
        alias="billing_api",
        **plantuml_attrs("Backend"),
    )
    billing_portal = Component(
        "Billing Portal",
        "Supports billing processing.",
        technology="Single-page Application",
        alias="billing_portal",
        **plantuml_attrs("Frontend"),
    )
    customer = Person(
        "Customer",
        "Owner of electronic equipment and support plan; reports issues.",
        alias="customer",
        **plantuml_attrs("User"),
    )
    customer_api = Component(
        "Customer API",
        "Handles registration, profiles, tickets, surveys and billing history.",
        technology="Container Service",
        alias="customer_api",
        **plantuml_attrs("Backend"),
    )
    customer_notifications_queue = ComponentQueue(
        "Customer Notifications",
        "Asynchronous message channel for customer notifications.",
        technology="Message Queue",
        alias="customer_notifications_queue",
        **plantuml_attrs("Queue"),
    )
    customer_portal = Component(
        "Customer Portal",
        "Provides access to customer profile, billing, ticket creation and history.",
        technology="Single-page Application",
        alias="customer_portal",
        **plantuml_attrs("Frontend"),
    )
    email_system = ComponentExt(
        "E-mail System",
        "Internal mail system used for e-mail delivery.",
        technology="SMTP",
        alias="email_system",
        **plantuml_attrs("External"),
    )
    expert_notifications_queue = ComponentQueue(
        "Expert Notifications",
        "Asynchronous message channel for expert notifications.",
        technology="Message Queue",
        alias="expert_notifications_queue",
        **plantuml_attrs("Queue"),
    )
    helpdesk = Person(
        "Helpdesk",
        "First line of support; provides direct phone support.",
        alias="helpdesk",
        **plantuml_attrs("User"),
    )
    helpdesk_portal = Component(
        "Helpdesk Portal",
        "Provides access to tickets and status.",
        technology="Single-page Application",
        alias="helpdesk_portal",
        **plantuml_attrs("Frontend"),
    )
    invoice_queue = ComponentQueue(
        "Invoice",
        "Asynchronous message channel for invoice processing.",
        technology="Message Queue",
        alias="invoice_queue",
        **plantuml_attrs("Queue"),
    )
    knowledge_base = Component(
        "Knowledge Base",
        "Supports searching and updating knowledge-base articles.",
        technology="Single-page Application",
        alias="knowledge_base",
        **plantuml_attrs("Frontend"),
    )
    manager = Person(
        "Manager",
        "Monitors expert performance and customer satisfaction.",
        alias="manager",
        **plantuml_attrs("User"),
    )
    mobile_app = Component(
        "Mobile App",
        "Provides access to assigned tickets and knowledge-base search.",
        technology="iOS / Android App",
        alias="mobile_app",
        **plantuml_attrs("Frontend"),
    )
    notification_service = Component(
        "Notification Service",
        "Sends SMS and e-mail messages based on notification preferences.",
        technology="Container Service",
        alias="notification_service",
        **plantuml_attrs("Backend"),
    )
    payment_job = Component(
        "Payment",
        "Runs monthly and performs payment operations.",
        technology="Container Job",
        alias="payment_job",
        **plantuml_attrs("Worker"),
    )
    payment_provider = ComponentExt(
        "Payment Service Provider",
        "External online payment service.",
        technology="HTTPS/API",
        alias="payment_provider",
        **plantuml_attrs("External"),
    )
    sms_provider = ComponentExt(
        "SMS Service Provider",
        "Provides SMS text messaging.",
        technology="SMS API",
        alias="sms_provider",
        **plantuml_attrs("External"),
    )
    support_api = Component(
        "Support API",
        "Ticket orchestration, search, assignment handling and knowledge-base updates.",
        technology="Container Service",
        alias="support_api",
        **plantuml_attrs("Backend"),
    )
    support_dashboard = Component(
        "Support Dashboard",
        "Provides analytics and operational reports.",
        technology="Single-page Application",
        alias="support_dashboard",
        **plantuml_attrs("Frontend"),
    )
    support_database = ComponentDb(
        "Support Database",
        "Stores tickets, users, customer contacts and knowledge-base content.",
        technology="Relational Database",
        alias="support_database",
        **plantuml_attrs("Database"),
    )
    support_expert = Person(
        "Support Expert",
        "Technology expert who fixes customer electronic devices.",
        alias="support_expert",
        **plantuml_attrs("User"),
    )
    ticket_assigned_queue = ComponentQueue(
        "Ticket Assigned",
        "Asynchronous message channel for assigned tickets.",
        technology="Message Queue",
        alias="ticket_assigned_queue",
        **plantuml_attrs("Queue"),
    )
    ticket_created_queue = ComponentQueue(
        "Ticket Created",
        "Asynchronous message channel for created tickets.",
        technology="Message Queue",
        alias="ticket_created_queue",
        **plantuml_attrs("Queue"),
    )
    ticket_progress_queue = ComponentQueue(
        "Ticket In-Progress/Closed",
        "Asynchronous message channel for ticket progress and closure notifications.",
        technology="Message Queue",
        alias="ticket_progress_queue",
        **plantuml_attrs("Queue"),
    )
    ticket_processor = Component(
        "Ticket Processor",
        "Runs periodically, scans ticket statuses, and creates assignments.",
        technology="Container Job",
        alias="ticket_processor",
        **plantuml_attrs("Worker"),
    )

    (
        admin_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            **plantuml_rel("DataAccess"),
        )
        >> support_database
    )
    (
        admin_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            **plantuml_rel("Sync"),
        )
        >> api_gateway
    )
    (
        analytics_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            **plantuml_rel("DataAccess"),
        )
        >> support_database
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            **plantuml_rel("Sync"),
        )
        >> customer_api
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            **plantuml_rel("Sync"),
        )
        >> support_api
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            **plantuml_rel("Sync"),
        )
        >> admin_api
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            **plantuml_rel("Sync"),
        )
        >> billing_api
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            **plantuml_rel("Sync"),
        )
        >> analytics_api
    )
    (
        billing_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            **plantuml_rel("DataAccess"),
        )
        >> support_database
    )
    (
        billing_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            **plantuml_rel("Sync"),
        )
        >> api_gateway
    )
    (
        customer_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            **plantuml_rel("DataAccess"),
        )
        >> support_database
    )
    (
        customer_api
        >> Rel(
            "Sends ticket created event",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> ticket_created_queue
    )
    (
        customer_portal
        >> Rel(
            "Authenticates using",
            technology="OIDC/OAuth2",
            **plantuml_rel("ExternalCall"),
        )
        >> auth0
    )
    (
        customer_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            **plantuml_rel("Sync"),
        )
        >> api_gateway
    )
    (
        helpdesk_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            **plantuml_rel("Sync"),
        )
        >> api_gateway
    )
    (
        knowledge_base
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            **plantuml_rel("Sync"),
        )
        >> api_gateway
    )
    (
        mobile_app
        >> Rel(
            "Authenticates using",
            technology="OIDC/OAuth2",
            **plantuml_rel("ExternalCall"),
        )
        >> auth0
    )
    (
        mobile_app
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            **plantuml_rel("Sync"),
        )
        >> api_gateway
    )
    (
        notification_service
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            **plantuml_rel("DataAccess"),
        )
        >> support_database
    )
    (
        notification_service
        >> Rel(
            "Sends e-mail using",
            technology="SMTP",
            **plantuml_rel("ExternalCall"),
        )
        >> email_system
    )
    (
        notification_service
        >> Rel(
            "Sends SMS using",
            technology="SMS API",
            **plantuml_rel("ExternalCall"),
        )
        >> sms_provider
    )
    (
        payment_job
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            **plantuml_rel("DataAccess"),
        )
        >> support_database
    )
    (
        payment_job
        >> Rel(
            "Sends invoice event",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> invoice_queue
    )
    (
        payment_job
        >> Rel(
            "Executes payments using",
            technology="HTTPS/API",
            **plantuml_rel("ExternalCall"),
        )
        >> payment_provider
    )
    (
        support_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            **plantuml_rel("DataAccess"),
        )
        >> support_database
    )
    (
        support_api
        >> Rel(
            "Sends expert notification event",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> expert_notifications_queue
    )
    (
        support_api
        >> Rel(
            "Sends customer notification event",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> customer_notifications_queue
    )
    (
        support_api
        >> Rel(
            "Sends progress/closed event",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> ticket_progress_queue
    )
    (
        support_dashboard
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            **plantuml_rel("Sync"),
        )
        >> api_gateway
    )
    (
        ticket_processor
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            **plantuml_rel("DataAccess"),
        )
        >> support_database
    )
    (
        ticket_processor
        >> Rel(
            "Sends ticket assignment event",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> ticket_assigned_queue
    )
    (
        administrator
        >> Rel(
            "Maintains users and reference data",
            technology="HTTPS",
            **plantuml_rel("Sync"),
        )
        >> admin_portal
    )
    (
        administrator
        >> Rel(
            "Manages billing operations",
            technology="HTTPS",
            **plantuml_rel("Sync"),
        )
        >> billing_portal
    )
    (
        customer
        >> Rel("Uses", technology="HTTPS", **plantuml_rel("Sync"))
        >> customer_portal
    )
    (
        customer
        >> Rel("Uses", technology="HTTPS", **plantuml_rel("Sync"))
        >> mobile_app
    )
    (
        helpdesk
        >> Rel(
            "Creates/searches tickets",
            technology="HTTPS",
            **plantuml_rel("Sync"),
        )
        >> helpdesk_portal
    )
    (
        manager
        >> Rel(
            "Tracks operations and generates reports",
            technology="HTTPS",
            **plantuml_rel("Sync"),
        )
        >> support_dashboard
    )
    (
        support_expert
        >> Rel("Uses", technology="HTTPS", **plantuml_rel("Sync"))
        >> mobile_app
    )
    (
        support_expert
        >> Rel(
            "Updates articles",
            technology="HTTPS",
            **plantuml_rel("Sync"),
        )
        >> knowledge_base
    )
    (
        customer_notifications_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> notification_service
    )
    (
        expert_notifications_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> notification_service
    )
    (
        invoice_queue
        >> Rel(
            "Calls billing APIs through",
            technology="REST/HTTP",
            **plantuml_rel("Async"),
        )
        >> api_gateway
    )
    (
        ticket_assigned_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> support_api
    )
    (
        ticket_created_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> ticket_processor
    )
    (
        ticket_progress_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            **plantuml_rel("Async"),
        )
        >> customer_api
    )

plantuml_render_options = (
    PlantUMLRenderOptionsBuilder()
    .layout_top_down(with_legend=True)
    .show_legend(hide_stereotype=False, details="Normal")
    .update_legend_title("Customer Support Component Legend")
    .add_person_tag(
        tag_stereo="User",
        bg_color="#e8f5e9",
        font_color="#1b5e20",
        border_color="#66bb6a",
        shadowing=False,
        legend_text="Operational user",
        legend_sprite="user",
    )
    .add_component_tag(
        tag_stereo="Frontend",
        bg_color="#e3f2fd",
        font_color="#0d47a1",
        border_color="#42a5f5",
        shadowing=True,
        technology="UI",
        legend_text="User-facing frontend",
        legend_sprite="browser",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_component_tag(
        tag_stereo="Gateway",
        bg_color="#fce4ec",
        font_color="#880e4f",
        border_color="#ec407a",
        shadowing=True,
        technology="Gateway",
        legend_text="API gateway",
        legend_sprite="server",
        border_style="BoldLine",
        border_thickness="2",
    )
    .add_component_tag(
        tag_stereo="Backend",
        bg_color="#ede7f6",
        font_color="#311b92",
        border_color="#7e57c2",
        shadowing=True,
        technology="Service",
        legend_text="Backend service",
        legend_sprite="server",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_component_tag(
        tag_stereo="Worker",
        bg_color="#fff3e0",
        font_color="#e65100",
        border_color="#fb8c00",
        shadowing=True,
        technology="Job",
        legend_text="Background worker",
        legend_sprite="server",
        border_style="SolidLine",
        border_thickness="2",
    )
    .add_component_tag(
        tag_stereo="Database",
        bg_color="#fff8e1",
        font_color="#5d4037",
        border_color="#ffb300",
        shadowing=False,
        technology="Database",
        legend_text="Operational datastore",
        legend_sprite="database",
    )
    .add_component_tag(
        tag_stereo="Queue",
        bg_color="#e0f2f1",
        font_color="#004d40",
        border_color="#26a69a",
        shadowing=False,
        technology="Queue",
        legend_text="Asynchronous event stream",
        legend_sprite="queue",
    )
    .add_external_component_tag(
        tag_stereo="External",
        bg_color="#f5f5f5",
        font_color="#424242",
        border_color="#9e9e9e",
        shadowing=False,
        technology="External",
        legend_text="External dependency",
        legend_sprite="cloud",
        border_style="DashedLine",
    )
    .add_rel_tag(
        tag_stereo="Sync",
        text_color="#1565c0",
        line_color="#1e88e5",
        line_style="SolidLine",
        technology="HTTPS",
        legend_text="Synchronous request",
    )
    .add_rel_tag(
        tag_stereo="DataAccess",
        text_color="#6d4c41",
        line_color="#8d6e63",
        line_style="DashedLine",
        technology="SQL",
        legend_text="Database access",
    )
    .add_rel_tag(
        tag_stereo="Async",
        text_color="#00695c",
        line_color="#00897b",
        line_style="DottedLine",
        line_thickness="2",
        technology="Queue/Event",
        legend_text="Asynchronous event flow",
        legend_sprite="queue",
    )
    .add_rel_tag(
        tag_stereo="ExternalCall",
        text_color="#455a64",
        line_color="#78909c",
        line_style="DashedLine",
        technology="External",
        legend_text="External integration",
    )
    .update_element_style(
        element_name="component",
        shape="RoundedBoxShape",
        border_style="SolidLine",
    )
    .build()
)

diagram.set_render_options(
    plantuml=plantuml_render_options,
)

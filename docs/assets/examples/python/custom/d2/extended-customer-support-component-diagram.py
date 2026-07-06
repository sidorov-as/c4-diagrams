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
    D2Legend,
    D2LegendElement,
    D2LegendRel,
    D2RenderOptionsBuilder,
)


def d2_node(
    fill: str,
    stroke: str,
    font_color: str,
    shape: str | None = None,
    stroke_dash: int | None = None,
) -> dict[str, object]:
    style: dict[str, object] = {
        "fill": fill,
        "stroke": stroke,
        "font_color": font_color,
        "stroke_width": 2,
    }
    if stroke_dash is not None:
        style["stroke_dash"] = stroke_dash

    node: dict[str, object] = {"style": style}
    if shape:
        node["shape"] = shape

    return node


def d2_edge(
    color: str,
    text_color: str | None = None,
    stroke_dash: int | None = None,
) -> dict[str, object]:
    style: dict[str, object] = {
        "stroke": color,
        "font_color": text_color or color,
    }
    if stroke_dash is not None:
        style["stroke_dash"] = stroke_dash

    return {"style": style}


USER = d2_node("#e8f5e9", "#66bb6a", "#1b5e20", shape="c4-person")
FRONTEND = d2_node("#e3f2fd", "#42a5f5", "#0d47a1")
GATEWAY = d2_node("#fce4ec", "#ec407a", "#880e4f")
BACKEND = d2_node("#ede7f6", "#7e57c2", "#311b92")
JOB = d2_node("#fff3e0", "#fb8c00", "#e65100")
DATABASE = d2_node("#fff8e1", "#ffb300", "#5d4037")
QUEUE = d2_node("#e0f2f1", "#26a69a", "#004d40")
EXTERNAL = d2_node("#f5f5f5", "#9e9e9e", "#424242", stroke_dash=5)

SYNC = d2_edge("#1e88e5", "#1565c0")
ASYNC = d2_edge("#00897b", "#00695c", stroke_dash=3)
DATA_ACCESS = d2_edge("#8d6e63", "#6d4c41")
EXTERNAL_CALL = d2_edge("#78909c", "#455a64", stroke_dash=5)

with ComponentDiagram(
    title="Customer Support System - Extended Component View",
) as diagram:
    admin_api = Component(
        "Admin API",
        "User management and reference-data management.",
        technology="Container Service",
        alias="admin_api",
        d2=BACKEND,
    )
    admin_portal = Component(
        "Admin Portal",
        "Manages system users and reference data.",
        technology="Single-page Application",
        alias="admin_portal",
        d2=FRONTEND,
    )
    administrator = Person(
        "Administrator",
        "Internal user with administrative access.",
        alias="administrator",
        d2=USER,
    )
    analytics_api = Component(
        "Analytics API",
        "Ticket status reports, survey analysis and performance reports.",
        technology="Container Service",
        alias="analytics_api",
        d2=BACKEND,
    )
    api_gateway = Component(
        "API Gateway",
        "Performs access control, security checks and request routing.",
        technology="Container Service",
        alias="api_gateway",
        d2=GATEWAY,
    )
    auth0 = ComponentExt(
        "Auth0",
        "External identity provider for authentication.",
        technology="OIDC/OAuth2",
        alias="auth0",
        d2=EXTERNAL,
    )
    billing_api = Component(
        "Billing API",
        "Billing management and financial reports.",
        technology="Container Service",
        alias="billing_api",
        d2=BACKEND,
    )
    billing_portal = Component(
        "Billing Portal",
        "Supports billing processing.",
        technology="Single-page Application",
        alias="billing_portal",
        d2=FRONTEND,
    )
    customer = Person(
        "Customer",
        "Owner of electronic equipment and support plan; reports issues.",
        alias="customer",
        d2=USER,
    )
    customer_api = Component(
        "Customer API",
        "Handles registration, profiles, tickets, surveys and billing history.",
        technology="Container Service",
        alias="customer_api",
        d2=BACKEND,
    )
    customer_notifications_queue = ComponentQueue(
        "Customer Notifications",
        "Asynchronous message channel for customer notifications.",
        technology="Message Queue",
        alias="customer_notifications_queue",
        d2=QUEUE,
    )
    customer_portal = Component(
        "Customer Portal",
        "Provides access to customer profile, billing, ticket creation and history.",
        technology="Single-page Application",
        alias="customer_portal",
        d2=FRONTEND,
    )
    email_system = ComponentExt(
        "E-mail System",
        "Internal mail system used for e-mail delivery.",
        technology="SMTP",
        alias="email_system",
        d2=EXTERNAL,
    )
    expert_notifications_queue = ComponentQueue(
        "Expert Notifications",
        "Asynchronous message channel for expert notifications.",
        technology="Message Queue",
        alias="expert_notifications_queue",
        d2=QUEUE,
    )
    helpdesk = Person(
        "Helpdesk",
        "First line of support; provides direct phone support.",
        alias="helpdesk",
        d2=USER,
    )
    helpdesk_portal = Component(
        "Helpdesk Portal",
        "Provides access to tickets and status.",
        technology="Single-page Application",
        alias="helpdesk_portal",
        d2=FRONTEND,
    )
    invoice_queue = ComponentQueue(
        "Invoice",
        "Asynchronous message channel for invoice processing.",
        technology="Message Queue",
        alias="invoice_queue",
        d2=QUEUE,
    )
    knowledge_base = Component(
        "Knowledge Base",
        "Supports searching and updating knowledge-base articles.",
        technology="Single-page Application",
        alias="knowledge_base",
        d2=FRONTEND,
    )
    manager = Person(
        "Manager",
        "Monitors expert performance and customer satisfaction.",
        alias="manager",
        d2=USER,
    )
    mobile_app = Component(
        "Mobile App",
        "Provides access to assigned tickets and knowledge-base search.",
        technology="iOS / Android App",
        alias="mobile_app",
        d2=FRONTEND,
    )
    notification_service = Component(
        "Notification Service",
        "Sends SMS and e-mail messages based on notification preferences.",
        technology="Container Service",
        alias="notification_service",
        d2=BACKEND,
    )
    payment_job = Component(
        "Payment",
        "Runs monthly and performs payment operations.",
        technology="Container Job",
        alias="payment_job",
        d2=JOB,
    )
    payment_provider = ComponentExt(
        "Payment Service Provider",
        "External online payment service.",
        technology="HTTPS/API",
        alias="payment_provider",
        d2=EXTERNAL,
    )
    sms_provider = ComponentExt(
        "SMS Service Provider",
        "Provides SMS text messaging.",
        technology="SMS API",
        alias="sms_provider",
        d2=EXTERNAL,
    )
    support_api = Component(
        "Support API",
        "Ticket orchestration, search, assignment handling and knowledge-base updates.",
        technology="Container Service",
        alias="support_api",
        d2=BACKEND,
    )
    support_dashboard = Component(
        "Support Dashboard",
        "Provides analytics and operational reports.",
        technology="Single-page Application",
        alias="support_dashboard",
        d2=FRONTEND,
    )
    support_database = ComponentDb(
        "Support Database",
        "Stores tickets, users, customer contacts and knowledge-base content.",
        technology="Relational Database",
        alias="support_database",
        d2=DATABASE,
    )
    support_expert = Person(
        "Support Expert",
        "Technology expert who fixes customer electronic devices.",
        alias="support_expert",
        d2=USER,
    )
    ticket_assigned_queue = ComponentQueue(
        "Ticket Assigned",
        "Asynchronous message channel for assigned tickets.",
        technology="Message Queue",
        alias="ticket_assigned_queue",
        d2=QUEUE,
    )
    ticket_created_queue = ComponentQueue(
        "Ticket Created",
        "Asynchronous message channel for created tickets.",
        technology="Message Queue",
        alias="ticket_created_queue",
        d2=QUEUE,
    )
    ticket_progress_queue = ComponentQueue(
        "Ticket In-Progress/Closed",
        "Asynchronous message channel for ticket progress and closure notifications.",
        technology="Message Queue",
        alias="ticket_progress_queue",
        d2=QUEUE,
    )
    ticket_processor = Component(
        "Ticket Processor",
        "Runs periodically, scans ticket statuses, and creates assignments.",
        technology="Container Job",
        alias="ticket_processor",
        d2=JOB,
    )

    (
        admin_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            d2=DATA_ACCESS,
        )
        >> support_database
    )
    (
        admin_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            d2=SYNC,
        )
        >> api_gateway
    )
    (
        analytics_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            d2=DATA_ACCESS,
        )
        >> support_database
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            d2=SYNC,
        )
        >> customer_api
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            d2=SYNC,
        )
        >> support_api
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            d2=SYNC,
        )
        >> admin_api
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            d2=SYNC,
        )
        >> billing_api
    )
    (
        api_gateway
        >> Rel(
            "Routes API calls to",
            technology="REST/HTTP",
            d2=SYNC,
        )
        >> analytics_api
    )
    (
        billing_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            d2=DATA_ACCESS,
        )
        >> support_database
    )
    (
        billing_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            d2=SYNC,
        )
        >> api_gateway
    )
    (
        customer_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            d2=DATA_ACCESS,
        )
        >> support_database
    )
    (
        customer_api
        >> Rel(
            "Sends ticket created event",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> ticket_created_queue
    )
    (
        customer_portal
        >> Rel(
            "Authenticates using",
            technology="OIDC/OAuth2",
            d2=EXTERNAL_CALL,
        )
        >> auth0
    )
    (
        customer_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            d2=SYNC,
        )
        >> api_gateway
    )
    (
        helpdesk_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            d2=SYNC,
        )
        >> api_gateway
    )
    (
        knowledge_base
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            d2=SYNC,
        )
        >> api_gateway
    )
    (
        mobile_app
        >> Rel(
            "Authenticates using",
            technology="OIDC/OAuth2",
            d2=EXTERNAL_CALL,
        )
        >> auth0
    )
    (
        mobile_app
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            d2=SYNC,
        )
        >> api_gateway
    )
    (
        notification_service
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            d2=DATA_ACCESS,
        )
        >> support_database
    )
    (
        notification_service
        >> Rel(
            "Sends e-mail using",
            technology="SMTP",
            d2=EXTERNAL_CALL,
        )
        >> email_system
    )
    (
        notification_service
        >> Rel(
            "Sends SMS using",
            technology="SMS API",
            d2=EXTERNAL_CALL,
        )
        >> sms_provider
    )
    (
        payment_job
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            d2=DATA_ACCESS,
        )
        >> support_database
    )
    (
        payment_job
        >> Rel(
            "Sends invoice event",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> invoice_queue
    )
    (
        payment_job
        >> Rel(
            "Executes payments using",
            technology="HTTPS/API",
            d2=EXTERNAL_CALL,
        )
        >> payment_provider
    )
    (
        support_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            d2=DATA_ACCESS,
        )
        >> support_database
    )
    (
        support_api
        >> Rel(
            "Sends expert notification event",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> expert_notifications_queue
    )
    (
        support_api
        >> Rel(
            "Sends customer notification event",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> customer_notifications_queue
    )
    (
        support_api
        >> Rel(
            "Sends progress/closed event",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> ticket_progress_queue
    )
    (
        support_dashboard
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
            d2=SYNC,
        )
        >> api_gateway
    )
    (
        ticket_processor
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
            d2=DATA_ACCESS,
        )
        >> support_database
    )
    (
        ticket_processor
        >> Rel(
            "Sends ticket assignment event",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> ticket_assigned_queue
    )
    (
        administrator
        >> Rel(
            "Maintains users and reference data",
            technology="HTTPS",
            d2=SYNC,
        )
        >> admin_portal
    )
    (
        administrator
        >> Rel(
            "Manages billing operations",
            technology="HTTPS",
            d2=SYNC,
        )
        >> billing_portal
    )
    customer >> Rel("Uses", technology="HTTPS", d2=SYNC) >> customer_portal
    customer >> Rel("Uses", technology="HTTPS", d2=SYNC) >> mobile_app
    (
        helpdesk
        >> Rel(
            "Creates/searches tickets",
            technology="HTTPS",
            d2=SYNC,
        )
        >> helpdesk_portal
    )
    (
        manager
        >> Rel(
            "Tracks operations and generates reports",
            technology="HTTPS",
            d2=SYNC,
        )
        >> support_dashboard
    )
    support_expert >> Rel("Uses", technology="HTTPS", d2=SYNC) >> mobile_app
    (
        support_expert
        >> Rel(
            "Updates articles",
            technology="HTTPS",
            d2=SYNC,
        )
        >> knowledge_base
    )
    (
        customer_notifications_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> notification_service
    )
    (
        expert_notifications_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> notification_service
    )
    (
        invoice_queue
        >> Rel(
            "Calls billing APIs through",
            technology="REST/HTTP",
            d2=ASYNC,
        )
        >> api_gateway
    )
    (
        ticket_assigned_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> support_api
    )
    (
        ticket_created_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> ticket_processor
    )
    (
        ticket_progress_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
            d2=ASYNC,
        )
        >> customer_api
    )

d2_render_options = (
    D2RenderOptionsBuilder()
    .direction("down")
    .include_technology()
    .legend(
        D2Legend(
            label="Customer Support Component Legend",
            items=[
                D2LegendElement(
                    "Operational user", shape="person", style=USER["style"]
                ),
                D2LegendElement(
                    "User-facing frontend", style=FRONTEND["style"]
                ),
                D2LegendElement("API gateway", style=GATEWAY["style"]),
                D2LegendElement("Backend service", style=BACKEND["style"]),
                D2LegendElement("Background worker", style=JOB["style"]),
                D2LegendElement(
                    "Operational datastore",
                    shape="cylinder",
                    style=DATABASE["style"],
                ),
                D2LegendElement(
                    "Asynchronous event stream",
                    shape="queue",
                    style=QUEUE["style"],
                ),
                D2LegendElement("External dependency", style=EXTERNAL["style"]),
                D2LegendRel("Synchronous request", style=SYNC["style"]),
                D2LegendRel("Database access", style=DATA_ACCESS["style"]),
                D2LegendRel("Asynchronous event", style=ASYNC["style"]),
                D2LegendRel(
                    "External integration", style=EXTERNAL_CALL["style"]
                ),
            ],
        ),
    )
    .build()
)

diagram.set_render_options(
    d2=d2_render_options,
)

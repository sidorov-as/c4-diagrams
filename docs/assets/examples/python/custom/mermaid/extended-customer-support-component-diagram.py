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
    MermaidRenderOptionsBuilder,
)


def mermaid_node(fill: str, stroke: str, font_color: str) -> dict[str, str]:
    return {
        "bg_color": fill,
        "border_color": stroke,
        "font_color": font_color,
    }


def mermaid_edge(color: str, text_color: str | None = None) -> dict[str, str]:
    return {
        "line_color": color,
        "text_color": text_color or color,
    }


MERMAID_USER = mermaid_node("#e8f5e9", "#66bb6a", "#1b5e20")
MERMAID_FRONTEND = mermaid_node("#e3f2fd", "#42a5f5", "#0d47a1")
MERMAID_GATEWAY = mermaid_node("#fce4ec", "#ec407a", "#880e4f")
MERMAID_BACKEND = mermaid_node("#ede7f6", "#7e57c2", "#311b92")
MERMAID_JOB = mermaid_node("#fff3e0", "#fb8c00", "#e65100")
MERMAID_DATABASE = mermaid_node("#fff8e1", "#ffb300", "#5d4037")
MERMAID_QUEUE = mermaid_node("#e0f2f1", "#26a69a", "#004d40")
MERMAID_EXTERNAL = mermaid_node("#f5f5f5", "#9e9e9e", "#424242")

MERMAID_SYNC = mermaid_edge("#1e88e5", "#1565c0")
MERMAID_ASYNC = mermaid_edge("#00897b", "#00695c")
MERMAID_DATA_ACCESS = mermaid_edge("#8d6e63", "#6d4c41")
MERMAID_EXTERNAL_CALL = mermaid_edge("#78909c", "#455a64")

with ComponentDiagram(
    title="Customer Support System - Extended Component View",
) as diagram:
    admin_api = Component(
        "Admin API",
        "User management and reference-data management.",
        technology="Container Service",
        alias="admin_api",
    )
    admin_portal = Component(
        "Admin Portal",
        "Manages system users and reference data.",
        technology="Single-page Application",
        alias="admin_portal",
    )
    administrator = Person(
        "Administrator",
        "Internal user with administrative access.",
        alias="administrator",
    )
    analytics_api = Component(
        "Analytics API",
        "Ticket status reports, survey analysis and performance reports.",
        technology="Container Service",
        alias="analytics_api",
    )
    api_gateway = Component(
        "API Gateway",
        "Performs access control, security checks and request routing.",
        technology="Container Service",
        alias="api_gateway",
    )
    auth0 = ComponentExt(
        "Auth0",
        "External identity provider for authentication.",
        technology="OIDC/OAuth2",
        alias="auth0",
    )
    billing_api = Component(
        "Billing API",
        "Billing management and financial reports.",
        technology="Container Service",
        alias="billing_api",
    )
    billing_portal = Component(
        "Billing Portal",
        "Supports billing processing.",
        technology="Single-page Application",
        alias="billing_portal",
    )
    customer = Person(
        "Customer",
        "Owner of electronic equipment and support plan; reports issues.",
        alias="customer",
    )
    customer_api = Component(
        "Customer API",
        "Handles registration, profiles, tickets, surveys and billing history.",
        technology="Container Service",
        alias="customer_api",
    )
    customer_notifications_queue = ComponentQueue(
        "Customer Notifications",
        "Asynchronous message channel for customer notifications.",
        technology="Message Queue",
        alias="customer_notifications_queue",
    )
    customer_portal = Component(
        "Customer Portal",
        "Provides access to customer profile, billing, ticket creation and history.",
        technology="Single-page Application",
        alias="customer_portal",
    )
    email_system = ComponentExt(
        "E-mail System",
        "Internal mail system used for e-mail delivery.",
        technology="SMTP",
        alias="email_system",
    )
    expert_notifications_queue = ComponentQueue(
        "Expert Notifications",
        "Asynchronous message channel for expert notifications.",
        technology="Message Queue",
        alias="expert_notifications_queue",
    )
    helpdesk = Person(
        "Helpdesk",
        "First line of support; provides direct phone support.",
        alias="helpdesk",
    )
    helpdesk_portal = Component(
        "Helpdesk Portal",
        "Provides access to tickets and status.",
        technology="Single-page Application",
        alias="helpdesk_portal",
    )
    invoice_queue = ComponentQueue(
        "Invoice",
        "Asynchronous message channel for invoice processing.",
        technology="Message Queue",
        alias="invoice_queue",
    )
    knowledge_base = Component(
        "Knowledge Base",
        "Supports searching and updating knowledge-base articles.",
        technology="Single-page Application",
        alias="knowledge_base",
    )
    manager = Person(
        "Manager",
        "Monitors expert performance and customer satisfaction.",
        alias="manager",
    )
    mobile_app = Component(
        "Mobile App",
        "Provides access to assigned tickets and knowledge-base search.",
        technology="iOS / Android App",
        alias="mobile_app",
    )
    notification_service = Component(
        "Notification Service",
        "Sends SMS and e-mail messages based on notification preferences.",
        technology="Container Service",
        alias="notification_service",
    )
    payment_job = Component(
        "Payment",
        "Runs monthly and performs payment operations.",
        technology="Container Job",
        alias="payment_job",
    )
    payment_provider = ComponentExt(
        "Payment Service Provider",
        "External online payment service.",
        technology="HTTPS/API",
        alias="payment_provider",
    )
    sms_provider = ComponentExt(
        "SMS Service Provider",
        "Provides SMS text messaging.",
        technology="SMS API",
        alias="sms_provider",
    )
    support_api = Component(
        "Support API",
        "Ticket orchestration, search, assignment handling and knowledge-base updates.",
        technology="Container Service",
        alias="support_api",
    )
    support_dashboard = Component(
        "Support Dashboard",
        "Provides analytics and operational reports.",
        technology="Single-page Application",
        alias="support_dashboard",
    )
    support_database = ComponentDb(
        "Support Database",
        "Stores tickets, users, customer contacts and knowledge-base content.",
        technology="Relational Database",
        alias="support_database",
    )
    support_expert = Person(
        "Support Expert",
        "Technology expert who fixes customer electronic devices.",
        alias="support_expert",
    )
    ticket_assigned_queue = ComponentQueue(
        "Ticket Assigned",
        "Asynchronous message channel for assigned tickets.",
        technology="Message Queue",
        alias="ticket_assigned_queue",
    )
    ticket_created_queue = ComponentQueue(
        "Ticket Created",
        "Asynchronous message channel for created tickets.",
        technology="Message Queue",
        alias="ticket_created_queue",
    )
    ticket_progress_queue = ComponentQueue(
        "Ticket In-Progress/Closed",
        "Asynchronous message channel for ticket progress and closure notifications.",
        technology="Message Queue",
        alias="ticket_progress_queue",
    )
    ticket_processor = Component(
        "Ticket Processor",
        "Runs periodically, scans ticket statuses, and creates assignments.",
        technology="Container Job",
        alias="ticket_processor",
    )

    (
        admin_api
        >> Rel("Reads from and writes to", technology="SQL/TCP")
        >> support_database
    )
    (
        admin_portal
        >> Rel("Makes API calls to", technology="REST/HTTPS")
        >> api_gateway
    )
    (
        analytics_api
        >> Rel("Reads from and writes to", technology="SQL/TCP")
        >> support_database
    )
    (
        api_gateway
        >> Rel("Routes API calls to", technology="REST/HTTP")
        >> customer_api
    )
    (
        api_gateway
        >> Rel("Routes API calls to", technology="REST/HTTP")
        >> support_api
    )
    (
        api_gateway
        >> Rel("Routes API calls to", technology="REST/HTTP")
        >> admin_api
    )
    (
        api_gateway
        >> Rel("Routes API calls to", technology="REST/HTTP")
        >> billing_api
    )
    (
        api_gateway
        >> Rel("Routes API calls to", technology="REST/HTTP")
        >> analytics_api
    )
    (
        billing_api
        >> Rel("Reads from and writes to", technology="SQL/TCP")
        >> support_database
    )
    (
        billing_portal
        >> Rel("Makes API calls to", technology="REST/HTTPS")
        >> api_gateway
    )
    (
        customer_api
        >> Rel("Reads from and writes to", technology="SQL/TCP")
        >> support_database
    )
    (
        customer_api
        >> Rel("Sends ticket created event", technology="Queue / Event")
        >> ticket_created_queue
    )
    (
        customer_portal
        >> Rel(
            "Authenticates using",
            technology="OIDC/OAuth2",
        )
        >> auth0
    )
    (
        customer_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
        )
        >> api_gateway
    )
    (
        helpdesk_portal
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
        )
        >> api_gateway
    )
    (
        knowledge_base
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
        )
        >> api_gateway
    )
    (
        mobile_app
        >> Rel(
            "Authenticates using",
            technology="OIDC/OAuth2",
        )
        >> auth0
    )
    (
        mobile_app
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
        )
        >> api_gateway
    )
    (
        notification_service
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
        )
        >> support_database
    )
    (
        notification_service
        >> Rel(
            "Sends e-mail using",
            technology="SMTP",
        )
        >> email_system
    )
    (
        notification_service
        >> Rel(
            "Sends SMS using",
            technology="SMS API",
        )
        >> sms_provider
    )
    (
        payment_job
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
        )
        >> support_database
    )
    (
        payment_job
        >> Rel(
            "Sends invoice event",
            technology="Queue / Event",
        )
        >> invoice_queue
    )
    (
        payment_job
        >> Rel(
            "Executes payments using",
            technology="HTTPS/API",
        )
        >> payment_provider
    )
    (
        support_api
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
        )
        >> support_database
    )
    (
        support_api
        >> Rel(
            "Sends expert notification event",
            technology="Queue / Event",
        )
        >> expert_notifications_queue
    )
    (
        support_api
        >> Rel(
            "Sends customer notification event",
            technology="Queue / Event",
        )
        >> customer_notifications_queue
    )
    (
        support_api
        >> Rel(
            "Sends progress/closed event",
            technology="Queue / Event",
        )
        >> ticket_progress_queue
    )
    (
        support_dashboard
        >> Rel(
            "Makes API calls to",
            technology="REST/HTTPS",
        )
        >> api_gateway
    )
    (
        ticket_processor
        >> Rel(
            "Reads from and writes to",
            technology="SQL/TCP",
        )
        >> support_database
    )
    (
        ticket_processor
        >> Rel(
            "Sends ticket assignment event",
            technology="Queue / Event",
        )
        >> ticket_assigned_queue
    )
    (
        administrator
        >> Rel(
            "Maintains users and reference data",
            technology="HTTPS",
        )
        >> admin_portal
    )
    (
        administrator
        >> Rel(
            "Manages billing operations",
            technology="HTTPS",
        )
        >> billing_portal
    )
    customer >> Rel("Uses", technology="HTTPS") >> customer_portal
    customer >> Rel("Uses", technology="HTTPS") >> mobile_app
    (
        helpdesk
        >> Rel(
            "Creates/searches tickets",
            technology="HTTPS",
        )
        >> helpdesk_portal
    )
    (
        manager
        >> Rel(
            "Tracks operations and generates reports",
            technology="HTTPS",
        )
        >> support_dashboard
    )
    support_expert >> Rel("Uses", technology="HTTPS") >> mobile_app
    (
        support_expert
        >> Rel(
            "Updates articles",
            technology="HTTPS",
        )
        >> knowledge_base
    )
    (
        customer_notifications_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
        )
        >> notification_service
    )
    (
        expert_notifications_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
        )
        >> notification_service
    )
    (
        invoice_queue
        >> Rel(
            "Calls billing APIs through",
            technology="REST/HTTP",
        )
        >> api_gateway
    )
    (
        ticket_assigned_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
        )
        >> support_api
    )
    (
        ticket_created_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
        )
        >> ticket_processor
    )
    (
        ticket_progress_queue
        >> Rel(
            "Consumed by",
            technology="Queue / Event",
        )
        >> customer_api
    )

mermaid_render_options_builder = (
    MermaidRenderOptionsBuilder().update_layout_config(
        c4_shape_in_row=5,
        c4_boundary_in_row=1,
    )
)

for element in (administrator, customer, helpdesk, manager, support_expert):
    mermaid_render_options_builder.update_element_style(element, **MERMAID_USER)

for element in (
    admin_portal,
    billing_portal,
    customer_portal,
    helpdesk_portal,
    knowledge_base,
    mobile_app,
    support_dashboard,
):
    mermaid_render_options_builder.update_element_style(
        element, **MERMAID_FRONTEND
    )

for element in (
    admin_api,
    analytics_api,
    billing_api,
    customer_api,
    notification_service,
    support_api,
):
    mermaid_render_options_builder.update_element_style(
        element, **MERMAID_BACKEND
    )

for element in (auth0, email_system, payment_provider, sms_provider):
    mermaid_render_options_builder.update_element_style(
        element, **MERMAID_EXTERNAL
    )

for element in (
    customer_notifications_queue,
    expert_notifications_queue,
    invoice_queue,
    ticket_assigned_queue,
    ticket_created_queue,
    ticket_progress_queue,
):
    mermaid_render_options_builder.update_element_style(
        element, **MERMAID_QUEUE
    )

mermaid_render_options_builder.update_element_style(
    api_gateway, **MERMAID_GATEWAY
)
mermaid_render_options_builder.update_element_style(payment_job, **MERMAID_JOB)
mermaid_render_options_builder.update_element_style(
    ticket_processor, **MERMAID_JOB
)
mermaid_render_options_builder.update_element_style(
    support_database, **MERMAID_DATABASE
)

for source, target in (
    (admin_api, support_database),
    (analytics_api, support_database),
    (billing_api, support_database),
    (customer_api, support_database),
    (notification_service, support_database),
    (payment_job, support_database),
    (support_api, support_database),
    (ticket_processor, support_database),
):
    mermaid_render_options_builder.update_rel_style(
        source,
        target,
        offset_y=-35,
        **MERMAID_DATA_ACCESS,
    )

for source, target in (
    (customer_api, ticket_created_queue),
    (payment_job, invoice_queue),
    (support_api, expert_notifications_queue),
    (support_api, customer_notifications_queue),
    (support_api, ticket_progress_queue),
    (ticket_processor, ticket_assigned_queue),
    (customer_notifications_queue, notification_service),
    (expert_notifications_queue, notification_service),
    (invoice_queue, api_gateway),
    (ticket_assigned_queue, support_api),
    (ticket_created_queue, ticket_processor),
    (ticket_progress_queue, customer_api),
):
    mermaid_render_options_builder.update_rel_style(
        source,
        target,
        offset_y=35,
        **MERMAID_ASYNC,
    )

for source, target in (
    (customer_portal, auth0),
    (mobile_app, auth0),
    (notification_service, email_system),
    (notification_service, sms_provider),
    (payment_job, payment_provider),
):
    mermaid_render_options_builder.update_rel_style(
        source,
        target,
        offset_y=-35,
        **MERMAID_EXTERNAL_CALL,
    )

for source, target in (
    (admin_portal, api_gateway),
    (api_gateway, customer_api),
    (api_gateway, support_api),
    (api_gateway, admin_api),
    (api_gateway, billing_api),
    (api_gateway, analytics_api),
    (billing_portal, api_gateway),
    (customer_portal, api_gateway),
    (helpdesk_portal, api_gateway),
    (knowledge_base, api_gateway),
    (mobile_app, api_gateway),
    (support_dashboard, api_gateway),
    (administrator, admin_portal),
    (administrator, billing_portal),
    (customer, customer_portal),
    (customer, mobile_app),
    (helpdesk, helpdesk_portal),
    (manager, support_dashboard),
    (support_expert, mobile_app),
    (support_expert, knowledge_base),
):
    mermaid_render_options_builder.update_rel_style(
        source, target, **MERMAID_SYNC
    )

diagram.set_render_options(
    mermaid=mermaid_render_options_builder.build(),
)

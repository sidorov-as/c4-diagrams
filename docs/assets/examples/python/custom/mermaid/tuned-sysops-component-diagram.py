from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentExt,
    ComponentQueue,
    ContainerBoundary,
    Person,
    Rel,
)
from c4.renderers import (
    MermaidRenderOptionsBuilder,
)


with ComponentDiagram(title='Customer Support System - Tuned Component View') as diagram:
    customer = Person(
        'Customer',
        'Reports equipment issues and tracks repair progress.',
        alias='customer',
    )
    expert = Person(
        'Support Expert',
        'Accepts assignments and records repair updates.',
        alias='expert',
    )

    auth0 = ComponentExt(
        'Auth0',
        'External identity provider.',
        technology='OIDC/OAuth2',
        alias='auth0',
    )
    email_system = ComponentExt(
        'E-mail System',
        'Delivers customer and expert notifications.',
        technology='SMTP',
        alias='email_system',
    )

    with ContainerBoundary(
        'Customer Support System',
        'Components that handle support tickets and expert assignments.',
        mermaid={'type': 'system boundary'},
        alias='sysops_system',
    ):
        api_gateway = Component(
            'API Gateway',
            'Access control and request routing.',
            technology='Container Service',
            alias='api_gateway',
        )
        customer_portal = Component(
            'Customer Portal',
            'Ticket creation and status tracking.',
            technology='SPA',
            alias='customer_portal',
        )
        mobile_app = Component(
            'Expert Mobile App',
            'Assignment queue and field repair updates.',
            technology='iOS / Android',
            alias='mobile_app',
        )
        ticket_api = Component(
            'Ticket API',
            'Ticket orchestration, search, and assignment updates.',
            technology='Container Service',
            alias='ticket_api',
        )
        ticket_processor = Component(
            'Ticket Processor',
            'Creates expert assignments for new tickets.',
            technology='Container Job',
            alias='ticket_processor',
        )
        notification_service = Component(
            'Notification Service',
            'Sends customer and expert notifications.',
            technology='Container Service',
            alias='notification_service',
        )
        sysops_database = ComponentDb(
            'Support Database',
            'Tickets, contacts, assignments, and repair history.',
            technology='PostgreSQL',
            alias='sysops_database',
        )
        ticket_created_queue = ComponentQueue(
            'Ticket Created',
            'Event stream for new support tickets.',
            technology='Message Queue',
            alias='ticket_created_queue',
        )

    customer >> Rel('Uses', technology='HTTPS') >> customer_portal
    expert >> Rel('Uses', technology='HTTPS') >> mobile_app

    customer_portal >> Rel('Authenticates', technology='OIDC') >> auth0
    mobile_app >> Rel('Authenticates', technology='OIDC') >> auth0

    customer_portal >> Rel('Calls', technology='REST/HTTPS') >> api_gateway
    mobile_app >> Rel('Calls', technology='REST/HTTPS') >> api_gateway
    api_gateway >> Rel('Routes', technology='REST/HTTP') >> ticket_api

    ticket_api >> Rel('Reads/writes', technology='SQL/TCP') >> sysops_database
    ticket_processor >> Rel('Reads/writes', technology='SQL/TCP') >> sysops_database
    ticket_api >> Rel('Publishes', technology='Queue/Event') >> ticket_created_queue
    ticket_created_queue >> Rel('Triggers', technology='Queue/Event') >> ticket_processor
    ticket_processor >> Rel('Requests notification', technology='REST/HTTP') >> notification_service
    notification_service >> Rel('Sends e-mail', technology='SMTP') >> email_system


mermaid_render_options = (
    MermaidRenderOptionsBuilder()
    .update_layout_config(
        c4_shape_in_row=3,
        c4_boundary_in_row=1,
    )
    .update_element_style('customer', bg_color='#e8f5e9', font_color='#1b5e20', border_color='#66bb6a')
    .update_element_style('expert', bg_color='#e8f5e9', font_color='#1b5e20', border_color='#66bb6a')
    .update_element_style('customer_portal', bg_color='#e3f2fd', font_color='#0d47a1', border_color='#42a5f5')
    .update_element_style('mobile_app', bg_color='#e3f2fd', font_color='#0d47a1', border_color='#42a5f5')
    .update_element_style('api_gateway', bg_color='#fce4ec', font_color='#880e4f', border_color='#ec407a')
    .update_element_style('ticket_api', bg_color='#ede7f6', font_color='#311b92', border_color='#7e57c2')
    .update_element_style('notification_service', bg_color='#ede7f6', font_color='#311b92', border_color='#7e57c2')
    .update_element_style('ticket_processor', bg_color='#fff3e0', font_color='#e65100', border_color='#fb8c00')
    .update_element_style('sysops_database', bg_color='#fff8e1', font_color='#5d4037', border_color='#ffb300')
    .update_element_style('ticket_created_queue', bg_color='#e0f2f1', font_color='#004d40', border_color='#26a69a')
    .update_element_style('auth0', bg_color='#f5f5f5', font_color='#424242', border_color='#9e9e9e')
    .update_element_style('email_system', bg_color='#f5f5f5', font_color='#424242', border_color='#9e9e9e')
    .update_rel_style('customer_portal', 'auth0', line_color='#78909c', text_color='#455a64', offset_y=-35)
    .update_rel_style('mobile_app', 'auth0', line_color='#78909c', text_color='#455a64', offset_y=35)
    .update_rel_style('customer_portal', 'api_gateway', line_color='#1e88e5', text_color='#1565c0', offset_y=-70)
    .update_rel_style('mobile_app', 'api_gateway', line_color='#1e88e5', text_color='#1565c0', offset_y=70)
    .update_rel_style('api_gateway', 'ticket_api', line_color='#1e88e5', text_color='#1565c0', offset_x=-70)
    .update_rel_style('ticket_api', 'sysops_database', line_color='#8d6e63', text_color='#6d4c41', offset_y=-30)
    .update_rel_style('ticket_processor', 'sysops_database', line_color='#8d6e63', text_color='#6d4c41', offset_y=30)
    .update_rel_style('ticket_api', 'ticket_created_queue', line_color='#00897b', text_color='#00695c', offset_x=45)
    .update_rel_style('ticket_created_queue', 'ticket_processor', line_color='#00897b', text_color='#00695c', offset_x=-65)
    .update_rel_style('ticket_processor', 'notification_service', line_color='#1e88e5', text_color='#1565c0', offset_y=-60)
    .update_rel_style('notification_service', 'email_system', line_color='#78909c', text_color='#455a64', offset_y=-35)
    .build()
)

diagram.set_render_options(
    mermaid=mermaid_render_options,
)

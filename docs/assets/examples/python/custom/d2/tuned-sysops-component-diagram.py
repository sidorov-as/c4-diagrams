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
    D2Legend,
    D2LegendElement,
    D2LegendRel,
    D2RenderOptionsBuilder,
)

USER_STYLE = {
    'fill': '#e8f5e9',
    'font_color': '#1b5e20',
    'stroke': '#66bb6a',
}
FRONTEND_STYLE = {
    'fill': '#e3f2fd',
    'font_color': '#0d47a1',
    'stroke': '#42a5f5',
}
GATEWAY_STYLE = {
    'fill': '#fce4ec',
    'font_color': '#880e4f',
    'stroke': '#ec407a',
    'stroke_width': 2,
}
BACKEND_STYLE = {
    'fill': '#ede7f6',
    'font_color': '#311b92',
    'stroke': '#7e57c2',
}
WORKER_STYLE = {
    'fill': '#fff3e0',
    'font_color': '#e65100',
    'stroke': '#fb8c00',
}
DATABASE_STYLE = {
    'fill': '#fff8e1',
    'font_color': '#5d4037',
    'stroke': '#ffb300',
}
QUEUE_STYLE = {
    'fill': '#e0f2f1',
    'font_color': '#004d40',
    'stroke': '#26a69a',
}
EXTERNAL_STYLE = {
    'fill': '#f5f5f5',
    'font_color': '#424242',
    'stroke': '#9e9e9e',
    'stroke_dash': 5,
}
SYNC_REL_STYLE = {
    'stroke': '#1e88e5',
    'font_color': '#1565c0',
}
DATA_REL_STYLE = {
    'stroke': '#8d6e63',
    'font_color': '#6d4c41',
}
ASYNC_REL_STYLE = {
    'stroke': '#00897b',
    'font_color': '#00695c',
    'stroke_dash': 3,
}
EXTERNAL_REL_STYLE = {
    'stroke': '#78909c',
    'font_color': '#455a64',
    'stroke_dash': 5,
}

with ComponentDiagram(title='Customer Support System - Tuned Component View') as diagram:
    customer = Person(
        'Customer',
        'Reports equipment issues and tracks repair progress.',
        d2={'style': USER_STYLE},
        alias='customer',
    )
    expert = Person(
        'Support Expert',
        'Accepts assignments and records repair updates.',
        d2={'style': USER_STYLE},
        alias='expert',
    )

    auth0 = ComponentExt(
        'Auth0',
        'External identity provider.',
        technology='OIDC/OAuth2',
        d2={'style': EXTERNAL_STYLE},
        alias='auth0',
    )
    email_system = ComponentExt(
        'E-mail System',
        'Delivers customer and expert notifications.',
        technology='SMTP',
        d2={'style': EXTERNAL_STYLE},
        alias='email_system',
    )

    with ContainerBoundary(
        'Customer Support System',
        'Components that handle support tickets and expert assignments.',
        d2={
            'direction': 'right',
            'style': {
                'fill': '#fafafa',
                'stroke': '#90a4ae',
                'stroke_dash': 4,
            },
        },
        alias='sysops_system',
    ):
        customer_portal = Component(
            'Customer Portal',
            'Ticket creation and status tracking.',
            technology='SPA',
            d2={'style': FRONTEND_STYLE},
            alias='customer_portal',
        )
        mobile_app = Component(
            'Expert Mobile App',
            'Assignment queue and field repair updates.',
            technology='iOS / Android',
            d2={'style': FRONTEND_STYLE},
            alias='mobile_app',
        )
        api_gateway = Component(
            'API Gateway',
            'Access control and request routing.',
            technology='Container Service',
            d2={'style': GATEWAY_STYLE},
            alias='api_gateway',
        )
        ticket_api = Component(
            'Ticket API',
            'Ticket orchestration, search, and assignment updates.',
            technology='Container Service',
            d2={'style': BACKEND_STYLE},
            alias='ticket_api',
        )
        ticket_processor = Component(
            'Ticket Processor',
            'Creates expert assignments for new tickets.',
            technology='Container Job',
            d2={'style': WORKER_STYLE},
            alias='ticket_processor',
        )
        notification_service = Component(
            'Notification Service',
            'Sends customer and expert notifications.',
            technology='Container Service',
            d2={'style': BACKEND_STYLE},
            alias='notification_service',
        )
        sysops_database = ComponentDb(
            'Support Database',
            'Tickets, contacts, assignments, and repair history.',
            technology='PostgreSQL',
            d2={'style': DATABASE_STYLE},
            alias='sysops_database',
        )
        ticket_created_queue = ComponentQueue(
            'Ticket Created',
            'Event stream for new support tickets.',
            technology='Message Queue',
            d2={'style': QUEUE_STYLE},
            alias='ticket_created_queue',
        )

    customer >> Rel('Uses', technology='HTTPS', d2={'style': SYNC_REL_STYLE}) >> customer_portal
    expert >> Rel('Uses', technology='HTTPS', d2={'style': SYNC_REL_STYLE}) >> mobile_app

    customer_portal >> Rel('Authenticates', technology='OIDC', d2={'style': EXTERNAL_REL_STYLE}) >> auth0
    mobile_app >> Rel('Authenticates', technology='OIDC', d2={'style': EXTERNAL_REL_STYLE}) >> auth0

    customer_portal >> Rel('Calls', technology='REST/HTTPS', d2={'style': SYNC_REL_STYLE}) >> api_gateway
    mobile_app >> Rel('Calls', technology='REST/HTTPS', d2={'style': SYNC_REL_STYLE}) >> api_gateway
    api_gateway >> Rel('Routes', technology='REST/HTTP', d2={'style': SYNC_REL_STYLE}) >> ticket_api

    ticket_api >> Rel('Reads/writes', technology='SQL/TCP', d2={'style': DATA_REL_STYLE}) >> sysops_database
    ticket_processor >> Rel('Reads/writes', technology='SQL/TCP', d2={'style': DATA_REL_STYLE}) >> sysops_database
    ticket_api >> Rel('Publishes', technology='Queue/Event', d2={'style': ASYNC_REL_STYLE}) >> ticket_created_queue
    ticket_created_queue >> Rel('Triggers', technology='Queue/Event', d2={'style': ASYNC_REL_STYLE}) >> ticket_processor
    ticket_processor >> Rel('Requests notification', technology='REST/HTTP',
                            d2={'style': SYNC_REL_STYLE}) >> notification_service
    notification_service >> Rel('Sends e-mail', technology='SMTP', d2={'style': EXTERNAL_REL_STYLE}) >> email_system

d2_render_options = (
    D2RenderOptionsBuilder()
    .direction('down')
    .legend(
        D2Legend(
            label='Customer Support Component Legend',
            items=[
                D2LegendElement('Operational user', shape='person', style=USER_STYLE),
                D2LegendElement('User-facing frontend', style=FRONTEND_STYLE),
                D2LegendElement('API gateway', style=GATEWAY_STYLE),
                D2LegendElement('Backend service', style=BACKEND_STYLE),
                D2LegendElement('Background worker', style=WORKER_STYLE),
                D2LegendElement('Operational datastore', shape='cylinder', style=DATABASE_STYLE),
                D2LegendElement('Asynchronous event stream', shape='queue', style=QUEUE_STYLE),
                D2LegendElement('External dependency', style=EXTERNAL_STYLE),
                D2LegendRel('Synchronous call', style=SYNC_REL_STYLE),
                D2LegendRel('Asynchronous event', style=ASYNC_REL_STYLE),
                D2LegendRel('External call', style=EXTERNAL_REL_STYLE),
            ],
        ),
    )
    .build()
)

diagram.set_render_options(
    d2=d2_render_options,
)

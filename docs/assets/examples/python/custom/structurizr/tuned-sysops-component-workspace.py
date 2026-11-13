from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import AutoLayout


workspace = Workspace('Customer Support System - Tuned Component View')

# One style per element role, selected by tag.
workspace.styles.element('User', background='#e8f5e9', color='#1b5e20', stroke='#66bb6a', shape='Person')
workspace.styles.element('Frontend', background='#e3f2fd', color='#0d47a1', stroke='#42a5f5')
workspace.styles.element('Gateway', background='#fce4ec', color='#880e4f', stroke='#ec407a')
workspace.styles.element('Backend', background='#ede7f6', color='#311b92', stroke='#7e57c2')
workspace.styles.element('Worker', background='#fff3e0', color='#e65100', stroke='#fb8c00')
workspace.styles.element('Database', background='#fff8e1', color='#5d4037', stroke='#ffb300', shape='Cylinder')
workspace.styles.element('Queue', background='#e0f2f1', color='#004d40', stroke='#26a69a', shape='Pipe')
workspace.styles.element('External', background='#f5f5f5', color='#424242', stroke='#9e9e9e', border='Dashed')

# One style per relationship role.
workspace.styles.relationship('Sync', color='#1e88e5', border='Solid', thickness=2)
workspace.styles.relationship('Data', color='#8d6e63', border='Solid', thickness=2)
workspace.styles.relationship('Async', color='#00897b', border='Dotted', thickness=2)
workspace.styles.relationship('External', color='#78909c', border='Dashed', thickness=2)

with workspace.model as model:
    customer = model.Person(
        'Customer',
        description='Reports equipment issues and tracks repair progress.',
        alias='customer',
        tags=['User'],
    )
    expert = model.Person(
        'Support Expert',
        description='Accepts assignments and records repair updates.',
        alias='expert',
        tags=['User'],
    )
    auth0 = model.SoftwareSystem(
        'Auth0',
        description='External identity provider.',
        alias='auth0',
        tags=['External'],
    )
    email_system = model.SoftwareSystem(
        'E-mail System',
        description='Delivers customer and expert notifications.',
        alias='email_system',
        tags=['External'],
    )
    support = model.SoftwareSystem(
        'Customer Support System',
        description='Handles support tickets and expert assignments.',
        alias='support',
    )
    platform = model.Container(
        'Support Platform',
        description='Components that handle support tickets and expert assignments.',
        technology='Container Service',
        alias='platform',
        owner=support,
    )
    api_gateway = model.Component(
        'API Gateway',
        description='Access control and request routing.',
        technology='Container Service',
        alias='api_gateway',
        tags=['Gateway'],
        owner=platform,
    )
    customer_portal = model.Component(
        'Customer Portal',
        description='Ticket creation and status tracking.',
        technology='SPA',
        alias='customer_portal',
        tags=['Frontend'],
        owner=platform,
    )
    mobile_app = model.Component(
        'Expert Mobile App',
        description='Assignment queue and field repair updates.',
        technology='iOS / Android',
        alias='mobile_app',
        tags=['Frontend'],
        owner=platform,
    )
    notification_service = model.Component(
        'Notification Service',
        description='Sends customer and expert notifications.',
        technology='Container Service',
        alias='notification_service',
        tags=['Backend'],
        owner=platform,
    )
    sysops_database = model.Component(
        'Support Database',
        description='Tickets, contacts, assignments, and repair history.',
        technology='PostgreSQL',
        alias='sysops_database',
        tags=['Database'],
        owner=platform,
    )
    ticket_api = model.Component(
        'Ticket API',
        description='Ticket orchestration, search, and assignment updates.',
        technology='Container Service',
        alias='ticket_api',
        tags=['Backend'],
        owner=platform,
    )
    ticket_created_queue = model.Component(
        'Ticket Created',
        description='Event stream for new support tickets.',
        technology='Message Queue',
        alias='ticket_created_queue',
        tags=['Queue'],
        owner=platform,
    )
    ticket_processor = model.Component(
        'Ticket Processor',
        description='Creates expert assignments for new tickets.',
        technology='Container Job',
        alias='ticket_processor',
        tags=['Worker'],
        owner=platform,
    )

    customer.uses(customer_portal, 'Uses', technology='HTTPS', tags=['Sync'])
    expert.uses(mobile_app, 'Uses', technology='HTTPS', tags=['Sync'])
    customer_portal.uses(auth0, 'Authenticates', technology='OIDC', tags=['External'])
    mobile_app.uses(auth0, 'Authenticates', technology='OIDC', tags=['External'])
    customer_portal.uses(api_gateway, 'Calls', technology='REST/HTTPS', tags=['Sync'])
    mobile_app.uses(api_gateway, 'Calls', technology='REST/HTTPS', tags=['Sync'])
    api_gateway.uses(ticket_api, 'Routes', technology='REST/HTTP', tags=['Sync'])
    ticket_api.uses(sysops_database, 'Reads/writes', technology='SQL/TCP', tags=['Data'])
    ticket_processor.uses(sysops_database, 'Reads/writes', technology='SQL/TCP', tags=['Data'])
    ticket_api.uses(ticket_created_queue, 'Publishes', technology='Queue/Event', tags=['Async'])
    ticket_created_queue.uses(ticket_processor, 'Triggers', technology='Queue/Event', tags=['Async'])
    ticket_processor.uses(notification_service, 'Requests notification', technology='REST/HTTP', tags=['Sync'])
    notification_service.uses(email_system, 'Sends e-mail', technology='SMTP', tags=['External'])

workspace.views.ComponentView(
    platform,
    key='components',
    title='Customer Support System - Tuned Component View',
    auto_layout=AutoLayout(rank_direction='TopBottom'),
)

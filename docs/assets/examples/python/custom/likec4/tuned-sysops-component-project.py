from c4.contrib.likec4 import Project, Wildcard


project = Project('Customer Support System - Tuned Component View', view_key='components')

spec = project.specification
spec.color('user', '#66bb6a')
spec.color('frontend', '#42a5f5')
spec.color('gateway', '#ec407a')
spec.color('backend', '#7e57c2')
spec.color('worker', '#fb8c00')
spec.color('database', '#ffb300')
spec.color('queue', '#26a69a')
spec.color('external', '#9e9e9e')
spec.element('actor', notation='Person', color='user', shape='person')
spec.element('system', color='primary')
spec.element('external', notation='External system', color='external')
spec.element('frontend', notation='Frontend', color='frontend', shape='browser')
spec.element('gateway', notation='API gateway', color='gateway')
spec.element('backend', notation='Backend service', color='backend', shape='component')
spec.element('worker', notation='Background worker', color='worker', shape='component')
spec.element('database', notation='Datastore', color='database', shape='storage')
spec.element('queue', notation='Event stream', color='queue', shape='queue')
spec.relationship('sync', color='sky')
spec.relationship('data', color='amber')
spec.relationship('async', color='green', line='dotted')
spec.relationship('external-call', color='muted', line='dashed')

model = project.model
customer = model.element(
    'actor',
    'Customer',
    alias='customer',
    description='Reports equipment issues and tracks repair progress.',
)
expert = model.element(
    'actor',
    'Support Expert',
    alias='expert',
    description='Accepts assignments and records repair updates.',
)
auth0 = model.element(
    'external',
    'Auth0',
    alias='auth0',
    description='External identity provider.',
    technology='OIDC/OAuth2',
)
email_system = model.element(
    'external',
    'E-mail System',
    alias='email_system',
    description='Delivers customer and expert notifications.',
    technology='SMTP',
)
support = model.element(
    'system',
    'Customer Support System',
    alias='support',
    description='Components that handle support tickets and expert assignments.',
)
api_gateway = model.element(
    'gateway',
    'API Gateway',
    parent=support,
    alias='api_gateway',
    description='Access control and request routing.',
    technology='Container Service',
)
customer_portal = model.element(
    'frontend',
    'Customer Portal',
    parent=support,
    alias='customer_portal',
    description='Ticket creation and status tracking.',
    technology='SPA',
)
mobile_app = model.element(
    'frontend',
    'Expert Mobile App',
    parent=support,
    alias='mobile_app',
    description='Assignment queue and field repair updates.',
    technology='iOS / Android',
)
notification_service = model.element(
    'backend',
    'Notification Service',
    parent=support,
    alias='notification_service',
    description='Sends customer and expert notifications.',
    technology='Container Service',
)
sysops_database = model.element(
    'database',
    'Support Database',
    parent=support,
    alias='sysops_database',
    description='Tickets, contacts, assignments, and repair history.',
    technology='PostgreSQL',
)
ticket_api = model.element(
    'backend',
    'Ticket API',
    parent=support,
    alias='ticket_api',
    description='Ticket orchestration, search, and assignment updates.',
    technology='Container Service',
)
ticket_created_queue = model.element(
    'queue',
    'Ticket Created',
    parent=support,
    alias='ticket_created_queue',
    description='Event stream for new support tickets.',
    technology='Message Queue',
)
ticket_processor = model.element(
    'worker',
    'Ticket Processor',
    parent=support,
    alias='ticket_processor',
    description='Creates expert assignments for new tickets.',
    technology='Container Job',
)

customer.uses(customer_portal, 'Uses', technology='HTTPS', kind='sync')
expert.uses(mobile_app, 'Uses', technology='HTTPS', kind='sync')
customer_portal.uses(auth0, 'Authenticates', technology='OIDC', kind='external-call')
mobile_app.uses(auth0, 'Authenticates', technology='OIDC', kind='external-call')
customer_portal.uses(api_gateway, 'Calls', technology='REST/HTTPS', kind='sync')
mobile_app.uses(api_gateway, 'Calls', technology='REST/HTTPS', kind='sync')
api_gateway.uses(ticket_api, 'Routes', technology='REST/HTTP', kind='sync')
ticket_api.uses(sysops_database, 'Reads/writes', technology='SQL/TCP', kind='data')
ticket_processor.uses(sysops_database, 'Reads/writes', technology='SQL/TCP', kind='data')
ticket_api.uses(ticket_created_queue, 'Publishes', technology='Queue/Event', kind='async')
ticket_created_queue.uses(ticket_processor, 'Triggers', technology='Queue/Event', kind='async')
ticket_processor.uses(notification_service, 'Requests notification', technology='REST/HTTP', kind='sync')
notification_service.uses(email_system, 'Sends e-mail', technology='SMTP', kind='external-call')

components = project.views.element_view(
    'components', 'Customer Support System - Tuned Component View', of=support
)
components.include(Wildcard())
components.auto_layout('TopBottom')

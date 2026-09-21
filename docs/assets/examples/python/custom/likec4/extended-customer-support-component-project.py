from c4.contrib.likec4 import Project, Wildcard


project = Project('Customer Support System - Extended Component View', view_key='components')

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
administrator = model.element(
    'actor',
    'Administrator',
    alias='administrator',
    description='Internal user with administrative access.',
)
customer = model.element(
    'actor',
    'Customer',
    alias='customer',
    description='Owner of electronic equipment and support plan; reports issues.',
)
helpdesk = model.element(
    'actor',
    'Helpdesk',
    alias='helpdesk',
    description='First line of support; provides direct phone support.',
)
manager = model.element(
    'actor',
    'Manager',
    alias='manager',
    description='Monitors expert performance and customer satisfaction.',
)
support_expert = model.element(
    'actor',
    'Support Expert',
    alias='support_expert',
    description='Technology expert who fixes customer electronic devices.',
)
auth0 = model.element(
    'external',
    'Auth0',
    alias='auth0',
    description='External identity provider for authentication.',
    technology='OIDC/OAuth2',
)
email_system = model.element(
    'external',
    'E-mail System',
    alias='email_system',
    description='Internal mail system used for e-mail delivery.',
    technology='SMTP',
)
payment_provider = model.element(
    'external',
    'Payment Service Provider',
    alias='payment_provider',
    description='External online payment service.',
    technology='HTTPS/API',
)
sms_provider = model.element(
    'external',
    'SMS Service Provider',
    alias='sms_provider',
    description='Provides SMS text messaging.',
    technology='SMS API',
)
support = model.element(
    'system',
    'Customer Support System',
    alias='support',
    description='Components that handle support tickets and expert assignments.',
)
admin_api = model.element(
    'backend',
    'Admin API',
    parent=support,
    alias='admin_api',
    description='User management and reference-data management.',
    technology='Container Service',
)
admin_portal = model.element(
    'frontend',
    'Admin Portal',
    parent=support,
    alias='admin_portal',
    description='Manages system users and reference data.',
    technology='Single-page Application',
)
analytics_api = model.element(
    'backend',
    'Analytics API',
    parent=support,
    alias='analytics_api',
    description='Ticket status reports, survey analysis and performance reports.',
    technology='Container Service',
)
api_gateway = model.element(
    'gateway',
    'API Gateway',
    parent=support,
    alias='api_gateway',
    description='Performs access control, security checks and request routing.',
    technology='Container Service',
)
billing_api = model.element(
    'backend',
    'Billing API',
    parent=support,
    alias='billing_api',
    description='Billing management and financial reports.',
    technology='Container Service',
)
billing_portal = model.element(
    'frontend',
    'Billing Portal',
    parent=support,
    alias='billing_portal',
    description='Supports billing processing.',
    technology='Single-page Application',
)
customer_api = model.element(
    'backend',
    'Customer API',
    parent=support,
    alias='customer_api',
    description='Handles registration, profiles, tickets, surveys and billing history.',
    technology='Container Service',
)
customer_notifications_queue = model.element(
    'queue',
    'Customer Notifications',
    parent=support,
    alias='customer_notifications_queue',
    description='Asynchronous message channel for customer notifications.',
    technology='Message Queue',
)
customer_portal = model.element(
    'frontend',
    'Customer Portal',
    parent=support,
    alias='customer_portal',
    description='Provides access to customer profile, billing, ticket creation and history.',
    technology='Single-page Application',
)
expert_notifications_queue = model.element(
    'queue',
    'Expert Notifications',
    parent=support,
    alias='expert_notifications_queue',
    description='Asynchronous message channel for expert notifications.',
    technology='Message Queue',
)
helpdesk_portal = model.element(
    'frontend',
    'Helpdesk Portal',
    parent=support,
    alias='helpdesk_portal',
    description='Provides access to tickets and status.',
    technology='Single-page Application',
)
invoice_queue = model.element(
    'queue',
    'Invoice',
    parent=support,
    alias='invoice_queue',
    description='Asynchronous message channel for invoice processing.',
    technology='Message Queue',
)
knowledge_base = model.element(
    'frontend',
    'Knowledge Base',
    parent=support,
    alias='knowledge_base',
    description='Supports searching and updating knowledge-base articles.',
    technology='Single-page Application',
)
mobile_app = model.element(
    'frontend',
    'Mobile App',
    parent=support,
    alias='mobile_app',
    description='Provides access to assigned tickets and knowledge-base search.',
    technology='iOS / Android App',
)
notification_service = model.element(
    'backend',
    'Notification Service',
    parent=support,
    alias='notification_service',
    description='Sends SMS and e-mail messages based on notification preferences.',
    technology='Container Service',
)
payment_job = model.element(
    'worker',
    'Payment',
    parent=support,
    alias='payment_job',
    description='Runs monthly and performs payment operations.',
    technology='Container Job',
)
support_api = model.element(
    'backend',
    'Support API',
    parent=support,
    alias='support_api',
    description='Ticket orchestration, search, assignment handling and knowledge-base updates.',
    technology='Container Service',
)
support_dashboard = model.element(
    'frontend',
    'Support Dashboard',
    parent=support,
    alias='support_dashboard',
    description='Provides analytics and operational reports.',
    technology='Single-page Application',
)
support_database = model.element(
    'database',
    'Support Database',
    parent=support,
    alias='support_database',
    description='Stores tickets, users, customer contacts and knowledge-base content.',
    technology='Relational Database',
)
ticket_assigned_queue = model.element(
    'queue',
    'Ticket Assigned',
    parent=support,
    alias='ticket_assigned_queue',
    description='Asynchronous message channel for assigned tickets.',
    technology='Message Queue',
)
ticket_created_queue = model.element(
    'queue',
    'Ticket Created',
    parent=support,
    alias='ticket_created_queue',
    description='Asynchronous message channel for created tickets.',
    technology='Message Queue',
)
ticket_processor = model.element(
    'worker',
    'Ticket Processor',
    parent=support,
    alias='ticket_processor',
    description='Runs periodically, scans ticket statuses, and creates assignments.',
    technology='Container Job',
)
ticket_progress_queue = model.element(
    'queue',
    'Ticket In-Progress/Closed',
    parent=support,
    alias='ticket_progress_queue',
    description='Asynchronous message channel for ticket progress and closure notifications.',
    technology='Message Queue',
)

admin_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', kind='data')
admin_portal.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', kind='sync')
analytics_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', kind='data')
api_gateway.uses(customer_api, 'Routes API calls to', technology='REST/HTTP', kind='sync')
api_gateway.uses(support_api, 'Routes API calls to', technology='REST/HTTP', kind='sync')
api_gateway.uses(admin_api, 'Routes API calls to', technology='REST/HTTP', kind='sync')
api_gateway.uses(billing_api, 'Routes API calls to', technology='REST/HTTP', kind='sync')
api_gateway.uses(analytics_api, 'Routes API calls to', technology='REST/HTTP', kind='sync')
billing_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', kind='data')
billing_portal.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', kind='sync')
customer_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', kind='data')
customer_api.uses(ticket_created_queue, 'Sends ticket created event', technology='Queue / Event', kind='async')
customer_portal.uses(auth0, 'Authenticates using', technology='OIDC/OAuth2', kind='external-call')
customer_portal.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', kind='sync')
helpdesk_portal.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', kind='sync')
knowledge_base.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', kind='sync')
mobile_app.uses(auth0, 'Authenticates using', technology='OIDC/OAuth2', kind='external-call')
mobile_app.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', kind='sync')
notification_service.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', kind='data')
notification_service.uses(email_system, 'Sends e-mail using', technology='SMTP', kind='external-call')
notification_service.uses(sms_provider, 'Sends SMS using', technology='SMS API', kind='external-call')
payment_job.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', kind='data')
payment_job.uses(invoice_queue, 'Sends invoice event', technology='Queue / Event', kind='async')
payment_job.uses(payment_provider, 'Executes payments using', technology='HTTPS/API', kind='external-call')
support_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', kind='data')
support_api.uses(expert_notifications_queue, 'Sends expert notification event', technology='Queue / Event', kind='async')
support_api.uses(customer_notifications_queue, 'Sends customer notification event', technology='Queue / Event', kind='async')
support_api.uses(ticket_progress_queue, 'Sends progress/closed event', technology='Queue / Event', kind='async')
support_dashboard.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', kind='sync')
ticket_processor.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', kind='data')
ticket_processor.uses(ticket_assigned_queue, 'Sends ticket assignment event', technology='Queue / Event', kind='async')
administrator.uses(admin_portal, 'Maintains users and reference data', technology='HTTPS', kind='sync')
administrator.uses(billing_portal, 'Manages billing operations', technology='HTTPS', kind='sync')
customer.uses(customer_portal, 'Uses', technology='HTTPS', kind='sync')
customer.uses(mobile_app, 'Uses', technology='HTTPS', kind='sync')
helpdesk.uses(helpdesk_portal, 'Creates/searches tickets', technology='HTTPS', kind='sync')
manager.uses(support_dashboard, 'Tracks operations and generates reports', technology='HTTPS', kind='sync')
support_expert.uses(mobile_app, 'Uses', technology='HTTPS', kind='sync')
support_expert.uses(knowledge_base, 'Updates articles', technology='HTTPS', kind='sync')
customer_notifications_queue.uses(notification_service, 'Consumed by', technology='Queue / Event', kind='async')
expert_notifications_queue.uses(notification_service, 'Consumed by', technology='Queue / Event', kind='async')
invoice_queue.uses(api_gateway, 'Calls billing APIs through', technology='REST/HTTP', kind='async')
ticket_assigned_queue.uses(support_api, 'Consumed by', technology='Queue / Event', kind='async')
ticket_created_queue.uses(ticket_processor, 'Consumed by', technology='Queue / Event', kind='async')
ticket_progress_queue.uses(customer_api, 'Consumed by', technology='Queue / Event', kind='async')

components = project.views.element_view(
    'components', 'Customer Support System - Extended Component View', of=support
)
components.include(Wildcard())
components.auto_layout('TopBottom')

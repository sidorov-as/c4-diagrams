from c4.contrib.structurizr import Workspace
from c4.contrib.structurizr.renderer import AutoLayout


workspace = Workspace('Customer Support System - Extended Component View')

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
    administrator = model.Person(
        'Administrator',
        description='Internal user with administrative access.',
        alias='administrator',
        tags=['User'],
    )
    customer = model.Person(
        'Customer',
        description='Owner of electronic equipment and support plan; reports issues.',
        alias='customer',
        tags=['User'],
    )
    helpdesk = model.Person(
        'Helpdesk',
        description='First line of support; provides direct phone support.',
        alias='helpdesk',
        tags=['User'],
    )
    manager = model.Person(
        'Manager',
        description='Monitors expert performance and customer satisfaction.',
        alias='manager',
        tags=['User'],
    )
    support_expert = model.Person(
        'Support Expert',
        description='Technology expert who fixes customer electronic devices.',
        alias='support_expert',
        tags=['User'],
    )
    auth0 = model.SoftwareSystem(
        'Auth0',
        description='External identity provider for authentication.',
        alias='auth0',
        tags=['External'],
    )
    email_system = model.SoftwareSystem(
        'E-mail System',
        description='Internal mail system used for e-mail delivery.',
        alias='email_system',
        tags=['External'],
    )
    payment_provider = model.SoftwareSystem(
        'Payment Service Provider',
        description='External online payment service.',
        alias='payment_provider',
        tags=['External'],
    )
    sms_provider = model.SoftwareSystem(
        'SMS Service Provider',
        description='Provides SMS text messaging.',
        alias='sms_provider',
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
    admin_api = model.Component(
        'Admin API',
        description='User management and reference-data management.',
        technology='Container Service',
        alias='admin_api',
        tags=['Backend'],
        owner=platform,
    )
    admin_portal = model.Component(
        'Admin Portal',
        description='Manages system users and reference data.',
        technology='Single-page Application',
        alias='admin_portal',
        tags=['Frontend'],
        owner=platform,
    )
    analytics_api = model.Component(
        'Analytics API',
        description='Ticket status reports, survey analysis and performance reports.',
        technology='Container Service',
        alias='analytics_api',
        tags=['Backend'],
        owner=platform,
    )
    api_gateway = model.Component(
        'API Gateway',
        description='Performs access control, security checks and request routing.',
        technology='Container Service',
        alias='api_gateway',
        tags=['Gateway'],
        owner=platform,
    )
    billing_api = model.Component(
        'Billing API',
        description='Billing management and financial reports.',
        technology='Container Service',
        alias='billing_api',
        tags=['Backend'],
        owner=platform,
    )
    billing_portal = model.Component(
        'Billing Portal',
        description='Supports billing processing.',
        technology='Single-page Application',
        alias='billing_portal',
        tags=['Frontend'],
        owner=platform,
    )
    customer_api = model.Component(
        'Customer API',
        description='Handles registration, profiles, tickets, surveys and billing history.',
        technology='Container Service',
        alias='customer_api',
        tags=['Backend'],
        owner=platform,
    )
    customer_notifications_queue = model.Component(
        'Customer Notifications',
        description='Asynchronous message channel for customer notifications.',
        technology='Message Queue',
        alias='customer_notifications_queue',
        tags=['Queue'],
        owner=platform,
    )
    customer_portal = model.Component(
        'Customer Portal',
        description='Provides access to customer profile, billing, ticket creation and history.',
        technology='Single-page Application',
        alias='customer_portal',
        tags=['Frontend'],
        owner=platform,
    )
    expert_notifications_queue = model.Component(
        'Expert Notifications',
        description='Asynchronous message channel for expert notifications.',
        technology='Message Queue',
        alias='expert_notifications_queue',
        tags=['Queue'],
        owner=platform,
    )
    helpdesk_portal = model.Component(
        'Helpdesk Portal',
        description='Provides access to tickets and status.',
        technology='Single-page Application',
        alias='helpdesk_portal',
        tags=['Frontend'],
        owner=platform,
    )
    invoice_queue = model.Component(
        'Invoice',
        description='Asynchronous message channel for invoice processing.',
        technology='Message Queue',
        alias='invoice_queue',
        tags=['Queue'],
        owner=platform,
    )
    knowledge_base = model.Component(
        'Knowledge Base',
        description='Supports searching and updating knowledge-base articles.',
        technology='Single-page Application',
        alias='knowledge_base',
        tags=['Frontend'],
        owner=platform,
    )
    mobile_app = model.Component(
        'Mobile App',
        description='Provides access to assigned tickets and knowledge-base search.',
        technology='iOS / Android App',
        alias='mobile_app',
        tags=['Frontend'],
        owner=platform,
    )
    notification_service = model.Component(
        'Notification Service',
        description='Sends SMS and e-mail messages based on notification preferences.',
        technology='Container Service',
        alias='notification_service',
        tags=['Backend'],
        owner=platform,
    )
    payment_job = model.Component(
        'Payment',
        description='Runs monthly and performs payment operations.',
        technology='Container Job',
        alias='payment_job',
        tags=['Worker'],
        owner=platform,
    )
    support_api = model.Component(
        'Support API',
        description='Ticket orchestration, search, assignment handling and knowledge-base updates.',
        technology='Container Service',
        alias='support_api',
        tags=['Backend'],
        owner=platform,
    )
    support_dashboard = model.Component(
        'Support Dashboard',
        description='Provides analytics and operational reports.',
        technology='Single-page Application',
        alias='support_dashboard',
        tags=['Frontend'],
        owner=platform,
    )
    support_database = model.Component(
        'Support Database',
        description='Stores tickets, users, customer contacts and knowledge-base content.',
        technology='Relational Database',
        alias='support_database',
        tags=['Database'],
        owner=platform,
    )
    ticket_assigned_queue = model.Component(
        'Ticket Assigned',
        description='Asynchronous message channel for assigned tickets.',
        technology='Message Queue',
        alias='ticket_assigned_queue',
        tags=['Queue'],
        owner=platform,
    )
    ticket_created_queue = model.Component(
        'Ticket Created',
        description='Asynchronous message channel for created tickets.',
        technology='Message Queue',
        alias='ticket_created_queue',
        tags=['Queue'],
        owner=platform,
    )
    ticket_processor = model.Component(
        'Ticket Processor',
        description='Runs periodically, scans ticket statuses, and creates assignments.',
        technology='Container Job',
        alias='ticket_processor',
        tags=['Worker'],
        owner=platform,
    )
    ticket_progress_queue = model.Component(
        'Ticket In-Progress/Closed',
        description='Asynchronous message channel for ticket progress and closure notifications.',
        technology='Message Queue',
        alias='ticket_progress_queue',
        tags=['Queue'],
        owner=platform,
    )

    admin_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', tags=['Data'])
    admin_portal.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', tags=['Sync'])
    analytics_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', tags=['Data'])
    api_gateway.uses(customer_api, 'Routes API calls to', technology='REST/HTTP', tags=['Sync'])
    api_gateway.uses(support_api, 'Routes API calls to', technology='REST/HTTP', tags=['Sync'])
    api_gateway.uses(admin_api, 'Routes API calls to', technology='REST/HTTP', tags=['Sync'])
    api_gateway.uses(billing_api, 'Routes API calls to', technology='REST/HTTP', tags=['Sync'])
    api_gateway.uses(analytics_api, 'Routes API calls to', technology='REST/HTTP', tags=['Sync'])
    billing_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', tags=['Data'])
    billing_portal.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', tags=['Sync'])
    customer_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', tags=['Data'])
    customer_api.uses(ticket_created_queue, 'Sends ticket created event', technology='Queue / Event', tags=['Async'])
    customer_portal.uses(auth0, 'Authenticates using', technology='OIDC/OAuth2', tags=['External'])
    customer_portal.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', tags=['Sync'])
    helpdesk_portal.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', tags=['Sync'])
    knowledge_base.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', tags=['Sync'])
    mobile_app.uses(auth0, 'Authenticates using', technology='OIDC/OAuth2', tags=['External'])
    mobile_app.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', tags=['Sync'])
    notification_service.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', tags=['Data'])
    notification_service.uses(email_system, 'Sends e-mail using', technology='SMTP', tags=['External'])
    notification_service.uses(sms_provider, 'Sends SMS using', technology='SMS API', tags=['External'])
    payment_job.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', tags=['Data'])
    payment_job.uses(invoice_queue, 'Sends invoice event', technology='Queue / Event', tags=['Async'])
    payment_job.uses(payment_provider, 'Executes payments using', technology='HTTPS/API', tags=['External'])
    support_api.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', tags=['Data'])
    support_api.uses(expert_notifications_queue, 'Sends expert notification event', technology='Queue / Event', tags=['Async'])
    support_api.uses(customer_notifications_queue, 'Sends customer notification event', technology='Queue / Event', tags=['Async'])
    support_api.uses(ticket_progress_queue, 'Sends progress/closed event', technology='Queue / Event', tags=['Async'])
    support_dashboard.uses(api_gateway, 'Makes API calls to', technology='REST/HTTPS', tags=['Sync'])
    ticket_processor.uses(support_database, 'Reads from and writes to', technology='SQL/TCP', tags=['Data'])
    ticket_processor.uses(ticket_assigned_queue, 'Sends ticket assignment event', technology='Queue / Event', tags=['Async'])
    administrator.uses(admin_portal, 'Maintains users and reference data', technology='HTTPS', tags=['Sync'])
    administrator.uses(billing_portal, 'Manages billing operations', technology='HTTPS', tags=['Sync'])
    customer.uses(customer_portal, 'Uses', technology='HTTPS', tags=['Sync'])
    customer.uses(mobile_app, 'Uses', technology='HTTPS', tags=['Sync'])
    helpdesk.uses(helpdesk_portal, 'Creates/searches tickets', technology='HTTPS', tags=['Sync'])
    manager.uses(support_dashboard, 'Tracks operations and generates reports', technology='HTTPS', tags=['Sync'])
    support_expert.uses(mobile_app, 'Uses', technology='HTTPS', tags=['Sync'])
    support_expert.uses(knowledge_base, 'Updates articles', technology='HTTPS', tags=['Sync'])
    customer_notifications_queue.uses(notification_service, 'Consumed by', technology='Queue / Event', tags=['Async'])
    expert_notifications_queue.uses(notification_service, 'Consumed by', technology='Queue / Event', tags=['Async'])
    invoice_queue.uses(api_gateway, 'Calls billing APIs through', technology='REST/HTTP', tags=['Async'])
    ticket_assigned_queue.uses(support_api, 'Consumed by', technology='Queue / Event', tags=['Async'])
    ticket_created_queue.uses(ticket_processor, 'Consumed by', technology='Queue / Event', tags=['Async'])
    ticket_progress_queue.uses(customer_api, 'Consumed by', technology='Queue / Event', tags=['Async'])

workspace.views.ComponentView(
    platform,
    key='components',
    title='Customer Support System - Extended Component View',
    auto_layout=AutoLayout(rank_direction='TopBottom'),
)

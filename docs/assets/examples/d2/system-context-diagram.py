from c4 import (
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    System,
    SystemContextDiagram,
    SystemExt,
)
from c4.renderers import (
    D2RenderOptionsBuilder,
)


with SystemContextDiagram(title='Retail Platform - System Context') as diagram:
    customer = Person('Customer', 'Browses products, places orders, and tracks delivery.', d2={'style': {'stroke': '#7c3aed', 'fill': '#f7f0ff'}, 'tooltip': 'Primary customer persona for the commerce platform.'}, alias='customer')
    customer.add_property('Channel', 'Web / Mobile')
    customer.add_property('Auth', 'OIDC')

    support_agent = PersonExt('Support Agent', 'Investigates order and payment issues from a vendor CRM.', d2={'style': {'stroke': '#ea580c', 'fill': '#fff7ed'}}, alias='support_agent')
    support_agent.add_property('Organization', 'Support Vendor')
    support_agent.add_property('SLA', 'Business hours')

    payment_provider = SystemExt('Payment Provider', 'Authorizes payments and sends asynchronous payment webhooks.', d2={'style': {'stroke': '#059669', 'fill': '#ecfdf5'}}, alias='payment_provider')
    payment_provider.add_property('PCI scope', 'External')
    payment_provider.add_property('Webhook retry', '24 hours')

    crm_platform = SystemExt('CRM Platform', 'External case management system used by support agents.', alias='crm_platform')
    crm_platform.add_property('Vendor', 'Zendesk')
    crm_platform.add_property('Data sync', 'Near real-time')

    notification_gateway = SystemExt('Email & SMS Gateway', 'Delivers transactional notifications to customers.', alias='notification_gateway')
    notification_gateway.add_property('Provider', 'Multi-region')
    notification_gateway.add_property('Fallback', 'SMS')

    with EnterpriseBoundary('Acme Corp', 'Internal systems owned by Acme.', d2={'style': {'stroke': '#4f46e5', 'fill': '#eef2ff'}}, alias='acme_enterprise'):
        retail_platform = System('Retail Platform', 'Core platform for catalog, checkout, payments, and order management.', d2={'style': {'stroke': '#2563eb', 'fill': '#eff6ff'}}, alias='retail_platform')
        retail_platform.add_property('Owner', 'Commerce Platform')
        retail_platform.add_property('Availability', '99.95%')

        analytics_platform = System('Analytics Platform', 'Consumes commerce events for reporting and personalization.', d2={'style': {'stroke': '#0f766e', 'fill': '#f0fdfa'}}, alias='analytics_platform')
        analytics_platform.add_property('Owner', 'Data Platform')
        analytics_platform.add_property('Freshness', '< 15 min')

    customer >> Rel('Browses catalog and places orders', technology='HTTPS', d2={'style': {'stroke': '#2563eb'}}) >> retail_platform
    retail_platform >> Rel('Creates payment intents', technology='REST/JSON') >> payment_provider
    payment_provider >> Rel('Sends payment webhooks', technology='HTTPS') >> retail_platform
    retail_platform >> Rel('Sends order notifications', technology='SMTP / SMPP') >> notification_gateway
    support_agent >> Rel('Manages customer cases', technology='Web UI') >> crm_platform
    crm_platform >> Rel('Queries order status', technology='OAuth2 / REST') >> retail_platform
    retail_platform >> Rel('Publishes commerce events', technology='Kafka') >> analytics_platform


d2_render_options = (
    D2RenderOptionsBuilder()
    .include_properties(
        True,
    )
    .bidirectional_relationships(
        'single_edge',
    )
    .build()
)

diagram.set_render_options(
    d2=d2_render_options,
)

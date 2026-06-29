from c4 import (
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDbExt,
    ContainerDiagram,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    SystemBoundary,
    SystemExt,
)
from c4.renderers import (
    D2RenderOptionsBuilder,
)


with ContainerDiagram(title='Online Shop - Container Diagram') as diagram:
    customer = Person('Customer', 'Browses products and places orders.', d2={'style': {'stroke': '#7c3aed', 'fill': '#f7f0ff'}}, alias='customer')
    customer.add_property('Channel', 'Web / Mobile')
    customer.add_property('Auth', 'OIDC')

    support_agent = PersonExt('Support Agent', 'Investigates customer issues from an external support tool.', alias='support_agent')
    support_agent.add_property('Organization', 'Support Vendor')
    support_agent.add_property('Tooling', 'CRM')

    payment_provider = SystemExt('Payment Provider', 'Processes card payments and payment webhooks.', alias='payment_provider')
    payment_provider.add_property('PCI scope', 'External')
    payment_provider.add_property('Webhook retry', '24 hours')

    recommendation_api = ContainerExt('Recommendation API', 'Returns personalized product recommendations.', technology='REST API', alias='recommendation_api')
    recommendation_api.add_property('Latency SLO', '150ms')
    recommendation_api.add_property('Owner', 'Growth')

    fraud_db = ContainerDbExt('Fraud Signals DB', 'External datastore containing fraud intelligence.', technology='Vendor DB', alias='fraud_db')
    fraud_db.add_property('Feed', 'Hourly')
    fraud_db.add_property('Access', 'Read-only')

    shipping_events = ContainerQueueExt('Shipping Events Topic', 'External topic used by logistics partner.', technology='Kafka', alias='shipping_events')
    shipping_events.add_property('Contract', 'Avro')
    shipping_events.add_property('Retention', '14 days')

    with EnterpriseBoundary('Acme Corp', 'Enterprise boundary for internal commerce platforms.', d2={'style': {'stroke': '#4f46e5', 'fill': '#eef2ff'}}, alias='acme'):
        with SystemBoundary('Online Shop Platform', 'Main system boundary for the commerce platform.', d2={'direction': 'right'}, alias='shop_boundary'):
            web_app = Container('Web Application', 'Serves the storefront and checkout UI.', d2={'style': {'stroke': '#2563eb', 'fill': '#eff6ff'}}, technology='React + Next.js', alias='web_app')
            web_app.add_property('Runtime', 'Node.js')
            web_app.add_property('Team', 'Storefront')

            backend_api = Container('Backend API', 'Handles catalog, carts, checkout, and order APIs.', d2={'style': {'stroke': '#0f766e', 'fill': '#f0fdfa'}}, technology='Python / FastAPI', alias='backend_api')
            backend_api.add_property('Runtime', 'Python 3.12')
            backend_api.add_property('Team', 'Platform')

            orders_db = ContainerDb('Orders Database', 'Stores orders, payments, and status transitions.', technology='PostgreSQL', alias='orders_db')
            orders_db.add_property('Engine', 'PostgreSQL 16')
            orders_db.add_property('HA', 'Primary / Replica')

            order_events = ContainerQueue('Order Events Queue', 'Publishes asynchronous order lifecycle events.', technology='Kafka', alias='order_events')
            order_events.add_property('Retention', '7 days')
            order_events.add_property('Format', 'JSON')

            with ContainerBoundary('Checkout Subsystem', 'Groups checkout-related containers.', d2={'direction': 'right'}, alias='checkout_boundary'):
                checkout_api = Container('Checkout API', 'Handles checkout and payment orchestration.', technology='Python / FastAPI', alias='checkout_api')
                checkout_api.add_property('Autoscaling', 'Enabled')
                checkout_api.add_property('SLO', '99.9%')

                checkout_db = ContainerDb('Checkout DB', 'Stores checkout sessions.', technology='PostgreSQL', alias='checkout_db')
                checkout_db.add_property('TTL', '30 days')
                checkout_db.add_property('Encryption', 'KMS')

                checkout_api >> Rel('Reads and writes', technology='SQL') >> checkout_db

    customer >> Rel('Uses', technology='HTTPS') >> web_app
    web_app >> Rel('Calls', technology='HTTPS/JSON') >> backend_api
    web_app >> Rel('Submits checkout', technology='HTTPS/JSON') >> checkout_api
    backend_api >> Rel('Reads and writes', technology='SQL') >> orders_db
    backend_api >> Rel('Publishes order events', technology='Kafka') >> order_events
    checkout_api >> Rel('Creates payment intents', technology='REST API') >> payment_provider
    backend_api >> Rel('Fetches recommendations', technology='REST API') >> recommendation_api
    backend_api >> Rel('Checks fraud signals', technology='JDBC') >> fraud_db
    shipping_events >> Rel('Delivers shipping updates', technology='Kafka') >> backend_api
    support_agent >> Rel('Queries order state', technology='HTTPS') >> backend_api


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

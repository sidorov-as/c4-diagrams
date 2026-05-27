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


with ContainerDiagram(title='Online Shop - Container Diagram') as diagram:
    customer = Person('Customer', 'Browses products and places orders.', plantuml={'tags': []}, alias='customer')
    customer.add_property('Channel', 'Web / Mobile')

    support_agent = PersonExt('Support Agent', 'Investigates customer issues from an external support tool.', plantuml={'tags': []}, alias='support_agent')
    support_agent.add_property('Organization', 'Support Vendor')

    payment_provider = SystemExt('Payment Provider', 'Processes card payments and payment webhooks.', plantuml={'tags': []}, alias='payment_provider')

    recommendation_api = ContainerExt('Recommendation API', 'Returns personalized product recommendations.', plantuml={'tags': []}, alias='recommendation_api')

    fraud_db = ContainerDbExt('Fraud Signals DB', 'External datastore containing fraud intelligence.', plantuml={'tags': []}, technology='Vendor DB', alias='fraud_db')

    shipping_events = ContainerQueueExt('Shipping Events Topic', 'External topic used by logistics partner.', plantuml={'tags': []}, technology='Kafka', alias='shipping_events')

    with EnterpriseBoundary('Acme Corp', 'Enterprise boundary for internal platforms.', alias='acme'):
        with SystemBoundary('Online Shop Platform', 'Main system boundary for the commerce platform.', alias='shop_boundary'):
            web_app = Container('Web Application', 'Serves the storefront and checkout UI.', plantuml={'tags': []}, technology='React + Next.js', alias='web_app')
            web_app.add_property('Runtime', 'Node.js')
            web_app.add_property('Team', 'Storefront')

            backend_api = Container('Backend API', 'Handles catalog, carts, checkout, and order APIs.', plantuml={'tags': []}, technology='Python / FastAPI', alias='backend_api')
            backend_api.add_property('Runtime', 'Python 3.12')
            backend_api.add_property('Team', 'Platform')

            orders_db = ContainerDb('Orders Database', 'Stores orders, payments, and status transitions.', plantuml={'tags': []}, technology='PostgreSQL', alias='orders_db')
            orders_db.add_property('Engine', 'PostgreSQL 16')
            orders_db.add_property('HA', 'Primary / Replica')

            order_events = ContainerQueue('Order Events Queue', 'Publishes asynchronous order lifecycle events.', plantuml={'tags': []}, technology='Kafka', alias='order_events')
            order_events.add_property('Retention', '7 days')
            order_events.add_property('Format', 'JSON')

            with ContainerBoundary('Checkout Subsystem', 'Groups checkout-related containers.', alias='checkout_boundary'):
                checkout_api = Container('Checkout API', 'Handles checkout and payment orchestration.', plantuml={'tags': []}, technology='Python / FastAPI', alias='checkout_api')

                checkout_db = ContainerDb('Checkout DB', 'Stores checkout sessions.', plantuml={'tags': []}, technology='PostgreSQL', alias='checkout_db')

                checkout_api >> Rel('Reads and writes', technology='SQL', plantuml={'tags': []}) >> checkout_db

    customer >> Rel('Uses', technology='HTTPS', plantuml={'tags': []}) >> web_app
    web_app >> Rel('Calls', technology='HTTPS/JSON', plantuml={'tags': []}) >> backend_api
    backend_api >> Rel('Reads and writes', technology='SQL', plantuml={'tags': []}) >> orders_db
    backend_api >> Rel('Publishes order events', technology='Kafka', plantuml={'tags': []}) >> order_events
    backend_api >> Rel('Creates payment intents', technology='REST API', plantuml={'tags': []}) >> payment_provider
    backend_api >> Rel('Fetches recommendations', technology='REST API', plantuml={'tags': []}) >> recommendation_api
    backend_api >> Rel('Checks fraud signals', technology='JDBC', plantuml={'tags': []}) >> fraud_db
    shipping_events >> Rel('Delivers shipping updates', technology='Kafka', plantuml={'tags': []}) >> backend_api
    support_agent >> Rel('Queries order state', technology='HTTPS', plantuml={'tags': []}) >> backend_api

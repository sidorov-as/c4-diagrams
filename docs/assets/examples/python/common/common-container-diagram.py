from c4 import (
    Container,
    ContainerDb,
    ContainerDiagram,
    ContainerQueue,
    Person,
    Rel,
    SystemBoundary,
    SystemExt,
)


with ContainerDiagram(title='Retail Platform - Containers') as diagram:
    customer = Person(
        'Customer',
        'Browses products and places orders.',
        alias='customer',
    )
    payment_provider = SystemExt(
        'Payment Provider',
        'Processes card payments.',
        alias='payment_provider',
    )

    with SystemBoundary(
        'Retail Platform',
        'Customer-facing commerce platform.',
        alias='retail_platform',
    ):
        web_app = Container(
            'Web Application',
            'Serves storefront and checkout screens.',
            technology='React',
            alias='web_app',
        )
        api = Container(
            'Backend API',
            'Handles catalog, cart, checkout, and order APIs.',
            technology='Python / FastAPI',
            alias='api',
        )
        database = ContainerDb(
            'Orders Database',
            'Stores orders, payments, and fulfillment status.',
            technology='PostgreSQL',
            alias='database',
        )
        events = ContainerQueue(
            'Order Events',
            'Publishes order lifecycle events.',
            technology='Kafka',
            alias='events',
        )

    customer >> Rel('Uses', technology='HTTPS') >> web_app
    web_app >> Rel('Calls', technology='HTTPS/JSON') >> api
    api >> Rel('Reads and writes', technology='SQL') >> database
    api >> Rel('Publishes events to', technology='Kafka') >> events
    api >> Rel('Creates payment intents with', technology='HTTPS') >> payment_provider

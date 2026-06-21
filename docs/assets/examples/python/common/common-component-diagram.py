from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentQueue,
    Container,
    ContainerBoundary,
    Rel,
    SystemExt,
)


with ComponentDiagram(title='Checkout API - Components') as diagram:
    web_app = Container(
        'Web Application',
        'Starts checkout from the storefront.',
        technology='React',
        alias='web_app',
    )
    payment_provider = SystemExt(
        'Payment Provider',
        'Authorizes and captures card payments.',
        alias='payment_provider',
    )

    with ContainerBoundary(
        'Checkout API',
        'Components that coordinate checkout.',
        alias='checkout_api',
    ):
        controller = Component(
            'Checkout Controller',
            'Receives checkout requests.',
            technology='FastAPI',
            alias='controller',
        )
        checkout_service = Component(
            'Checkout Service',
            'Validates carts and creates orders.',
            technology='Python',
            alias='checkout_service',
        )
        payment_adapter = Component(
            'Payment Adapter',
            'Wraps payment provider calls.',
            technology='Python',
            alias='payment_adapter',
        )
        order_store = ComponentDb(
            'Order Store',
            'Persists checkout and order records.',
            technology='PostgreSQL',
            alias='order_store',
        )
        event_publisher = ComponentQueue(
            'Event Publisher',
            'Publishes order-created events.',
            technology='Kafka',
            alias='event_publisher',
        )

    web_app >> Rel('Submits checkout to', technology='HTTPS/JSON') >> controller
    controller >> Rel('Delegates to', technology='Python call') >> checkout_service
    checkout_service >> Rel('Authorizes payment through', technology='Python call') >> payment_adapter
    payment_adapter >> Rel('Calls', technology='HTTPS/JSON') >> payment_provider
    checkout_service >> Rel('Stores order in', technology='SQL') >> order_store
    checkout_service >> Rel('Publishes event with', technology='Kafka') >> event_publisher

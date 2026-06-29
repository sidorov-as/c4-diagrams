from c4 import (
    Component,
    ComponentDiagram,
    ComponentExt,
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerQueue,
    Rel,
)
from c4.renderers import (
    D2RenderOptionsBuilder,
)


with ComponentDiagram(title='Checkout API - Component Diagram') as diagram:
    web_app = Container('Web Application', 'Storefront and checkout UI.', technology='Next.js', alias='web_app')
    web_app.add_property('Runtime', 'Node.js')
    web_app.add_property('Team', 'Storefront')

    order_events = ContainerQueue('Order Events', 'Asynchronous stream for order lifecycle events.', technology='Kafka', alias='order_events')
    order_events.add_property('Retention', '7 days')
    order_events.add_property('Partitions', '24')

    checkout_db = ContainerDb('Checkout Database', 'Stores checkout sessions, idempotency keys, and payment state.', technology='PostgreSQL', alias='checkout_db')
    checkout_db.add_property('HA', 'Multi-AZ')
    checkout_db.add_property('Backups', 'PITR')

    payment_provider = ComponentExt('Payment Provider', 'External card authorization and capture API.', alias='payment_provider')
    payment_provider.add_property('Timeout budget', '2s')
    payment_provider.add_property('Webhook signature', 'HMAC')

    inventory_service = ComponentExt('Inventory Service', 'Reserves stock before payment capture.', alias='inventory_service')
    inventory_service.add_property('Consistency', 'Strong')
    inventory_service.add_property('Owner', 'Supply Chain')

    with ContainerBoundary('Checkout API', 'Components that orchestrate checkout and payment.', d2={'direction': 'right'}, alias='checkout_api_boundary'):
        checkout_controller = Component('Checkout Controller', 'HTTP entrypoint for checkout commands.', d2={'style': {'stroke': '#2563eb', 'fill': '#eff6ff'}}, technology='FastAPI', alias='checkout_controller')
        checkout_controller.add_property('Endpoint', '/checkout')
        checkout_controller.add_property('Auth', 'JWT')

        checkout_orchestrator = Component('Checkout Orchestrator', 'Coordinates validation, inventory reservation, payment, and persistence.', technology='Python', alias='checkout_orchestrator')
        checkout_orchestrator.add_property('Pattern', 'Application service')
        checkout_orchestrator.add_property('Retries', 'Bounded')

        inventory_client = Component('Inventory Client', 'Calls the inventory service and maps reservation failures.', technology='gRPC client', alias='inventory_client')
        inventory_client.add_property('Timeout', '750ms')
        inventory_client.add_property('Circuit breaker', 'Enabled')

        payment_adapter = Component('Payment Adapter', 'Wraps payment provider calls and webhook verification.', technology='Python', alias='payment_adapter')
        payment_adapter.add_property('Idempotency', 'Required')
        payment_adapter.add_property('Capture mode', 'Manual')

        order_publisher = Component('Order Publisher', 'Publishes order-created and payment-authorized events.', technology='Kafka producer', alias='order_publisher')
        order_publisher.add_property('Schema', 'JSON Schema')
        order_publisher.add_property('Acks', 'all')

    web_app >> Rel('Submits checkout', technology='HTTPS/JSON') >> checkout_controller
    checkout_controller >> Rel('Delegates command', technology='Python call') >> checkout_orchestrator
    checkout_orchestrator >> Rel('Reserves stock', technology='gRPC') >> inventory_client
    inventory_client >> Rel('Reserve items', technology='mTLS / gRPC') >> inventory_service
    checkout_orchestrator >> Rel('Authorizes payment', technology='Python call') >> payment_adapter
    payment_adapter >> Rel('Creates payment intent', technology='REST/JSON') >> payment_provider
    checkout_orchestrator >> Rel('Persists checkout state', technology='SQL') >> checkout_db
    checkout_orchestrator >> Rel('Emits domain events', technology='Python call') >> order_publisher
    order_publisher >> Rel('Publishes events', technology='Kafka') >> order_events


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

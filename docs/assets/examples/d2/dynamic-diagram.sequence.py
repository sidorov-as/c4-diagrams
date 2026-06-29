from c4 import (
    Container,
    ContainerDb,
    ContainerQueue,
    DynamicDiagram,
    Person,
    Rel,
    SystemExt,
)
from c4.renderers import (
    D2RenderOptionsBuilder,
)


with DynamicDiagram(title='Checkout and Fulfillment Flow') as diagram:
    customer = Person('Customer', 'Places an order in the online store.', alias='customer')
    customer.add_property('Channel', 'Mobile')
    customer.add_property('Auth', 'OIDC')

    web_app = Container('Web Application', 'Checkout UI.', technology='Next.js', alias='web_app')

    checkout_api = Container('Checkout API', 'Orchestrates checkout and payment.', technology='FastAPI', alias='checkout_api')

    checkout_db = ContainerDb('Checkout DB', 'Stores checkout state.', technology='PostgreSQL', alias='checkout_db')

    payment_provider = SystemExt('Payment Provider', 'Authorizes card payments.', alias='payment_provider')

    inventory_service = SystemExt('Inventory Service', 'Reserves inventory.', alias='inventory_service')

    order_events = ContainerQueue('Order Events', 'Order lifecycle event stream.', technology='Kafka', alias='order_events')

    warehouse_system = SystemExt('Warehouse System', 'Fulfills reserved orders.', alias='warehouse_system')

    customer >> Rel('Starts checkout', technology='HTTPS') >> web_app
    web_app >> Rel('POST /checkout', technology='JSON/HTTPS') >> checkout_api
    checkout_api >> Rel('Reserve items', technology='mTLS / gRPC') >> inventory_service
    inventory_service >> Rel('Reservation confirmed', technology='gRPC') >> checkout_api
    checkout_api >> Rel('Authorize payment', technology='REST/JSON') >> payment_provider
    payment_provider >> Rel('Authorization result', technology='Webhook') >> checkout_api
    checkout_api >> Rel('Persist payment state', technology='SQL') >> checkout_db
    checkout_api >> Rel('Publish OrderCreated', technology='Kafka') >> order_events
    order_events >> Rel('Fulfillment request', technology='AMQP bridge') >> warehouse_system
    warehouse_system >> Rel('Ships order', technology='Email / SMS') >> customer


d2_render_options = (
    D2RenderOptionsBuilder()
    .sequence_diagram(
        True,
    )
    .auto_number_relationships(
        True,
    )
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

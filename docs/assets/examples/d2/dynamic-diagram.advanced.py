from c4 import (
    DynamicDiagram,
    Person,
    Rel,
    System,
    SystemExt,
)
from c4.renderers import (
    D2RenderOptionsBuilder,
)


with DynamicDiagram(title='Order Fulfillment Flow') as diagram:
    customer = Person('Customer', 'Places orders in the online store.', alias='customer')

    online_store = System('Online Store', 'Customer-facing commerce platform.', alias='online_store')

    payment_gateway = SystemExt('Payment Gateway', 'External provider that authorizes card payments.', alias='payment_gateway')

    warehouse_system = SystemExt('Warehouse System', 'External warehouse platform that reserves and ships items.', alias='warehouse_system')

    customer >> Rel('Places order', technology='HTTPS') >> online_store
    online_store >> Rel('Authorizes payment', technology='REST API') >> payment_gateway
    payment_gateway >> Rel('Returns authorization result', technology='HTTPS') >> online_store
    online_store >> Rel('Sends fulfillment request', technology='AMQP') >> warehouse_system
    warehouse_system >> Rel('Confirms reservation', technology='AMQP') >> online_store


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

from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentExt,
    ComponentQueue,
    Rel,
)


with ComponentDiagram(title='Order Processing API - Component Diagram') as diagram:
    order_controller = Component('Order Controller', 'HTTP entrypoint for order submission and status queries.', technology='FastAPI', alias='order_controller')

    order_app_service = Component('Order Application Service', 'Coordinates validation, payment, and order creation.', technology='Python', alias='order_app_service')

    inventory_checker = Component('Inventory Checker', 'Verifies stock availability before an order is confirmed.', technology='Python', alias='inventory_checker')

    payment_adapter = Component('Payment Adapter', 'Wraps external payment provider calls.', technology='Python', alias='payment_adapter')

    order_db = ComponentDb('Order Database', 'Stores orders, line items, and order status history.', technology='PostgreSQL', alias='order_db')

    payment_gateway_api = ComponentExt('Payment Gateway API', 'External provider API for payment authorization and capture.', technology='REST API', alias='payment_gateway_api')

    order_events_bus = ComponentQueue('Order Events Bus', 'Publishes order-created and order-paid events.', technology='Kafka', alias='order_events_bus')

    order_controller >> Rel('Invokes', technology='Python call') >> order_app_service
    order_app_service >> Rel('Checks stock via', technology='Python call') >> inventory_checker
    order_app_service >> Rel('Requests payment through', technology='Python call') >> payment_adapter
    payment_adapter >> Rel('Authorizes payment via', technology='HTTPS/JSON') >> payment_gateway_api
    order_app_service >> Rel('Reads and writes', technology='SQL') >> order_db
    order_app_service >> Rel('Publishes events to', technology='Kafka') >> order_events_bus

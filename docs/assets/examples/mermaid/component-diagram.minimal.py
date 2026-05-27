from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentExt,
    Rel,
)


with ComponentDiagram(title='Checkout API - Component Diagram') as diagram:
    checkout_controller = Component('Checkout Controller', 'Receives checkout requests and orchestrates payment flow.', technology='FastAPI', alias='checkout_controller')

    payment_service = Component('Payment Service', 'Creates payment intents and handles payment state updates.', technology='Python', alias='payment_service')

    payment_store = ComponentDb('Payment Store', 'Stores payment records and statuses.', technology='PostgreSQL', alias='payment_store')

    payment_gateway_api = ComponentExt('Payment Gateway API', 'External API for payment authorization and capture.', technology='REST API', alias='payment_gateway_api')

    checkout_controller >> Rel('Calls', technology='Python call') >> payment_service
    payment_service >> Rel('Reads and writes', technology='SQL') >> payment_store
    payment_service >> Rel('Creates payments via', technology='HTTPS/JSON') >> payment_gateway_api

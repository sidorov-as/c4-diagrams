from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentExt,
    Rel,
)


with ComponentDiagram(title='Checkout API - Component Diagram') as diagram:
    checkout_controller = Component('Checkout Controller', 'Receives checkout requests and orchestrates payment flow.', plantuml={'tags': []}, technology='FastAPI', alias='checkout_controller')

    payment_service = Component('Payment Service', 'Creates payment intents and handles payment state updates.', plantuml={'tags': []}, technology='Python', alias='payment_service')

    payment_store = ComponentDb('Payment Store', 'Stores payment records and statuses.', plantuml={'tags': []}, technology='PostgreSQL', alias='payment_store')

    payment_gateway_api = ComponentExt('Payment Gateway API', 'External API for payment authorization and capture.', plantuml={'tags': []}, technology='REST API', alias='payment_gateway_api')

    checkout_controller >> Rel('Calls', technology='Python call', plantuml={'tags': []}) >> payment_service
    payment_service >> Rel('Reads and writes', technology='SQL', plantuml={'tags': []}) >> payment_store
    payment_service >> Rel('Creates payments via', technology='HTTPS/JSON', plantuml={'tags': []}) >> payment_gateway_api

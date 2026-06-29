from c4 import (
    Container,
    ContainerDb,
    ContainerExt,
    ContainerQueue,
    DeploymentDiagram,
    DeploymentNode,
    Node,
    Person,
    Rel,
)
from c4.renderers import (
    D2RenderOptionsBuilder,
)


with DeploymentDiagram(title='Online Shop - Production Deployment') as diagram:
    customer = Person('Customer', 'Uses the online shop through a browser.', alias='customer')
    customer.add_property('Boundary', 'External')
    customer.add_property('Protocol', 'HTTPS')

    payment_gateway = ContainerExt('Payment Gateway', 'External service that processes card payments.', technology='HTTPS API', alias='payment_gateway')
    payment_gateway.add_property('Boundary', 'External')
    payment_gateway.add_property('Protocol', 'HTTPS API')

    with Node('AWS Production Account', 'Production cloud account for the online shop.', alias='aws_prod'):
        with Node('Public Subnet', 'Internet-facing network segment.', alias='public_subnet'):
            with DeploymentNode('Application Load Balancer', 'Terminates TLS and routes requests to the web tier.', alias='alb'):
                web_app = Container('Web Application', 'Serves the storefront UI.', technology='Next.js', alias='web_app')

        with Node('Private Subnet', 'Internal network segment for application and data services.', alias='private_subnet'):
            with DeploymentNode('Kubernetes Cluster', 'Runs backend services and asynchronous workers.', alias='app_cluster'):
                backend_api = Container('Backend API', 'Handles catalog, checkout, and order processing.', technology='Python / FastAPI', alias='backend_api')

                order_events = ContainerQueue('Order Events', 'Internal asynchronous event stream.', technology='Kafka', alias='order_events')

            with DeploymentNode('Managed PostgreSQL', 'Managed relational database service.', alias='db_service'):
                orders_db = ContainerDb('Orders Database', 'Stores orders, payments, and fulfillment data.', technology='PostgreSQL', alias='orders_db')

    customer >> Rel('Uses', technology='HTTPS') >> web_app
    web_app >> Rel('Routes traffic to', technology='HTTPS') >> backend_api
    backend_api >> Rel('Reads and writes', technology='TLS / SQL') >> orders_db
    backend_api >> Rel('Calls', technology='HTTPS/JSON') >> payment_gateway
    backend_api >> Rel('Publishes events to', technology='Kafka') >> order_events


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

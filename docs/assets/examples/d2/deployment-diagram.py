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
    customer = Person('Customer', 'Uses the online shop through a browser or mobile device.', alias='customer')
    customer.add_property('Network', 'Internet')
    customer.add_property('Auth', 'OIDC')

    payment_gateway = ContainerExt('Payment Gateway', 'External service that processes card payments.', technology='HTTPS API', alias='payment_gateway')
    payment_gateway.add_property('Provider', 'External PSP')
    payment_gateway.add_property('SLA', '99.99%')

    with Node('AWS Production Account', 'Production cloud account for the online shop.', d2={'direction': 'right'}, alias='aws_prod'):
        with Node('Edge Network', 'Global ingress layer.', alias='edge'):
            with DeploymentNode('CloudFront Distribution', 'Caches static assets and forwards API traffic.', alias='cdn') as cdn:
                web_app = Container('Web Application', 'Serves the storefront UI.', technology='Next.js', alias='web_app')

        with Node('Public Subnet', 'Internet-facing network segment.', alias='public_subnet'):
            with DeploymentNode('Application Load Balancer', 'Terminates TLS and routes requests to application services.', alias='alb') as alb:
                pass

        with Node('Private Subnet', 'Internal network segment for application and data services.', alias='private_subnet'):
            with DeploymentNode('Kubernetes Cluster', 'Runs backend services and asynchronous workers.', alias='app_cluster'):
                backend_api = Container('Backend API', 'Handles catalog, checkout, and order processing.', technology='Python / FastAPI', alias='backend_api')

                checkout_worker = Container('Checkout Worker', 'Consumes payment and fulfillment tasks.', technology='Python', alias='checkout_worker')

                order_events = ContainerQueue('Order Events', 'Internal asynchronous event stream.', technology='Kafka', alias='order_events')

            with DeploymentNode('Managed PostgreSQL', 'Managed relational database service.', alias='db_service'):
                orders_db = ContainerDb('Orders Database', 'Stores orders, payments, and fulfillment data.', technology='PostgreSQL', alias='orders_db')

    customer >> Rel('Uses storefront', technology='HTTPS') >> cdn
    cdn >> Rel('Forwards API requests', technology='HTTPS') >> alb
    alb >> Rel('Routes traffic to', technology='HTTPS') >> backend_api
    backend_api >> Rel('Reads and writes', technology='TLS / SQL') >> orders_db
    backend_api >> Rel('Creates payment intents', technology='HTTPS/JSON') >> payment_gateway
    backend_api >> Rel('Publishes events to', technology='Kafka') >> order_events
    order_events >> Rel('Triggers async work', technology='Kafka') >> checkout_worker


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

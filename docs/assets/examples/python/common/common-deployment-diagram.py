from c4 import (
    Container,
    ContainerDb,
    DeploymentDiagram,
    DeploymentNode,
    Node,
    Person,
    Rel,
    SystemExt,
)


with DeploymentDiagram(title='Retail Platform - Deployment') as diagram:
    customer = Person(
        'Customer',
        'Uses the online shop through a browser.',
        alias='customer',
    )
    payment_provider = SystemExt(
        'Payment Provider',
        'External service that processes payments.',
        alias='payment_provider',
    )

    with Node(
        'Production Environment',
        'Cloud-hosted production runtime.',
        alias='production',
    ):
        with DeploymentNode(
            'Edge',
            'Public entrypoint for web traffic.',
            alias='edge',
        ):
            web_app = Container(
                'Web Application',
                'Serves the storefront UI.',
                technology='Next.js',
                alias='web_app',
            )

        with DeploymentNode(
            'Application Runtime',
            'Runs backend services.',
            alias='runtime',
        ):
            api = Container(
                'Backend API',
                'Handles catalog, checkout, and orders.',
                technology='Python / FastAPI',
                alias='api',
            )

        with DeploymentNode(
            'Managed Database',
            'Managed relational database service.',
            alias='database_node',
        ):
            database = ContainerDb(
                'Orders Database',
                'Stores orders and payment state.',
                technology='PostgreSQL',
                alias='database',
            )

    customer >> Rel('Uses', technology='HTTPS') >> web_app
    web_app >> Rel('Calls', technology='HTTPS/JSON') >> api
    api >> Rel('Reads and writes', technology='SQL') >> database
    api >> Rel('Requests payment authorization from', technology='HTTPS') >> payment_provider

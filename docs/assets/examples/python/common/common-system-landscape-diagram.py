from c4 import (
    EnterpriseBoundary,
    Person,
    Rel,
    System,
    SystemExt,
    SystemLandscapeDiagram,
)


with SystemLandscapeDiagram(title='Acme Retail - System Landscape') as diagram:
    customer = Person(
        'Customer',
        'Places orders through digital channels.',
        alias='customer',
    )
    support_agent = Person(
        'Support Agent',
        'Supports customers after purchase.',
        alias='support_agent',
    )
    payment_provider = SystemExt(
        'Payment Provider',
        'Processes card payments.',
        alias='payment_provider',
    )
    warehouse_system = SystemExt(
        'Warehouse System',
        'Reserves stock and coordinates fulfillment.',
        alias='warehouse_system',
    )

    with EnterpriseBoundary(
        'Acme Retail',
        'Internal systems owned by Acme Retail.',
        alias='acme_retail',
    ):
        retail_platform = System(
            'Retail Platform',
            'Supports browsing, checkout, and order management.',
            alias='retail_platform',
        )
        support_portal = System(
            'Support Portal',
            'Helps support teams investigate customer orders.',
            alias='support_portal',
        )
        reporting_platform = System(
            'Reporting Platform',
            'Provides operational and sales reporting.',
            alias='reporting_platform',
        )

    customer >> Rel('Places orders through', technology='HTTPS') >> retail_platform
    support_agent >> Rel('Uses', technology='HTTPS') >> support_portal
    support_portal >> Rel('Reads order data from', technology='HTTPS') >> retail_platform
    retail_platform >> Rel('Requests payments from', technology='HTTPS') >> payment_provider
    retail_platform >> Rel('Sends fulfillment requests to', technology='HTTPS') >> warehouse_system
    retail_platform >> Rel('Publishes order facts to', technology='Kafka') >> reporting_platform

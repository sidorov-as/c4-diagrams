from c4 import (
    EnterpriseBoundary,
    Person,
    Rel,
    System,
    SystemContextDiagram,
    SystemExt,
)


with SystemContextDiagram(title='Retail Platform - System Context') as diagram:
    customer = Person(
        'Customer',
        'Browses products and places orders.',
        alias='customer',
    )
    support_agent = Person(
        'Support Agent',
        'Helps customers with order questions.',
        alias='support_agent',
    )
    payment_provider = SystemExt(
        'Payment Provider',
        'Processes card payments.',
        alias='payment_provider',
    )

    with EnterpriseBoundary(
        'Acme Retail',
        'Systems owned by Acme Retail.',
        alias='acme_retail',
    ):
        retail_platform = System(
            'Retail Platform',
            'Handles catalog browsing, checkout, and order management.',
            alias='retail_platform',
        )
        support_portal = System(
            'Support Portal',
            'Provides order lookup and customer support workflows.',
            alias='support_portal',
        )

    customer >> Rel('Places orders using', technology='HTTPS') >> retail_platform
    support_agent >> Rel('Investigates orders in', technology='HTTPS') >> support_portal
    support_portal >> Rel('Reads order data from', technology='HTTPS') >> retail_platform
    retail_platform >> Rel('Requests payments from', technology='HTTPS') >> payment_provider

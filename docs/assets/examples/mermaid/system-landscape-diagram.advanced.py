from c4 import (
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    System,
    SystemExt,
    SystemLandscapeDiagram,
)


with SystemLandscapeDiagram(title='Retail Platform') as diagram:
    customer = Person('Customer', 'Places orders through the storefront.', alias='customer')

    support_agent = PersonExt('Support Agent', 'Handles issues in an external CRM.', alias='support_agent')

    payment_gateway = SystemExt('Payment Gateway', 'Processes card payments.', alias='payment_gateway')

    crm_platform = SystemExt('CRM Platform', 'External CRM used by support agents.', alias='crm_platform')

    with EnterpriseBoundary('Acme Corp', 'Internal systems owned by Acme.', alias='acme_enterprise'):
        retail_platform = System('Retail Platform', 'Core platform for catalog, checkout, and order management.', alias='retail_platform')

    customer >> Rel('Browses and places orders', technology='HTTPS') >> retail_platform
    retail_platform >> Rel('Charges card', technology='REST API') >> payment_gateway
    support_agent >> Rel('Manages customer issues', technology='Web UI') >> crm_platform

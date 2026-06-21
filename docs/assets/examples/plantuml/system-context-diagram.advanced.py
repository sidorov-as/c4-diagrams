from c4 import (
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    System,
    SystemContextDiagram,
    SystemExt,
)


with SystemContextDiagram(title='Retail Platform') as diagram:
    customer = Person('Customer', 'Places orders through the storefront.', plantuml={'tags': []}, alias='customer')

    support_agent = PersonExt('Support Agent', 'Handles issues in an external CRM.', plantuml={'tags': []}, alias='support_agent')

    payment_gateway = SystemExt('Payment Gateway', 'Processes card payments.', plantuml={'tags': []}, alias='payment_gateway')

    crm_platform = SystemExt('CRM Platform', 'External CRM used by support agents.', plantuml={'tags': []}, alias='crm_platform')

    with EnterpriseBoundary('Acme Corp', 'Internal systems owned by Acme.', alias='acme_enterprise'):
        retail_platform = System('Retail Platform', 'Core platform for catalog, checkout, and order management.', plantuml={'tags': []}, alias='retail_platform')

    customer >> Rel('Browses and places orders', technology='HTTPS', plantuml={'tags': []}) >> retail_platform
    retail_platform >> Rel('Charges card', technology='REST API', plantuml={'tags': []}) >> payment_gateway
    support_agent >> Rel('Manages customer issues', technology='Web UI', plantuml={'tags': []}) >> crm_platform

from c4 import (
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    System,
    SystemExt,
    SystemLandscapeDiagram,
)
from c4.renderers import (
    D2RenderOptionsBuilder,
)


with SystemLandscapeDiagram(title='Retail Platform') as diagram:
    customer = Person('Customer', 'Places orders through the storefront.', alias='customer')
    customer.add_property('Role', 'User')
    customer.add_property('Visibility', 'Public')

    support_agent = PersonExt('Support Agent', 'Handles issues in an external CRM.', alias='support_agent')
    support_agent.add_property('Role', 'External actor')
    support_agent.add_property('Visibility', 'Public')

    payment_gateway = SystemExt('Payment Gateway', 'Processes card payments.', alias='payment_gateway')
    payment_gateway.add_property('Role', 'External actor')
    payment_gateway.add_property('Visibility', 'Public')

    crm_platform = SystemExt('CRM Platform', 'External CRM used by support agents.', alias='crm_platform')
    crm_platform.add_property('Role', 'External actor')
    crm_platform.add_property('Visibility', 'Public')

    with EnterpriseBoundary('Acme Corp', 'Internal systems owned by Acme.', alias='acme_enterprise'):
        retail_platform = System('Retail Platform', 'Core platform for catalog, checkout, and order management.', alias='retail_platform')
        retail_platform.add_property('Owner', 'Commerce Platform')
        retail_platform.add_property('Availability', '99.95%')

    customer >> Rel('Browses and places orders', technology='HTTPS') >> retail_platform
    retail_platform >> Rel('Charges card', technology='REST API') >> payment_gateway
    support_agent >> Rel('Manages customer issues', technology='Web UI') >> crm_platform


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

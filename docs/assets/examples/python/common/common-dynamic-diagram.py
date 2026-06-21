from c4 import (
    DynamicDiagram,
    Person,
    Rel,
    System,
    SystemExt,
)


with DynamicDiagram(title='Checkout Flow') as diagram:
    customer = Person(
        'Customer',
        'Places an order in the online store.',
        alias='customer',
    )
    retail_platform = System(
        'Retail Platform',
        'Coordinates checkout and order processing.',
        alias='retail_platform',
    )
    payment_provider = SystemExt(
        'Payment Provider',
        'Authorizes card payments.',
        alias='payment_provider',
    )
    warehouse_system = SystemExt(
        'Warehouse System',
        'Reserves stock and starts fulfillment.',
        alias='warehouse_system',
    )

    customer >> Rel('Submits checkout', technology='HTTPS') >> retail_platform
    retail_platform >> Rel('Authorizes payment', technology='HTTPS') >> payment_provider
    retail_platform >> Rel('Reserves stock', technology='HTTPS') >> warehouse_system
    retail_platform >> Rel('Confirms order', technology='HTTPS') >> customer

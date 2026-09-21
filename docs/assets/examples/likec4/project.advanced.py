from c4.contrib.likec4 import (
    Between,
    Children,
    Project,
    RawPredicate,
    Rel,
    Where,
    Wildcard,
)


project = Project('Shop', view_key='index')

spec = project.specification
spec.color('brand', '#0b5fff')
spec.element('actor', notation='Person', color='brand', shape='person')
spec.element('system', color='primary')
spec.element('service', technology='Python', shape='component')
spec.element('database', color='amber', shape='storage')
spec.relationship('async', line='dotted', head='diamond')
spec.tag('critical', color='red')
spec.tag('deprecated')
spec.deployment_node('environment', notation='Environment', color='gray')
spec.deployment_node('vm')

model = project.model
customer = model.element(
    'actor',
    'Customer',
    alias='customer',
    description='Buys goods in the **shop**.',
)
shop = model.element(
    'system',
    'Online Shop',
    alias='shop',
    summary='Sells goods online',
    metadata={'owner': 'team-shop', 'tiers': ['web', 'api']},
    links=[('https://example.com/shop', 'Docs')],
)
web = model.element(
    'service',
    'Web',
    parent=shop,
    alias='web',
    icon='tech:react',
)
api = model.element(
    'service',
    'API',
    parent=shop,
    alias='api',
    description='Handles [[orders]] and payments.',
    tags=['critical'],
)
db = model.element(
    'database',
    'Database',
    parent=shop,
    alias='db',
    tags=['deprecated'],
)
queue = model.element('service', 'Order Queue', alias='queue')

customer >> Rel('opens', technology='HTTPS') >> web
web >> Rel('calls', technology='REST', tags=['critical']) >> api
api >> Rel('reads and writes', technology='SQL') >> db
api >> Rel('publishes orders', kind='async', navigate_to='checkout') >> queue

deployment = project.deployment
prod = deployment.node('environment', 'Production', alias='prod')
app = deployment.node('vm', 'App VM', parent=prod, alias='app')
data = deployment.node('vm', 'Data VM', parent=prod, alias='data')

app.instance(api, 'primary')
app.instance(api, 'secondary')
app.instance(web)
data.instance(db)

app >> Rel('queries', technology='TCP/5432') >> data

views = project.views

index = views.element_view('index', 'Landscape')
index.include(Wildcard())
index.style(customer, color='brand')
index.auto_layout('LeftRight', 80, 100)

shop_detail = views.element_view(
    'shop-detail',
    'Shop',
    of=shop,
    tags=['critical'],
)
shop_detail.include(
    Wildcard(),
    Where(Children(shop), tag='critical'),
    Between(web, api),
)
shop_detail.exclude(db)
shop_detail.include(api, navigate_to='checkout')

critical = views.element_view('critical')
critical.include(RawPredicate('shop.** where tag is #critical'))

production = views.deployment_view('production', 'Production')
production.include(prod, Children(prod))
production.style(prod, color='green')

checkout = views.dynamic_view('checkout', 'Checkout', variant='sequence')
checkout.step(customer, web, 'opens checkout', technology='HTTPS')
checkout.step(web, api, 'places order', notes='Validates the **cart**.')
checkout.back(web, api, 'order id')
checkout.step(api, queue, 'enqueues', color='amber')

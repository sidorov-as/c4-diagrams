from c4.contrib.structurizr import Rel, Workspace
from c4.contrib.structurizr.renderer import AutoLayout


workspace = Workspace('Payments', description='Payments architecture')
workspace.styles.element('Person', shape='Person')
workspace.styles.element('Staff', background='#455a64', color='#ffffff')
workspace.styles.element('External', background='#999999', color='#ffffff', border='Dashed')
workspace.styles.element('Critical', background='#ffcc00', color='#111111')
workspace.styles.element('Frontend', shape='WebBrowser')
workspace.styles.element('Mobile', shape='MobileDevicePortrait')
workspace.styles.element('Storage', shape='Cylinder')
workspace.styles.element('Queue', shape='Pipe')
workspace.styles.element('Worker', shape='Hexagon')
workspace.styles.relationship('Persistent', thickness=4)
workspace.styles.relationship('Async', border='Dashed')
workspace.styles.relationship('Critical', color='#c62828', thickness=3)

with workspace.model as model:
    customer = model.Person('Customer', alias='customer', description='Pays for goods and services.', tags=['External'], properties={'segment': 'retail'}, url='https://example.com/customer')
    agent = model.Person('Support Agent', alias='agent', description='Investigates failed and disputed payments.', tags=['Staff'])
    analyst = model.Person('Fraud Analyst', alias='analyst', description='Reviews suspicious transactions.', tags=['Staff'])
    payments = model.SoftwareSystem('Payments', alias='payments', description='Collects money.')
    psp = model.SoftwareSystem('Payment Provider', alias='psp', description='Card acquiring and 3-D Secure.', tags=['External'])
    bank = model.SoftwareSystem('Banking Network', alias='bank', description='Settles funds with issuing banks.', tags=['External'])
    identity = model.SoftwareSystem('Identity Provider', alias='identity', description='Authenticates customers and staff.', tags=['External'])
    notifier = model.SoftwareSystem('Notification Service', alias='notifier', description='Delivers e-mail and SMS receipts.', tags=['External'])
    web = model.Container('Web App', alias='web', description='Customer checkout UI.', technology='Django', tags=['Frontend'], owner=payments)
    mobile = model.Container('Mobile App', alias='mobile', description='Checkout and payment history on phones.', technology='React Native', tags=['Mobile'], owner=payments)
    backoffice = model.Container('Back Office', alias='backoffice', description='Payment search, refunds and disputes.', technology='React', tags=['Frontend'], owner=payments)
    api = model.Container('API', alias='api', description='Checkout API.', technology='FastAPI', tags=['Critical'], owner=payments)
    fraud = model.Container('Fraud Engine', alias='fraud', description='Scores payments in real time.', technology='Python / scikit-learn', tags=['Critical'], owner=payments)
    worker = model.Container('Settlement Worker', alias='worker', description='Settles captured payments and sends receipts.', technology='Celery', tags=['Worker'], owner=payments)
    broker = model.Container('Message Broker', alias='broker', description='Payment lifecycle events.', technology='RabbitMQ', tags=['Queue'], owner=payments)
    cache = model.Container('Session Cache', alias='cache', description='Idempotency keys and checkout sessions.', technology='Redis', tags=['Storage'], owner=payments)
    database = model.Container('Database', alias='database', description='Payments and ledger.', technology='PostgreSQL', tags=['Storage'], owner=payments)
    controller = model.Component('Checkout Controller', alias='controller', description='Validates requests and exposes the checkout endpoints.', technology='FastAPI Router', owner=api)
    checkout = model.Component('Checkout', alias='checkout', description='Orchestrates a payment from cart to confirmation.', technology='Python', owner=api)
    risk_client = model.Component('Risk Client', alias='risk_client', description='Asks the fraud engine to score a payment.', technology='gRPC', owner=api)
    psp_adapter = model.Component('PSP Adapter', alias='psp_adapter', description='Talks to the payment provider and maps its errors.', technology='Python', owner=api)
    ledger_repo = model.Component('Ledger Repository', alias='ledger_repo', description='Persists payments and double-entry ledger records.', technology='SQLAlchemy', owner=api)
    events = model.Component('Event Publisher', alias='events', description='Publishes payment lifecycle events.', technology='Python', owner=api)
    customer >> Rel('Uses', technology='HTTPS') >> web
    customer >> Rel('Uses', technology='HTTPS') >> mobile
    agent >> Rel('Looks up payments', technology='HTTPS') >> backoffice
    analyst >> Rel('Reviews flagged payments', technology='HTTPS') >> backoffice
    web >> Rel('Calls', technology='JSON/HTTPS') >> api
    mobile >> Rel('Calls', technology='JSON/HTTPS') >> api
    backoffice >> Rel('Calls', technology='JSON/HTTPS') >> api
    web >> Rel('Signs customers in', technology='OIDC') >> identity
    backoffice >> Rel('Signs staff in', technology='OIDC') >> identity
    api >> Rel('Reads and writes sessions', technology='Redis protocol') >> cache
    api >> Rel('Scores payments', technology='gRPC') >> fraud
    api >> Rel('Authorises and captures', technology='HTTPS', tags=['Critical']) >> psp
    api >> Rel('Publishes events', technology='AMQP', tags=['Async']) >> broker
    api >> Rel('Reads from and writes to', technology='SQL', tags=['Persistent']) >> database
    fraud >> Rel('Reads payment history', technology='SQL') >> database
    broker >> Rel('Delivers events', technology='AMQP', tags=['Async']) >> worker
    worker >> Rel('Updates settlements', technology='SQL', tags=['Persistent']) >> database
    worker >> Rel('Submits settlement files', technology='SFTP') >> bank
    worker >> Rel('Sends receipts', technology='HTTPS', tags=['Async']) >> notifier
    psp >> Rel('Routes card transactions', technology='ISO 8583') >> bank
    web >> Rel('Submits checkout', technology='JSON/HTTPS') >> controller
    mobile >> Rel('Submits checkout', technology='JSON/HTTPS') >> controller
    backoffice >> Rel('Requests refunds', technology='JSON/HTTPS') >> controller
    controller >> Rel('Starts payment') >> checkout
    checkout >> Rel('Requests risk score') >> risk_client
    checkout >> Rel('Charges the card') >> psp_adapter
    checkout >> Rel('Records payment') >> ledger_repo
    checkout >> Rel('Emits payment events') >> events
    risk_client >> Rel('Scores payments', technology='gRPC') >> fraud
    psp_adapter >> Rel('Authorises and captures', technology='HTTPS', tags=['Critical']) >> psp
    ledger_repo >> Rel('Reads from and writes to', technology='SQL', tags=['Persistent']) >> database
    events >> Rel('Publishes events', technology='AMQP', tags=['Async']) >> broker

workspace.views.SystemLandscapeView(key='landscape')

workspace.views.SystemContextView(payments, key='context', include=['*'], exclude=['relationship.tag==Deprecated'])

workspace.views.ContainerView(payments, key='containers', include=['*', 'element.tag==Storage'], auto_layout=AutoLayout(rank_direction='TopBottom'), animation=[[customer, web, mobile], [api, cache, fraud], [database, broker, worker]])

workspace.views.ComponentView(api, key='components', auto_layout=AutoLayout(rank_direction='TopBottom'))

checkout_flow = workspace.views.DynamicView(payments, key='checkout-flow')
checkout_flow.step(customer, web, 'Starts checkout', technology='HTTPS')
checkout_flow.step(web, api, 'Submits checkout', technology='JSON/HTTPS')
checkout_flow.step(api, fraud, 'Scores the payment', technology='gRPC')
checkout_flow.step(api, psp, 'Authorises the card', technology='HTTPS')
checkout_flow.step(api, database, 'Persists checkout', technology='SQL')
checkout_flow.step(api, broker, 'Publishes payment captured', technology='AMQP')

settlement_flow = workspace.views.DynamicView(payments, key='settlement-flow')
settlement_flow.step(broker, worker, 'Delivers payment captured', technology='AMQP')
settlement_flow.step(worker, database, 'Marks payment as settled', technology='SQL')
settlement_flow.step(worker, bank, 'Submits settlement file', technology='SFTP')
settlement_flow.step(worker, notifier, 'Sends receipt', technology='HTTPS')

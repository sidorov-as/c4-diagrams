from c4 import (
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDbExt,
    ContainerDiagram,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    SystemBoundary,
    SystemExt,
)
from c4.contrib.plantuml import (
    LayD,
    LayR,
)
from c4.renderers import (
    PlantUMLRenderOptionsBuilder,
)


with ContainerDiagram(title='Online Shop - Container Diagram') as diagram:
    customer = Person('Customer', 'Browses products and places orders.', plantuml={'tags': ['Customer'], 'type': 'Primary User'}, alias='customer')
    customer.add_property('Channel', 'Web / Mobile')

    support_agent = PersonExt('Support Agent', 'Investigates customer issues from an external support tool.', plantuml={'tags': ['ExternalSupport'], 'type': 'External User'}, alias='support_agent')
    support_agent.add_property('Organization', 'Support Vendor')

    payment_provider = SystemExt('Payment Provider', 'Processes card payments and payment webhooks.', plantuml={'tags': ['ExternalSystem'], 'type': 'External System'}, alias='payment_provider')

    recommendation_api = ContainerExt('Recommendation API', 'Returns personalized product recommendations.', plantuml={'tags': ['ExternalContainer']}, technology='REST API', alias='recommendation_api')

    fraud_db = ContainerDbExt('Fraud Signals DB', 'External datastore containing fraud intelligence.', plantuml={'tags': ['ExternalDataStore']}, technology='Vendor DB', alias='fraud_db')

    shipping_events = ContainerQueueExt('Shipping Events Topic', 'External topic used by logistics partner.', plantuml={'tags': ['ExternalAsyncChannel']}, technology='Kafka', alias='shipping_events')

    with EnterpriseBoundary('Acme Corp', 'Enterprise boundary for internal platforms.', plantuml={'tags': ['EnterpriseBoundary']}, alias='acme'):
        with SystemBoundary('Online Shop Platform', 'Main system boundary for the commerce platform.', plantuml={'tags': ['SystemBoundary']}, alias='shop_boundary'):
            web_app = Container('Web Application', 'Serves the storefront and checkout UI.', plantuml={'tags': ['Frontend']}, technology='React + Next.js', alias='web_app')
            web_app.add_property('Runtime', 'Node.js')
            web_app.add_property('Team', 'Storefront')

            backend_api = Container('Backend API', 'Handles catalog, carts, checkout, and order APIs.', plantuml={'tags': ['Backend', 'CoreRuntime']}, technology='Python / FastAPI', alias='backend_api')
            backend_api.add_property('Runtime', 'Python 3.12')
            backend_api.add_property('Team', 'Platform')

            orders_db = ContainerDb('Orders Database', 'Stores orders, payments, and status transitions.', plantuml={'tags': ['DataStore']}, technology='PostgreSQL', alias='orders_db')
            orders_db.add_property('Engine', 'PostgreSQL 16')
            orders_db.add_property('HA', 'Primary / Replica')

            order_events = ContainerQueue('Order Events Queue', 'Publishes asynchronous order lifecycle events.', plantuml={'tags': ['AsyncChannel']}, technology='Kafka', alias='order_events')
            order_events.add_property('Retention', '7 days')
            order_events.add_property('Format', 'JSON')

            with ContainerBoundary('Checkout Subsystem', 'Groups checkout-related containers.', plantuml={'tags': ['ContainerBoundary']}, alias='checkout_boundary'):
                checkout_api = Container('Checkout API', 'Handles checkout and payment orchestration.', plantuml={'tags': ['Backend']}, technology='Python / FastAPI', alias='checkout_api')

                checkout_db = ContainerDb('Checkout DB', 'Stores checkout sessions.', plantuml={'tags': ['DataStore']}, technology='PostgreSQL', alias='checkout_db')

                checkout_api >> Rel('Reads and writes', technology='SQL', plantuml={'tags': ['DataAccess']}) >> checkout_db

    customer >> Rel('Uses', technology='HTTPS', plantuml={'tags': ['SyncRequest']}) >> web_app
    web_app >> Rel('Calls', technology='HTTPS/JSON', plantuml={'tags': ['SyncRequest']}) >> backend_api
    backend_api >> Rel('Reads and writes', technology='SQL', plantuml={'tags': ['DataAccess']}) >> orders_db
    backend_api >> Rel('Publishes order events', technology='Kafka', plantuml={'tags': ['AsyncRequest']}) >> order_events
    backend_api >> Rel('Creates payment intents', technology='REST API', plantuml={'tags': ['ExternalCall']}) >> payment_provider
    backend_api >> Rel('Fetches recommendations', technology='REST API', plantuml={'tags': ['ExternalCall']}) >> recommendation_api
    backend_api >> Rel('Checks fraud signals', technology='JDBC', plantuml={'tags': ['ExternalCall']}) >> fraud_db
    shipping_events >> Rel('Delivers shipping updates', technology='Kafka', plantuml={'tags': ['AsyncRequest']}) >> backend_api
    support_agent >> Rel('Queries order state', technology='HTTPS', plantuml={'tags': ['SupportFlow']}) >> backend_api
    LayR(customer, web_app)

    LayR(web_app, backend_api)

    LayD(backend_api, orders_db)

    LayD(backend_api, order_events)

    LayR(backend_api, payment_provider)


plantuml_render_options = (
    PlantUMLRenderOptionsBuilder()
    .layout_left_right(
        with_legend=True,
    )
    .set_sketch_style(
        bg_color='#ffffff',
        font_color='#222222',
        warning_color='#cc3300',
        font_name='Inter',
        footer_warning='Architecture draft',
        footer_text='Container view',
    )
    .show_legend(
        hide_stereotype=False,
        details='Normal',
    )
    .show_floating_legend(
        alias='legend_box',
    )
    .update_legend_title(
        'Container Diagram Legend',
    )
    .show_person_outline()
    .show_person_sprite(
        'person',
    )
    .add_person_tag(
        tag_stereo='Customer',
        bg_color='#e8f5e9',
        font_color='#1b5e20',
        border_color='#66bb6a',
        shadowing=False,
        legend_text='Primary customer actor',
        legend_sprite='user',
        border_style='SolidLine',
        border_thickness='1',
    )
    .add_external_person_tag(
        tag_stereo='ExternalSupport',
        bg_color='#f5f5f5',
        font_color='#424242',
        border_color='#9e9e9e',
        shadowing=False,
        legend_text='External support user',
        legend_sprite='user',
        border_style='DashedLine',
        border_thickness='1',
    )
    .add_external_system_tag(
        tag_stereo='ExternalSystem',
        bg_color='#f5f5f5',
        font_color='#424242',
        border_color='#9e9e9e',
        shadowing=False,
        shape='RoundedBoxShape',
        legend_text='External system dependency',
        legend_sprite='cloud',
        border_style='DashedLine',
        border_thickness='1',
    )
    .add_container_tag(
        tag_stereo='Frontend',
        bg_color='#e3f2fd',
        font_color='#0d47a1',
        border_color='#64b5f6',
        shadowing=True,
        technology='Web UI',
        legend_text='User-facing frontend container',
        legend_sprite='browser',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_container_tag(
        tag_stereo='Backend',
        bg_color='#ede7f6',
        font_color='#311b92',
        border_color='#673ab7',
        shadowing=True,
        technology='Python / FastAPI',
        legend_text='Backend application container',
        legend_sprite='server',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_container_tag(
        tag_stereo='CoreRuntime',
        bg_color='#ede7f6',
        font_color='#4527a0',
        border_color='#7e57c2',
        shadowing=True,
        technology='Python 3.12',
        legend_text='Core runtime container',
        legend_sprite='server',
        border_style='BoldLine',
        border_thickness='2',
    )
    .add_container_tag(
        tag_stereo='DataStore',
        bg_color='#fff8e1',
        font_color='#5d4037',
        border_color='#ffb300',
        shadowing=False,
        technology='PostgreSQL',
        legend_text='Internal data store',
        legend_sprite='database',
        border_style='SolidLine',
        border_thickness='1',
    )
    .add_container_tag(
        tag_stereo='AsyncChannel',
        bg_color='#fff3e0',
        font_color='#e65100',
        border_color='#fb8c00',
        shadowing=False,
        technology='Kafka',
        legend_text='Internal asynchronous channel',
        legend_sprite='queue',
        border_style='SolidLine',
        border_thickness='1',
    )
    .add_external_container_tag(
        tag_stereo='ExternalContainer',
        bg_color='#f5f5f5',
        font_color='#424242',
        border_color='#9e9e9e',
        shadowing=False,
        shape='RoundedBoxShape',
        technology='REST API',
        legend_text='External container dependency',
        legend_sprite='cloud',
        border_style='DashedLine',
        border_thickness='1',
    )
    .add_external_container_tag(
        tag_stereo='ExternalDataStore',
        bg_color='#f5f5f5',
        font_color='#424242',
        border_color='#9e9e9e',
        shadowing=False,
        technology='Vendor DB',
        legend_text='External data store',
        legend_sprite='database',
        border_style='DashedLine',
        border_thickness='1',
    )
    .add_external_container_tag(
        tag_stereo='ExternalAsyncChannel',
        bg_color='#f3e5f5',
        font_color='#6a1b9a',
        border_color='#ab47bc',
        shadowing=False,
        technology='Kafka',
        legend_text='External asynchronous channel',
        legend_sprite='queue',
        border_style='DashedLine',
        border_thickness='1',
    )
    .add_boundary_tag(
        tag_stereo='EnterpriseBoundary',
        bg_color='#fafafa',
        font_color='#424242',
        border_color='#9e9e9e',
        shadowing=False,
        legend_text='Enterprise boundary',
        border_style='SolidLine',
        border_thickness='1',
    )
    .add_boundary_tag(
        tag_stereo='SystemBoundary',
        bg_color='#fff8e1',
        font_color='#5d4037',
        border_color='#ffb300',
        shadowing=False,
        legend_text='System boundary',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_boundary_tag(
        tag_stereo='ContainerBoundary',
        bg_color='#f1f8e9',
        font_color='#33691e',
        border_color='#8bc34a',
        shadowing=False,
        legend_text='Container boundary',
        border_style='DashedLine',
        border_thickness='1',
    )
    .add_rel_tag(
        tag_stereo='SyncRequest',
        text_color='#1565c0',
        line_color='#1e88e5',
        technology='HTTPS/JSON',
        legend_text='Synchronous request/response flow',
        line_style='SolidLine',
        line_thickness='1',
    )
    .add_rel_tag(
        tag_stereo='DataAccess',
        text_color='#6d4c41',
        line_color='#8d6e63',
        technology='SQL',
        legend_text='Database access',
        line_style='DashedLine',
        line_thickness='1',
    )
    .add_rel_tag(
        tag_stereo='AsyncRequest',
        text_color='#6a1b9a',
        line_color='#8e24aa',
        technology='Kafka',
        legend_text='Asynchronous messaging flow',
        legend_sprite='queue',
        line_style='DottedLine',
        line_thickness='2',
    )
    .add_rel_tag(
        tag_stereo='ExternalCall',
        text_color='#455a64',
        line_color='#78909c',
        technology='REST API / JDBC',
        legend_text='External service/data call',
        line_style='DashedLine',
        line_thickness='1',
    )
    .add_rel_tag(
        tag_stereo='SupportFlow',
        text_color='#2e7d32',
        line_color='#43a047',
        technology='HTTPS',
        legend_text='Support access flow',
        line_style='SolidLine',
        line_thickness='1',
    )
    .update_element_style(
        element_name='container',
        bg_color='#ede7f6',
        font_color='#311b92',
        border_color='#673ab7',
        shadowing=True,
        shape='RoundedBoxShape',
        legend_text='Application container',
        legend_sprite='server',
        border_style='SolidLine',
        border_thickness='2',
    )
    .update_system_boundary_style(
        bg_color='#fff8e1',
        font_color='#5d4037',
        border_color='#ffb300',
        shadowing=False,
        shape='RoundedBoxShape',
        legend_text='System boundary',
        border_style='SolidLine',
        border_thickness='2',
    )
    .update_container_boundary_style(
        bg_color='#f1f8e9',
        font_color='#33691e',
        border_color='#8bc34a',
        shadowing=False,
        shape='RoundedBoxShape',
        legend_text='Container boundary',
        border_style='DashedLine',
        border_thickness='1',
    )
    .update_rel_style(
        text_color='#37474f',
        line_color='#546e7a',
    )
    .build()
)

diagram.set_render_options(
    plantuml=plantuml_render_options,
)

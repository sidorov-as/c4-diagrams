from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentExt,
    ComponentQueue,
    LayD,
    LayR,
    Rel,
)
from c4.renderers import (
    PlantUMLRenderOptionsBuilder,
    RenderOptions,
)


with ComponentDiagram(title='Order Processing API - Component Diagram') as diagram:
    order_controller = Component('Order Controller', 'HTTP entrypoint for order submission and status queries.', tags=['Entrypoint', 'CoreComponent'], technology='FastAPI', alias='order_controller')
    order_app_service = Component('Order Application Service', 'Coordinates validation, payment, and order creation.', tags=['CoreComponent', 'Orders'], technology='Python', alias='order_app_service')
    inventory_checker = Component('Inventory Checker', 'Verifies stock availability before an order is confirmed.', tags=['CoreComponent'], technology='Python', alias='inventory_checker')
    payment_adapter = Component('Payment Adapter', 'Wraps external payment provider calls.', tags=['CoreComponent', 'Payments'], technology='Python', alias='payment_adapter')
    order_db = ComponentDb('Order Database', 'Stores orders, line items, and order status history.', tags=['ComponentDatabase'], technology='PostgreSQL', alias='order_db')
    payment_gateway_api = ComponentExt('Payment Gateway API', 'External provider API for payment authorization and capture.', tags=['ExternalComponent'], technology='REST API', alias='payment_gateway_api')
    order_events_bus = ComponentQueue('Order Events Bus', 'Publishes order-created and order-paid events.', tags=['AsyncComponent'], technology='Kafka', alias='order_events_bus')

    order_controller >> Rel('Invokes', technology='Python call', tags=['SyncCall']) >> order_app_service
    order_app_service >> Rel('Checks stock via', technology='Python call', tags=['SyncCall']) >> inventory_checker
    order_app_service >> Rel('Requests payment through', technology='Python call', tags=['SyncCall']) >> payment_adapter
    payment_adapter >> Rel('Authorizes payment via', technology='HTTPS/JSON', tags=['ExternalCall']) >> payment_gateway_api
    order_app_service >> Rel('Reads and writes', technology='SQL', tags=['DataAccess']) >> order_db
    order_app_service >> Rel('Publishes events to', technology='Kafka', tags=['AsyncFlow']) >> order_events_bus

    LayR(order_controller, order_app_service)
    LayR(order_app_service, inventory_checker)
    LayD(order_app_service, order_db)
    LayR(inventory_checker, payment_adapter)
    LayR(payment_adapter, payment_gateway_api)
    LayD(payment_adapter, order_events_bus)


plantuml_render_options = (
    PlantUMLRenderOptionsBuilder()
    .layout_left_right(
        with_legend=True,
    )
    .show_legend(
        hide_stereotype=False,
        details='Normal',
    )
    .update_legend_title(
        'Order Processing Component Legend',
    )
    .add_component_tag(
        tag_stereo='Entrypoint',
        bg_color='#e3f2fd',
        font_color='#0d47a1',
        border_color='#42a5f5',
        shadowing=True,
        shape='RoundedBoxShape',
        technology='FastAPI',
        legend_text='HTTP/API entrypoint component',
        legend_sprite='server',
        border_style='BoldLine',
        border_thickness='2',
    )
    .add_component_tag(
        tag_stereo='CoreComponent',
        bg_color='#e8f5e9',
        font_color='#1b5e20',
        border_color='#66bb6a',
        shadowing=True,
        shape='RoundedBoxShape',
        technology='Python',
        legend_text='Internal business component',
        legend_sprite='server',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_component_tag(
        tag_stereo='Orders',
        bg_color='#fff3e0',
        font_color='#e65100',
        border_color='#fb8c00',
        shadowing=True,
        shape='RoundedBoxShape',
        technology='Python',
        legend_text='Order management component',
        legend_sprite='server',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_component_tag(
        tag_stereo='Payments',
        bg_color='#ede7f6',
        font_color='#311b92',
        border_color='#7e57c2',
        shadowing=True,
        shape='RoundedBoxShape',
        technology='Python',
        legend_text='Payment-related component',
        legend_sprite='server',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_component_tag(
        tag_stereo='ComponentDatabase',
        bg_color='#fff8e1',
        font_color='#5d4037',
        border_color='#ffb300',
        shadowing=False,
        shape='RoundedBoxShape',
        technology='PostgreSQL',
        legend_text='Internal component database',
        legend_sprite='database',
        border_style='SolidLine',
        border_thickness='1',
    )
    .add_external_component_tag(
        tag_stereo='ExternalComponent',
        bg_color='#f5f5f5',
        font_color='#424242',
        border_color='#9e9e9e',
        shadowing=False,
        shape='RoundedBoxShape',
        technology='REST API',
        legend_text='External component dependency',
        legend_sprite='cloud',
        border_style='DashedLine',
        border_thickness='1',
    )
    .add_component_tag(
        tag_stereo='AsyncComponent',
        bg_color='#f3e5f5',
        font_color='#6a1b9a',
        border_color='#ab47bc',
        shadowing=False,
        shape='RoundedBoxShape',
        technology='Kafka',
        legend_text='Internal asynchronous component',
        legend_sprite='queue',
        border_style='SolidLine',
        border_thickness='1',
    )
    .add_rel_tag(
        tag_stereo='SyncCall',
        text_color='#1565c0',
        line_color='#1e88e5',
        technology='Python call',
        legend_text='Synchronous internal call',
        line_style='SolidLine',
        line_thickness='1',
    )
    .add_rel_tag(
        tag_stereo='ExternalCall',
        text_color='#455a64',
        line_color='#78909c',
        technology='HTTPS/JSON',
        legend_text='External service call',
        line_style='DashedLine',
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
        tag_stereo='AsyncFlow',
        text_color='#6a1b9a',
        line_color='#8e24aa',
        technology='Kafka',
        legend_text='Asynchronous event flow',
        legend_sprite='queue',
        line_style='DottedLine',
        line_thickness='2',
    )
    .update_element_style(
        element_name='component',
        shape='RoundedBoxShape',
        border_style='SolidLine',
    )
    .update_rel_style(
        text_color='#37474f',
        line_color='#546e7a',
    )
    .build()
)

render_options = RenderOptions(
    plantuml=plantuml_render_options,
)

diagram.render_options = render_options

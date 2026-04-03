from c4 import (
    DynamicDiagram,
    LayD,
    LayR,
    Person,
    Rel,
    RelBack,
    System,
    SystemExt,
)
from c4.renderers import RenderOptions
from c4.renderers.plantuml import LayoutOptions


with DynamicDiagram(title='Order Fulfillment Flow') as diagram:
    customer = Person('Customer', 'Places orders in the online store.', tags=['person', 'customer'], alias='customer')
    online_store = System('Online Store', 'Customer-facing commerce platform.', type_='Software System', tags=['system', 'core'], alias='online_store')
    payment_gateway = SystemExt('Payment Gateway', 'External provider that authorizes card payments.', type_='External System', tags=['system', 'external'], alias='payment_gateway')
    warehouse_system = SystemExt('Warehouse System', 'External warehouse platform that reserves and ships items.', type_='External System', tags=['system', 'external', 'fulfillment'], alias='warehouse_system')
    customer >> Rel('Places order', technology='HTTPS', tags=['request'], index='1') >> online_store
    online_store >> Rel('Authorizes payment', technology='REST API', tags=['payment_call', 'request'], index='2') >> payment_gateway
    payment_gateway >> RelBack('Returns authorization result', technology='HTTPS', tags=['payment_call', 'response'], index='3') >> online_store
    online_store >> Rel('Sends fulfillment request', technology='AMQP', tags=['fulfillment_call'], index='4') >> warehouse_system
    warehouse_system >> RelBack('Confirms reservation', technology='AMQP', tags=['fulfillment_call', 'response'], index='5') >> online_store
    LayR(customer, online_store)
    LayR(online_store, payment_gateway)
    LayD(payment_gateway, warehouse_system)


plantuml_layout_options = (
    LayoutOptions()
    .layout_left_right()
    .show_legend(
        details='Normal',
    )
    .update_legend_title(
        'Dynamic Flow Legend',
    )
    .add_person_tag(
        tag_stereo='customer',
        bg_color='#08427B',
        font_color='#FFFFFF',
        border_color='#052E56',
        shadowing=False,
        legend_text='Customer actor',
    )
    .add_system_tag(
        tag_stereo='core',
        bg_color='#1168BD',
        font_color='#FFFFFF',
        border_color='#0B4884',
        shadowing=False,
        legend_text='Core internal system',
    )
    .add_external_system_tag(
        tag_stereo='external',
        bg_color='#999999',
        font_color='#FFFFFF',
        border_color='#6B6B6B',
        shadowing=False,
        legend_text='External system',
    )
    .add_rel_tag(
        tag_stereo='payment_call',
        text_color='#0B4884',
        line_color='#0B4884',
        legend_text='Payment interaction',
        line_style='BoldLine',
    )
    .add_rel_tag(
        tag_stereo='fulfillment_call',
        text_color='#1B5E20',
        line_color='#1B5E20',
        legend_text='Fulfillment interaction',
    )
    .add_rel_tag(
        tag_stereo='response',
        text_color='#6B6B6B',
        line_color='#6B6B6B',
        legend_text='Response message',
        line_style='DottedLine',
    )
    .update_element_style(
        element_name='person',
        font_color='#FFFFFF',
    )
    .update_element_style(
        element_name='system',
        font_color='#FFFFFF',
    )
    .update_rel_style(
        text_color='#222222',
        line_color='#444444',
    )
    .build()
)

render_options = RenderOptions(
    plantuml=plantuml_layout_options,
)

diagram.render_options = render_options

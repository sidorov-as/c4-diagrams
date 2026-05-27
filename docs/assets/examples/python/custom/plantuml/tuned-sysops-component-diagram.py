from c4 import (
    Component,
    ComponentDb,
    ComponentDiagram,
    ComponentExt,
    ComponentQueue,
    ContainerBoundary,
    Person,
    Rel,
)
from c4.contrib.plantuml import (
    LayD,
    LayL,
    RelL,
)
from c4.renderers import (
    PlantUMLRenderOptionsBuilder,
)


with ComponentDiagram(title='Sysops Support System - Tuned Component View') as diagram:
    customer = Person(
        'Customer',
        'Reports equipment issues and tracks repair progress.',
        plantuml={'tags': ['User']},
        alias='customer',
    )
    expert = Person(
        'Sysops Expert',
        'Accepts assignments and records repair updates.',
        plantuml={'tags': ['User']},
        alias='expert',
    )

    auth0 = ComponentExt(
        'Auth0',
        'External identity provider.',
        plantuml={'tags': ['External']},
        technology='OIDC/OAuth2',
        alias='auth0',
    )
    email_system = ComponentExt(
        'E-mail System',
        'Delivers customer and expert notifications.',
        plantuml={'tags': ['External']},
        technology='SMTP',
        alias='email_system',
    )

    with ContainerBoundary(
        'Sysops Support System',
        'Components that handle support tickets and expert assignments.',
        plantuml={'tags': ['Boundary']},
        alias='sysops_system',
    ) as sysops_system:
        customer_portal = Component(
            'Customer Portal',
            'Ticket creation and status tracking.',
            plantuml={'tags': ['Frontend']},
            technology='SPA',
            alias='customer_portal',
        )
        mobile_app = Component(
            'Expert Mobile App',
            'Assignment queue and field repair updates.',
            plantuml={'tags': ['Frontend']},
            technology='iOS / Android',
            alias='mobile_app',
        )
        api_gateway = Component(
            'API Gateway',
            'Access control and request routing.',
            plantuml={'tags': ['Gateway']},
            technology='Container Service',
            alias='api_gateway',
        )
        ticket_api = Component(
            'Ticket API',
            'Ticket orchestration, search, and assignment updates.',
            plantuml={'tags': ['Backend']},
            technology='Container Service',
            alias='ticket_api',
        )
        notification_service = Component(
            'Notification Service',
            'Sends customer and expert notifications.',
            plantuml={'tags': ['Backend']},
            technology='Container Service',
            alias='notification_service',
        )
        ticket_processor = Component(
            'Ticket Processor',
            'Creates expert assignments for new tickets.',
            plantuml={'tags': ['Worker']},
            technology='Container Job',
            alias='ticket_processor',
        )
        sysops_database = ComponentDb(
            'Sysops Database',
            'Tickets, contacts, assignments, and repair history.',
            plantuml={'tags': ['Database']},
            technology='PostgreSQL',
            alias='sysops_database',
        )
        ticket_created_queue = ComponentQueue(
            'Ticket Created',
            'Event stream for new support tickets.',
            plantuml={'tags': ['Queue']},
            technology='Message Queue',
            alias='ticket_created_queue',
        )

    customer >> Rel('Uses', technology='HTTPS', plantuml={'tags': ['Sync']}) >> customer_portal
    expert >> Rel('Uses', technology='HTTPS', plantuml={'tags': ['Sync']}) >> mobile_app

    customer_portal >> Rel('Authenticates', technology='OIDC', plantuml={'tags': ['ExternalCall']}) >> auth0
    mobile_app >> Rel('Authenticates', technology='OIDC', plantuml={'tags': ['ExternalCall']}) >> auth0

    customer_portal >> Rel('Calls', technology='REST/HTTPS', plantuml={'tags': ['Sync']}) >> api_gateway
    mobile_app >> Rel('Calls', technology='REST/HTTPS', plantuml={'tags': ['Sync']}) >> api_gateway
    api_gateway >> Rel('Routes', technology='REST/HTTP', plantuml={'tags': ['Sync']}) >> ticket_api

    ticket_api >> Rel('Reads/writes', technology='SQL/TCP', plantuml={'tags': ['DataAccess']}) >> sysops_database
    ticket_processor >> Rel('Reads/writes', technology='SQL/TCP', plantuml={'tags': ['DataAccess']}) >> sysops_database
    ticket_api >> RelL('Publishes', technology='Queue/Event', plantuml={'tags': ['Async']}) >> ticket_created_queue
    ticket_created_queue >> Rel('Triggers', technology='Queue/Event', plantuml={'tags': ['Async']}) >> ticket_processor
    ticket_processor >> RelL('Requests notification', technology='REST/HTTP', plantuml={'tags': ['Sync']}) >> notification_service
    notification_service >> Rel('Sends e-mail', technology='SMTP', plantuml={'tags': ['ExternalCall']}) >> email_system

    LayD(customer, customer_portal)
    LayD(expert, mobile_app)
    LayL(customer_portal, mobile_app)
    LayL(notification_service, email_system)
    LayL(sysops_system, email_system)


plantuml_render_options = (
    PlantUMLRenderOptionsBuilder()
    .layout_top_down(with_legend=True)
    .show_legend(hide_stereotype=False, details='Normal')
    .update_legend_title('Sysops Component Legend')
    .add_person_tag(
        tag_stereo='User',
        bg_color='#e8f5e9',
        font_color='#1b5e20',
        border_color='#66bb6a',
        shadowing=False,
        legend_text='Operational user',
        legend_sprite='user',
    )
    .add_component_tag(
        tag_stereo='Frontend',
        bg_color='#e3f2fd',
        font_color='#0d47a1',
        border_color='#42a5f5',
        shadowing=True,
        technology='UI',
        legend_text='User-facing frontend',
        legend_sprite='browser',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_component_tag(
        tag_stereo='Gateway',
        bg_color='#fce4ec',
        font_color='#880e4f',
        border_color='#ec407a',
        shadowing=True,
        technology='Gateway',
        legend_text='API gateway',
        legend_sprite='server',
        border_style='BoldLine',
        border_thickness='2',
    )
    .add_component_tag(
        tag_stereo='Backend',
        bg_color='#ede7f6',
        font_color='#311b92',
        border_color='#7e57c2',
        shadowing=True,
        technology='Service',
        legend_text='Backend service',
        legend_sprite='server',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_component_tag(
        tag_stereo='Worker',
        bg_color='#fff3e0',
        font_color='#e65100',
        border_color='#fb8c00',
        shadowing=True,
        technology='Job',
        legend_text='Background worker',
        legend_sprite='server',
        border_style='SolidLine',
        border_thickness='2',
    )
    .add_component_tag(
        tag_stereo='Database',
        bg_color='#fff8e1',
        font_color='#5d4037',
        border_color='#ffb300',
        shadowing=False,
        technology='Database',
        legend_text='Operational datastore',
        legend_sprite='database',
    )
    .add_component_tag(
        tag_stereo='Queue',
        bg_color='#e0f2f1',
        font_color='#004d40',
        border_color='#26a69a',
        shadowing=False,
        technology='Queue',
        legend_text='Asynchronous event stream',
        legend_sprite='queue',
    )
    .add_external_component_tag(
        tag_stereo='External',
        bg_color='#f5f5f5',
        font_color='#424242',
        border_color='#9e9e9e',
        shadowing=False,
        technology='External',
        legend_text='External dependency',
        legend_sprite='cloud',
        border_style='DashedLine',
    )
    .add_boundary_tag(
        tag_stereo='Boundary',
        bg_color='#fafafa',
        font_color='#424242',
        border_color='#9e9e9e',
        shadowing=False,
        legend_text='System boundary',
    )
    .add_rel_tag(
        tag_stereo='Sync',
        text_color='#1565c0',
        line_color='#1e88e5',
        line_style='SolidLine',
        technology='HTTPS',
        legend_text='Synchronous request',
    )
    .add_rel_tag(
        tag_stereo='DataAccess',
        text_color='#6d4c41',
        line_color='#8d6e63',
        line_style='DashedLine',
        technology='SQL',
        legend_text='Database access',
    )
    .add_rel_tag(
        tag_stereo='Async',
        text_color='#00695c',
        line_color='#00897b',
        line_style='DottedLine',
        line_thickness='2',
        technology='Queue/Event',
        legend_text='Asynchronous event flow',
        legend_sprite='queue',
    )
    .add_rel_tag(
        tag_stereo='ExternalCall',
        text_color='#455a64',
        line_color='#78909c',
        line_style='DashedLine',
        technology='External',
        legend_text='External integration',
    )
    .update_element_style(
        element_name='component',
        shape='RoundedBoxShape',
        border_style='SolidLine',
    )
    .build()
)

diagram.set_render_options(
    plantuml=plantuml_render_options,
)

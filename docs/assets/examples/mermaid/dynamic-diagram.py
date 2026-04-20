from c4 import (
    Component,
    Container,
    ContainerBoundary,
    ContainerDb,
    DynamicDiagram,
    Rel,
)
from c4.renderers import (
    MermaidRenderOptionsBuilder,
    RenderOptions,
)


with DynamicDiagram(title='Dynamic diagram for Internet Banking System - API Application') as diagram:
    c4 = ContainerDb('Database', 'Stores user registration information, hashed authentication credentials, access logs, etc.', technology='Relational Database Schema', alias='c4')
    c1 = Container('Single-Page Application', 'Provides all of the Internet banking functionality to customers via their web browser.', technology='JavaScript and Angular', alias='c1')

    with ContainerBoundary('API Application', alias='b'):
        c3 = Component('Security Component', 'Provides functionality Related to signing in, changing passwords, etc.', technology='Spring Bean', alias='c3')
        c2 = Component('Sign In Controller', 'Allows users to sign in to the Internet Banking System.', technology='Spring MVC Rest Controller', alias='c2')

    c1 >> Rel('Submits credentials to', technology='JSON/HTTPS') >> c2
    c2 >> Rel('Calls isAuthenticated() on') >> c3
    c3 >> Rel('select * from users where username = ?', technology='JDBC') >> c4


mermaid_render_options = (
    MermaidRenderOptionsBuilder()
    .update_rel_style(
        from_element='c1',
        to_element='c2',
        text_color='red',
        offset_y=-40,
    )
    .update_rel_style(
        from_element='c2',
        to_element='c3',
        text_color='red',
        offset_x=-40,
        offset_y=60,
    )
    .update_rel_style(
        from_element='c3',
        to_element='c4',
        text_color='red',
        offset_x=10,
        offset_y=-40,
    )
    .build()
)

render_options = RenderOptions(
    mermaid=mermaid_render_options,
)

diagram.render_options = render_options

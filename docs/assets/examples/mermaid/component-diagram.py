from c4 import (
    Component,
    ComponentDiagram,
    Container,
    ContainerBoundary,
    ContainerDb,
    Rel,
    RelBack,
    SystemExt,
)
from c4.renderers import (
    MermaidRenderOptionsBuilder,
    RenderOptions,
)


with ComponentDiagram(title='Component diagram for Internet Banking System - API Application') as diagram:
    spa = Container('Single Page Application', 'Provides all the internet banking functionality to customers via their web browser.', technology='javascript and angular', alias='spa')
    ma = Container('Mobile App', 'Provides a limited subset to the internet banking functionality to customers via their mobile device.', technology='Xamarin', alias='ma')
    db = ContainerDb('Database', 'Stores user registration information, hashed authentication credentials, access logs, etc.', technology='Relational Database Schema', alias='db')
    mbs = SystemExt('Mainframe Banking System', 'Stores all of the core banking information about customers, accounts, transactions, etc.', alias='mbs')

    with ContainerBoundary('API Application', alias='api'):
        sign = Component('Sign In Controller', 'Allows users to sign in to the internet banking system', technology='MVC Rest Controller', alias='sign')
        accounts = Component('Accounts Summary Controller', 'Provides customers with a summary of their bank accounts', technology='MVC Rest Controller', alias='accounts')
        security = Component('Security Component', 'Provides functionality related to singing in, changing passwords, etc.', technology='Spring Bean', alias='security')
        mbsfacade = Component('Mainframe Banking System Facade', 'A facade onto the mainframe banking system.', technology='Spring Bean', alias='mbsfacade')

        sign >> Rel('Uses') >> security
        accounts >> Rel('Uses') >> mbsfacade
        security >> Rel('Read & write to', technology='JDBC') >> db
        mbsfacade >> Rel('Uses', technology='XML/HTTPS') >> mbs

    spa >> RelBack('Uses', technology='JSON/HTTPS') >> sign
    spa >> Rel('Uses', technology='JSON/HTTPS') >> accounts
    ma >> Rel('Uses', technology='JSON/HTTPS') >> sign
    ma >> Rel('Uses', technology='JSON/HTTPS') >> accounts


mermaid_render_options = (
    MermaidRenderOptionsBuilder()
    .update_rel_style(
        from_element='spa',
        to_element='sign',
        offset_y=-40,
    )
    .update_rel_style(
        from_element='spa',
        to_element='accounts',
        offset_x=-70,
        offset_y=40,
    )
    .update_rel_style(
        from_element='ma',
        to_element='sign',
        offset_x=-90,
        offset_y=40,
    )
    .update_rel_style(
        from_element='ma',
        to_element='accounts',
        offset_y=-40,
    )
    .update_rel_style(
        from_element='sign',
        to_element='security',
        offset_x=-160,
        offset_y=10,
    )
    .update_rel_style(
        from_element='accounts',
        to_element='mbsfacade',
        offset_x=140,
        offset_y=10,
    )
    .update_rel_style(
        from_element='security',
        to_element='db',
        offset_y=-40,
    )
    .update_rel_style(
        from_element='mbsfacade',
        to_element='mbs',
        offset_y=-40,
    )
    .build()
)

render_options = RenderOptions(
    mermaid=mermaid_render_options,
)

diagram.render_options = render_options

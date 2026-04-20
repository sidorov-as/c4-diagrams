from c4 import (
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDbExt,
    ContainerDiagram,
    ContainerExt,
    Person,
    Rel,
    RelBack,
    SystemExt,
)
from c4.renderers import (
    MermaidRenderOptionsBuilder,
    RenderOptions,
)


with ContainerDiagram(title='Container diagram for Internet Banking System') as diagram:
    email_system = SystemExt('E-Mail System', 'The internal Microsoft Exchange system', alias='email_system')
    customer = Person('Customer', 'A customer of the bank, with personal bank accounts', alias='customer')
    banking_system = SystemExt('Mainframe Banking System', 'Stores all of the core banking information about customers, accounts, transactions, etc.', alias='banking_system')

    with ContainerBoundary('Internet Banking', alias='c1'):
        spa = Container('Single-Page App', 'Provides all the Internet banking functionality to customers via their web browser', technology='JavaScript, Angular', alias='spa')
        mobile_app = ContainerExt('Mobile App', 'Provides a limited subset of the Internet banking functionality to customers via their mobile device', technology='C#, Xamarin', alias='mobile_app')
        web_app = Container('Web Application', 'Delivers the static content and the Internet banking SPA', technology='Java, Spring MVC', alias='web_app')
        database = ContainerDb('Database', 'Stores user registration information, hashed auth credentials, access logs, etc.', technology='SQL Database', alias='database')
        backend_api = ContainerDbExt('API Application', 'Provides Internet banking functionality via API', technology='Java, Docker Container', alias='backend_api')

    customer >> Rel('Uses', technology='HTTPS') >> web_app
    customer >> Rel('Uses', technology='HTTPS') >> spa
    customer >> Rel('Uses') >> mobile_app
    web_app >> Rel('Delivers') >> spa
    spa >> Rel('Uses', technology='async, JSON/HTTPS') >> backend_api
    mobile_app >> Rel('Uses', technology='async, JSON/HTTPS') >> backend_api
    database >> RelBack('Reads from and writes to', technology='sync, JDBC') >> backend_api
    email_system >> Rel('Sends e-mails to') >> customer
    backend_api >> Rel('Sends e-mails using', technology='sync, SMTP') >> email_system
    backend_api >> Rel('Uses', technology='sync/async, XML/HTTPS') >> banking_system


mermaid_render_options = (
    MermaidRenderOptionsBuilder()
    .update_rel_style(
        from_element='customer',
        to_element='web_app',
        offset_x=90,
        offset_y=60,
    )
    .update_rel_style(
        from_element='customer',
        to_element='spa',
        offset_y=-40,
    )
    .update_rel_style(
        from_element='customer',
        to_element='mobile_app',
        offset_y=-30,
    )
    .update_rel_style(
        from_element='web_app',
        to_element='spa',
        offset_x=130,
    )
    .update_rel_style(
        from_element='email_system',
        to_element='customer',
        offset_x=-45,
    )
    .update_rel_style(
        from_element='backend_api',
        to_element='email_system',
        offset_x=-130,
        offset_y=-60,
    )
    .update_rel_style(
        from_element='backend_api',
        to_element='banking_system',
        offset_x=-140,
        offset_y=-50,
    )
    .build()
)

render_options = RenderOptions(
    mermaid=mermaid_render_options,
)

diagram.render_options = render_options

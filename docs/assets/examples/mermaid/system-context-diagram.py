from c4 import (
    BiRel,
    Boundary,
    EnterpriseBoundary,
    Person,
    PersonExt,
    Rel,
    System,
    SystemBoundary,
    SystemContextDiagram,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemQueue,
    SystemQueueExt,
)
from c4.renderers import (
    MermaidRenderOptionsBuilder,
    RenderOptions,
)


with SystemContextDiagram(title='System Context diagram for Internet Banking System') as diagram:
    with EnterpriseBoundary('BankBoundary0', alias='b0'):
        customerA = Person('Banking Customer A', 'A customer of the bank, with personal bank accounts.', alias='customerA')
        customerB = Person('Banking Customer B', alias='customerB')
        customerC = PersonExt('Banking Customer C', 'desc', alias='customerC')
        customerD = Person('Banking Customer D', 'A customer of the bank, <br/> with personal bank accounts.', alias='customerD')
        SystemAA = System('Internet Banking System', 'Allows customers to view information about their bank accounts, and make payments.', alias='SystemAA')

        with EnterpriseBoundary('BankBoundary', alias='b1'):
            SystemE = SystemDbExt('Mainframe Banking System', 'Stores all of the core banking information about customers, accounts, transactions, etc.', alias='SystemE')
            SystemC = SystemExt('E-mail system', 'The internal Microsoft Exchange e-mail system.', alias='SystemC')
            SystemD = SystemDb('Banking System D Database', 'A system of the bank, with personal bank accounts.', alias='SystemD')

            with SystemBoundary('BankBoundary2', alias='b2'):
                SystemA = System('Banking System A', alias='SystemA')
                SystemB = System('Banking System B', 'A system of the bank, with personal bank accounts. next line.', alias='SystemB')

            with Boundary('BankBoundary3', type_='boundary', alias='b3'):
                SystemF = SystemQueue('Banking System F Queue', 'A system of the bank.', alias='SystemF')
                SystemG = SystemQueueExt('Banking System G Queue', 'A system of the bank, with personal bank accounts.', alias='SystemG')

    customerA >> BiRel('Uses') >> SystemAA
    SystemAA >> BiRel('Uses') >> SystemE
    SystemAA >> Rel('Sends e-mails', technology='SMTP') >> SystemC
    SystemC >> Rel('Sends e-mails to') >> customerA


mermaid_render_options = (
    MermaidRenderOptionsBuilder()
    .update_element_style(
        element='customerA',
        bg_color='grey',
        font_color='red',
        border_color='red',
    )
    .update_rel_style(
        from_element='customerA',
        to_element='SystemAA',
        text_color='blue',
        line_color='blue',
        offset_x=5,
    )
    .update_rel_style(
        from_element='SystemAA',
        to_element='SystemE',
        text_color='blue',
        line_color='blue',
        offset_x=-10,
    )
    .update_rel_style(
        from_element='SystemAA',
        to_element='SystemC',
        text_color='blue',
        line_color='blue',
        offset_x=-40,
        offset_y=-50,
    )
    .update_rel_style(
        from_element='SystemC',
        to_element='customerA',
        text_color='red',
        line_color='red',
        offset_x=-50,
        offset_y=20,
    )
    .update_layout_config(
        c4_shape_in_row=3,
        c4_boundary_in_row=1,
    )
    .build()
)

render_options = RenderOptions(
    mermaid=mermaid_render_options,
)

diagram.render_options = render_options

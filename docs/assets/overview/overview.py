from c4 import Person, Rel, System, SystemContextDiagram

with SystemContextDiagram("Online Shop") as diagram:
    customer = Person("Customer", "Buys goods online.")
    shop = System("Online Shop", "Takes orders from customers.")
    payments = System("Payment Provider", "Processes card payments.")

    customer >> Rel("Buys goods") >> shop
    shop >> Rel("Takes payments") >> payments

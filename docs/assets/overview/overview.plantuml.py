from c4 import Person, System, SystemContextDiagram
from c4.contrib.plantuml import RelRight

with SystemContextDiagram("Online Shop") as diagram:
    customer = Person("Customer", "Buys goods online.")
    shop = System("Online Shop", "Takes orders from customers.")
    payments = System("Payment Provider", "Processes card payments.")

    customer >> RelRight("Buys goods") >> shop
    shop >> RelRight("Takes payments") >> payments

from c4.contrib.likec4 import Project, Rel, Wildcard

project = Project("Online Shop")

spec = project.specification
spec.element("actor", shape="person")
spec.element("system")

model = project.model
customer = model.element("actor", "Customer", alias="customer")
shop = model.element("system", "Online Shop", alias="shop")
payments = model.element("system", "Payment Provider", alias="payments")

customer >> Rel("buys goods") >> shop
shop >> Rel("takes payments") >> payments

index = project.views.element_view("index", "Landscape")
index.include(Wildcard())
index.auto_layout("LeftRight")

from c4.contrib.structurizr import Workspace

workspace = Workspace("Online Shop")
with workspace.model as model:
    customer = model.Person(
        "Customer", description="Buys goods online.", alias="customer"
    )
    shop = model.SoftwareSystem(
        "Online Shop", description="Takes orders from customers.", alias="shop"
    )
    payments = model.SoftwareSystem(
        "Payment Provider",
        description="Processes card payments.",
        alias="payments",
    )

    customer.uses(shop, "Buys goods")
    shop.uses(payments, "Takes payments")

workspace.views.SystemLandscapeView(key="landscape")

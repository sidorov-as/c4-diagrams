from c4.contrib.structurizr import Rel, Workspace


workspace = Workspace('Workspace')
with workspace.model as model:
    customer = model.Person('Customer', alias='customer')
    shop = model.SoftwareSystem('Online Shop', alias='shop')
    customer >> Rel('Buys goods') >> shop

workspace.views.SystemLandscapeView(key='landscape')

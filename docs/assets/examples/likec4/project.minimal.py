from c4.contrib.likec4 import Project, Rel, Wildcard


project = Project('Shop')

spec = project.specification
spec.element('actor', shape='person')
spec.element('system')

model = project.model
customer = model.element('actor', 'Customer', alias='customer')
shop = model.element('system', 'Online Shop', alias='shop')

customer >> Rel('buys goods') >> shop

views = project.views

index = views.element_view('index', 'Landscape')
index.include(Wildcard())

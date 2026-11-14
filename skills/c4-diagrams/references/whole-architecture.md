# Structurizr and LikeC4

One model, many views. Elements are declared once in the model; a view selects them. Neither accepts portable `Diagram`
classes. Both need `c4-diagrams>=0.8.0`.

Docs: https://sidorov-as.github.io/c4-diagrams/concepts/authoring-models/

## Structurizr: `c4.contrib.structurizr`

Docs: https://sidorov-as.github.io/c4-diagrams/concepts/structurizr-model/
and https://sidorov-as.github.io/c4-diagrams/renderers/structurizr/authoring/

Public names: `Workspace`, `Model`, `Views`, `Styles`, `Rel`, `AutoLayout`, `ViewSelector`, `ViewTag`, `RawSelector`,
`StructurizrElement`, `Person`, `SoftwareSystem`, `Container`, `Component`, `DeploymentEnvironment`, `DeploymentNode`,
`InfrastructureNode`, `SoftwareSystemInstance`, `ContainerInstance`, `DynamicView`, `DynamicStep`.

```python
from c4.contrib.structurizr import Rel, Workspace

workspace = Workspace("Shop")  # name, description, theme, render_options
with workspace.model as model:
    customer = model.Person("Customer")
    shop = model.SoftwareSystem("Shop")
    payments = model.SoftwareSystem("Payment Gateway", tags=["External"])
    web = model.Container("Web App", technology="Django", owner=shop)
    db = model.Container("Database", technology="PostgreSQL", owner=shop, tags=["Database"])
    customer >> Rel("Uses", technology="HTTPS") >> web
    web >> "Reads and writes" >> db

workspace.views.ContainerView(shop, key="containers")
print(workspace.render())  # or workspace.save(path)
```

Model factories (all `(name, *, description, technology, alias, tags, properties, url, style)`):

- `model.Person(name)`, `model.SoftwareSystem(name)`
- `model.Container(name, owner=system)`, `model.Component(name, owner=container)`
- Deployment: `env = model.DeploymentEnvironment(name)`, `env.DeploymentNode(...)`, nested `node.DeploymentNode(...)`,
  `node.InfrastructureNode(...)`, `node.SoftwareSystemInstance(target)`, `node.ContainerInstance(target)`; or
  `model.DeploymentNode(name, environment=..., parent=...)`.

There are no `External` or `Database` classes: use tags (`tags=["External"]`, `tags=["Database"]`), and style them with
`workspace.styles.element(...)`, `.tag(...)`, `.relationship(...)`.

Relationships: `a >> Rel("Uses", technology="HTTPS") >> b`, `a >> "Uses" >> b`, `a.uses(b, ...)`, `a.used_by(b, ...)`.

Views (`workspace.views.*`), each with `key`, `title`, `description`, `include`, `exclude`, `tags`, `properties`,
`auto_layout=AutoLayout(...)`, `animation`:

| Method                                                                              | Scope argument         |
|-------------------------------------------------------------------------------------|------------------------|
| `SystemLandscapeView()`                                                             | none                   |
| `SystemContextView(system)`                                                         | the system             |
| `ContainerView(system)`                                                             | the system             |
| `ComponentView(container)`                                                          | the container          |
| `DynamicView(scope=None, steps=...)`; `view.step(source, destination, description)` | optional element       |
| `DeploymentView(scope=None, environment=...)`                                       | `environment` required |

Export:
`c4 export workspace.py --structurizr --structurizr-backend local --structurizr-view-key <key> -f png -o out.png`. The
view key is required unless the workspace has exactly one view. Local formats: PNG, SVG.

## LikeC4: `c4.contrib.likec4`

Docs: https://sidorov-as.github.io/c4-diagrams/concepts/likec4-model/
and https://sidorov-as.github.io/c4-diagrams/renderers/likec4/authoring/

Public names: `Project`, `Specification`, `Model`, `Element`, `Views`, `ElementView`, `DynamicView`, `DynamicStep`,
`DeploymentView`, `Deployment`, `DeploymentNode`, `DeploymentInstance`, `DeploymentRelationship`, `Rel`, `Relationship`,
`ElementKind`, `RelationshipKind`, `Tag`, `CustomColor`, `Link`, `Preset`, `C4`, predicates `Wildcard`, `Children`,
`Descendants`, `Incoming`, `Outgoing`, `InOut`, `Between`, `Where`, `RawPredicate`.

Order: specification first, then model, deployment, views.

```python
from c4.contrib.likec4 import C4, Project, Rel, Wildcard

project = Project("Shop")  # name, view_key
project.specification.use(C4)  # person, system, container, component, database, external
customer = project.model.person("Customer", alias="customer")
shop = project.model.system("Shop", alias="shop")
web = shop.container("Web App", alias="web", technology="Django")
customer >> Rel("Uses", technology="HTTPS") >> web
project.views.element_view("containers", "Containers", of=shop).include(Wildcard())
print(project.render())  # or project.save(path)
```

- Without `C4`, declare kinds: `project.specification.element("person", shape="person")`, `.deployment_node(...)`,
  `.relationship(...)`, `.tag(name, color)`, `.color(name, value)`; then
  `project.model.element("person", "Customer", alias=...)`.
- Nest children with `parent.element(kind, title, ...)` or `parent.container(...)`, `parent.component(...)`.
- Element arguments: `title, alias, summary, description, technology, tags, icon, metadata, links, **style`.
- Relationships: `a >> Rel(title, technology=...) >> b`, or `project.model.relate(a, b, title)`; `bidirectional=True`,
  `kind=`.
- Views: `project.views.element_view(key, title, of=element)` then `.include(...)`, `.exclude(...)`;
  `dynamic_view(key, title)` with `.step(a, b, title)` and `.back(...)`; `deployment_view(key, title)`.
- Deployment: `project.deployment.node(kind, title)`, `node.node(...)`, `node.instance(element)`,
  `project.deployment.relate(a, b)`.
- LikeC4 has no fixed C4 view types: a context, container or component view is an element view with a different `of=`
  and predicates.

Export:
`c4 export project.py --likec4 --likec4-backend local --likec4-bin "<cmd>" --likec4-view-key <key> -f png -o out.png`.
Formats: PNG, JPG. Needs Node and Playwright Chromium; `npx likec4@<version>` is a Tier B network
call ([consent.md](consent.md)).

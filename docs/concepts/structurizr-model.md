# Structurizr: Workspace, Model and Views

In Structurizr you do not write a diagram. You write a
[`Workspace`][c4.contrib.structurizr.Workspace] that owns three things:

- `workspace.model`: every person, system, container, component, deployment
  node and relationship, declared once.
- `workspace.views`: the views of that model. Each view picks which elements to
  show.
- `workspace.styles`: how elements and relationships look, keyed by tag.

```python
from c4.contrib.structurizr import Rel, Workspace

workspace = Workspace("Shop")

with workspace.model as model:
    customer = model.Person("Customer")
    shop = model.SoftwareSystem("Shop")
    web = model.Container("Web App", owner=shop)
    customer >> Rel("Uses") >> web

workspace.views.SystemContextView(shop, key="context")
workspace.views.ContainerView(shop, key="containers")

print(workspace.render())
```

Two views, one model: the relationship is written once and both views show it.

## C4 is built in

Structurizr has a factory for each C4 kind: `Person`, `SoftwareSystem`,
`Container`, `Component`, plus deployment nodes and instances. There is nothing
to declare first. Kinds the C4 model treats as variations are not separate
classes: an external system is a system with the `External` tag, and a database
is a container with the `Database` tag. Tags are also what styles select, so the
look of a kind is a style on its tag.

## Views have scopes

Each view type has a fixed scope. A container view needs the system whose
containers it shows, and a component view needs a container. The renderer
reports a missing or wrong scope. A view includes everything in its scope by
default and can `include` and `exclude` selectors.

## Where to go next

- [Authoring](../renderers/structurizr/authoring.md): the model, relationships
  and deployment in detail.
- [C4 cheat-sheet](../renderers/structurizr/c4-cheatsheet.md): each C4 concept
  and the view that shows it.
- [Views](../renderers/structurizr/views.md) and
  [Styles](../renderers/structurizr/styles.md).
- [Two authoring models](authoring-models.md): how this differs from the portable
  `Diagram` and from LikeC4.

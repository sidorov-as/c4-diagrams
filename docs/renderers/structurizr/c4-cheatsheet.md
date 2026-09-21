# Structurizr C4 Cheat-sheet

Structurizr has C4 built in. This page maps each C4 concept to the call that
creates it and to the view that shows it. Details are in
[Authoring](authoring.md), [Views](views.md) and [Styles](styles.md).

| C4 concept         | Python call                                                          | Shown in                                              |
|--------------------|----------------------------------------------------------------------|-------------------------------------------------------|
| [Person](#person)  | `model.Person(name)`                                                 | System landscape, system context, container views     |
| [Software system](#software-system) | `model.SoftwareSystem(name)`                        | Landscape, context; the scope of container views      |
| [Container](#container) | `model.Container(name, owner=system)`                           | `ContainerView(system)`; the scope of component views |
| [Component](#component) | `model.Component(name, owner=container)`                        | `ComponentView(container)`                            |
| [Database](#database) | `model.Container(..., tags=["Database"])`                         | Container and component views                         |
| [External](#external) | `tags=["External"]` on a person or system                         | Any view that includes it                             |
| [Boundary](#boundary) | The element that owns the others; nested deployment nodes        | Container and component views; deployment views       |
| [Deployment](#deployment) | `model.DeploymentEnvironment(name)` and nodes                | `DeploymentView(system, environment=...)`             |
| [Relationship](#relationship) | `a >> Rel("label") >> b`                                  | Every view that includes both ends                    |

The snippets below build one system and run as one script. The generated DSL
is the same one that [`Workspace.render()`][c4.contrib.structurizr.Workspace]
returns.

```python
from c4.contrib.structurizr import Rel, Workspace

workspace = Workspace("Shop")

with workspace.model as model:
    customer = model.Person("Customer")
    shop = model.SoftwareSystem("Shop")
    payments = model.SoftwareSystem("Payment Gateway", tags=["External"])
    web = model.Container("Web App", technology="Django", owner=shop)
    db = model.Container(
        "Database", technology="PostgreSQL", owner=shop, tags=["Database"]
    )
    auth = model.Component("Auth", technology="Python", owner=web)

    customer >> Rel("Uses", technology="HTTPS") >> web
    web >> "Reads and writes" >> db
    web >> "Charges" >> payments

    with model.DeploymentEnvironment("Live") as live:
        region = live.DeploymentNode("EU region")
        server = region.DeploymentNode("Server", technology="Ubuntu 24.04")
        server.ContainerInstance(web)

workspace.views.SystemContextView(shop, key="context")
workspace.views.ContainerView(shop, key="containers")
workspace.views.ComponentView(web, key="components")
workspace.views.DeploymentView(shop, environment="Live", key="live")

print(workspace.render())
```

## Person

[`model.Person(name)`][c4.contrib.structurizr.Person] creates a person. It has
no technology and no owner. The built-in tag `Person` selects its style.

```python
customer = model.Person("Customer", description="Buys goods")
```

## Software system

[`model.SoftwareSystem(name)`][c4.contrib.structurizr.SoftwareSystem] creates a
system. A system is the scope of `SystemContextView` and `ContainerView`.

```python
shop = model.SoftwareSystem("Shop")
```

## Container

[`model.Container(name, owner=system)`][c4.contrib.structurizr.Container]
creates a container; `system.Container(name)` is a shortcut. A container is
the scope of `ComponentView`.

```python
web = model.Container("Web App", technology="Django", owner=shop)
```

## Component

[`model.Component(name, owner=container)`][c4.contrib.structurizr.Component]
creates a component; `container.Component(name)` is a shortcut.

```python
auth = model.Component("Auth", technology="Python", owner=web)
```

## Database

Structurizr has no database element. A database is a container (or a
component) with the `Database` tag, drawn with the `Cylinder` shape. The
default `classic` preset already styles that tag; with
`style_preset=None`, or for a different look, style the tag yourself:

```python
db = model.Container(
    "Database", technology="PostgreSQL", owner=shop, tags=["Database"]
)

workspace.styles.element("Database", shape="Cylinder")
```

A message queue works the same way with the `Queue` tag and the `Pipe` shape.

## External

An external person or system is an ordinary one with the `External` tag. The
`classic` preset styles that tag in grey; style it yourself to change that:

```python
payments = model.SoftwareSystem("Payment Gateway", tags=["External"])

workspace.styles.element("External", background="#999999", color="#ffffff")
```

## Boundary

A system boundary in a container view and a container boundary in a component
view are drawn by Structurizr around the scope element, so there is nothing to
create: `ContainerView(shop)` draws a box around the containers of `shop`.

In a deployment model, nesting [`DeploymentNode`][c4.contrib.structurizr.DeploymentNode]
values is the boundary. Deployment nodes carry the `Boundary` tag, which the
`classic` preset draws with a dashed border:

```python
with model.DeploymentEnvironment("Live") as live:
    region = live.DeploymentNode("EU region")
    server = region.DeploymentNode("Server", technology="Ubuntu 24.04")
```

## Deployment

A deployment model has an environment, nested nodes and instances of model
elements. `ContainerInstance` takes a container and `SoftwareSystemInstance`
takes a system.

```python
with model.DeploymentEnvironment("Live") as live:
    region = live.DeploymentNode("EU region")
    server = region.DeploymentNode("Server", technology="Ubuntu 24.04")
    server.ContainerInstance(web)

workspace.views.DeploymentView(shop, environment="Live", key="live")
```

## Relationship

Relationships connect elements of one workspace. Use the
[Structurizr `Rel`][c4.contrib.structurizr.Rel] builder, a plain string label or
`uses`:

```python
customer >> Rel("Uses", technology="HTTPS") >> web
web >> "Reads and writes" >> db
web.uses(payments, "Charges")
```

`[a, b] >> Rel("Uses") >> c` and `c << Rel("Uses") << [a, b]` connect several
elements to one; a list on both sides raises `ValueError`. `a >> b` creates a
relationship without a description, and `a >> b | "Uses"` sets it.

## Concept to view

| View                                         | Scope required                | Shows                                                   |
|----------------------------------------------|-------------------------------|---------------------------------------------------------|
| [`SystemLandscapeView()`][c4.contrib.structurizr.workspace.SystemLandscapeView] | None                          | People and systems                                      |
| [`SystemContextView(system)`][c4.contrib.structurizr.workspace.SystemContextView] | A `SoftwareSystem`            | One system with the people and systems around it        |
| [`ContainerView(system)`][c4.contrib.structurizr.workspace.ContainerView] | A `SoftwareSystem`            | The containers of one system and their neighbours       |
| [`ComponentView(container)`][c4.contrib.structurizr.workspace.ComponentView] | A `Container`                 | The components of one container and their neighbours    |
| [`DynamicView(scope)`][c4.contrib.structurizr.DynamicView] | Optional system or container  | An ordered list of interactions                         |
| [`DeploymentView(scope, environment=...)`][c4.contrib.structurizr.workspace.DeploymentView] | Optional; `environment` is required | The instances in one deployment environment |

A missing or wrong scope is reported when the workspace is rendered. See
[Views](views.md#view-types-and-their-scope).

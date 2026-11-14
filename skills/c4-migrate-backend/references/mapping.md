# Mapping

Target APIs: [`c4-diagrams` whole-architecture reference](../../c4-diagrams/references/whole-architecture.md).

## Portable → Structurizr

| Portable                         | Structurizr                                                                           |
|----------------------------------|---------------------------------------------------------------------------------------|
| `Person`, `PersonExt`            | `model.Person`; Ext gets `tags=["External"]`                                          |
| `System`, `SystemExt`            | `model.SoftwareSystem`; Ext gets `tags=["External"]`                                  |
| `SystemDb`, `SystemQueue` (+Ext) | `SoftwareSystem` with tag `Database` or `Queue`                                       |
| `Container*`                     | `model.Container(..., owner=system)`; Db or Queue as a tag                            |
| `Component*`                     | `model.Component(..., owner=container)`; Db or Queue as a tag                         |
| `SystemBoundary("X")`            | the owner: its containers become `Container(owner=X)`                                 |
| `ContainerBoundary("X")`         | the owner: its components become `Component(owner=X)`                                 |
| `EnterpriseBoundary`             | no equivalent: drop, or tag its members; report it                                    |
| `Node`, `DeploymentNode`         | `DeploymentEnvironment` at the root, `DeploymentNode` below, nested as in the diagram |
| `Container` inside a node        | `ContainerInstance(target, parent=node)` of the model container                       |
| `Rel("l", "tech")`               | `a >> Rel("l", technology="tech") >> b`, in the model                                 |
| `add_property` rows              | `properties={...}`                                                                    |

| Portable diagram         | Structurizr view                                                                               |
|--------------------------|------------------------------------------------------------------------------------------------|
| `SystemContextDiagram`   | `views.SystemContextView(system)`                                                              |
| `SystemLandscapeDiagram` | `views.SystemLandscapeView()`                                                                  |
| `ContainerDiagram`       | `views.ContainerView(system)`                                                                  |
| `ComponentDiagram`       | `views.ComponentView(container)`                                                               |
| `DynamicDiagram`         | `views.DynamicView(scope)` with `step(source, destination, description)` in the original order |
| `DeploymentDiagram`      | `views.DeploymentView(environment=...)`                                                        |

The view scope is the system or container named by the diagram's boundary. If the diagram has none, ask which element is
the scope. Give each view a `key` from the diagram title.

## Portable → LikeC4

Apply the `C4` preset (`project.specification.use(C4)`) so the kinds exist, then:

| Portable                                     | LikeC4                                                                                                  |
|----------------------------------------------|---------------------------------------------------------------------------------------------------------|
| `Person`, `System`, `Container`, `Component` | `model.person/system/container/component`; children via `parent.container(...)`                         |
| `*Ext`                                       | kind `external`                                                                                         |
| `*Db`                                        | kind `database`                                                                                         |
| `*Queue`                                     | `element("queue", ...)` with a declared `queue` kind                                                    |
| Boundary                                     | nesting: members become children of the boundary element; `EnterpriseBoundary` becomes a parent element |
| `Rel`                                        | `a >> Rel(title, technology=...) >> b`                                                                  |
| Deployment nodes                             | `project.deployment.node(...)` with instances of model elements                                         |

LikeC4 has no fixed C4 view types. Each diagram becomes an element view:

| Portable diagram         | LikeC4 view                                                       |
|--------------------------|-------------------------------------------------------------------|
| `SystemLandscapeDiagram` | `element_view(key, title).include(Wildcard())`                    |
| `SystemContextDiagram`   | `element_view(key, title).include(RawPredicate("-> <alias> ->"))` |
| `ContainerDiagram`       | `element_view(key, title, of=system).include(Wildcard())`         |
| `ComponentDiagram`       | `element_view(key, title, of=container).include(Wildcard())`      |
| `DynamicDiagram`         | `dynamic_view(key, title)` with `step(a, b, title)`               |
| `DeploymentDiagram`      | `deployment_view(key, title).include(Wildcard())`                 |

## Reverse: view → portable

Write one portable diagram per view, in the diagram class that matches the view type (LikeC4: the view's `of` scope and
predicates decide: no `of` and top-level elements → landscape; `of` a system → container; `of` a container → component).

- Declare in each diagram only the elements the view selects, with their relationships.
- Structurizr tags `External`, `Database`, `Queue` pick the `Ext`, `Db`, `Queue` classes. LikeC4 kinds map by name (
  `external`, `database`).
- The owning system or container becomes a `SystemBoundary` or `ContainerBoundary` around its children.
- Dynamic steps become `Rel` labels numbered in step order (`"1. ..."`).
- Styles, `auto_layout`, animation, `include`/`exclude` expressions are not portable: drop and report.

# C4 Entities Across Backends

Each C4 concept has a different spelling in the portable core, in Structurizr
and in LikeC4. This table is a **general view**: it points you to the right
call, and the details differ per backend. Follow the links in the Structurizr
and LikeC4 columns for the exact call, the generated output and the view that
shows it.

!!! note "General view, backend details elsewhere"

    Structurizr has C4 kinds built in and uses tags and shapes for external
    systems and databases. LikeC4 has no C4 kinds, so you declare them in the
    specification, for example with `project.specification.use(C4)`. The LikeC4
    helpers (`model.person(...)` and the others) need those kinds declared and
    are shortcuts for `element("person", ...)`. One table cannot hold all of that. Read the
    [Structurizr](../renderers/structurizr/c4-cheatsheet.md) or
    [LikeC4](../renderers/likec4/c4-cheatsheet.md) cheat-sheet for the full
    answer. For the difference between the models, see
    [Two authoring models](authoring-models.md).

| C4 concept | Portable | Structurizr | LikeC4 |
|---|---|---|---|
| Person | [`Person`][c4.diagrams.system_context.Person], [`PersonExt`][c4.diagrams.system_context.PersonExt] | [`model.Person(...)`](../renderers/structurizr/c4-cheatsheet.md#person) | [`model.person(...)`](../renderers/likec4/c4-cheatsheet.md#person) |
| Software system | [`System`][c4.diagrams.system_context.System], [`SystemExt`][c4.diagrams.system_context.SystemExt] | [`model.SoftwareSystem(...)`](../renderers/structurizr/c4-cheatsheet.md#software-system) | [`model.system(...)`](../renderers/likec4/c4-cheatsheet.md#software-system) |
| Container | [`Container`][c4.diagrams.container.Container] | [`model.Container(..., owner=system)`](../renderers/structurizr/c4-cheatsheet.md#container) | [`system.container(...)`](../renderers/likec4/c4-cheatsheet.md#container) |
| Component | [`Component`][c4.diagrams.component.Component] | [`model.Component(..., owner=container)`](../renderers/structurizr/c4-cheatsheet.md#component) | [`container.component(...)`](../renderers/likec4/c4-cheatsheet.md#component) |
| Database | [`ContainerDb`][c4.diagrams.container.ContainerDb], [`ComponentDb`][c4.diagrams.component.ComponentDb] | [Container with the `Database` tag](../renderers/structurizr/c4-cheatsheet.md#database) | [`model.database(...)`](../renderers/likec4/c4-cheatsheet.md#database) |
| External | [`SystemExt`][c4.diagrams.system_context.SystemExt], [`ContainerExt`][c4.diagrams.container.ContainerExt], [`ComponentExt`][c4.diagrams.component.ComponentExt] | [The `External` tag](../renderers/structurizr/c4-cheatsheet.md#external) | [`model.external(...)`](../renderers/likec4/c4-cheatsheet.md#external) |
| Boundary | [`SystemBoundary`][c4.diagrams.system_context.SystemBoundary], [`ContainerBoundary`][c4.diagrams.container.ContainerBoundary] | [Drawn around the view scope](../renderers/structurizr/c4-cheatsheet.md#boundary) | [Nested elements](../renderers/likec4/c4-cheatsheet.md#boundary) |
| Deployment | [`DeploymentDiagram`][c4.diagrams.deployment.DeploymentDiagram], [`DeploymentNode`][c4.diagrams.deployment.DeploymentNode] | [`DeploymentEnvironment` and nodes](../renderers/structurizr/c4-cheatsheet.md#deployment) | [`deployment.node(...)`](../renderers/likec4/c4-cheatsheet.md#deployment) |
| Relationship | [`Rel`][c4.diagrams.core.Rel] | [`Rel`][c4.contrib.structurizr.Rel] or `uses` ([details](../renderers/structurizr/c4-cheatsheet.md#relationship)) | [`Rel`][c4.contrib.likec4.Rel] or `uses` ([details](../renderers/likec4/c4-cheatsheet.md#relationship)) |
| Views | One diagram class per view type | [`ContainerView` and others](../renderers/structurizr/c4-cheatsheet.md#concept-to-view) | [`element_view` with predicates](../renderers/likec4/c4-cheatsheet.md#c4-views) |

## Names for display text

The three backends call the display text of an element or a relationship by
different names. Each name is the word of that backend's own DSL, and the
meanings differ, so the names are **not unified**. What is shared is the call
shape: the first positional argument is the display text, and everything else is
passed by keyword.

| | Portable | Structurizr | LikeC4 |
|---|---|---|---|
| Element display text | `label` | `name` | `title` |
| Element short text | | | `summary` |
| Element long text | `description` | `description` | `description` |
| Relationship display text | `label` | `description` | `title` |
| Relationship long text | `description` | | `description` |

The same relationship reads the same way in all three backends:

```python
a >> "calls" >> b
a >> Rel("calls") >> b
a.uses(b, "calls")
```

The portable `Rel("calls", "long text")` reads its second argument as
`description`. In Structurizr and LikeC4 only the first argument of `Rel` is
positional; pass `description` and `technology` by name, as in
`Rel("calls", technology="HTTPS")`, so the code reads the same in every
backend.

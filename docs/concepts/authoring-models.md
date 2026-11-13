# Two Authoring Models

`c4-diagrams` has two ways to describe an architecture. Which one you use
depends on the backend you render to.

| | Portable core | Whole-architecture backends |
|---|---|---|
| Backends | PlantUML, Mermaid, D2 | Structurizr, LikeC4 |
| Root object | A [`Diagram`][c4.diagrams.core.Diagram] such as `ContainerDiagram` | A [`Workspace`][c4.contrib.structurizr.Workspace] (Structurizr) or a [`Project`][c4.contrib.likec4.Project] (LikeC4) |
| What it describes | One C4 diagram | One model and any number of views of it |
| Where elements live | Inside the diagram, in a `with` block | In `workspace.model` or `project.model`, once |
| Where views live | The diagram is the view | `workspace.views` or `project.views` |
| C4 kinds | Classes such as `Person` and `ContainerDb` | A factory per kind in Structurizr, kinds you declare in LikeC4 |

Use a `Diagram` when you need one C4 diagram, or the same diagram in several
formats. Use a `Workspace` or a `Project` when you keep one model and want
several views (context, containers, components, deployment) generated from it,
or when the artifact you want is Structurizr DSL or LikeC4 source. The two
models do not mix: Structurizr and LikeC4 do not accept the portable `Diagram`
classes.

## One model, several views

In a portable diagram an element exists only in the diagram that declares it. To
show the same system at two zoom levels you write two diagrams and declare the
shared elements twice (or share them with
[reusable elements](../guides/reusable-diagram-elements.md)).

In Structurizr and LikeC4 you declare an element once in the model. A view then
selects which of the model's elements to show, so a new view never repeats the
model. Relationships belong to the model too, and every view that includes both
ends shows them.

## The same system three times

A customer buys from a shop. The shop has a web application and a database and
charges cards through an external payment gateway.

=== "Portable"

    ```python
    from c4 import (
        Container,
        ContainerDb,
        ContainerDiagram,
        Person,
        Rel,
        SystemBoundary,
        SystemExt,
    )

    with ContainerDiagram("Shop") as diagram:
        customer = Person("Customer")
        payments = SystemExt("Payment Gateway")

        with SystemBoundary("Shop"):
            web = Container("Web App", technology="Django")
            db = ContainerDb("Database", technology="PostgreSQL")

        customer >> Rel("Uses", technology="HTTPS") >> web
        web >> "Reads and writes" >> db
        web >> "Charges" >> payments

    print(diagram.as_plantuml())
    ```

=== "Structurizr"

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

        customer >> Rel("Uses", technology="HTTPS") >> web
        web >> "Reads and writes" >> db
        web >> "Charges" >> payments

    workspace.views.ContainerView(shop, key="containers")

    print(workspace.render())
    ```

=== "LikeC4"

    ```python
    from c4.contrib.likec4 import Project, Rel, Wildcard

    project = Project("Shop")

    spec = project.specification
    spec.element("person", shape="person")
    spec.element("system")
    spec.element("container")
    spec.element("database", shape="storage")
    spec.element("external", border="dashed")

    customer = project.model.element("person", "Customer", alias="customer")
    shop = project.model.element("system", "Shop", alias="shop")
    payments = project.model.element("external", "Payment Gateway", alias="payments")
    web = shop.element("container", "Web App", alias="web", technology="Django")
    db = shop.element("database", "Database", alias="db", technology="PostgreSQL")

    customer >> Rel("Uses", technology="HTTPS") >> web
    web >> Rel("Reads and writes") >> db
    web >> Rel("Charges") >> payments

    project.views.element_view("containers", "Containers", of=shop).include(Wildcard())

    print(project.render())
    ```

The differences to notice:

- The portable form has no separate model: the elements, the boundary and the
  relationships are all part of the container diagram.
- Structurizr has the C4 kinds built in. External and database are tags on an
  ordinary system or container.
- LikeC4 has no C4 kinds. The `specification` block declares them first, then
  the model uses them. The [LikeC4 cheat-sheet](../renderers/likec4/c4-cheatsheet.md)
  has a complete specification.
- In Structurizr and LikeC4 the view is a separate call. Adding a context view of
  the same model is one more line.

The table in [C4 entities across backends](c4-entities.md) lists every C4
concept in all three forms. Each model has its own page under
**Authoring in depth**: [Diagrams and components](diagrams.md) (portable),
[Structurizr](structurizr-model.md) and [LikeC4](likec4-model.md).

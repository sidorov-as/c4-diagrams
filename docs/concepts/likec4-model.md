# LikeC4: Project, Specification and Model

In LikeC4 you write a [`Project`][c4.contrib.likec4.Project] with four parts,
and they depend on each other in this order:

1. `project.specification`: the vocabulary. Every element kind, relationship
   kind, tag and custom color is declared here first.
2. `project.model`: the elements and relationships, using the declared kinds.
3. `project.deployment`: deployment nodes and instances of model elements.
4. `project.views`: the views. Each view selects which part of the model to show.

```python
from c4.contrib.likec4 import Project, Rel, Wildcard

project = Project("Shop")

project.specification.element("actor", shape="person").element("system")

customer = project.model.element("actor", "Customer", alias="customer")
shop = project.model.element("system", "Shop", alias="shop")
customer >> Rel("buys goods") >> shop

project.views.element_view("index", "Landscape").include(Wildcard())

print(project.render())
```

## Kinds are declared, not built in

LikeC4 has no built-in C4 kinds: `person`, `container` and `database` exist only
if the specification declares them. That makes the vocabulary yours. The shape
and color of each kind are defaults set in the specification. The
[C4 cheat-sheet](../renderers/likec4/c4-cheatsheet.md) has a ready-to-copy
specification that declares the C4 kinds.

If you want the standard C4 vocabulary without copying the block, apply the
optional `C4` preset with `project.specification.use(C4)`. It is never applied
by default, and the model still works with any kinds you declare yourself. The
`person`, `system`, `container`, `component`, `database` and `external` methods
on `Model` and `Element` then replace `element("person", ...)`.

## Views are predicates

LikeC4 has no fixed C4 view types. An element view shows whatever its predicates
select: `*` for the scope, `x.*` for children, `a -> b` for relationships,
`where` for filters. The context, container and component views of the C4 model
are element views with different scopes and predicates.

## Where to go next

- [Authoring](../renderers/likec4/authoring.md): specification, model,
  relationships and deployment in detail.
- [C4 cheat-sheet](../renderers/likec4/c4-cheatsheet.md): each C4 concept and
  the view that shows it.
- [Views](../renderers/likec4/views.md) and [Styles](../renderers/likec4/styles.md).
- [Two authoring models](authoring-models.md): how this differs from the portable
  `Diagram` and from Structurizr.

# PlantUML Dynamic Indexes

Dynamic diagram indexes are PlantUML-only helpers for C4-PlantUML dynamic
relationship ordering. Import them from `c4.contrib.plantuml` and pass index
values through `plantuml={"index": ...}` on relationships.

## Index helpers

- [`Index`][c4.contrib.plantuml.Index]: returns the current index and advances it.
- [`LastIndex`][c4.contrib.plantuml.LastIndex]: returns the last used index.
- [`SetIndex`][c4.contrib.plantuml.SetIndex]: sets the current index and returns it.
- [`increment`][c4.contrib.plantuml.increment]: inserts a C4-PlantUML index increment.
- [`set_index`][c4.contrib.plantuml.set_index]: inserts a C4-PlantUML set-index call.

```python
from c4 import Container, DynamicDiagram, Person, Rel
from c4.contrib.plantuml import Index, LastIndex, RelR, SetIndex, increment, set_index


with DynamicDiagram("Order flow") as diagram:
    customer = Person("Customer")
    web = Container("Web App")
    api = Container("Orders API")
    payments = Container("Payments")

    customer >> Rel("Places order", plantuml={"index": Index()}) >> web
    web >> Rel("POST /orders", plantuml={"index": Index()}) >> api
    api >> RelR("Authorize payment", plantuml={"index": LastIndex()}) >> payments

    increment()
    api >> Rel("Create order", plantuml={"index": Index() - 1}) >> web

    set_index(10)
    web >> Rel("Send receipt", plantuml={"index": SetIndex(12) - 1}) >> customer
```

Indexes are rendered only by the PlantUML rendering backend. Mermaid has no
equivalent concept, so PlantUML index extension data is ignored by Mermaid
unless strict extension validation is enabled.

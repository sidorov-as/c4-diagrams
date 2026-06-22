# Reusable Diagram Elements

For larger documentation sets, define frequently used people, systems,
containers, and components once, then import them into each diagram as small
element factories.

This keeps each diagram focused on the relationships it explains instead of
repeating long element declarations. It also makes diagrams easier to maintain:
when a shared system name, description, technology, or property changes, update
the shared definition once.

!!! note

    This page uses "elements" in the C4 sense: people, systems, containers,
    components, and related diagram objects. It does not refer only to
    [`Component`](../api_docs/component.md) elements.

## Shared element library

Create a small Python package or module for reusable C4 elements. Each exported
name is a factory that creates a fresh element instance in the active diagram
context.

```python
# architecture/elements.py
from functools import partial

from c4 import Person, System, SystemExt, with_properties


CustomerSupportAgent = with_properties(
    partial(
        Person,
        label="Customer Support Agent",
        description="Handles customer tickets and escalations.",
    ),
    ("Team", "Customer Support"),
)

SupportPortal = partial(
    System,
    label="Support Portal",
    description="Web application used to manage customer support cases.",
)

AuditedSupportPortal = with_properties(
    SupportPortal,
    ("Owner", "Customer Support"),
    ("Audit", "Enabled"),
)

TicketingService = partial(
    System,
    label="Ticketing Service",
    description="Stores tickets, comments, assignments, and status history.",
)

NotificationProvider = partial(
    SystemExt,
    label="Notification Provider",
    description="Sends email and SMS notifications to customers and agents.",
)
```

`functools.partial` pre-fills the bulky constructor arguments, while
[`with_properties`](../api_docs/core/#c4.diagrams.core.BaseDiagramElement.with_properties) can add
property rows to every element created by that factory.

## Use shared elements in diagrams

Import the factories into a diagram file and call them inside the diagram
context:

```python
# diagrams/support_context.py
from c4 import Rel, SystemContextDiagram

from architecture.elements import (
    AuditedSupportPortal,
    CustomerSupportAgent,
    NotificationProvider,
    TicketingService,
)


with SystemContextDiagram("Customer support context") as diagram:
    support_agent = CustomerSupportAgent()
    support_portal = AuditedSupportPortal()
    ticketing_service = TicketingService()
    notification_provider = NotificationProvider()

    support_agent >> Rel("Reviews and updates tickets", "HTTPS") >> support_portal
    support_portal >> Rel("Creates and updates tickets", "REST API") >> ticketing_service
    ticketing_service >> Rel("Sends ticket status notifications") >> notification_provider
```

The resulting diagram file stays small because it describes only the elements
that participate in this view and the relationships between them.

## Organizing shared elements

For a small project, a single module is usually enough:

```text
architecture/
  __init__.py
  elements.py

diagrams/
  support_context.py
  billing_context.py
```

For a larger documentation set, split the library by domain or C4 level:

```text
architecture/
  __init__.py
  people.py
  systems.py
  containers.py
  components.py

diagrams/
  support_context.py
  billing_containers.py
  ticketing_components.py
```

Keep shared factories close to stable model facts: names, descriptions,
technologies, aliases, tags, links, and property rows. Keep view-specific
relationships in the diagram files so each diagram remains easy to read.

## When to use this pattern

Use reusable element factories when the same person, system, container, or
component appears in multiple diagrams, or when element declarations are large
enough to distract from the diagram's purpose.

Inline declarations are still useful for one-off elements that appear in only
one diagram. A shared library should make diagrams clearer, not hide important
view-specific details.

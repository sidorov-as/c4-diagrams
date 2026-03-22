# JSON to Diagram Converter

Diagrams can be defined in a **JSON format** as an alternative to the Python DSL.

This feature allows you to **generate diagrams from structured data** instead of writing Python code,
making diagram creation more flexible, deterministic, and easier to automate.

## Why JSON?

The primary purpose of this feature is to decouple diagram definition from Python code and enable
diagram generation from external sources.

This approach is especially useful in the following scenarios:

### 1. Deterministic diagram generation (LLMs, automation)

JSON provides a **strict and predictable schema**, which makes it ideal for:

- Generating diagrams with **LLMs (AI agents)**
- Ensuring **consistent output across runs**

Instead of asking an LLM to write Python DSL (which may vary),
you can require it to produce **valid JSON conforming to a schema**.

### 2. Infrastructure and service introspection

JSON diagrams can be generated automatically by analyzing your system configuration:

- Docker / Docker Compose configurations
- Kubernetes manifests (Deployments, Services, etc.)
- Cloud infrastructure definitions
- Internal service metadata

This enables **automatic architecture visualization** without manual diagram maintenance.

### 3. Service catalogs and metadata-driven diagrams

Teams can define architecture using **declarative metadata files**, for example:

- `catalog-info.yaml` (similar to [Backstage](https://backstage.io/docs/features/software-catalog/descriptor-format/) and [Open edX](https://docs.openedx.org/projects/openedx-proposals/en/latest/processes/oep-0055/decisions/0001-use-backstage-to-support-maintainers.html#references))
- Custom service manifests in each repository

These files may describe:

- Service name and purpose
- Components (API, workers, schedulers, etc.)
- Dependencies and relationships

From this metadata, you can generate a **JSON diagram**, which is then rendered into a C4 diagram.

## Supported Diagram Types

Each diagram type has its own JSON specification:

- [SystemContextDiagram](specs/system_context_diagram.md)
- [SystemLandscapeDiagram](specs/system_landscape_diagram.md)
- [ContainerDiagram](specs/container_diagram.md)
- [ComponentDiagram](specs/component_diagram.md)
- [DeploymentDiagram](specs/deployment_diagram.md)
- [DynamicDiagram](specs/dynamic_diagram.md)


### Example: System Context Diagram (JSON)

```json
{
  "type": "SystemContextDiagram",
  "elements": [
    {
      "type": "Person",
      "alias": "user",
      "label": "User",
      "description": "System user"
    },
    {
      "type": "System",
      "alias": "app",
      "label": "Backend API",
      "description": "Main application backend"
    }
  ],
  "relationships": [
    {
      "type": "REL",
      "from": "user",
      "to": "app",
      "label": "Uses HTTP API"
    }
  ]
}
```

### Converting JSON to Python DSL

JSON diagrams are treated the same as Python-based diagrams and can be rendered or exported using the same tooling.

To convert a JSON diagram into Python DSL, run:

```shell
c4 convert diagram.json --json-to-py > diagram.py
```

This generates:

```python
# diagram.py
from c4 import (
    Person,
    Rel,
    System,
    SystemContextDiagram,
)

with SystemContextDiagram():
    user = Person('User', 'System user', alias='user')
    app = System('Backend API', 'Main application backend', alias='app')

    user >> Rel('Uses HTTP API') >> app
```

## How JSON diagrams can be generated

The following example shows how architecture information can be extracted from a `docker-compose.yaml` file:


??? abstract "Compose file"

    ```yaml
    version: "3.9"
    name: "Order Processing API"

    services:
      order_controller:
        # ...
        container_name: order_controller
        environment:
          SERVICE_NAME: order_controller
          SERVICE_LABEL: Order Controller
          SERVICE_TECHNOLOGY: FastAPI
          SERVICE_DESCRIPTION: HTTP entrypoint for order submission and status queries.
          SERVICE_TYPE: container
          SERVICE_TAGS: Entrypoint,CoreComponent
          DEPENDS_ON_SERVICES: order_app_service
        depends_on:
          - order_app_service

      order_app_service:
        # ...
        container_name: order_app_service
        environment:
          SERVICE_NAME: order_app_service
          SERVICE_LABEL: Order Application Service
          SERVICE_TECHNOLOGY: Python
          SERVICE_DESCRIPTION: Coordinates validation, payment, and order creation.
          SERVICE_TYPE: container
          SERVICE_TAGS: CoreComponent,Orders
          DEPENDS_ON_SERVICES: inventory_checker,payment_adapter,order_db,order_events_bus
        depends_on:
          - inventory_checker
          - payment_adapter
          - order_db
          - order_events_bus

      inventory_checker:
        # ...
        container_name: inventory_checker
        environment:
          SERVICE_NAME: inventory_checker
          SERVICE_LABEL: Inventory Checker
          SERVICE_TECHNOLOGY: Python
          SERVICE_DESCRIPTION: Verifies stock availability before an order is confirmed.
          SERVICE_TYPE: container
          SERVICE_TAGS: CoreComponent

      payment_adapter:
        # ...
        container_name: payment_adapter
        environment:
          SERVICE_NAME: payment_adapter
          SERVICE_LABEL: Payment Adapter
          SERVICE_TECHNOLOGY: Python
          SERVICE_DESCRIPTION: Wraps external payment provider calls.
          SERVICE_TYPE: container
          SERVICE_TAGS: CoreComponent,Payments
          DEPENDS_ON_SERVICES: payment_gateway_api
        depends_on:
          - payment_gateway_api

      order_db:
        image: postgres:16
        container_name: order_db
        environment:
          # ...
          SERVICE_NAME: order_db
          SERVICE_LABEL: Order Database
          SERVICE_TECHNOLOGY: PostgreSQL
          SERVICE_DESCRIPTION: Stores orders, line items, and order status history.
          SERVICE_TYPE: database
          SERVICE_TAGS: ComponentDatabase

      order_events_bus:
        # ...
        container_name: order_events_bus
        environment:
          SERVICE_NAME: order_events_bus
          SERVICE_LABEL: Order Events Bus
          SERVICE_TECHNOLOGY: Kafka
          SERVICE_DESCRIPTION: Publishes order-created and order-paid events.
          SERVICE_TYPE: queue
          SERVICE_TAGS: AsyncComponent

      payment_gateway_api:
        # ...
        container_name: payment_gateway_api
        environment:
          SERVICE_NAME: payment_gateway_api
          SERVICE_LABEL: Payment Gateway API
          SERVICE_TECHNOLOGY: REST API
          SERVICE_DESCRIPTION: External provider API for payment authorization and capture.
          SERVICE_TYPE: external
          SERVICE_TAGS: ExternalComponent
    ```

??? abstract "Diagram generator"

    ```python
    import yaml


    def parse_tags(value: str | None) -> list[str]:
        if not value:
            return []
        return [item.strip() for item in value.split(",") if item.strip()]


    def parse_compose(file_path: str) -> dict:
        compose = yaml.safe_load(open(file_path))
        services = compose["services"]
        title = compose.get("name", "Container Diagram")

        elements = []
        relationships = []

        type_map = {
            "container": "Container",
            "database": "ContainerDb",
            "queue": "ContainerQueue",
            "external": "ContainerExt",
        }

        for service_name, service in services.items():
            env = service.get("environment", {})

            service_kind = env.get("SERVICE_TYPE", "container")
            element_type = type_map.get(service_kind, "Container")

            elements.append({
                "type": element_type,
                "alias": service_name,
                "label": env.get("SERVICE_LABEL", service_name),
                "technology": env.get("SERVICE_TECHNOLOGY"),
                "description": env.get("SERVICE_DESCRIPTION", "Docker service"),
                "tags": parse_tags(env.get("SERVICE_TAGS")),
            })

            for dep in service.get("depends_on", []):
                relationships.append({
                    "type": "REL",
                    "from": service_name,
                    "to": dep,
                    "label": "Depends on",
                    "tags": ["InfraDependency"],
                })

        return {
            "type": "ContainerDiagram",
            "title": title,
            "elements": elements,
            "relationships": relationships,
            "render_options": {
                "plantuml": {
                    "show_legend": {
                        "details": "Normal",
                        "hide_stereotype": True
                    },
                }
            }
        }
    ```

This generates the diagram below:

<figure markdown="span">
  ![docker-compose-diagram](../../assets/converters/docker-compose-diagram.png)
  <figcaption>docker-compose-diagram</figcaption>
</figure>

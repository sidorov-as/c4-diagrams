# ComponentDiagram Spec

> **Source:** [component_diagram.json](../../../assets/specs/component_diagram.json)


This schema describes the [ComponentDiagram][c4.diagrams.component.ComponentDiagram] spec.

## Properties

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type of the diagram. Must be exactly `ComponentDiagram`. |
    | `title` | `string` \| `null` | Optional diagram title. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `layouts` | <code>array[<a href="#layoutschema">LayoutSchema</a>]</code> | Relative layout constraints between elements. |
    | `render_options` | <code><a href="#renderoptionsschema">RenderOptionsSchema</a></code> | Optional renderer-specific options |

??? abstract "Minimal example"

    ```json
    {
      "type": "ComponentDiagram",
      "title": "Checkout API - Component Diagram",
      "elements": [
        {
          "alias": "checkout_controller",
          "description": "Receives checkout requests and orchestrates payment flow.",
          "label": "Checkout Controller",
          "tags": [
            "Entrypoint"
          ],
          "technology": "FastAPI",
          "type": "Component"
        },
        {
          "alias": "payment_service",
          "description": "Creates payment intents and handles payment state updates.",
          "label": "Payment Service",
          "tags": [
            "CoreComponent"
          ],
          "technology": "Python",
          "type": "Component"
        },
        {
          "alias": "payment_store",
          "description": "Stores payment records and statuses.",
          "label": "Payment Store",
          "tags": [
            "ComponentDatabase"
          ],
          "technology": "PostgreSQL",
          "type": "ComponentDb"
        },
        {
          "alias": "payment_gateway_api",
          "description": "External API for payment authorization and capture.",
          "label": "Payment Gateway API",
          "tags": [
            "ExternalComponent"
          ],
          "technology": "REST API",
          "type": "ComponentExt"
        }
      ],
      "relationships": [
        {
          "from": "checkout_controller",
          "label": "Calls",
          "technology": "Python call",
          "to": "payment_service",
          "type": "REL"
        },
        {
          "from": "payment_service",
          "label": "Reads and writes",
          "technology": "SQL",
          "to": "payment_store",
          "type": "REL"
        },
        {
          "from": "payment_service",
          "label": "Creates payments via",
          "technology": "HTTPS/JSON",
          "to": "payment_gateway_api",
          "type": "REL"
        }
      ],
      "layouts": [
        {
          "from": "checkout_controller",
          "to": "payment_service",
          "type": "LAY_R"
        },
        {
          "from": "payment_service",
          "to": "payment_store",
          "type": "LAY_D"
        },
        {
          "from": "payment_service",
          "to": "payment_gateway_api",
          "type": "LAY_R"
        }
      ],
      "render_options": {
        "plantuml": {
          "layout": "LAYOUT_LEFT_RIGHT",
          "layout_with_legend": true,
          "legend_title": "Checkout Component Legend",
          "show_legend": {
            "details": "Normal",
            "hide_stereotype": false
          },
          "tags": [
            {
              "bg_color": "#e3f2fd",
              "border_color": "#42a5f5",
              "border_style": "BoldLine",
              "border_thickness": "2",
              "font_color": "#0d47a1",
              "legend_sprite": "server",
              "legend_text": "API entrypoint component",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "sprite": "server",
              "tag_stereo": "Entrypoint",
              "technology": "FastAPI",
              "type": "ComponentTag"
            },
            {
              "bg_color": "#e8f0fe",
              "border_color": "#64b5f6",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#0d47a1",
              "legend_sprite": "server",
              "legend_text": "Internal core component",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "sprite": "server",
              "tag_stereo": "CoreComponent",
              "technology": "Python",
              "type": "ComponentTag"
            },
            {
              "bg_color": "#fff8e1",
              "border_color": "#ffb300",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#5d4037",
              "legend_sprite": "database",
              "legend_text": "Internal component database",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "sprite": "database",
              "tag_stereo": "ComponentDatabase",
              "technology": "PostgreSQL",
              "type": "ComponentTag"
            },
            {
              "bg_color": "#f5f5f5",
              "border_color": "#9e9e9e",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "font_color": "#424242",
              "legend_sprite": "cloud",
              "legend_text": "External component dependency",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "sprite": "cloud",
              "tag_stereo": "ExternalComponent",
              "technology": "REST API",
              "type": "ExternalComponentTag"
            }
          ]
        }
      }
    }
    ```



??? abstract "Advanced example"

    ```json
    {
      "type": "ComponentDiagram",
      "title": "Order Processing API - Component Diagram",
      "elements": [
        {
          "alias": "order_controller",
          "description": "HTTP entrypoint for order submission and status queries.",
          "label": "Order Controller",
          "sprite": "server",
          "tags": [
            "Entrypoint",
            "CoreComponent"
          ],
          "technology": "FastAPI",
          "type": "Component"
        },
        {
          "alias": "order_app_service",
          "description": "Coordinates validation, payment, and order creation.",
          "label": "Order Application Service",
          "sprite": "server",
          "tags": [
            "CoreComponent",
            "Orders"
          ],
          "technology": "Python",
          "type": "Component"
        },
        {
          "alias": "inventory_checker",
          "description": "Verifies stock availability before an order is confirmed.",
          "label": "Inventory Checker",
          "sprite": "server",
          "tags": [
            "CoreComponent"
          ],
          "technology": "Python",
          "type": "Component"
        },
        {
          "alias": "payment_adapter",
          "description": "Wraps external payment provider calls.",
          "label": "Payment Adapter",
          "sprite": "server",
          "tags": [
            "CoreComponent",
            "Payments"
          ],
          "technology": "Python",
          "type": "Component"
        },
        {
          "alias": "order_db",
          "description": "Stores orders, line items, and order status history.",
          "label": "Order Database",
          "sprite": "database",
          "tags": [
            "ComponentDatabase"
          ],
          "technology": "PostgreSQL",
          "type": "ComponentDb"
        },
        {
          "alias": "payment_gateway_api",
          "description": "External provider API for payment authorization and capture.",
          "label": "Payment Gateway API",
          "sprite": "cloud",
          "tags": [
            "ExternalComponent"
          ],
          "technology": "REST API",
          "type": "ComponentExt"
        },
        {
          "alias": "order_events_bus",
          "description": "Publishes order-created and order-paid events.",
          "label": "Order Events Bus",
          "sprite": "queue",
          "tags": [
            "AsyncComponent"
          ],
          "technology": "Kafka",
          "type": "ComponentQueue"
        }
      ],
      "relationships": [
        {
          "from": "order_controller",
          "label": "Invokes",
          "tags": [
            "SyncCall"
          ],
          "technology": "Python call",
          "to": "order_app_service",
          "type": "REL"
        },
        {
          "from": "order_app_service",
          "label": "Checks stock via",
          "tags": [
            "SyncCall"
          ],
          "technology": "Python call",
          "to": "inventory_checker",
          "type": "REL"
        },
        {
          "from": "order_app_service",
          "label": "Requests payment through",
          "tags": [
            "SyncCall"
          ],
          "technology": "Python call",
          "to": "payment_adapter",
          "type": "REL"
        },
        {
          "from": "payment_adapter",
          "label": "Authorizes payment via",
          "tags": [
            "ExternalCall"
          ],
          "technology": "HTTPS/JSON",
          "to": "payment_gateway_api",
          "type": "REL"
        },
        {
          "from": "order_app_service",
          "label": "Reads and writes",
          "tags": [
            "DataAccess"
          ],
          "technology": "SQL",
          "to": "order_db",
          "type": "REL"
        },
        {
          "from": "order_app_service",
          "label": "Publishes events to",
          "tags": [
            "AsyncFlow"
          ],
          "technology": "Kafka",
          "to": "order_events_bus",
          "type": "REL"
        }
      ],
      "layouts": [
        {
          "from": "order_controller",
          "to": "order_app_service",
          "type": "LAY_R"
        },
        {
          "from": "order_app_service",
          "to": "inventory_checker",
          "type": "LAY_R"
        },
        {
          "from": "order_app_service",
          "to": "order_db",
          "type": "LAY_D"
        },
        {
          "from": "inventory_checker",
          "to": "payment_adapter",
          "type": "LAY_R"
        },
        {
          "from": "payment_adapter",
          "to": "payment_gateway_api",
          "type": "LAY_R"
        },
        {
          "from": "payment_adapter",
          "to": "order_events_bus",
          "type": "LAY_D"
        }
      ],
      "render_options": {
        "plantuml": {
          "layout": "LAYOUT_LEFT_RIGHT",
          "layout_with_legend": true,
          "legend_title": "Order Processing Component Legend",
          "show_legend": {
            "details": "Normal",
            "hide_stereotype": false
          },
          "styles": [
            {
              "border_style": "SolidLine",
              "element_name": "component",
              "shape": "RoundedBoxShape",
              "type": "ElementStyle"
            },
            {
              "line_color": "#546e7a",
              "text_color": "#37474f",
              "type": "RelStyle"
            }
          ],
          "tags": [
            {
              "bg_color": "#e3f2fd",
              "border_color": "#42a5f5",
              "border_style": "BoldLine",
              "border_thickness": "2",
              "font_color": "#0d47a1",
              "legend_sprite": "server",
              "legend_text": "HTTP/API entrypoint component",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "sprite": "server",
              "tag_stereo": "Entrypoint",
              "technology": "FastAPI",
              "type": "ComponentTag"
            },
            {
              "bg_color": "#e8f5e9",
              "border_color": "#66bb6a",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#1b5e20",
              "legend_sprite": "server",
              "legend_text": "Internal business component",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "sprite": "server",
              "tag_stereo": "CoreComponent",
              "technology": "Python",
              "type": "ComponentTag"
            },
            {
              "bg_color": "#fff3e0",
              "border_color": "#fb8c00",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#e65100",
              "legend_sprite": "server",
              "legend_text": "Order management component",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "sprite": "server",
              "tag_stereo": "Orders",
              "technology": "Python",
              "type": "ComponentTag"
            },
            {
              "bg_color": "#ede7f6",
              "border_color": "#7e57c2",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#311b92",
              "legend_sprite": "server",
              "legend_text": "Payment-related component",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "sprite": "server",
              "tag_stereo": "Payments",
              "technology": "Python",
              "type": "ComponentTag"
            },
            {
              "bg_color": "#fff8e1",
              "border_color": "#ffb300",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#5d4037",
              "legend_sprite": "database",
              "legend_text": "Internal component database",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "sprite": "database",
              "tag_stereo": "ComponentDatabase",
              "technology": "PostgreSQL",
              "type": "ComponentTag"
            },
            {
              "bg_color": "#f5f5f5",
              "border_color": "#9e9e9e",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "font_color": "#424242",
              "legend_sprite": "cloud",
              "legend_text": "External component dependency",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "sprite": "cloud",
              "tag_stereo": "ExternalComponent",
              "technology": "REST API",
              "type": "ExternalComponentTag"
            },
            {
              "bg_color": "#f3e5f5",
              "border_color": "#ab47bc",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#6a1b9a",
              "legend_sprite": "queue",
              "legend_text": "Internal asynchronous component",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "sprite": "queue",
              "tag_stereo": "AsyncComponent",
              "technology": "Kafka",
              "type": "ComponentTag"
            },
            {
              "legend_text": "Synchronous internal call",
              "line_color": "#1e88e5",
              "line_style": "SolidLine",
              "line_thickness": "1",
              "tag_stereo": "SyncCall",
              "technology": "Python call",
              "text_color": "#1565c0",
              "type": "RelTag"
            },
            {
              "legend_text": "External service call",
              "line_color": "#78909c",
              "line_style": "DashedLine",
              "line_thickness": "1",
              "tag_stereo": "ExternalCall",
              "technology": "HTTPS/JSON",
              "text_color": "#455a64",
              "type": "RelTag"
            },
            {
              "legend_text": "Database access",
              "line_color": "#8d6e63",
              "line_style": "DashedLine",
              "line_thickness": "1",
              "tag_stereo": "DataAccess",
              "technology": "SQL",
              "text_color": "#6d4c41",
              "type": "RelTag"
            },
            {
              "legend_sprite": "queue",
              "legend_text": "Asynchronous event flow",
              "line_color": "#8e24aa",
              "line_style": "DottedLine",
              "line_thickness": "2",
              "sprite": "queue",
              "tag_stereo": "AsyncFlow",
              "technology": "Kafka",
              "text_color": "#6a1b9a",
              "type": "RelTag"
            }
          ]
        }
      }
    }
    ```

### Elements

- [PersonSchema](#personschema)
- [PersonExtSchema](#personextschema)
- [SystemSchema](#systemschema)
- [SystemExtSchema](#systemextschema)
- [SystemDbSchema](#systemdbschema)
- [SystemDbExtSchema](#systemdbextschema)
- [SystemQueueSchema](#systemqueueschema)
- [SystemQueueExtSchema](#systemqueueextschema)
- [ContainerSchema](#containerschema)
- [ContainerExtSchema](#containerextschema)
- [ContainerDbSchema](#containerdbschema)
- [ContainerDbExtSchema](#containerdbextschema)
- [ContainerQueueSchema](#containerqueueschema)
- [ContainerQueueExtSchema](#containerqueueextschema)
- [ComponentSchema](#componentschema)
- [ComponentExtSchema](#componentextschema)
- [ComponentDbSchema](#componentdbschema)
- [ComponentDbExtSchema](#componentdbextschema)
- [ComponentQueueSchema](#componentqueueschema)
- [ComponentQueueExtSchema](#componentqueueextschema)

### Boundaries

- [EnterpriseBoundarySchema](#enterpriseboundaryschema)
- [SystemBoundarySchema](#systemboundaryschema)
- [ContainerBoundarySchema](#containerboundaryschema)

### Relationships

- [RelationshipSchema](#relationshipschema)

- [RelationshipSchema types](#relationshiptype)

### Layouts

- [LayoutSchema](#layoutschema)

- [LayoutSchema types](#layouttype)

## Definitions


???+ warning "About **labels** and **aliases**"

    `label` is a display name for the element.

    `alias` is a unique identifier used for referencing elements
    in relationships and layouts.
    If omitted, it is generated automatically.


    You can also use `label` for referencing elements in relationships     and layouts, but each `label` must be **unique** within the diagram.


<br/>

### RelationshipType

Enum representing different types of relationships between
diagram elements.

???+ info "Items"

    <div class="code-nowrap"></div>

    | Type | Description |
    |---|---|
    | `BI_REL` | A bidirectional relationship between two elements. |
    | `BI_REL_D` | A bidirectional downward relationship. Shorthand for `BI_REL_DOWN`. |
    | `BI_REL_DOWN` | A bidirectional downward relationship. |
    | `BI_REL_L` | A bidirectional leftward relationship. Shorthand for `BI_REL_LEFT`. |
    | `BI_REL_LEFT` | A bidirectional leftward relationship. |
    | `BI_REL_NEIGHBOR` | A bidirectional neighboring relationship between two elements. |
    | `BI_REL_R` | A bidirectional rightward relationship. Shorthand for `BI_REL_RIGHT`. |
    | `BI_REL_RIGHT` | A bidirectional rightward relationship. |
    | `BI_REL_U` | A bidirectional upward relationship. Shorthand for `BI_REL_UP`. |
    | `BI_REL_UP` | A bidirectional upward relationship. |
    | `REL` | A unidirectional relationship between two elements. |
    | `REL_BACK` | A unidirectional relationship pointing backward. |
    | `REL_BACK_NEIGHBOR` | A unidirectional relationship combining backward and neighboring semantics. |
    | `REL_D` | A unidirectional downward relationship. Shorthand for `REL_DOWN`. |
    | `REL_DOWN` | A unidirectional downward relationship. |
    | `REL_L` | A unidirectional leftward relationship. Shorthand for `REL_LEFT`. |
    | `REL_LEFT` | A unidirectional leftward relationship. |
    | `REL_NEIGHBOR` | A unidirectional relationship representing a lateral or neighboring interaction. |
    | `REL_R` | A unidirectional rightward relationship. Shorthand for `REL_RIGHT`. |
    | `REL_RIGHT` | A unidirectional rightward relationship. |
    | `REL_U` | A unidirectional upward relationship. Shorthand for `REL_UP`. |
    | `REL_UP` | A unidirectional upward relationship. |

### LayoutType

Enum representing layout modifiers for diagram elements.

???+ info "Items"

    <div class="code-nowrap"></div>

    | Type | Description |
    |---|---|
    | `LAY_D` | Positions `from` element below `to` element. Shorthand for `LAY_DOWN` layout. |
    | `LAY_DOWN` | Positions `from` element below `to` element. |
    | `LAY_L` | Positions `from` element to the left of `to` element. Shorthand for `LAY_LEFT` layout. |
    | `LAY_LEFT` | Positions `from` element to the left of `to` element. |
    | `LAY_R` | Positions `from` element to the right of `to` element. Shorthand for `LAY_RIGHT` layout. |
    | `LAY_RIGHT` | Positions `from` element to the right of `to` element. |
    | `LAY_U` | Positions `from` element above `to` element. Shorthand for `LAY_UP` layout. |
    | `LAY_UP` | Positions `from` element above `to` element. |

### ComponentDbExtSchema

This schema describes the
[`ComponentDbExt`][c4.diagrams.component.ComponentDbExt]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ComponentDbExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ComponentDbSchema

This schema describes the
[`ComponentDb`][c4.diagrams.component.ComponentDb]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ComponentDb`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ComponentExtSchema

This schema describes the
[`ComponentExt`][c4.diagrams.component.ComponentExt]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ComponentExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `base_shape` | `string` \| `null` | Optional base shape override (supported by some element classes). |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ComponentQueueExtSchema

This schema describes the
[`ComponentQueueExt`][c4.diagrams.component.ComponentQueueExt]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ComponentQueueExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ComponentQueueSchema

This schema describes the
[`ComponentQueue`][c4.diagrams.component.ComponentQueue]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ComponentQueue`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ComponentSchema

This schema describes the
[`Component`][c4.diagrams.component.Component]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `Component`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `base_shape` | `string` \| `null` | Optional base shape override (supported by some element classes). |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ContainerBoundarySchema

This schema describes the
[`ContainerBoundary`][c4.diagrams.container.ContainerBoundary]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ContainerBoundary`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Elements may be nested arbitrarily. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Boundaries may be nested arbitrarily. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Relationships declared inside the boundary. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### ContainerDbExtSchema

This schema describes the
[`ContainerDbExt`][c4.diagrams.container.ContainerDbExt]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ContainerDbExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ContainerDbSchema

This schema describes the
[`ContainerDb`][c4.diagrams.container.ContainerDb]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ContainerDb`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ContainerExtSchema

This schema describes the
[`ContainerExt`][c4.diagrams.container.ContainerExt]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ContainerExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `base_shape` | `string` \| `null` | Optional base shape override (supported by some element classes). |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ContainerQueueExtSchema

This schema describes the
[`ContainerQueueExt`][c4.diagrams.container.ContainerQueueExt]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ContainerQueueExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ContainerQueueSchema

This schema describes the
[`ContainerQueue`][c4.diagrams.container.ContainerQueue]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ContainerQueue`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### ContainerSchema

This schema describes the
[`Container`][c4.diagrams.container.Container]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `Container`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `base_shape` | `string` \| `null` | Optional base shape override (supported by some element classes). |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | Optional technology. |

### DiagramElementPropertiesSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `header` | <code>array[string]</code> | Header columns. Default: `["Property", "Value"]`. |
    | **`properties(required)`** | <code>array[array[string]]</code> | List of rows (each row is a list of string values). |
    | `show_header` | `boolean` | Whether to display the header row. Default: `true`. |

### EnterpriseBoundarySchema

This schema describes the
[`EnterpriseBoundary`][c4.diagrams.system_context.EnterpriseBoundary]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `EnterpriseBoundary`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Elements may be nested arbitrarily. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Boundaries may be nested arbitrarily. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Relationships declared inside the boundary. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### LayoutSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | <code><a href="#layouttype">LayoutType</a></code> | Type of the layout. |
    | **`from(required)`** | `string` | The source element alias (or unique label). |
    | **`to(required)`** | `string` | The destination element alias (or unique label). |

### PersonExtSchema

This schema describes the
[`PersonExt`][c4.diagrams.system_context.PersonExt] diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `PersonExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### PersonSchema

This schema describes the [`Person`][c4.diagrams.system_context.Person]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `Person`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### PlantUMLLayoutOptionsSchema

Final layout configuration for rendering a C4-PlantUML diagram.

Encapsulates layout directives, macros, tag definitions, and visual styles
applied at render time.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `hide_person_sprite` | `boolean` | Whether to hide person sprites globally. Default: `false`. |
    | `hide_stereotype` | `boolean` | Whether to hide stereotype labels globally. Default: `false`. |
    | `layout` | <code><a href="#diagramlayout">DiagramLayout</a></code> | Layout direction. |
    | `layout_as_sketch` | `boolean` | Whether to apply the LAYOUT_AS_SKETCH macro. Default: `false`. |
    | `layout_with_legend` | `boolean` | Whether to apply the LAYOUT_WITH_LEGEND macro. Default: `false`. |
    | `legend_title` | `string` \| `null` | Optional title displayed above the legend. |
    | `set_sketch_style` | <code><a href="#setsketchstyleschema">SetSketchStyleSchema</a></code> | Optional sketch-style visual customization. |
    | `show_floating_legend` | <code><a href="#showfloatinglegendschema">ShowFloatingLegendSchema</a></code> | Configuration for the SHOW_FLOATING_LEGEND macro. |
    | `show_legend` | <code><a href="#showlegendschema">ShowLegendSchema</a></code> | Configuration for the SHOW_LEGEND macro. |
    | `show_person_outline` | `boolean` | Whether to enable person outlines. Default: `false`. |
    | `show_person_portrait` | `boolean` | Whether to enable person portraits. Default: `false`. |
    | `show_person_sprite` | <code><a href="#showpersonspriteschema">ShowPersonSpriteSchema</a></code> | Configuration for the SHOW_PERSON_SPRITE macro. |
    | `styles` | <code>array</code> | List of style update macro configurations. |
    | `tags` | <code>array</code> | List of tag macro configurations. |
    | `without_property_header` | `boolean` | If true, omit the header row and render the second column in bold. Default: `false`. |

### RelationshipSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | <code><a href="#relationshiptype">RelationshipType</a></code> | Type of the relationship. |
    | `description` | `string` \| `null` | Additional details about the relationship. |
    | **`from(required)`** | `string` | The source element alias (or unique label). |
    | **`label(required)`** | `string` | The label shown on the relationship edge. |
    | `link` | `string` \| `null` | Optional URL link associated with the relationship. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon to represent the relationship. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |
    | `technology` | `string` \| `null` | The technology used in the communication. |
    | **`to(required)`** | `string` | The destination element alias (or unique label). |

### RenderOptionsSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `plantuml` | <code><a href="#plantumllayoutoptionsschema">PlantUMLLayoutOptionsSchema</a></code> | PlantUML-specific render options. |

### SystemBoundarySchema

This schema describes the
[`SystemBoundary`][c4.diagrams.system_context.SystemBoundary]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `SystemBoundary`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Elements may be nested arbitrarily. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Boundaries may be nested arbitrarily. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Relationships declared inside the boundary. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### SystemDbExtSchema

This schema describes the
[`SystemDbExt`][c4.diagrams.system_context.SystemDbExt]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `SystemDbExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### SystemDbSchema

This schema describes the
[`SystemDb`][c4.diagrams.system_context.SystemDb]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `SystemDb`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### SystemExtSchema

This schema describes the
[`SystemExt`][c4.diagrams.system_context.SystemExt] diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `SystemExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `base_shape` | `string` \| `null` | Optional base shape override (supported by some element classes). |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### SystemQueueExtSchema

This schema describes the
[`SystemQueueExt`][c4.diagrams.system_context.SystemQueueExt]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `SystemQueueExt`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### SystemQueueSchema

This schema describes the
[`SystemQueue`][c4.diagrams.system_context.SystemQueue]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `SystemQueue`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### SystemSchema

This schema describes the
[`System`][c4.diagrams.system_context.System] diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `System`. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `base_shape` | `string` \| `null` | Optional base shape override (supported by some element classes). |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite/icon reference. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |



## Render Options


### DiagramLayout

Defines layout direction options for a PlantUML diagram.

This enum controls how diagram elements are arranged visually using
predefined PlantUML layout macros.

Members:
    - LAYOUT_TOP_DOWN: Arrange elements vertically from top to bottom.
    - LAYOUT_LEFT_RIGHT: Arrange elements horizontally from left to right.
    - LAYOUT_LANDSCAPE: Apply PlantUML's landscape layout orientation.

- `LAYOUT_LANDSCAPE`
- `LAYOUT_LEFT_RIGHT`
- `LAYOUT_TOP_DOWN`

### BoundaryStyleSchema

Style update for a boundary element (container/system/enterprise boundary).

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `BoundaryStyle`. |
    | `bg_color` | `string` \| `null` | Background color. |
    | `border_color` | `string` \| `null` | Border line color. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the border line. |
    | **`element_name(required)`** | `string` | C4 element type to style (e.g. 'person', 'system', 'container'). This applies to all elements of the given type, not a specific instance. |
    | `font_color` | `string` \| `null` | Font/text color. |
    | `legend_sprite` | `string` \| `null` | Legend sprite for this styled element. |
    | `legend_text` | `string` \| `null` | Legend label for this styled element. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. |
    | `shape` | `string` \| `null` | Shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon applied to the element. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### BoundaryTagSchema

Tag for diagram boundaries (containers/systems).

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `BoundaryTag`. |
    | `bg_color` | `string` \| `null` | Background color of the element. |
    | `border_color` | `string` \| `null` | Color of the element border. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the element border line. |
    | `font_color` | `string` \| `null` | Font color used for labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### ComponentTagSchema

Tag for internal software components.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ComponentTag`. |
    | `bg_color` | `string` \| `null` | Background color of the element. |
    | `border_color` | `string` \| `null` | Color of the element border. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the element border line. |
    | `font_color` | `string` \| `null` | Font color used for labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### ContainerBoundaryStyleSchema

Style update for container boundaries.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ContainerBoundaryStyle`. |
    | `bg_color` | `string` \| `null` | Background color. |
    | `border_color` | `string` \| `null` | Border line color. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the border line. |
    | **`element_name(required)`** | `string` | C4 element type to style (e.g. 'person', 'system', 'container'). This applies to all elements of the given type, not a specific instance. |
    | `font_color` | `string` \| `null` | Font/text color. |
    | `legend_sprite` | `string` \| `null` | Legend sprite for this styled element. |
    | `legend_text` | `string` \| `null` | Legend label for this styled element. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. |
    | `shape` | `string` \| `null` | Shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon applied to the element. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### ContainerTagSchema

Tag for internal containers (microservices, databases, etc.).

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ContainerTag`. |
    | `bg_color` | `string` \| `null` | Background color of the element. |
    | `border_color` | `string` \| `null` | Color of the element border. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the element border line. |
    | `font_color` | `string` \| `null` | Font color used for labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### ElementStyleSchema

Style update for an individual diagram element.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ElementStyle`. |
    | `bg_color` | `string` \| `null` | Background color. |
    | `border_color` | `string` \| `null` | Border line color. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the border line. |
    | **`element_name(required)`** | `string` | C4 element type to style (e.g. 'person', 'system', 'container'). This applies to all elements of the given type, not a specific instance. |
    | `font_color` | `string` \| `null` | Font/text color. |
    | `legend_sprite` | `string` \| `null` | Legend sprite for this styled element. |
    | `legend_text` | `string` \| `null` | Legend label for this styled element. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. |
    | `shape` | `string` \| `null` | Shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon applied to the element. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### ElementTagSchema

Represents a tag for general diagram elements
(containers, nodes, components).

Defines color, border, shape, and optional technology metadata.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ElementTag`. |
    | `bg_color` | `string` \| `null` | Background color of the element. |
    | `border_color` | `string` \| `null` | Color of the element border. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the element border line. |
    | `font_color` | `string` \| `null` | Font color used for labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### EnterpriseBoundaryStyleSchema

Style update for enterprise boundaries.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `EnterpriseBoundaryStyle`. |
    | `bg_color` | `string` \| `null` | Background color. |
    | `border_color` | `string` \| `null` | Border line color. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the border line. |
    | **`element_name(required)`** | `string` | C4 element type to style (e.g. 'person', 'system', 'container'). This applies to all elements of the given type, not a specific instance. |
    | `font_color` | `string` \| `null` | Font/text color. |
    | `legend_sprite` | `string` \| `null` | Legend sprite for this styled element. |
    | `legend_text` | `string` \| `null` | Legend label for this styled element. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. |
    | `shape` | `string` \| `null` | Shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon applied to the element. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### ExternalComponentTagSchema

Tag for external software components.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ExternalComponentTag`. |
    | `bg_color` | `string` \| `null` | Background color of the element. |
    | `border_color` | `string` \| `null` | Color of the element border. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the element border line. |
    | `font_color` | `string` \| `null` | Font color used for labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### ExternalContainerTagSchema

Tag for external containers.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ExternalContainerTag`. |
    | `bg_color` | `string` \| `null` | Background color of the element. |
    | `border_color` | `string` \| `null` | Color of the element border. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the element border line. |
    | `font_color` | `string` \| `null` | Font color used for labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### ExternalPersonTagSchema

Tag for external people (outside the system boundary).

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ExternalPersonTag`. |
    | `bg_color` | `string` \| `null` | Background color of the person symbol. |
    | `border_color` | `string` \| `null` | Border color of the person symbol. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the person border line. |
    | `font_color` | `string` \| `null` | Font color used in the label. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |

### ExternalSystemTagSchema

Tag for external software systems.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `ExternalSystemTag`. |
    | `bg_color` | `string` \| `null` | Background color of the system element. |
    | `border_color` | `string` \| `null` | Border color of the system element. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the system border line. |
    | `font_color` | `string` \| `null` | Font color used in system labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |

### NodeTagSchema

Tag for nodes (typically infrastructure elements).

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `NodeTag`. |
    | `bg_color` | `string` \| `null` | Background color of the element. |
    | `border_color` | `string` \| `null` | Color of the element border. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the element border line. |
    | `font_color` | `string` \| `null` | Font color used for labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### PersonTagSchema

Tag for internal Person elements (actors, users, roles).

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `PersonTag`. |
    | `bg_color` | `string` \| `null` | Background color of the person symbol. |
    | `border_color` | `string` \| `null` | Border color of the person symbol. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the person border line. |
    | `font_color` | `string` \| `null` | Font color used in the label. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |

### RelStyleSchema

Style update for relationship lines.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `RelStyle`. |
    | `line_color` | `string` \| `null` | Color of the relationship line. |
    | `text_color` | `string` \| `null` | Color of the relationship label text. |

### RelTagSchema

Represents a tag for relationship styling in the diagram.

Includes text and line formatting, plus optional technology
and sprite metadata.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `RelTag`. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `line_color` | `string` \| `null` | Color of the relationship line. |
    | `line_style` | `string` \| `null` | Relationship line style macro. |
    | `line_thickness` | `string` \| `null` | Thickness of the relationship line. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |
    | `technology` | `string` \| `null` | Technology label associated with the relationship. |
    | `text_color` | `string` \| `null` | Color of the relationship label text. |

### SetSketchStyleSchema

Configuration for the SET_SKETCH_STYLE macro.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `bg_color` | `string` \| `null` | Background color of the diagram. |
    | `font_color` | `string` \| `null` | Font color for all diagram text. |
    | `font_name` | `string` \| `null` | Font family name to use. |
    | `footer_text` | `string` \| `null` | Optional footer text message. |
    | `footer_warning` | `string` \| `null` | Optional warning message shown in the footer. |
    | `warning_color` | `string` \| `null` | Color used for warning messages in the footer. |

### ShowFloatingLegendSchema

Configuration for the SHOW_FLOATING_LEGEND macro.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `alias` | `string` \| `null` | Optional alias for the floating legend box. |
    | `details` | `string` | Legend detail level. Default: `Small`. |
    | `hide_stereotype` | `boolean` \| `null` | Whether to hide stereotype labels in the legend. |

### ShowLegendSchema

Configuration for the SHOW_LEGEND macro in PlantUML.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `details` | `string` | Legend detail level. Default: `Small`. |
    | `hide_stereotype` | `boolean` \| `null` | Whether to hide stereotype labels in the legend. |

### ShowPersonSpriteSchema

Configuration for the SHOW_PERSON_SPRITE macro.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `alias` | `string` \| `null` | Optional sprite alias used for the person icon. |

### SystemBoundaryStyleSchema

Style update for system boundaries.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `SystemBoundaryStyle`. |
    | `bg_color` | `string` \| `null` | Background color. |
    | `border_color` | `string` \| `null` | Border line color. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the border line. |
    | **`element_name(required)`** | `string` | C4 element type to style (e.g. 'person', 'system', 'container'). This applies to all elements of the given type, not a specific instance. |
    | `font_color` | `string` \| `null` | Font/text color. |
    | `legend_sprite` | `string` \| `null` | Legend sprite for this styled element. |
    | `legend_text` | `string` \| `null` | Legend label for this styled element. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. |
    | `shape` | `string` \| `null` | Shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon applied to the element. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `technology` | `string` \| `null` | Technology label shown on the element. |

### SystemTagSchema

Tag for internal software systems.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `SystemTag`. |
    | `bg_color` | `string` \| `null` | Background color of the system element. |
    | `border_color` | `string` \| `null` | Border color of the system element. |
    | `border_style` | `string` \| `null` | Border line style macro. |
    | `border_thickness` | `string` \| `null` | Thickness of the system border line. |
    | `font_color` | `string` \| `null` | Font color used in system labels. |
    | `legend_sprite` | `string` \| `null` | Sprite displayed in the legend for this tag. |
    | `legend_text` | `string` \| `null` | Text shown in the diagram legend for this tag. |
    | `shadowing` | `boolean` \| `null` | Shadow style/toggle. Default: `false`. |
    | `shape` | `string` \| `null` | Optional shape macro used for rendering. |
    | `sprite` | `string` \| `null` | Sprite icon associated with the element or relationship. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | **`tag_stereo(required)`** | `string` | Stereotype name of the tag. Must match one of the tags declared in the `tags` field of a diagram component. |

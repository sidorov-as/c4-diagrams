# ContainerDiagram Spec

> **Source:** [container_diagram.json](../../../assets/specs/container_diagram.json)


This schema describes the [ContainerDiagram][c4.diagrams.container.ContainerDiagram] spec.

## Properties

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type of the diagram. Must be exactly `ContainerDiagram`. |
    | `title` | `string` \| `null` | Optional diagram title. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `layouts` | <code>array[<a href="#layoutschema">LayoutSchema</a>]</code> | Relative layout constraints between elements. |
    | `render_options` | <code><a href="#renderoptionsschema">RenderOptionsSchema</a></code> | Optional renderer-specific options |

??? abstract "Minimal example"

    ```json
    {
      "type": "ContainerDiagram",
      "title": "Web App",
      "elements": [
        {
          "alias": "user",
          "label": "User",
          "tags": [
            "User"
          ],
          "type": "Person"
        }
      ],
      "boundaries": [
        {
          "alias": "system",
          "boundaries": [],
          "elements": [
            {
              "alias": "web",
              "label": "Web App",
              "tags": [
                "Frontend"
              ],
              "technology": "React",
              "type": "Container"
            },
            {
              "alias": "api",
              "label": "API",
              "tags": [
                "Backend"
              ],
              "technology": "Python",
              "type": "Container"
            },
            {
              "alias": "db",
              "label": "Database",
              "tags": [
                "Database"
              ],
              "technology": "PostgreSQL",
              "type": "ContainerDb"
            }
          ],
          "label": "Simple System",
          "relationships": [],
          "tags": [
            "SystemBoundary"
          ],
          "type": "SystemBoundary"
        }
      ],
      "relationships": [
        {
          "from": "user",
          "label": "Uses",
          "tags": [
            "Sync"
          ],
          "to": "web",
          "type": "REL"
        },
        {
          "from": "web",
          "label": "Calls",
          "tags": [
            "Sync"
          ],
          "to": "api",
          "type": "REL"
        },
        {
          "from": "api",
          "label": "Reads/Writes",
          "tags": [
            "Data"
          ],
          "to": "db",
          "type": "REL"
        }
      ],
      "render_options": {
        "plantuml": {
          "layout": "LAYOUT_LEFT_RIGHT",
          "styles": [
            {
              "bg_color": "#eeeeff",
              "element_name": "container",
              "type": "ElementStyle"
            }
          ],
          "tags": [
            {
              "tag_stereo": "User",
              "type": "PersonTag"
            },
            {
              "tag_stereo": "Frontend",
              "type": "ContainerTag"
            },
            {
              "tag_stereo": "Backend",
              "type": "ContainerTag"
            },
            {
              "tag_stereo": "Database",
              "type": "ContainerTag"
            },
            {
              "tag_stereo": "SystemBoundary",
              "type": "BoundaryTag"
            },
            {
              "tag_stereo": "Sync",
              "type": "RelTag"
            },
            {
              "tag_stereo": "Data",
              "type": "RelTag"
            }
          ]
        }
      }
    }
    ```



??? abstract "Advanced example"

    ```json
    {
      "type": "ContainerDiagram",
      "title": "Online Shop - Container Diagram",
      "elements": [
        {
          "alias": "customer",
          "description": "Browses products and places orders.",
          "label": "Customer",
          "properties": {
            "properties": [
              [
                "Channel",
                "Web / Mobile"
              ]
            ]
          },
          "sprite": "user",
          "stereotype": "Primary User",
          "tags": [
            "Customer"
          ],
          "type": "Person"
        },
        {
          "alias": "support_agent",
          "description": "Investigates customer issues from an external support tool.",
          "label": "Support Agent",
          "properties": {
            "properties": [
              [
                "Organization",
                "Support Vendor"
              ]
            ]
          },
          "sprite": "user",
          "stereotype": "External User",
          "tags": [
            "ExternalSupport"
          ],
          "type": "PersonExt"
        },
        {
          "alias": "payment_provider",
          "description": "Processes card payments and payment webhooks.",
          "label": "Payment Provider",
          "sprite": "cloud",
          "stereotype": "External System",
          "tags": [
            "ExternalSystem"
          ],
          "type": "SystemExt"
        },
        {
          "alias": "recommendation_api",
          "description": "Returns personalized product recommendations.",
          "label": "Recommendation API",
          "sprite": "cloud",
          "tags": [
            "ExternalContainer"
          ],
          "technology": "REST API",
          "type": "ContainerExt"
        },
        {
          "alias": "fraud_db",
          "description": "External datastore containing fraud intelligence.",
          "label": "Fraud Signals DB",
          "sprite": "database",
          "tags": [
            "ExternalDataStore"
          ],
          "technology": "Vendor DB",
          "type": "ContainerDbExt"
        },
        {
          "alias": "shipping_events",
          "description": "External topic used by logistics partner.",
          "label": "Shipping Events Topic",
          "sprite": "queue",
          "tags": [
            "ExternalAsyncChannel"
          ],
          "technology": "Kafka",
          "type": "ContainerQueueExt"
        }
      ],
      "boundaries": [
        {
          "alias": "acme",
          "boundaries": [
            {
              "alias": "shop_boundary",
              "boundaries": [
                {
                  "alias": "checkout_boundary",
                  "boundaries": [],
                  "description": "Groups checkout-related containers.",
                  "elements": [
                    {
                      "alias": "checkout_api",
                      "description": "Handles checkout and payment orchestration.",
                      "label": "Checkout API",
                      "tags": [
                        "Backend"
                      ],
                      "technology": "Python / FastAPI",
                      "type": "Container"
                    },
                    {
                      "alias": "checkout_db",
                      "description": "Stores checkout sessions.",
                      "label": "Checkout DB",
                      "tags": [
                        "DataStore"
                      ],
                      "technology": "PostgreSQL",
                      "type": "ContainerDb"
                    }
                  ],
                  "label": "Checkout Subsystem",
                  "properties": {
                    "properties": [
                      [
                        "Owner",
                        "Checkout Team"
                      ],
                      [
                        "Criticality",
                        "High"
                      ]
                    ]
                  },
                  "relationships": [
                    {
                      "from": "checkout_api",
                      "label": "Reads and writes",
                      "tags": [
                        "DataAccess"
                      ],
                      "technology": "SQL",
                      "to": "checkout_db",
                      "type": "REL"
                    }
                  ],
                  "tags": [
                    "ContainerBoundary"
                  ],
                  "type": "ContainerBoundary"
                }
              ],
              "description": "Main system boundary for the commerce platform.",
              "elements": [
                {
                  "alias": "web_app",
                  "description": "Serves the storefront and checkout UI.",
                  "label": "Web Application",
                  "properties": {
                    "properties": [
                      [
                        "Runtime",
                        "Node.js"
                      ],
                      [
                        "Team",
                        "Storefront"
                      ]
                    ]
                  },
                  "sprite": "browser",
                  "tags": [
                    "Frontend"
                  ],
                  "technology": "React + Next.js",
                  "type": "Container"
                },
                {
                  "alias": "backend_api",
                  "description": "Handles catalog, carts, checkout, and order APIs.",
                  "label": "Backend API",
                  "properties": {
                    "properties": [
                      [
                        "Runtime",
                        "Python 3.12"
                      ],
                      [
                        "Team",
                        "Platform"
                      ]
                    ]
                  },
                  "sprite": "server",
                  "tags": [
                    "Backend",
                    "CoreRuntime"
                  ],
                  "technology": "Python / FastAPI",
                  "type": "Container"
                },
                {
                  "alias": "orders_db",
                  "description": "Stores orders, payments, and status transitions.",
                  "label": "Orders Database",
                  "properties": {
                    "properties": [
                      [
                        "Engine",
                        "PostgreSQL 16"
                      ],
                      [
                        "HA",
                        "Primary / Replica"
                      ]
                    ]
                  },
                  "sprite": "database",
                  "tags": [
                    "DataStore"
                  ],
                  "technology": "PostgreSQL",
                  "type": "ContainerDb"
                },
                {
                  "alias": "order_events",
                  "description": "Publishes asynchronous order lifecycle events.",
                  "label": "Order Events Queue",
                  "properties": {
                    "properties": [
                      [
                        "Retention",
                        "7 days"
                      ],
                      [
                        "Format",
                        "JSON"
                      ]
                    ]
                  },
                  "sprite": "queue",
                  "tags": [
                    "AsyncChannel"
                  ],
                  "technology": "Kafka",
                  "type": "ContainerQueue"
                }
              ],
              "label": "Online Shop Platform",
              "properties": {
                "properties": [
                  [
                    "Owner",
                    "Commerce Team"
                  ],
                  [
                    "Environment",
                    "Production"
                  ]
                ]
              },
              "relationships": [],
              "tags": [
                "SystemBoundary"
              ],
              "type": "SystemBoundary"
            }
          ],
          "description": "Enterprise boundary for internal platforms.",
          "elements": [],
          "label": "Acme Corp",
          "properties": {
            "properties": [
              [
                "Region",
                "EU"
              ],
              [
                "Business Unit",
                "Digital Commerce"
              ]
            ]
          },
          "relationships": [],
          "tags": [
            "EnterpriseBoundary"
          ],
          "type": "EnterpriseBoundary"
        }
      ],
      "relationships": [
        {
          "from": "customer",
          "label": "Uses",
          "tags": [
            "SyncRequest"
          ],
          "technology": "HTTPS",
          "to": "web_app",
          "type": "REL"
        },
        {
          "from": "web_app",
          "label": "Calls",
          "tags": [
            "SyncRequest"
          ],
          "technology": "HTTPS/JSON",
          "to": "backend_api",
          "type": "REL"
        },
        {
          "from": "backend_api",
          "label": "Reads and writes",
          "tags": [
            "DataAccess"
          ],
          "technology": "SQL",
          "to": "orders_db",
          "type": "REL"
        },
        {
          "from": "backend_api",
          "label": "Publishes order events",
          "tags": [
            "AsyncRequest"
          ],
          "technology": "Kafka",
          "to": "order_events",
          "type": "REL"
        },
        {
          "from": "backend_api",
          "label": "Creates payment intents",
          "tags": [
            "ExternalCall"
          ],
          "technology": "REST API",
          "to": "payment_provider",
          "type": "REL"
        },
        {
          "from": "backend_api",
          "label": "Fetches recommendations",
          "tags": [
            "ExternalCall"
          ],
          "technology": "REST API",
          "to": "recommendation_api",
          "type": "REL"
        },
        {
          "from": "backend_api",
          "label": "Checks fraud signals",
          "tags": [
            "ExternalCall"
          ],
          "technology": "JDBC",
          "to": "fraud_db",
          "type": "REL"
        },
        {
          "from": "shipping_events",
          "label": "Delivers shipping updates",
          "tags": [
            "AsyncRequest"
          ],
          "technology": "Kafka",
          "to": "backend_api",
          "type": "REL"
        },
        {
          "from": "support_agent",
          "label": "Queries order state",
          "tags": [
            "SupportFlow"
          ],
          "technology": "HTTPS",
          "to": "backend_api",
          "type": "REL"
        }
      ],
      "layouts": [
        {
          "from": "customer",
          "to": "web_app",
          "type": "LAY_R"
        },
        {
          "from": "web_app",
          "to": "backend_api",
          "type": "LAY_R"
        },
        {
          "from": "backend_api",
          "to": "orders_db",
          "type": "LAY_D"
        },
        {
          "from": "backend_api",
          "to": "order_events",
          "type": "LAY_D"
        },
        {
          "from": "backend_api",
          "to": "payment_provider",
          "type": "LAY_R"
        }
      ],
      "render_options": {
        "plantuml": {
          "hide_person_sprite": false,
          "hide_stereotype": false,
          "layout": "LAYOUT_LEFT_RIGHT",
          "layout_as_sketch": false,
          "layout_with_legend": true,
          "legend_title": "Container Diagram Legend",
          "set_sketch_style": {
            "bg_color": "#ffffff",
            "font_color": "#222222",
            "font_name": "Inter",
            "footer_text": "Container view",
            "footer_warning": "Architecture draft",
            "warning_color": "#cc3300"
          },
          "show_floating_legend": {
            "alias": "legend_box",
            "details": "Small",
            "hide_stereotype": true
          },
          "show_legend": {
            "details": "Normal",
            "hide_stereotype": false
          },
          "show_person_outline": true,
          "show_person_portrait": false,
          "show_person_sprite": {
            "alias": "person"
          },
          "styles": [
            {
              "bg_color": "#ede7f6",
              "border_color": "#673ab7",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "element_name": "container",
              "font_color": "#311b92",
              "legend_sprite": "server",
              "legend_text": "Application container",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "type": "ElementStyle"
            },
            {
              "bg_color": "#fff8e1",
              "border_color": "#ffb300",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "element_name": "systemboundary",
              "font_color": "#5d4037",
              "legend_text": "System boundary",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "type": "SystemBoundaryStyle"
            },
            {
              "bg_color": "#f1f8e9",
              "border_color": "#8bc34a",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "element_name": "containerboundary",
              "font_color": "#33691e",
              "legend_text": "Container boundary",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "type": "ContainerBoundaryStyle"
            },
            {
              "line_color": "#546e7a",
              "text_color": "#37474f",
              "type": "RelStyle"
            }
          ],
          "tags": [
            {
              "bg_color": "#e8f5e9",
              "border_color": "#66bb6a",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#1b5e20",
              "legend_sprite": "user",
              "legend_text": "Primary customer actor",
              "shadowing": false,
              "sprite": "user",
              "tag_stereo": "Customer",
              "type": "PersonTag"
            },
            {
              "bg_color": "#f5f5f5",
              "border_color": "#9e9e9e",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "font_color": "#424242",
              "legend_sprite": "user",
              "legend_text": "External support user",
              "shadowing": false,
              "sprite": "user",
              "tag_stereo": "ExternalSupport",
              "type": "ExternalPersonTag"
            },
            {
              "bg_color": "#f5f5f5",
              "border_color": "#9e9e9e",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "font_color": "#424242",
              "legend_sprite": "cloud",
              "legend_text": "External system dependency",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "sprite": "cloud",
              "tag_stereo": "ExternalSystem",
              "type": "ExternalSystemTag"
            },
            {
              "bg_color": "#e3f2fd",
              "border_color": "#64b5f6",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#0d47a1",
              "legend_sprite": "browser",
              "legend_text": "User-facing frontend container",
              "shadowing": true,
              "sprite": "browser",
              "tag_stereo": "Frontend",
              "technology": "Web UI",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#ede7f6",
              "border_color": "#673ab7",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#311b92",
              "legend_sprite": "server",
              "legend_text": "Backend application container",
              "shadowing": true,
              "sprite": "server",
              "tag_stereo": "Backend",
              "technology": "Python / FastAPI",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#ede7f6",
              "border_color": "#7e57c2",
              "border_style": "BoldLine",
              "border_thickness": "2",
              "font_color": "#4527a0",
              "legend_sprite": "server",
              "legend_text": "Core runtime container",
              "shadowing": true,
              "sprite": "server",
              "tag_stereo": "CoreRuntime",
              "technology": "Python 3.12",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#fff8e1",
              "border_color": "#ffb300",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#5d4037",
              "legend_sprite": "database",
              "legend_text": "Internal data store",
              "shadowing": false,
              "sprite": "database",
              "tag_stereo": "DataStore",
              "technology": "PostgreSQL",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#fff3e0",
              "border_color": "#fb8c00",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#e65100",
              "legend_sprite": "queue",
              "legend_text": "Internal asynchronous channel",
              "shadowing": false,
              "sprite": "queue",
              "tag_stereo": "AsyncChannel",
              "technology": "Kafka",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#f5f5f5",
              "border_color": "#9e9e9e",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "font_color": "#424242",
              "legend_sprite": "cloud",
              "legend_text": "External container dependency",
              "shadowing": false,
              "shape": "RoundedBoxShape",
              "sprite": "cloud",
              "tag_stereo": "ExternalContainer",
              "technology": "REST API",
              "type": "ExternalContainerTag"
            },
            {
              "bg_color": "#f5f5f5",
              "border_color": "#9e9e9e",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "font_color": "#424242",
              "legend_sprite": "database",
              "legend_text": "External data store",
              "shadowing": false,
              "sprite": "database",
              "tag_stereo": "ExternalDataStore",
              "technology": "Vendor DB",
              "type": "ExternalContainerTag"
            },
            {
              "bg_color": "#f3e5f5",
              "border_color": "#ab47bc",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "font_color": "#6a1b9a",
              "legend_sprite": "queue",
              "legend_text": "External asynchronous channel",
              "shadowing": false,
              "sprite": "queue",
              "tag_stereo": "ExternalAsyncChannel",
              "technology": "Kafka",
              "type": "ExternalContainerTag"
            },
            {
              "bg_color": "#fafafa",
              "border_color": "#9e9e9e",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#424242",
              "legend_text": "Enterprise boundary",
              "shadowing": false,
              "tag_stereo": "EnterpriseBoundary",
              "type": "BoundaryTag"
            },
            {
              "bg_color": "#fff8e1",
              "border_color": "#ffb300",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#5d4037",
              "legend_text": "System boundary",
              "shadowing": false,
              "tag_stereo": "SystemBoundary",
              "type": "BoundaryTag"
            },
            {
              "bg_color": "#f1f8e9",
              "border_color": "#8bc34a",
              "border_style": "DashedLine",
              "border_thickness": "1",
              "font_color": "#33691e",
              "legend_text": "Container boundary",
              "shadowing": false,
              "tag_stereo": "ContainerBoundary",
              "type": "BoundaryTag"
            },
            {
              "legend_text": "Synchronous request/response flow",
              "line_color": "#1e88e5",
              "line_style": "SolidLine",
              "line_thickness": "1",
              "tag_stereo": "SyncRequest",
              "technology": "HTTPS/JSON",
              "text_color": "#1565c0",
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
              "legend_text": "Asynchronous messaging flow",
              "line_color": "#8e24aa",
              "line_style": "DottedLine",
              "line_thickness": "2",
              "sprite": "queue",
              "tag_stereo": "AsyncRequest",
              "technology": "Kafka",
              "text_color": "#6a1b9a",
              "type": "RelTag"
            },
            {
              "legend_text": "External service/data call",
              "line_color": "#78909c",
              "line_style": "DashedLine",
              "line_thickness": "1",
              "tag_stereo": "ExternalCall",
              "technology": "REST API / JDBC",
              "text_color": "#455a64",
              "type": "RelTag"
            },
            {
              "legend_text": "Support access flow",
              "line_color": "#43a047",
              "line_style": "SolidLine",
              "line_thickness": "1",
              "tag_stereo": "SupportFlow",
              "technology": "HTTPS",
              "text_color": "#2e7d32",
              "type": "RelTag"
            }
          ],
          "without_property_header": false
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

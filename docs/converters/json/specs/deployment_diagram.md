# DeploymentDiagram Spec

> **Source:** [deployment_diagram.json](../../../assets/specs/deployment_diagram.json)


This schema describes the [DeploymentDiagram][c4.diagrams.deployment.DeploymentDiagram] spec.

## Properties

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type of the diagram. Must be exactly `DeploymentDiagram`. |
    | `title` | `string` \| `null` | Optional diagram title. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `layouts` | <code>array[<a href="#layoutschema">LayoutSchema</a>]</code> | Relative layout constraints between elements. |
    | `render_options` | <code><a href="#renderoptionsschema">RenderOptionsSchema</a></code> | Optional renderer-specific options |

??? abstract "Minimal example"

    ```json
    {
      "type": "DeploymentDiagram",
      "title": "Web App Deployment",
      "elements": [
        {
          "alias": "user",
          "description": "Uses the web application.",
          "label": "User",
          "tags": [
            "person"
          ],
          "type": "Person"
        }
      ],
      "boundaries": [
        {
          "alias": "web_node",
          "boundaries": [],
          "description": "Hosts the frontend application.",
          "elements": [
            {
              "alias": "web_app",
              "description": "Customer-facing web application.",
              "label": "Web App",
              "tags": [
                "frontend"
              ],
              "technology": "Next.js",
              "type": "Container"
            }
          ],
          "label": "Web Server",
          "relationships": [],
          "sprite": "server",
          "stereotype": "Compute Node",
          "tags": [
            "runtime_node"
          ],
          "type": "DeploymentNodeLeft"
        },
        {
          "alias": "db_node",
          "boundaries": [],
          "description": "Hosts the application database.",
          "elements": [
            {
              "alias": "app_db",
              "description": "Stores application data.",
              "label": "App Database",
              "tags": [
                "database"
              ],
              "technology": "PostgreSQL",
              "type": "ContainerDb"
            }
          ],
          "label": "Database Server",
          "relationships": [],
          "sprite": "database",
          "stereotype": "Data Node",
          "tags": [
            "data_node"
          ],
          "type": "DeploymentNodeRight"
        }
      ],
      "relationships": [
        {
          "from": "user",
          "label": "Uses",
          "tags": [
            "encrypted_traffic"
          ],
          "technology": "HTTPS",
          "to": "web_node",
          "type": "REL"
        },
        {
          "from": "web_node",
          "label": "Reads and writes",
          "tags": [
            "encrypted_traffic"
          ],
          "technology": "TLS / SQL",
          "to": "db_node",
          "type": "REL"
        }
      ],
      "layouts": [
        {
          "from": "user",
          "to": "web_node",
          "type": "LAY_R"
        },
        {
          "from": "web_node",
          "to": "db_node",
          "type": "LAY_R"
        }
      ],
      "render_options": {
        "plantuml": {
          "layout": "LAYOUT_LEFT_RIGHT",
          "tags": [
            {
              "legend_text": "End user",
              "sprite": "user",
              "tag_stereo": "person",
              "type": "PersonTag"
            },
            {
              "legend_text": "Frontend container",
              "sprite": "browser",
              "tag_stereo": "frontend",
              "type": "ContainerTag"
            },
            {
              "legend_text": "Database container",
              "sprite": "database",
              "tag_stereo": "database",
              "type": "ContainerTag"
            },
            {
              "legend_text": "Runtime deployment node",
              "shape": "RoundedBoxShape",
              "sprite": "server",
              "tag_stereo": "runtime_node",
              "technology": "Runtime",
              "type": "NodeTag"
            },
            {
              "legend_text": "Data deployment node",
              "shape": "RoundedBoxShape",
              "sprite": "database",
              "tag_stereo": "data_node",
              "technology": "Data",
              "type": "NodeTag"
            },
            {
              "legend_text": "Encrypted communication",
              "sprite": "lock",
              "tag_stereo": "encrypted_traffic",
              "technology": "TLS",
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
      "type": "DeploymentDiagram",
      "title": "Online Shop - Production Deployment",
      "elements": [
        {
          "alias": "customer",
          "description": "Uses the online shop through a browser.",
          "label": "Customer",
          "tags": [
            "person"
          ],
          "type": "Person"
        },
        {
          "alias": "payment_gateway",
          "description": "External service that processes card payments.",
          "label": "Payment Gateway",
          "tags": [
            "external_service"
          ],
          "technology": "HTTPS API",
          "type": "ContainerExt"
        }
      ],
      "boundaries": [
        {
          "alias": "aws_prod",
          "boundaries": [
            {
              "alias": "public_subnet",
              "boundaries": [
                {
                  "alias": "alb",
                  "boundaries": [],
                  "description": "Terminates TLS and routes requests to the web tier.",
                  "elements": [
                    {
                      "alias": "web_app",
                      "description": "Serves the storefront UI.",
                      "label": "Web Application",
                      "tags": [
                        "frontend"
                      ],
                      "technology": "Next.js",
                      "type": "Container"
                    }
                  ],
                  "label": "Application Load Balancer",
                  "relationships": [],
                  "sprite": "router",
                  "stereotype": "Ingress",
                  "tags": [
                    "edge_node"
                  ],
                  "type": "DeploymentNodeLeft"
                }
              ],
              "description": "Internet-facing network segment.",
              "elements": [],
              "label": "Public Subnet",
              "relationships": [],
              "sprite": "network",
              "stereotype": "Network Segment",
              "tags": [
                "public_network"
              ],
              "type": "NodeLeft"
            },
            {
              "alias": "private_subnet",
              "boundaries": [
                {
                  "alias": "app_cluster",
                  "boundaries": [],
                  "description": "Runs backend services and asynchronous workers.",
                  "elements": [
                    {
                      "alias": "backend_api",
                      "description": "Handles catalog, checkout, and order processing.",
                      "label": "Backend API",
                      "tags": [
                        "backend"
                      ],
                      "technology": "Python / FastAPI",
                      "type": "Container"
                    },
                    {
                      "alias": "order_events",
                      "description": "Internal asynchronous event stream.",
                      "label": "Order Events",
                      "tags": [
                        "message_bus"
                      ],
                      "technology": "Kafka",
                      "type": "ContainerQueue"
                    }
                  ],
                  "label": "Kubernetes Cluster",
                  "properties": {
                    "properties": [
                      [
                        "Platform",
                        "EKS"
                      ],
                      [
                        "Autoscaling",
                        "Enabled"
                      ]
                    ]
                  },
                  "relationships": [],
                  "sprite": "server",
                  "stereotype": "Runtime Environment",
                  "tags": [
                    "runtime_node"
                  ],
                  "type": "DeploymentNode"
                },
                {
                  "alias": "db_service",
                  "boundaries": [],
                  "description": "Managed relational database service.",
                  "elements": [
                    {
                      "alias": "orders_db",
                      "description": "Stores orders, payments, and fulfillment data.",
                      "label": "Orders Database",
                      "tags": [
                        "database"
                      ],
                      "technology": "PostgreSQL",
                      "type": "ContainerDb"
                    }
                  ],
                  "label": "Managed PostgreSQL",
                  "properties": {
                    "properties": [
                      [
                        "Service",
                        "RDS"
                      ],
                      [
                        "Mode",
                        "Multi-AZ"
                      ]
                    ]
                  },
                  "relationships": [],
                  "sprite": "database",
                  "stereotype": "Data Platform",
                  "tags": [
                    "data_node"
                  ],
                  "type": "DeploymentNodeRight"
                }
              ],
              "description": "Internal network segment for application and data services.",
              "elements": [],
              "label": "Private Subnet",
              "relationships": [],
              "sprite": "network",
              "stereotype": "Network Segment",
              "tags": [
                "private_network"
              ],
              "type": "NodeRight"
            }
          ],
          "description": "Production cloud account for the online shop.",
          "elements": [],
          "label": "AWS Production Account",
          "properties": {
            "properties": [
              [
                "Environment",
                "Production"
              ],
              [
                "Region",
                "eu-central-1"
              ]
            ]
          },
          "relationships": [],
          "sprite": "cloud",
          "stereotype": "Cloud Account",
          "tags": [
            "cloud_account"
          ],
          "type": "Node"
        }
      ],
      "relationships": [
        {
          "from": "customer",
          "label": "Uses",
          "tags": [
            "encrypted_traffic"
          ],
          "technology": "HTTPS",
          "to": "alb",
          "type": "REL"
        },
        {
          "from": "alb",
          "label": "Routes traffic to",
          "tags": [
            "encrypted_traffic"
          ],
          "technology": "HTTPS",
          "to": "app_cluster",
          "type": "REL"
        },
        {
          "from": "app_cluster",
          "label": "Reads and writes",
          "tags": [
            "encrypted_traffic"
          ],
          "technology": "TLS / SQL",
          "to": "db_service",
          "type": "REL"
        },
        {
          "from": "app_cluster",
          "label": "Calls",
          "tags": [
            "encrypted_traffic"
          ],
          "technology": "HTTPS/JSON",
          "to": "payment_gateway",
          "type": "REL"
        },
        {
          "from": "backend_api",
          "label": "Publishes events to",
          "tags": [
            "async_flow"
          ],
          "technology": "Kafka",
          "to": "order_events",
          "type": "REL"
        }
      ],
      "layouts": [
        {
          "from": "customer",
          "to": "alb",
          "type": "LAY_R"
        },
        {
          "from": "alb",
          "to": "app_cluster",
          "type": "LAY_R"
        },
        {
          "from": "app_cluster",
          "to": "db_service",
          "type": "LAY_D"
        },
        {
          "from": "app_cluster",
          "to": "payment_gateway",
          "type": "LAY_R"
        }
      ],
      "render_options": {
        "plantuml": {
          "hide_person_sprite": false,
          "hide_stereotype": false,
          "layout": "LAYOUT_LEFT_RIGHT",
          "layout_with_legend": true,
          "legend_title": "Deployment Legend",
          "show_legend": {
            "details": "Normal",
            "hide_stereotype": false
          },
          "show_person_outline": true,
          "show_person_sprite": {
            "alias": "person"
          },
          "styles": [
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
              "border_thickness": "2",
              "font_color": "#1b5e20",
              "legend_text": "End user",
              "sprite": "user",
              "tag_stereo": "person",
              "type": "PersonTag"
            },
            {
              "bg_color": "#f3e5f5",
              "border_color": "#ab47bc",
              "border_style": "DashedLine",
              "border_thickness": "2",
              "font_color": "#4a148c",
              "legend_text": "External service",
              "sprite": "cloud",
              "tag_stereo": "external_service",
              "type": "ExternalContainerTag"
            },
            {
              "bg_color": "#e3f2fd",
              "border_color": "#42a5f5",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#0d47a1",
              "legend_text": "Frontend container",
              "sprite": "browser",
              "tag_stereo": "frontend",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#ede7f6",
              "border_color": "#7e57c2",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#311b92",
              "legend_text": "Backend container",
              "sprite": "server",
              "tag_stereo": "backend",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#fff3e0",
              "border_color": "#fb8c00",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#e65100",
              "legend_text": "Database container",
              "sprite": "database",
              "tag_stereo": "database",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#fce4ec",
              "border_color": "#ec407a",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#880e4f",
              "legend_text": "Message queue / stream",
              "sprite": "queue",
              "tag_stereo": "message_bus",
              "type": "ContainerTag"
            },
            {
              "bg_color": "#eef6ff",
              "border_color": "#64b5f6",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#0d47a1",
              "legend_sprite": "cloud",
              "legend_text": "Cloud account boundary",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "sprite": "cloud",
              "tag_stereo": "cloud_account",
              "technology": "Infrastructure",
              "type": "NodeTag"
            },
            {
              "bg_color": "#f1f8e9",
              "border_color": "#8bc34a",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#33691e",
              "legend_sprite": "network",
              "legend_text": "Public network zone",
              "shape": "RoundedBoxShape",
              "sprite": "network",
              "tag_stereo": "public_network",
              "technology": "DMZ",
              "type": "NodeTag"
            },
            {
              "bg_color": "#fbe9e7",
              "border_color": "#ff8a65",
              "border_style": "SolidLine",
              "border_thickness": "1",
              "font_color": "#bf360c",
              "legend_sprite": "network",
              "legend_text": "Private network zone",
              "shape": "RoundedBoxShape",
              "sprite": "network",
              "tag_stereo": "private_network",
              "technology": "Internal",
              "type": "NodeTag"
            },
            {
              "bg_color": "#e1f5fe",
              "border_color": "#29b6f6",
              "border_style": "BoldLine",
              "border_thickness": "2",
              "font_color": "#01579b",
              "legend_sprite": "router",
              "legend_text": "Ingress deployment node",
              "shape": "RoundedBoxShape",
              "sprite": "router",
              "tag_stereo": "edge_node",
              "technology": "Ingress",
              "type": "NodeTag"
            },
            {
              "bg_color": "#e8f5e9",
              "border_color": "#66bb6a",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#1b5e20",
              "legend_sprite": "server",
              "legend_text": "Runtime deployment node",
              "shadowing": true,
              "shape": "RoundedBoxShape",
              "sprite": "server",
              "tag_stereo": "runtime_node",
              "technology": "Runtime",
              "type": "NodeTag"
            },
            {
              "bg_color": "#fff8e1",
              "border_color": "#ffb300",
              "border_style": "SolidLine",
              "border_thickness": "2",
              "font_color": "#ff6f00",
              "legend_sprite": "database",
              "legend_text": "Data deployment node",
              "shape": "RoundedBoxShape",
              "sprite": "database",
              "tag_stereo": "data_node",
              "technology": "Data Platform",
              "type": "NodeTag"
            },
            {
              "legend_sprite": "lock",
              "legend_text": "Encrypted communication",
              "line_color": "#1976d2",
              "line_style": "SolidLine",
              "line_thickness": "2",
              "sprite": "lock",
              "tag_stereo": "encrypted_traffic",
              "technology": "TLS",
              "text_color": "#0d47a1",
              "type": "RelTag"
            },
            {
              "legend_sprite": "queue",
              "legend_text": "Asynchronous event flow",
              "line_color": "#8e24aa",
              "line_style": "DashedLine",
              "line_thickness": "2",
              "sprite": "queue",
              "tag_stereo": "async_flow",
              "technology": "Kafka",
              "text_color": "#4a148c",
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

### Boundaries

- [NodeSchema](#nodeschema)
- [NodeLeftSchema](#nodeleftschema)
- [NodeRightSchema](#noderightschema)
- [DeploymentNodeSchema](#deploymentnodeschema)
- [DeploymentNodeLeftSchema](#deploymentnodeleftschema)
- [DeploymentNodeRightSchema](#deploymentnoderightschema)

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

### DeploymentNodeLeftSchema

This schema describes the
[`DeploymentNodeLeft`][c4.diagrams.deployment.DeploymentNodeLeft]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `DeploymentNodeLeft`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite name to visually represent the node. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### DeploymentNodeRightSchema

This schema describes the
[`DeploymentNodeRight`][c4.diagrams.deployment.DeploymentNodeRight]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `DeploymentNodeRight`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite name to visually represent the node. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### DeploymentNodeSchema

This schema describes the
[`DeploymentNode`][c4.diagrams.deployment.DeploymentNode]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `DeploymentNode`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite name to visually represent the node. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### DiagramElementPropertiesSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `header` | <code>array[string]</code> | Header columns. Default: `["Property", "Value"]`. |
    | **`properties(required)`** | <code>array[array[string]]</code> | List of rows (each row is a list of string values). |
    | `show_header` | `boolean` | Whether to display the header row. Default: `true`. |

### LayoutSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | <code><a href="#layouttype">LayoutType</a></code> | Type of the layout. |
    | **`from(required)`** | `string` | The source element alias (or unique label). |
    | **`to(required)`** | `string` | The destination element alias (or unique label). |

### NodeLeftSchema

This schema describes the
[`NodeLeft`][c4.diagrams.deployment.NodeLeft]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `NodeLeft`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite name to visually represent the node. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### NodeRightSchema

This schema describes the
[`NodeRight`][c4.diagrams.deployment.NodeRight]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `NodeRight`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite name to visually represent the node. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

### NodeSchema

This schema describes the
[`Node`][c4.diagrams.deployment.Node]
diagram component.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Discriminator identifying the element type. Must be exactly `Node`. |
    | `elements` | <code>array[<a href="#elements">Element</a>]</code> | Top-level elements. |
    | `boundaries` | <code>array[<a href="#boundaries">Boundary</a>]</code> | Top-level boundaries. |
    | `relationships` | <code>array[<a href="#relationshipschema">RelationshipSchema</a>]</code> | Top-level relationships. |
    | `alias` | `string` \| `null` | Unique identifier for the element. If not provided, it is autogenerated from the label. |
    | `description` | `string` \| `null` | Optional description text. |
    | **`label(required)`** | `string` | Display name for the element. |
    | `link` | `string` \| `null` | Optional URL associated with the element. |
    | `properties` | <code><a href="#diagramelementpropertiesschema">DiagramElementPropertiesSchema</a></code> | Optional property table metadata. |
    | `sprite` | `string` \| `null` | Optional sprite name to visually represent the node. |
    | `stereotype` | `string` \| `null` | Optional custom type/stereotype label. |
    | `tags` | <code>array[string]</code> | Optional tags for grouping/styling. These tags can be referenced by `tag_stereo` in tag definitions. |

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

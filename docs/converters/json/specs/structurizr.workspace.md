# Structurizr Workspace Spec

> **Source:** [structurizr.workspace.json](../../../assets/specs/structurizr.workspace.json)


This schema describes the `Workspace` workspace spec for the Structurizr backend.

## Properties

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `render_options` | <code><a href="#structurizrrenderoptionsschema">StructurizrRenderOptionsSchema</a></code> |  |
    | **`backend(required)`** | `string` | Required discriminator for the Structurizr workspace JSON format. Must be exactly `structurizr`. |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`model(required)`** | <code><a href="#structurizrmodelschema">StructurizrModelSchema</a></code> |  |
    | `name` | `string` | Workspace name; defaults to the renderer's Workspace fallback. Default: `Workspace`. |
    | `properties` | `object` | Properties |
    | `styles` | <code><a href="#structurizrstylesschema">StructurizrStylesSchema</a></code> |  |
    | `theme` | <span style="white-space: nowrap;">`string` \| `null`</span> | Theme |
    | **`views(required)`** | <code><a href="#structurizrviewsschema">StructurizrViewsSchema</a></code> |  |

??? abstract "Examples"

    === "Minimal"

        ??? example "JSON source"

            ```json
            --8<-- "assets/examples/json/structurizr/workspace.minimal.json"
            ```

        ??? example "Rendered Structurizr DSL source"

            ```dsl
            --8<-- "assets/examples/structurizr/workspace.minimal.dsl"
            ```


    === "Advanced"

        ??? example "JSON source"

            ```json
            --8<-- "assets/examples/json/structurizr/workspace.advanced.json"
            ```

        ??? example "Rendered Structurizr DSL source"

            ```dsl
            --8<-- "assets/examples/structurizr/workspace.advanced.dsl"
            ```


## Definitions


### StructurizrModelSchema

The workspace model inventory.

Ownership is encoded structurally: containers belong to systems, components
belong to containers, and deployment content belongs to environments/nodes.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `relationships` | <code>array[<a href="#structurizrrelationshipschema">StructurizrRelationshipSchema</a>]</code> | Relationships |
    | `deployment` | <code><a href="#structurizrdeploymentschema">StructurizrDeploymentSchema</a></code> |  |
    | `people` | <code>array[<a href="#structurizrpersonschema">StructurizrPersonSchema</a>]</code> | People |
    | `software_systems` | <code>array[<a href="#structurizrsoftwaresystemschema">StructurizrSoftwareSystemSchema</a>]</code> | Software Systems |
### StructurizrPersonSchema

A root person in the workspace model.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`id(required)`** | `string` | Id |
    | **`name(required)`** | `string` | Name |
    | `properties` | `object` | Properties |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrSoftwareSystemSchema

A root software system and its explicitly owned containers.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `containers` | <code>array[<a href="#structurizrcontainerschema">StructurizrContainerSchema</a>]</code> | Containers |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`id(required)`** | `string` | Id |
    | **`name(required)`** | `string` | Name |
    | `properties` | `object` | Properties |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrContainerSchema

A container owned by its containing software system.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `components` | <code>array[<a href="#structurizrcomponentschema">StructurizrComponentSchema</a>]</code> | Components |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`id(required)`** | `string` | Id |
    | **`name(required)`** | `string` | Name |
    | `properties` | `object` | Properties |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `technology` | <span style="white-space: nowrap;">`string` \| `null`</span> | Technology |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrComponentSchema

A component owned by its containing container.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`id(required)`** | `string` | Id |
    | **`name(required)`** | `string` | Name |
    | `properties` | `object` | Properties |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `technology` | <span style="white-space: nowrap;">`string` \| `null`</span> | Technology |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrRelationshipSchema

A model-level relationship using c4-diagrams ``from``/``to`` spelling.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`from(required)`** | `string` | From |
    | `properties` | `object` | Properties |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `technology` | <span style="white-space: nowrap;">`string` \| `null`</span> | Technology |
    | **`to(required)`** | `string` | To |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrDeploymentSchema

Deployment environments and their explicitly owned node trees.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `environments` | <code>array[<a href="#structurizrdeploymentenvironmentschema">StructurizrDeploymentEnvironmentSchema</a>]</code> | Environments |
### StructurizrDeploymentEnvironmentSchema

A named deployment environment containing its root deployment nodes.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `deployment_nodes` | <code>array[<a href="#structurizrdeploymentnodeschema">StructurizrDeploymentNodeSchema</a>]</code> | Deployment Nodes |
    | **`name(required)`** | `string` | Name |
### StructurizrDeploymentNodeSchema

A deployment node with explicitly nested nodes and instances.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `container_instances` | <code>array[<a href="#structurizrcontainerinstanceschema">StructurizrContainerInstanceSchema</a>]</code> | Container Instances |
    | `deployment_nodes` | <code>array[<a href="#structurizrdeploymentnodeschema">StructurizrDeploymentNodeSchema</a>]</code> | Deployment Nodes |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`id(required)`** | `string` | Id |
    | `infrastructure_nodes` | <code>array[<a href="#structurizrinfrastructurenodeschema">StructurizrInfrastructureNodeSchema</a>]</code> | Infrastructure Nodes |
    | **`name(required)`** | `string` | Name |
    | `properties` | `object` | Properties |
    | `software_system_instances` | <code>array[<a href="#structurizrsoftwaresysteminstanceschema">StructurizrSoftwareSystemInstanceSchema</a>]</code> | Software System Instances |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `technology` | <span style="white-space: nowrap;">`string` \| `null`</span> | Technology |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrInfrastructureNodeSchema

Infrastructure nested below a deployment or infrastructure node.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `deployment_nodes` | <code>array[<a href="#structurizrdeploymentnodeschema">StructurizrDeploymentNodeSchema</a>]</code> | Deployment Nodes |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`id(required)`** | `string` | Id |
    | `infrastructure_nodes` | <code>array[<a href="#structurizrinfrastructurenodeschema">StructurizrInfrastructureNodeSchema</a>]</code> | Infrastructure Nodes |
    | **`name(required)`** | `string` | Name |
    | `properties` | `object` | Properties |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `technology` | <span style="white-space: nowrap;">`string` \| `null`</span> | Technology |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrSoftwareSystemInstanceSchema

A software-system instance and the model element it represents.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`id(required)`** | `string` | Id |
    | `properties` | <span style="white-space: nowrap;">`object` \| `null`</span> | Properties |
    | **`software_system(required)`** | `string` | Software System |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrContainerInstanceSchema

A container instance and the model element it represents.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`container(required)`** | `string` | Container |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`id(required)`** | `string` | Id |
    | `properties` | <span style="white-space: nowrap;">`object` \| `null`</span> | Properties |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrViewsSchema

Declared Structurizr views in authoring order.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `items` | <code>array[<br/>&nbsp;<code><a href="#structurizrsystemlandscapeviewschema">StructurizrSystemLandscapeViewSchema</a></code><br/>&nbsp;\|<code><a href="#structurizrsystemcontextviewschema">StructurizrSystemContextViewSchema</a></code><br/>&nbsp;\|<code><a href="#structurizrcontainerviewschema">StructurizrContainerViewSchema</a></code><br/>&nbsp;\|<code><a href="#structurizrcomponentviewschema">StructurizrComponentViewSchema</a></code><br/>&nbsp;\|<code><a href="#structurizrdynamicviewschema">StructurizrDynamicViewSchema</a></code><br/>&nbsp;\|<code><a href="#structurizrdeploymentviewschema">StructurizrDeploymentViewSchema</a></code><br/>]</code> | Items |
### StructurizrSystemLandscapeViewSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type Must be exactly `system_landscape`. |
    | `title` | <span style="white-space: nowrap;">`string` \| `null`</span> | Title |
    | `animation` | <code>array</code> | Animation |
    | `auto_layout` | <code><a href="#structurizrautolayoutschema">StructurizrAutoLayoutSchema</a></code> |  |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | `exclude` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Exclude |
    | `include` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Include |
    | `key` | <span style="white-space: nowrap;">`string` \| `null`</span> | Key |
    | `properties` | `object` | Properties |
    | `tags` | <code>array[string]</code> | Tags |
### StructurizrSystemContextViewSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type Must be exactly `system_context`. |
    | `title` | <span style="white-space: nowrap;">`string` \| `null`</span> | Title |
    | `animation` | <code>array</code> | Animation |
    | `auto_layout` | <code><a href="#structurizrautolayoutschema">StructurizrAutoLayoutSchema</a></code> |  |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | `exclude` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Exclude |
    | `include` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Include |
    | `key` | <span style="white-space: nowrap;">`string` \| `null`</span> | Key |
    | `properties` | `object` | Properties |
    | **`scope(required)`** | `string` | Scope |
    | `tags` | <code>array[string]</code> | Tags |
### StructurizrContainerViewSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type Must be exactly `container`. |
    | `title` | <span style="white-space: nowrap;">`string` \| `null`</span> | Title |
    | `animation` | <code>array</code> | Animation |
    | `auto_layout` | <code><a href="#structurizrautolayoutschema">StructurizrAutoLayoutSchema</a></code> |  |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | `exclude` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Exclude |
    | `include` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Include |
    | `key` | <span style="white-space: nowrap;">`string` \| `null`</span> | Key |
    | `properties` | `object` | Properties |
    | **`scope(required)`** | `string` | Scope |
    | `tags` | <code>array[string]</code> | Tags |
### StructurizrComponentViewSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type Must be exactly `component`. |
    | `title` | <span style="white-space: nowrap;">`string` \| `null`</span> | Title |
    | `animation` | <code>array</code> | Animation |
    | `auto_layout` | <code><a href="#structurizrautolayoutschema">StructurizrAutoLayoutSchema</a></code> |  |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | `exclude` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Exclude |
    | `include` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Include |
    | `key` | <span style="white-space: nowrap;">`string` \| `null`</span> | Key |
    | `properties` | `object` | Properties |
    | **`scope(required)`** | `string` | Scope |
    | `tags` | <code>array[string]</code> | Tags |
### StructurizrDynamicViewSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type Must be exactly `dynamic`. |
    | `title` | <span style="white-space: nowrap;">`string` \| `null`</span> | Title |
    | `animation` | <code>array</code> | Animation |
    | `auto_layout` | <code><a href="#structurizrautolayoutschema">StructurizrAutoLayoutSchema</a></code> |  |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | `exclude` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Exclude |
    | `include` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Include |
    | `key` | <span style="white-space: nowrap;">`string` \| `null`</span> | Key |
    | `properties` | `object` | Properties |
    | `scope` | <span style="white-space: nowrap;">`string` \| `null`</span> | Scope |
    | `steps` | <code>array[<a href="#structurizrdynamicstepschema">StructurizrDynamicStepSchema</a>]</code> | Steps |
    | `tags` | <code>array[string]</code> | Tags |
### StructurizrDeploymentViewSchema

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`type(required)`** | `string` | Type Must be exactly `deployment`. |
    | `title` | <span style="white-space: nowrap;">`string` \| `null`</span> | Title |
    | `animation` | <code>array</code> | Animation |
    | `auto_layout` | <code><a href="#structurizrautolayoutschema">StructurizrAutoLayoutSchema</a></code> |  |
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`environment(required)`** | `string` | Environment |
    | `exclude` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Exclude |
    | `include` | <code>array[<a href="#structurizrselectorschema">StructurizrSelectorSchema</a>]</code> | Include |
    | `key` | <span style="white-space: nowrap;">`string` \| `null`</span> | Key |
    | `properties` | `object` | Properties |
    | `scope` | <span style="white-space: nowrap;">`string` \| `null`</span> | Scope |
    | `tags` | <code>array[string]</code> | Tags |
### StructurizrDynamicStepSchema

A view-local ordered interaction; it is not a model relationship.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `description` | <span style="white-space: nowrap;">`string` \| `null`</span> | Description |
    | **`from(required)`** | `string` | From |
    | `properties` | `object` | Properties |
    | `style` | <span style="white-space: nowrap;">`object` \| `null`</span> | Style |
    | `tags` | <code>array[string]</code> | Tags |
    | `technology` | <span style="white-space: nowrap;">`string` \| `null`</span> | Technology |
    | **`to(required)`** | `string` | To |
    | `url` | <span style="white-space: nowrap;">`string` \| `null`</span> | Url |
### StructurizrSelectorSchema

A named element selector, to be resolved by workspace conversion.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | **`id(required)`** | `string` | Id |
### StructurizrAutoLayoutSchema

Structurizr automatic-layout settings.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `implementation` | <span style="white-space: nowrap;">`string` \| `null`</span> | Implementation |
    | `node_separation` | <span style="white-space: nowrap;">`integer` \| `null`</span> | Node Separation |
    | `rank_direction` | <code>enum[TopBottom \| BottomTop \| LeftRight \| RightLeft]</code> | Rank Direction Default: `LeftRight`. |
    | `rank_separation` | <span style="white-space: nowrap;">`integer` \| `null`</span> | Rank Separation |
### StructurizrStylesSchema

Workspace style declarations.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `elements` | <code>array[<a href="#structurizrstyleschema">StructurizrStyleSchema</a>]</code> | Elements |
    | `relationships` | <code>array[<a href="#structurizrstyleschema">StructurizrStyleSchema</a>]</code> | Relationships |
### StructurizrStyleSchema

A style declaration for an element tag or relationship tag.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `properties` | `object` | Properties |
    | **`target(required)`** | `string` | Target |
### StructurizrRenderOptionsSchema

Reserved Structurizr renderer options for workspace JSON.

???+ info "Properties"

    <div class="code-nowrap"></div>

    | Field | Type | Description |
    |---|---|---|
    | `auto_layout` | <code><a href="#structurizrautolayoutschema">StructurizrAutoLayoutSchema</a></code> |  |
    | `style_preset` | <span style="white-space: nowrap;"><code>enum[classic \| new-c4-style]</code> \| `null`</span> | Style Preset |

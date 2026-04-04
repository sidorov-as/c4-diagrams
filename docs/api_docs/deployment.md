# Deployment Diagram

::: c4.diagrams.deployment.DeploymentDiagram
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.deployment.Node
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - set_property_header
          - without_property_header
          - add_property


::: c4.diagrams.deployment.NodeLeft
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        members:
          - __init__
          - set_property_header
          - without_property_header
          - add_property


::: c4.diagrams.deployment.NodeRight
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        members:
          - __init__
          - set_property_header
          - without_property_header
          - add_property

::: c4.diagrams.deployment.DeploymentNode
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        members:
          - __init__
          - set_property_header
          - without_property_header
          - add_property


::: c4.diagrams.deployment.DeploymentNodeLeft
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        members:
          - __init__
          - set_property_header
          - without_property_header
          - add_property


::: c4.diagrams.deployment.DeploymentNodeRight
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        members:
          - __init__
          - set_property_header
          - without_property_header
          - add_property

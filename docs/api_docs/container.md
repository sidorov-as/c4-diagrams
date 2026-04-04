# Container Diagram

::: c4.diagrams.container.ContainerDiagram
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.container.Container
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


::: c4.diagrams.container.ContainerDb
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


::: c4.diagrams.container.ContainerQueue
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


::: c4.diagrams.container.ContainerExt
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


::: c4.diagrams.container.ContainerDbExt
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


::: c4.diagrams.container.ContainerQueueExt
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


::: c4.diagrams.container.ContainerBoundary
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

# System Context Diagram

::: c4.diagrams.system_context.SystemContextDiagram
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - title
          - elements
          - base_elements
          - boundaries
          - layouts
          - relationships
          - as_plantuml
          - render
          - save
          - save_as_plantuml

::: c4.diagrams.system_context.SystemLandscapeDiagram
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - title
          - elements
          - base_elements
          - boundaries
          - layouts
          - relationships
          - as_plantuml
          - render
          - save
          - save_as_plantuml

::: c4.diagrams.system_context.Person
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

::: c4.diagrams.system_context.PersonExt
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.system_context.System
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

::: c4.diagrams.system_context.SystemExt
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.system_context.SystemDb
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.system_context.SystemDbExt
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.system_context.SystemQueue
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.system_context.SystemQueueExt
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.system_context.SystemBoundary
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.system_context.EnterpriseBoundary
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

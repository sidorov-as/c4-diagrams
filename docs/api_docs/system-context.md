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
          - boundaries
          - ordered_elements
          - relationships
          - get_element_by_alias
          - get_elements_by_label
          - generate_alias
          - __enter__
          - __exit__
          - as_plantuml
          - as_mermaid
          - render
          - save
          - save_as_plantuml
          - save_as_mermaid
          - render_options
          - set_render_options

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
          - boundaries
          - ordered_elements
          - relationships
          - get_element_by_alias
          - get_elements_by_label
          - generate_alias
          - __enter__
          - __exit__
          - as_plantuml
          - as_mermaid
          - render
          - save
          - save_as_plantuml
          - save_as_mermaid
          - render_options
          - set_render_options

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
          - set_property_header
          - without_property_header
          - add_property

::: c4.diagrams.system_context.PersonExt
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
          - set_property_header
          - without_property_header
          - add_property


::: c4.diagrams.system_context.SystemExt
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


::: c4.diagrams.system_context.SystemDb
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


::: c4.diagrams.system_context.SystemDbExt
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


::: c4.diagrams.system_context.SystemQueue
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


::: c4.diagrams.system_context.SystemQueueExt
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


::: c4.diagrams.system_context.SystemBoundary
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
          - set_property_header
          - without_property_header
          - add_property

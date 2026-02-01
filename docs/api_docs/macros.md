# Macros

Some macros, attributes, and style options are **backend-specific**.

They may apply only to a particular renderer, such as **PlantUML**, **Mermaid**, or **Structurizr**,
and will be ignored or have no effect when used with other backends.

## PlantUML macros

::: c4.diagrams.core.Index
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

::: c4.diagrams.core.LastIndex
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false
        show_source: false

::: c4.diagrams.core.SetIndex
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        show_bases: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

::: c4.diagrams.core.increment
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

::: c4.diagrams.core.set_index
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

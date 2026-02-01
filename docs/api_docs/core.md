::: c4.diagrams.core.BaseDiagramElement
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - set_property_header
          - without_property_header
          - add_property

::: c4.diagrams.core.Element
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - uses
          - used_by

::: c4.diagrams.core.ElementWithTechnology
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

::: c4.diagrams.core.Boundary
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - elements
          - boundaries
          - relationships
          - __enter__
          - __exit__

::: c4.diagrams.core.RelationshipType
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false

::: c4.diagrams.core.Relationship
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - get_attrs
          - copy
          - get_relationship_by_type

!!! note

    You can find a detailed description of the different relationship types in the
    corresponding sections of the [documentation](../api_docs/relationships.md).

::: c4.diagrams.core.Diagram
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - title
          - elements
          - base_elements
          - boundaries
          - layouts
          - relationships
          - __enter__
          - __exit__
          - as_plantuml
          - render
          - save
          - save_as_plantuml


::: c4.diagrams.core.Layout
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

!!! note

    You can find a detailed description of the different layout types in the
    corresponding sections of the [documentation](../api_docs/layouts.md).

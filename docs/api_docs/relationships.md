# Relationships

The core API owns the portable relationship model and the backend-neutral
[`Rel`][c4.diagrams.core.Rel] shortcut. Directional, bidirectional, and layout
helper APIs are backend-specific contrib APIs:

- [PlantUML relationships](plantuml/relationships.md)
- [Mermaid relationships](mermaid/relationships.md)

::: c4.diagrams.core.Rel
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false

::: c4.diagrams.core.Relationship
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        inherited_members: true
        show_source: false
        members:
          - __init__
          - get_attrs
          - copy
          - get_relationship_by_type
          - set_property_header
          - without_property_header
          - add_property

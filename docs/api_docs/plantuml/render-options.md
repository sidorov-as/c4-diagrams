# Render options

See the official [C4-PlantUML Layout Options documentation](https://github.com/plantuml-stdlib/C4-PlantUML/blob/master/LayoutOptions.md)
for additional information.

::: c4.renderers.plantuml.options.PlantUMLRenderOptionsBuilder
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
            - add_element_tag
            - add_boundary_tag
            - add_rel_tag
            - add_component_tag
            - add_external_component_tag
            - add_container_tag
            - add_external_container_tag
            - add_node_tag
            - add_person_tag
            - add_external_person_tag
            - add_system_tag
            - add_external_system_tag
            - update_element_style
            - update_boundary_style
            - update_rel_style
            - update_container_boundary_style
            - update_system_boundary_style
            - update_enterprise_boundary_style
            - layout_top_down
            - layout_left_right
            - layout_landscape
            - layout_with_legend
            - layout_as_sketch
            - without_property_header
            - set_sketch_style
            - show_legend
            - show_floating_legend
            - update_legend_title
            - show_person_outline
            - show_element_descriptions
            - show_foot_boxes
            - show_index
            - show_person_sprite
            - hide_stereotype
            - hide_person_sprite
            - show_person_portrait
            - build


::: c4.renderers.plantuml.options.PlantUMLRenderOptions
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false


::: c4.renderers.plantuml.options.TagShape
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false


::: c4.renderers.plantuml.options.LineStyle
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false


::: c4.renderers.plantuml.options.Details
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false

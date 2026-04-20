# Render options

See the official [Mermaid documentation](https://mermaid.js.org/syntax/c4.html)
for additional information.

::: c4.renderers.mermaid.options.MermaidRenderOptionsBuilder
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
            - update_element_style
            - update_rel_style
            - update_layout_config
            - build


::: c4.renderers.mermaid.options.MermaidRenderOptions
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false

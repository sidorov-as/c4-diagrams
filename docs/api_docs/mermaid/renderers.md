# Mermaid rendering backends

::: c4.renderers.mermaid.renderer.MermaidRenderer
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - render
          - render_bytes
          - render_file


::: c4.renderers.mermaid.backends.BaseMermaidBackend
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__
          - to_bytes
          - to_file


::: c4.renderers.mermaid.backends.LocalMermaidBackend
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

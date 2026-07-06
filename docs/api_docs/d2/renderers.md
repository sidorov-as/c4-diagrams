# D2 Rendering Backends

::: c4.renderers.d2.renderer.D2Renderer
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false
        show_source: false
        members:
          - __init__
          - validate
          - render
          - render_bytes
          - render_file


::: c4.renderers.d2.backends.BaseD2Backend
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_bases: false
        show_source: false
        members:
          - to_bytes
          - to_file


::: c4.renderers.d2.backends.LocalD2Backend
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        members:
          - __init__

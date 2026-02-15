# PlantUML rendering backends

::: c4.renderers.plantuml.renderer.PlantUMLRenderer
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


::: c4.renderers.plantuml.backends.BasePlantUMLBackend
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


::: c4.renderers.plantuml.backends.LocalPlantUMLBackend
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__


::: c4.renderers.plantuml.backends.RemotePlantUMLBackend
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        # explicit members list so we can set order and include `__init__` easily
        members:
          - __init__

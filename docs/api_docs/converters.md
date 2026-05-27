# Converters

::: c4.converters.json.converter.JSONToDiagramConverter
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        members:
          - __init__
          - parse_diagram_backend
          - convert


::: c4.converters.json.converter.diagram_from_dict
    options:
        show_root_heading: true
        show_source: false


::: c4.converters.json.converter.diagram_backend_from_json
    options:
        show_root_heading: true
        show_source: false


::: c4.converters.json.converter.diagram_from_json
    options:
        show_root_heading: true
        show_source: false


::: c4.converters.python.converter.PythonCodegen
    options:
        show_root_heading: true
        merge_init_into_class: false
        group_by_category: false
        show_source: false
        members:
          - __init__
          - generate


::: c4.converters.python.converter.diagram_to_python_code
    options:
        show_root_heading: true
        show_source: false

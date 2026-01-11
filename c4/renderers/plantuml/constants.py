_C4_PLANTUML_REPO_FILES = (
    "https://raw.githubusercontent.com/plantuml-stdlib/C4-PlantUML/master"
)


RELATIVE_INCLUDE_COMMENT = (
    "' convert it with additional command line "
    'argument -DRELATIVE_INCLUDE="relative/absolute" to use locally'
)


C4_CONTEXT_INCLUDE = f"""\
!if %variable_exists("RELATIVE_INCLUDE")
    !include %get_variable_value("RELATIVE_INCLUDE")/C4_Context.puml
!else
    !include {_C4_PLANTUML_REPO_FILES}/C4_Context.puml
!endif\
"""


C4_CONTAINER_INCLUDE = f"""\
!if %variable_exists("RELATIVE_INCLUDE")
    !include %get_variable_value("RELATIVE_INCLUDE")/C4_Container.puml
!else
    !include {_C4_PLANTUML_REPO_FILES}/C4_Container.puml
!endif\
"""


C4_COMPONENT_INCLUDE = f"""\
!if %variable_exists("RELATIVE_INCLUDE")
    !include %get_variable_value("RELATIVE_INCLUDE")/C4_Component.puml
!else
    !include {_C4_PLANTUML_REPO_FILES}/C4_Component.puml
!endif\
"""


C4_DYNAMIC_INCLUDE = f"""\
!if %variable_exists("RELATIVE_INCLUDE")
    !include %get_variable_value("RELATIVE_INCLUDE")/C4_Dynamic.puml
!else
    !include {_C4_PLANTUML_REPO_FILES}/C4_Dynamic.puml
!endif\
"""


C4_DEPLOYMENT_INCLUDE = f"""\
!if %variable_exists("RELATIVE_INCLUDE")
    !include %get_variable_value("RELATIVE_INCLUDE")/C4_Deployment.puml
!else
    !include {_C4_PLANTUML_REPO_FILES}/C4_Deployment.puml
!endif\
"""

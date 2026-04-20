from pathlib import Path

from c4.enums import (
    JSON,
    MERMAID_DIAGRAM_FORMATS,
    PLANTUML_DIAGRAM_FORMATS,
    PY,
    DiagramFormat,
    RendererEnum,
)

VENDOR_DIR = Path(__file__).parent / "vendor"
C4_PLANTUML_LIBRARY_DIR = VENDOR_DIR / "c4_plantuml"

PLANTUML = RendererEnum.PLANTUML
MERMAID = RendererEnum.MERMAID
STRUCTURIZR = RendererEnum.STRUCTURIZR
D2 = RendererEnum.D2


DEFAULT_RENDERER_ENV_VAR = "DEFAULT_RENDERER"
DEFAULT_RENDERER = PLANTUML.value

KNOWN_RENDERERS = (PLANTUML, MERMAID)
# WIP: "structurizr", "d2"


LOCAL_BACKEND = "local"
REMOTE_BACKEND = "remote"

RENDERING_TIMEOUT_SECONDS_ENV_VAR = "RENDERING_TIMEOUT_SECONDS"
DEFAULT_RENDERING_TIMEOUT_SECONDS = 30.0


# PlantUML options
PLANTUML_SERVER_URL_ENV_VAR = "PLANTUML_SERVER_URL"
DEFAULT_PLANTUML_SERVER_URL = "https://www.plantuml.com/plantuml"

PLANTUML_BIN_ENV_VAR = "PLANTUML_BIN"
DEFAULT_PLANTUML_BIN = "plantuml"

PLANTUML_JAR_ENV_VAR = "PLANTUML_JAR"
JAVA_BIN_ENV_VAR = "JAVA_BIN"
DEFAULT_JAVA_BIN = "java"

PLANTUML_SKINPARAM_DPI_ENV_VAR = "PLANTUML_SKINPARAM_DPI"
PLANTUML_SKINPARAM_DPI_TEMPLATE = "skinparam dpi {dpi}"

# Mermaid options

MERMAID_BIN_ENV_VAR = "MERMAID_BIN"
DEFAULT_MERMAID_BIN = "mmdc"

MERMAID_SCALE_FACTOR_ENV_VAR = "MERMAID_SCALE_FACTOR"

DEFAULT_MERMAID_SCALE_FACTOR = 1

# Formats
DIAGRAM_FORMATS_BY_RENDERER: dict[RendererEnum, set[DiagramFormat]] = {
    PLANTUML: PLANTUML_DIAGRAM_FORMATS,
    MERMAID: MERMAID_DIAGRAM_FORMATS,
}

_formats_by_renderer_parts = []
for renderer, formats in sorted(DIAGRAM_FORMATS_BY_RENDERER.items()):
    fmt_list = ", ".join(sorted({fmt.value for fmt in formats}))
    _formats_by_renderer_parts.append(f"{renderer}: {fmt_list}")

FORMATS_BY_RENDERER_HELP_TEXT = "\n".join(_formats_by_renderer_parts)

ALL_DIAGRAM_FORMATS = sorted({fmt.value for fmt in DiagramFormat})

CONVERT_FROM_FORMATS = sorted({JSON.value})
CONVERT_TO_FORMATS = sorted({PY.value})

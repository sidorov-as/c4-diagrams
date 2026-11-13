from typing import Literal

from c4.compat import StrEnum


class RendererEnum(StrEnum):
    PLANTUML = "plantuml"
    MERMAID = "mermaid"
    STRUCTURIZR = "structurizr"
    D2 = "d2"
    LIKEC4 = "likec4"


class DiagramFormat(StrEnum):
    EPS = "eps"
    LATEX = "latex"
    SVG = "svg"
    PNG = "png"
    JPG = "jpg"
    TXT = "txt"
    UTXT = "utxt"
    PDF = "pdf"


EPS = DiagramFormat.EPS
LATEX = DiagramFormat.LATEX
SVG = DiagramFormat.SVG
PNG = DiagramFormat.PNG
JPG = DiagramFormat.JPG
TXT = DiagramFormat.TXT
UTXT = DiagramFormat.UTXT
PDF = DiagramFormat.PDF

PLANTUML_DIAGRAM_FORMATS = {
    EPS,
    LATEX,
    SVG,
    PNG,
    TXT,
    UTXT,
}

MERMAID_DIAGRAM_FORMATS = {
    SVG,
    PNG,
    PDF,
}

D2_DIAGRAM_FORMATS = {
    SVG,
    PNG,
    PDF,
}

STRUCTURIZR_DIAGRAM_FORMATS = {
    SVG,
    PNG,
    PDF,
}

# `structurizr export` renders only PNG and SVG; PDF is Kroki-only.
STRUCTURIZR_LOCAL_DIAGRAM_FORMATS = {
    SVG,
    PNG,
}

# `likec4 export` supports only raster output (checked on LikeC4 1.60.0).
LIKEC4_DIAGRAM_FORMATS = {
    PNG,
    JPG,
}


class DiagramConvertionFormat(StrEnum):
    JSON = "json"
    PY = "py"


JSON = DiagramConvertionFormat.JSON
PY = DiagramConvertionFormat.PY


class ConvertShortcut(StrEnum):
    JSON_TO_PY = "json_to_py"


class ExtensionValidationMode(StrEnum):
    """Renderer policy for backend extension validation."""

    STRICT = "strict"
    IGNORE_FOREIGN = "ignore_foreign"


ExtensionValidationModeType = (
    ExtensionValidationMode | Literal["strict", "ignore_foreign"]
)

STRICT = ExtensionValidationMode.STRICT
IGNORE_FOREIGN = ExtensionValidationMode.IGNORE_FOREIGN

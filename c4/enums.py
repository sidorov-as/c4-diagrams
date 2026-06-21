from typing import Literal

from c4.compat import StrEnum


class RendererEnum(StrEnum):
    PLANTUML = "plantuml"
    MERMAID = "mermaid"
    STRUCTURIZR = "structurizr"
    D2 = "d2"


class DiagramFormat(StrEnum):
    EPS = "eps"
    LATEX = "latex"
    SVG = "svg"
    PNG = "png"
    TXT = "txt"
    UTXT = "utxt"
    PDF = "pdf"


EPS = DiagramFormat.EPS
LATEX = DiagramFormat.LATEX
SVG = DiagramFormat.SVG
PNG = DiagramFormat.PNG
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

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


EPS = DiagramFormat.EPS
LATEX = DiagramFormat.LATEX
SVG = DiagramFormat.SVG
PNG = DiagramFormat.PNG
TXT = DiagramFormat.TXT
UTXT = DiagramFormat.UTXT

PLANTUML_DIAGRAM_FORMATS = {
    EPS,
    LATEX,
    SVG,
    PNG,
    TXT,
    UTXT,
}


class DiagramConvertionFormat(StrEnum):
    JSON = "json"
    PY = "py"


JSON = DiagramConvertionFormat.JSON
PY = DiagramConvertionFormat.PY


class ConvertShortcut(StrEnum):
    JSON_TO_PY = "json_to_py"

class C4Exception(Exception):
    """Base exception class for all C4-related errors."""


class PlantUMLError(C4Exception):
    """Base exception class for all PlantUML-related errors."""


class PlantUMLRenderingError(PlantUMLError):
    """Error raised when rendering fails."""


class PlantUMLRemoteRenderingError(PlantUMLRenderingError):
    """Error raised when rendering via a remote PlantUML server fails."""


class PlantUMLLocalRenderingError(PlantUMLRenderingError):
    """Error raised when rendering via a local PlantUML backend fails."""


class PlantUMLBackendConfigurationError(PlantUMLError):
    """Error raised when a PlantUML backend is incorrectly configured."""


class MermaidError(C4Exception):
    """Base exception class for all Mermaid-related errors."""


class MermaidRenderingError(MermaidError):
    """Error raised when rendering fails."""


class MermaidBackendConfigurationError(MermaidError):
    """Error raised when a Mermaid backend is incorrectly configured."""


class MermaidLocalRenderingError(MermaidError):
    """Error raised when rendering via a local Mermaid backend fails."""


class D2Error(C4Exception):
    """Base exception class for all D2-related errors."""


class D2RenderingError(D2Error):
    """Error raised when rendering fails."""


class D2BackendConfigurationError(D2Error):
    """Error raised when a D2 backend is incorrectly configured."""


class D2LocalRenderingError(D2Error):
    """Error raised when rendering via a local D2 backend fails."""

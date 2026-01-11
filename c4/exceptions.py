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

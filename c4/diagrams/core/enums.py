from __future__ import annotations

from enum import unique

from typing_extensions import Self

from c4.compat import StrEnum


class EnumDescriptionsMixin:
    """Mixin for enums that expose documentation descriptions."""

    @classmethod
    def get_descriptions(cls) -> dict[Self, str]:  # pragma: no cover
        """Return the Enum items description used in documentation."""
        raise NotImplementedError("Must be implemented by subclasses")


@unique
class RelationshipType(EnumDescriptionsMixin, StrEnum):
    """
    Relationship dispatch keys used by relationship DSL classes.

    `REL` is the portable core relationship type. The other values map to
    backend-specific C4-PlantUML relationship macros and should normally be
    used through `c4.contrib.plantuml` relationship classes.
    """

    REL = "REL"
    BI_REL = "BI_REL"
    REL_BACK = "REL_BACK"
    REL_NEIGHBOR = "REL_NEIGHBOR"
    BI_REL_NEIGHBOR = "BI_REL_NEIGHBOR"
    REL_BACK_NEIGHBOR = "REL_BACK_NEIGHBOR"
    REL_D = "REL_D"
    REL_DOWN = "REL_DOWN"
    BI_REL_D = "BI_REL_D"
    BI_REL_DOWN = "BI_REL_DOWN"
    REL_U = "REL_U"
    REL_UP = "REL_UP"
    BI_REL_U = "BI_REL_U"
    BI_REL_UP = "BI_REL_UP"
    REL_L = "REL_L"
    REL_LEFT = "REL_LEFT"
    BI_REL_L = "BI_REL_L"
    BI_REL_LEFT = "BI_REL_LEFT"
    REL_R = "REL_R"
    REL_RIGHT = "REL_RIGHT"
    BI_REL_R = "BI_REL_R"
    BI_REL_RIGHT = "BI_REL_RIGHT"

    @classmethod
    def get_descriptions(cls) -> dict[RelationshipType, str]:
        """Return the Enum items description used in documentation."""
        return {
            cls.BI_REL: "A bidirectional relationship between two elements.",
            cls.BI_REL_DOWN: "A bidirectional downward relationship.",
            cls.BI_REL_D: (
                "A bidirectional downward relationship. "
                "Shorthand for `BI_REL_DOWN`."
            ),
            cls.BI_REL_LEFT: "A bidirectional leftward relationship.",
            cls.BI_REL_L: (
                "A bidirectional leftward relationship. "
                "Shorthand for `BI_REL_LEFT`."
            ),
            cls.BI_REL_NEIGHBOR: (
                "A bidirectional neighboring relationship between two elements."
            ),
            cls.BI_REL_RIGHT: "A bidirectional rightward relationship.",
            cls.BI_REL_R: (
                "A bidirectional rightward relationship. "
                "Shorthand for `BI_REL_RIGHT`."
            ),
            cls.BI_REL_UP: "A bidirectional upward relationship.",
            cls.BI_REL_U: (
                "A bidirectional upward relationship. "
                "Shorthand for `BI_REL_UP`."
            ),
            cls.REL: "A unidirectional relationship between two elements.",
            cls.REL_BACK: "A unidirectional relationship pointing backward.",
            cls.REL_BACK_NEIGHBOR: (
                "A unidirectional relationship combining backward "
                "and neighboring semantics."
            ),
            cls.REL_DOWN: "A unidirectional downward relationship.",
            cls.REL_D: (
                "A unidirectional downward relationship. "
                "Shorthand for `REL_DOWN`."
            ),
            cls.REL_LEFT: "A unidirectional leftward relationship.",
            cls.REL_L: (
                "A unidirectional leftward relationship. "
                "Shorthand for `REL_LEFT`."
            ),
            cls.REL_NEIGHBOR: (
                "A unidirectional relationship representing a lateral "
                "or neighboring interaction."
            ),
            cls.REL_RIGHT: "A unidirectional rightward relationship.",
            cls.REL_R: (
                "A unidirectional rightward relationship. "
                "Shorthand for `REL_RIGHT`."
            ),
            cls.REL_UP: "A unidirectional upward relationship.",
            cls.REL_U: (
                "A unidirectional upward relationship. Shorthand for `REL_UP`."
            ),
        }


@unique
class DiagramType(StrEnum):
    """
    Enum representing diagram types.
    """

    DIAGRAM = "Diagram"
    SYSTEM_CONTEXT_DIAGRAM = "SystemContextDiagram"
    SYSTEM_LANDSCAPE_DIAGRAM = "SystemLandscapeDiagram"
    CONTAINER_DIAGRAM = "ContainerDiagram"
    COMPONENT_DIAGRAM = "ComponentDiagram"
    DYNAMIC_DIAGRAM = "DynamicDiagram"
    DEPLOYMENT_DIAGRAM = "DeploymentDiagram"

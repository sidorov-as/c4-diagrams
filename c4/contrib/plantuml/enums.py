from __future__ import annotations

from enum import unique

from c4.compat import StrEnum
from c4.diagrams.core.enums import EnumDescriptionsMixin


@unique
class LayoutType(EnumDescriptionsMixin, StrEnum):
    """
    Enum representing layout modifiers for diagram elements.
    """

    LAY_D = "LAY_D"
    LAY_DOWN = "LAY_DOWN"
    LAY_U = "LAY_U"
    LAY_UP = "LAY_UP"
    LAY_R = "LAY_R"
    LAY_RIGHT = "LAY_RIGHT"
    LAY_L = "LAY_L"
    LAY_LEFT = "LAY_LEFT"

    @classmethod
    def get_descriptions(cls) -> dict[LayoutType, str]:
        """Return the Enum items description used in documentation."""
        return {
            cls.LAY_DOWN: "Positions `from` element below `to` element.",
            cls.LAY_D: (
                "Positions `from` element below `to` element. "
                "Shorthand for `LAY_DOWN` layout."
            ),
            cls.LAY_UP: "Positions `from` element above `to` element.",
            cls.LAY_U: (
                "Positions `from` element above `to` element. "
                "Shorthand for `LAY_UP` layout."
            ),
            cls.LAY_RIGHT: (
                "Positions `from` element to the right of `to` element."
            ),
            cls.LAY_R: (
                "Positions `from` element to the right of `to` element. "
                "Shorthand for `LAY_RIGHT` layout."
            ),
            cls.LAY_LEFT: (
                "Positions `from` element to the left of `to` element."
            ),
            cls.LAY_L: (
                "Positions `from` element to the left of `to` element. "
                "Shorthand for `LAY_LEFT` layout."
            ),
        }

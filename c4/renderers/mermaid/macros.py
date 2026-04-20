from __future__ import annotations

import dataclasses
from typing import Any, ClassVar

from typing_extensions import override

from c4 import (
    Component,
    ComponentDb,
    ComponentDbExt,
    ComponentExt,
    ComponentQueue,
    ComponentQueueExt,
    Container,
    ContainerBoundary,
    ContainerDb,
    ContainerDbExt,
    ContainerExt,
    ContainerQueue,
    ContainerQueueExt,
    DeploymentNode,
    DeploymentNodeLeft,
    DeploymentNodeRight,
    EnterpriseBoundary,
    Node,
    NodeLeft,
    NodeRight,
    Person,
    PersonExt,
    System,
    SystemBoundary,
    SystemDb,
    SystemDbExt,
    SystemExt,
    SystemQueue,
    SystemQueueExt,
)
from c4.diagrams.core import (
    Boundary,
    Element,
    ElementWithTechnology,
    Relationship,
    RelationshipType,
)
from c4.renderers.macros import Argument, BaseMacro, quote, quote_and_escape
from c4.renderers.mermaid.options import (
    ElementStyle,
    RelStyle,
    UpdateLayoutConfig,
)

ELEMENT_TO_MERMAID_MACRO_MAP = {
    Person: "Person",
    PersonExt: "Person_Ext",
    System: "System",
    SystemDb: "SystemDb",
    SystemQueue: "SystemQueue",
    SystemExt: "System_Ext",
    SystemDbExt: "SystemDb_Ext",
    SystemQueueExt: "SystemQueue_Ext",
    Boundary: "Boundary",
    EnterpriseBoundary: "Enterprise_Boundary",
    SystemBoundary: "System_Boundary",
    Container: "Container",
    ContainerDb: "ContainerDb",
    ContainerQueue: "ContainerQueue",
    ContainerExt: "Container_Ext",
    ContainerDbExt: "ContainerDb_Ext",
    ContainerQueueExt: "ContainerQueue_Ext",
    ContainerBoundary: "Container_Boundary",
    Component: "Component",
    ComponentDb: "ComponentDb",
    ComponentQueue: "ComponentQueue",
    ComponentExt: "Component_Ext",
    ComponentDbExt: "ComponentDb_Ext",
    ComponentQueueExt: "ComponentQueue_Ext",
    Node: "Node",
    NodeLeft: "Node_L",
    NodeRight: "Node_R",
    DeploymentNode: "Deployment_Node",
    # Fallback
    DeploymentNodeLeft: "Deployment_Node",
    DeploymentNodeRight: "Deployment_Node",
}


RELATIONSHIP_TO_MERMAID_MACRO_MAP = {
    RelationshipType.REL: "Rel",
    RelationshipType.BI_REL: "BiRel",
    RelationshipType.REL_BACK: "Rel_Back",
    RelationshipType.REL_D: "Rel_D",
    RelationshipType.REL_DOWN: "Rel_Down",
    RelationshipType.REL_U: "Rel_U",
    RelationshipType.REL_UP: "Rel_Up",
    RelationshipType.REL_L: "Rel_L",
    RelationshipType.REL_LEFT: "Rel_Left",
    RelationshipType.REL_R: "Rel_R",
    RelationshipType.REL_RIGHT: "Rel_Right",
}
RELATIONSHIP_FALLBACK_MACRO = "Rel"


class RelationshipMermaidMacro(BaseMacro[Relationship]):
    """
    Mermaid macro renderer for `Relationship` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="from"),
        Argument(name="to"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="techn", source="technology", format=quote_and_escape),
    ]

    @override
    def get_macro(self) -> str | None:
        """
        Resolves the macro name based on the element's concrete class.
        """
        rel_type = self._diagram_element.relationship_type

        return RELATIONSHIP_TO_MERMAID_MACRO_MAP.get(
            rel_type, RELATIONSHIP_FALLBACK_MACRO
        )

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        relationship = self._diagram_element

        from_element, to_element = relationship.get_participants()  # type: ignore[var-annotated]

        return {
            "from": from_element.alias,
            "to": to_element.alias,
            "label": relationship.label,
            "technology": relationship.technology,
        }


class ElementMermaidMacro(BaseMacro[Element]):
    """
    Mermaid macro renderer for base Element instances.

    Handles common element attributes like label, sprite, link, type, etc.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="descr", source="description", format=quote_and_escape),
    ]

    @override
    def get_macro(self) -> str | None:
        """
        Resolves the macro name based on the element's concrete class.
        """
        return ELEMENT_TO_MERMAID_MACRO_MAP.get(type(self._diagram_element))

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        element = self._diagram_element

        return {
            "label": element.label,
            "alias": element.alias,
            "description": element.description,
        }

    @classmethod
    def from_element(cls, element: Element) -> BaseMacro:
        """
        Factory method that returns macro renderer based on the element type.

        Args:
            element: The element instance to wrap.

        Returns:
            The matching macro renderer subclass.
        """
        elements_with_technology = (
            Container,
            ContainerExt,
            Component,
            ElementWithTechnology,
        )

        if type(element) is Boundary:
            return BoundaryMermaidMacro(diagram_element=element)
        elif isinstance(element, elements_with_technology):
            return ElementWithTechnologyMermaidMacro(diagram_element=element)

        return cls(diagram_element=element)


class ElementWithTechnologyMermaidMacro(ElementMermaidMacro):
    """
    Mermaid macro renderer for `Element` instances with technology attribute.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(
            name="techn",
            source="technology",
            format=quote_and_escape,
        ),
        Argument(
            name="descr",
            source="description",
            format=quote_and_escape,
        ),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        element = self._diagram_element
        data = super().get_data()

        data["technology"] = element.technology

        return data


class BoundaryMermaidMacro(BaseMacro[Element]):
    """
    Mermaid macro renderer for Boundary instances.

    Handles common boundary attributes.
    """

    macro: ClassVar[str | None] = "Boundary"
    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="type", format=quote_and_escape),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        element = self._diagram_element

        return {
            "label": element.label,
            "alias": element.alias,
            "type": element.type,
        }


class ContainerPlantUMLMacro(BaseMacro[Container]):
    """
    Mermaid macro renderer for `Container` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="techn", source="technology", format=quote_and_escape),
        Argument(name="descr", source="description", format=quote_and_escape),
    ]


class UpdateRelStyleMermaidMacro(BaseMacro[RelStyle]):
    """
    Mermaid macro renderer for `UpdateRelStyle`.
    """

    macro: ClassVar[str | None] = "UpdateRelStyle"
    args: ClassVar[list[Argument]] = [
        Argument(
            name="from",
            source="from_element",
        ),
        Argument(
            name="to",
            source="to_element",
        ),
        Argument.keyword(
            name="textColor",
            source="text_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="lineColor",
            source="line_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="offsetX",
            source="offset_x",
            format=quote,
        ),
        Argument.keyword(
            name="offsetY",
            source="offset_y",
            format=quote,
        ),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        return dataclasses.asdict(self._diagram_element)


class UpdateElementStyleMermaidMacro(BaseMacro[ElementStyle]):
    """
    Mermaid macro renderer for `UpdateElementStyle`.
    """

    macro: ClassVar[str | None] = "UpdateElementStyle"
    args: ClassVar[list[Argument]] = [
        Argument(
            name="element",
            source="element",
        ),
        Argument.keyword(
            name="fontColor",
            source="font_color",
            format=quote,
        ),
        Argument.keyword(
            name="bgColor",
            source="bg_color",
            format=quote,
        ),
        Argument.keyword(
            name="borderColor",
            source="border_color",
            format=quote,
        ),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        return dataclasses.asdict(self._diagram_element)


class UpdateLayoutConfigMermaidMacro(BaseMacro[UpdateLayoutConfig]):
    """
    Mermaid macro renderer for `UpdateLayoutConfig`.
    """

    macro: ClassVar[str | None] = "UpdateLayoutConfig"
    args: ClassVar[list[Argument]] = [
        Argument.keyword(
            name="c4ShapeInRow",
            source="c4_shape_in_row",
            format=quote,
        ),
        Argument.keyword(
            name="c4BoundaryInRow",
            source="c4_boundary_in_row",
            format=quote,
        ),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        return dataclasses.asdict(self._diagram_element)

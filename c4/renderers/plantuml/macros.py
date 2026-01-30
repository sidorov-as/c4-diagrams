from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass, is_dataclass
from typing import (
    Any,
    ClassVar,
    Generic,
    TypeVar,
    cast,
    get_args,
    get_origin,
)

from typing_extensions import get_original_bases, override

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
    BaseDiagramElement,
    Boundary,
    DiagramElementProperties,
    Element,
    ElementWithTechnology,
    Layout,
    LayoutType,
    Relationship,
    RelationshipType,
    increment,
    set_index,
)
from c4.renderers.plantuml.layout_options import (
    BaseStyle,
    BaseTag,
    BoundaryStyle,
    BoundaryTag,
    ComponentTag,
    ContainerBoundaryStyle,
    ContainerTag,
    DiagramLayout,
    ElementStyle,
    ElementTag,
    EnterpriseBoundaryStyle,
    ExternalComponentTag,
    ExternalContainerTag,
    ExternalPersonTag,
    ExternalSystemTag,
    NodeTag,
    PersonTag,
    RelStyle,
    RelTag,
    SetSketchStyle,
    ShowFloatingLegend,
    ShowLegend,
    ShowPersonSprite,
    SystemBoundaryStyle,
    SystemTag,
)

_TDiagramElement = TypeVar("_TDiagramElement")


ELEMENT_TO_PLANTUML_MACRO_MAP = {
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
    DeploymentNodeLeft: "Deployment_Node_L",
    DeploymentNodeRight: "Deployment_Node_R",
}


RELATIONSHIP_TO_PLANTUML_MACRO_MAP = {
    RelationshipType.REL: "Rel",
    RelationshipType.BI_REL: "BiRel",
    RelationshipType.REL_BACK: "Rel_Back",
    RelationshipType.REL_NEIGHBOR: "Rel_Neighbor",
    RelationshipType.BI_REL_NEIGHBOR: "BiRel_Neighbor",
    RelationshipType.REL_BACK_NEIGHBOR: "Rel_Back_Neighbor",
    RelationshipType.REL_D: "Rel_D",
    RelationshipType.REL_DOWN: "Rel_Down",
    RelationshipType.BI_REL_D: "BiRel_D",
    RelationshipType.BI_REL_DOWN: "BiRel_Down",
    RelationshipType.REL_U: "Rel_U",
    RelationshipType.REL_UP: "Rel_Up",
    RelationshipType.BI_REL_U: "BiRel_U",
    RelationshipType.BI_REL_UP: "BiRel_Up",
    RelationshipType.REL_L: "Rel_L",
    RelationshipType.REL_LEFT: "Rel_Left",
    RelationshipType.BI_REL_L: "BiRel_L",
    RelationshipType.BI_REL_LEFT: "BiRel_Left",
    RelationshipType.REL_R: "Rel_R",
    RelationshipType.REL_RIGHT: "Rel_Right",
    RelationshipType.BI_REL_R: "BiRel_R",
    RelationshipType.BI_REL_RIGHT: "BiRel_Right",
}


LAYOUT_TO_PLANTUML_MACRO_MAP = {
    LayoutType.LAY_D: "Lay_D",
    LayoutType.LAY_DOWN: "Lay_Down",
    LayoutType.LAY_U: "Lay_U",
    LayoutType.LAY_UP: "Lay_Up",
    LayoutType.LAY_R: "Lay_R",
    LayoutType.LAY_RIGHT: "Lay_Right",
    LayoutType.LAY_L: "Lay_L",
    LayoutType.LAY_LEFT: "Lay_Left",
}


@dataclass(frozen=True)
class Argument:
    """
    Represents a single argument in a PlantUML macro call.

    Attributes:
        name: The PlantUML argument name (e.g. 'label', 'type').
        source: The name of the attribute or data key to pull from
            the diagram element. If None, defaults to the value of `name`.
        format: Optional function used to format the value
            before rendering (e.g., quoting or escaping).
        forced_keyword: If True, this argument will always be rendered
            as a keyword argument (e.g., `$name=value`).
    """

    name: str
    source: str | None = None
    format: Callable[[Any], str] | None = None
    forced_keyword: bool = False

    @classmethod
    def keyword(
        cls,
        name: str,
        source: str | None = None,
        format: Callable[[Any], str] | None = None,  # noqa: A002
    ) -> Argument:
        return cls(
            name=name,
            source=source,
            format=format,
            forced_keyword=True,
        )


def quote_and_escape(value: str) -> str:
    r"""
    Quote a string and escape newline and quote characters.

    Replaces all `\n` characters with `\\n` and `"` with `\"`,
    then wraps the result in double quotes.
    """
    value = value.replace("\n", "\\n").replace('"', '\\"')

    return f'"{value}"'


def quote(value: str) -> str:
    """
    Wrap a string in double quotes without escaping.
    """
    return f'"{value}"'


def quote_and_lower(value: str) -> str:
    """
    Wrap a string in double quotes without escaping and convert to lowercase.
    """
    return f'"{value}"'.lower()


def force_str(value: Any) -> str:
    """
    Converts the given value to a string.
    """
    return str(value)


def macro_call(value: str) -> str:
    """
    Formats the given string as a PlantUML macro call.
    """
    return f"{value}()"


class PlantUMLMacro(Generic[_TDiagramElement]):
    """
    Base class for rendering PlantUML macros from diagram elements.

    Subclasses must define `macro` and `args`. The class can be used to render
    any diagram element into its corresponding PlantUML macro syntax.

    Attributes:
        macro: The name of the PlantUML macro (e.g. "Person", "Rel").
        args: Ordered list of macro arguments.
    """

    macro: ClassVar[str | None] = None
    args: ClassVar[list[Argument]] = []

    def __init__(self, diagram_element: _TDiagramElement) -> None:
        """
        Initializes the macro wrapper for the given diagram element.

        Args:
            diagram_element: The element to render.
        """
        self._diagram_element = diagram_element

    def get_data(self) -> dict[str, Any]:
        """
        Returns a dictionary of macro args and values from the element.

        Subclasses must override this to extract values from their element.
        """
        if not self.args:
            return {}

        raise NotImplementedError(
            f"{self.__class__.__name__}.get_data() must be overridden "
            f"when 'args' are defined"
        )

    def get_macro(self) -> str | None:
        """
        Returns the name of the PlantUML macro.

        Can be overridden to provide dynamic macro name resolution.
        """
        return getattr(self, "macro", None)

    def get_properties(self) -> DiagramElementProperties | None:
        """
        Returns the properties defined on the diagram element, if supported.

        This method checks whether the wrapped diagram element is an instance
        of `BaseDiagramElement`. If so, it accesses and returns
        its `properties` attribute. Otherwise, it returns None, indicating
        that no properties are available.

        Returns:
            The `DiagramElementProperties` associated with the element,
            or None if the element does not support properties.
        """
        if not isinstance(self._diagram_element, BaseDiagramElement):
            return None

        return self._diagram_element.properties

    def check_macro(self) -> str:
        """
        Returns the macro name or raises if it is missing.
        """
        macro = self.get_macro()

        if not macro:
            raise AttributeError(
                f"Attribute `macro` not provided for {self.__class__.__name__}"
            )

        return macro

    def render(self) -> str:
        """
        Renders the element as a PlantUML macro call.

        Returns:
            Rendered PlantUML macro string.
        """
        macro = self.check_macro()
        data = self.get_data()

        parts = []
        forced_keyword = False
        args = self.args or []

        if args and not data:
            raise ValueError(
                f"Cannot render PlantUML macro for element "
                f"{self._diagram_element!r}: "
                f"arguments are defined ({[arg.name for arg in args]}), but "
                f"no input data was provided."
            )

        for arg in args:
            name = arg.source or arg.name

            value = data.get(name, "")

            if not value:
                forced_keyword = True
                continue

            if arg.format:
                value = arg.format(value)

            if forced_keyword or arg.forced_keyword:
                parts.append(f"${arg.name}={value}")
                forced_keyword = True
            else:
                parts.append(f"{value}")

        return f"{macro}({', '.join(parts)})"

    def render_properties(
        self, global_without_property_header: bool = False
    ) -> list[str]:
        """
        Renders PlantUML property-related statements for the diagram element.

        This includes optional calls to:
          - `WithoutPropertyHeader()` if headers are disabled.
          - `SetPropertyHeader(...)` with custom headers if enabled.
          - One or more `AddProperty(...)` lines with the element's properties.

        Args:
            global_without_property_header: If True, suppresses rendering of
                `SetPropertyHeader(...)` or `WithoutPropertyHeader()`.
                This allows callers to enforce global property header behavior,
                such as when wrapping multiple elements in a boundary.

        Returns:
            A list of PlantUML lines representing property configuration, or
            an empty list if no properties are defined for the element.
        """
        lines: list[str] = []

        properties = self.get_properties()

        if properties is None or not properties.properties:
            return lines

        if not global_without_property_header:
            if not properties.show_header:
                lines.append("WithoutPropertyHeader()")
            else:
                args = ", ".join(
                    quote_and_escape(val) for val in properties.header
                )
                lines.append(f"SetPropertyHeader({args})")

        for prop in properties.properties:
            args = ", ".join(quote_and_escape(val) for val in prop)
            lines.append(f"AddProperty({args})")

        return lines


class PlantUMLMacroWithoutArgs(PlantUMLMacro[None]):
    """
    Represents a PlantUML macro that takes no diagram element or arguments.
    """

    def __init__(self) -> None:
        """
        Initialize the macro with no associated diagram element.

        This sets the internal diagram element to `None` since this macro
        does not rely on element-specific data.
        """
        super().__init__(None)


class ElementPlantUMLMacro(PlantUMLMacro[Element]):
    """
    PlantUML macro renderer for base Element instances.

    Handles common element attributes like label, sprite, link, type, etc.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="descr", source="description", format=quote_and_escape),
        Argument.keyword(name="sprite", format=quote),
        Argument.keyword(name="tags", format=quote),
        Argument.keyword(name="link", format=quote),
        Argument.keyword(name="type", format=quote),
    ]

    @override
    def get_macro(self) -> str | None:
        """
        Resolves the macro name based on the element's concrete class.
        """
        return ELEMENT_TO_PLANTUML_MACRO_MAP.get(type(self._diagram_element))

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        element = self._diagram_element

        return {
            "label": element.label,
            "alias": element.alias,
            "sprite": element.sprite,
            "type": element.type,
            "tags": element.tags,
            "link": element.link,
            "description": element.description,
            "base_shape": element.base_shape,
            "technology": element.technology,
        }

    @classmethod
    def from_element(cls, element: Element) -> ElementPlantUMLMacro:
        """
        Factory method that returns macro renderer based on the element type.

        Args:
            element: The element instance to wrap.

        Returns:
            The matching macro renderer subclass.
        """
        if isinstance(element, System):
            return SystemPlantUMLMacro(diagram_element=element)
        if isinstance(element, Node):
            return NodePlantUMLMacro(diagram_element=element)
        if isinstance(element, Boundary):
            return BoundaryPlantUMLMacro(diagram_element=element)
        if isinstance(element, Container):
            return ContainerPlantUMLMacro(diagram_element=element)
        if isinstance(element, ElementWithTechnology):
            return ElementWithTechnologyPlantUMLMacro(diagram_element=element)
        if isinstance(element, Component):
            return ComponentPlantUMLMacro(diagram_element=element)

        return cls(diagram_element=element)


class ElementWithTechnologyPlantUMLMacro(ElementPlantUMLMacro):
    """
    PlantUML macro renderer for `Element` instances with technology attribute.
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
        Argument.keyword(name="sprite", format=quote),
        Argument.keyword(name="tags", format=quote),
        Argument.keyword(name="link", format=quote),
    ]


class SystemPlantUMLMacro(ElementPlantUMLMacro):
    """
    PlantUML macro renderer for `System` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="descr", source="description", format=quote_and_escape),
        Argument.keyword(name="sprite", format=quote),
        Argument.keyword(name="tags", format=quote),
        Argument.keyword(name="link", format=quote),
        Argument.keyword(name="type", format=quote),
        Argument.keyword(name="baseShape", source="base_shape", format=quote),
    ]


class BoundaryPlantUMLMacro(ElementPlantUMLMacro):
    """
    PlantUML macro renderer for `Boundary` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument.keyword(name="type", format=quote),
        Argument.keyword(name="tags", format=quote),
        Argument.keyword(name="link", format=quote),
        Argument.keyword(
            name="descr", source="description", format=quote_and_escape
        ),
    ]


class ContainerPlantUMLMacro(ElementPlantUMLMacro):
    """
    PlantUML macro renderer for `Container` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="techn", source="technology", format=quote_and_escape),
        Argument(name="descr", source="description", format=quote_and_escape),
        Argument.keyword(name="sprite", format=quote),
        Argument.keyword(name="tags", format=quote),
        Argument.keyword(name="link", format=quote),
        Argument.keyword(name="baseShape", source="base_shape", format=quote),
    ]


class ComponentPlantUMLMacro(ElementPlantUMLMacro):
    """
    PlantUML macro renderer for `Component` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="techn", source="technology", format=quote_and_escape),
        Argument(name="descr", source="description", format=quote_and_escape),
        Argument.keyword(name="sprite", format=quote),
        Argument.keyword(name="tags", format=quote),
        Argument.keyword(name="link", format=quote),
        Argument.keyword(name="baseShape", source="base_shape", format=quote),
    ]


class RelationshipPlantUMLMacro(PlantUMLMacro[Relationship]):
    """
    PlantUML macro renderer for `Relationship` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="from"),
        Argument(name="to"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="techn", source="technology", format=quote_and_escape),
        Argument(name="descr", source="description", format=quote_and_escape),
        Argument.keyword(name="sprite", format=quote),
        Argument.keyword(name="tags", format=quote),
        Argument.keyword(name="link", format=quote),
        Argument.keyword(name="index", format=force_str),
    ]

    @override
    def get_macro(self) -> str | None:
        """
        Resolves the macro name based on the element's concrete class.
        """
        rel_type = self._diagram_element.relationship_type
        return RELATIONSHIP_TO_PLANTUML_MACRO_MAP.get(rel_type)

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        relationship = self._diagram_element

        from_element = relationship.from_element
        to_element = relationship.to_element

        if not from_element:
            raise ValueError(
                f"Empty `from_element` for relationship {relationship}"
            )

        if not to_element:
            raise ValueError(
                f"Empty `to_element` for relationship {relationship}"
            )

        return {
            "from": from_element.alias,
            "to": to_element.alias,
            "label": relationship.label,
            "sprite": relationship.sprite,
            "tags": relationship.tags,
            "link": relationship.link,
            "index": relationship.index,
            "description": relationship.description,
            "technology": relationship.technology,
        }


class LayoutPlantUMLMacro(PlantUMLMacro[Layout]):
    """
    PlantUML macro renderer for `Layout` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="from"),
        Argument(name="to"),
    ]

    @override
    def get_macro(self) -> str:
        """
        Resolves the macro name based on the element's concrete class.
        """
        layout_type = self._diagram_element.layout_type

        return LAYOUT_TO_PLANTUML_MACRO_MAP[layout_type]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        layout = self._diagram_element

        return {
            "from": layout.from_element.alias,
            "to": layout.to_element.alias,
        }


class NodePlantUMLMacro(BoundaryPlantUMLMacro):
    """
    PlantUML macro renderer for `Node` instances.
    """

    args: ClassVar[list[Argument]] = [
        Argument(name="alias"),
        Argument(name="label", format=quote_and_escape),
        Argument(name="type", format=quote),
        Argument(name="descr", source="description", format=quote_and_escape),
        Argument.keyword(name="sprite", format=quote),
        Argument.keyword(name="tags", format=quote),
        Argument.keyword(name="link", format=quote),
    ]


class IncrementPlantUMLMacro(PlantUMLMacro[increment]):
    """
    PlantUML macro renderer for `increment` instances.
    """

    macro: ClassVar[str | None] = "increment"
    args: ClassVar[list[Argument]] = []


class SetIndexPlantUMLMacro(PlantUMLMacro[set_index]):
    """
    PlantUML macro renderer for `set_index` instances.
    """

    macro: ClassVar[str | None] = "setIndex"
    args: ClassVar[list[Argument]] = [
        Argument(name="new_index"),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        set_index_call = self._diagram_element

        return {
            "new_index": set_index_call.new_index,
        }


class DiagramLayoutPlantUMLMacro(PlantUMLMacro[DiagramLayout]):
    """
    PlantUML macro renderer for diagram layouts:
     - `LAYOUT_TOP_DOWN`
     - `LAYOUT_LEFT_RIGHT`
     - `LAYOUT_LANDSCAPE`.
    """

    @override
    def get_macro(self) -> str | None:
        """
        Returns the name of the PlantUML macro.
        """
        layout = self._diagram_element

        return cast(str, layout.value)


class LayoutWithLegendPlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `LAYOUT_WITH_LEGEND`.
    """

    macro: ClassVar[str | None] = "LAYOUT_WITH_LEGEND"


class LayoutAsSketchPlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `LAYOUT_AS_SKETCH`.
    """

    macro: ClassVar[str | None] = "LAYOUT_AS_SKETCH"


class HidePersonSpritePlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `HIDE_PERSON_SPRITE`.
    """

    macro: ClassVar[str | None] = "HIDE_PERSON_SPRITE"


class ShowPersonOutlinePlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `SHOW_PERSON_OUTLINE`.
    """

    macro: ClassVar[str | None] = "SHOW_PERSON_OUTLINE"


class ShowFootBoxesPlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `SHOW_FOOT_BOXES`.
    """

    macro: ClassVar[str | None] = "SHOW_FOOT_BOXES"


class ShowIndexPlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `SHOW_INDEX`.
    """

    macro: ClassVar[str | None] = "SHOW_INDEX"


class HideStereotypePlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `HIDE_STEREOTYPE`.
    """

    macro: ClassVar[str | None] = "HIDE_STEREOTYPE"


class ShowElementDescriptionsPlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `SHOW_ELEMENT_DESCRIPTIONS`.
    """

    macro: ClassVar[str | None] = "SHOW_ELEMENT_DESCRIPTIONS"


class WithoutPropertyHeaderPlantUMLMacro(PlantUMLMacroWithoutArgs):
    """
    PlantUML macro renderer for `WithoutPropertyHeader`.
    """

    macro: ClassVar[str | None] = "WithoutPropertyHeader"


class UpdateLegendTitlePlantUMLMacro(PlantUMLMacro[str]):
    """
    PlantUML macro renderer for `UpdateLegendTitle`.
    """

    macro: ClassVar[str | None] = "UpdateLegendTitle"
    args: ClassVar[list[Argument]] = [
        Argument(name="new_title", format=quote_and_escape),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        new_title = self._diagram_element

        return {
            "new_title": new_title,
        }


class SetSketchStylePlantUMLMacro(PlantUMLMacro[SetSketchStyle]):
    """
    PlantUML macro renderer for `SET_SKETCH_STYLE`.
    """

    macro: ClassVar[str | None] = "SET_SKETCH_STYLE"
    args: ClassVar[list[Argument]] = [
        Argument.keyword(
            name="bgColor",
            source="bg_color",
            format=quote,
        ),
        Argument.keyword(
            name="fontColor",
            source="font_color",
            format=quote,
        ),
        Argument.keyword(
            name="warningColor",
            source="warning_color",
            format=quote,
        ),
        Argument.keyword(
            name="fontName",
            source="font_name",
            format=quote,
        ),
        Argument.keyword(
            name="footerWarning",
            source="footer_warning",
            format=quote,
        ),
        Argument.keyword(
            name="footerText",
            source="footer_text",
            format=quote,
        ),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        return asdict(self._diagram_element)


class ShowLegendPlantUMLMacro(PlantUMLMacro[ShowLegend]):
    """
    PlantUML macro renderer for `SHOW_LEGEND`.
    """

    macro: ClassVar[str | None] = "SHOW_LEGEND"
    args: ClassVar[list[Argument]] = [
        Argument.keyword(
            name="hideStereotype",
            source="hide_stereotype",
            format=quote_and_lower,
        ),
        Argument.keyword(
            name="details",
            source="details",
            format=macro_call,
        ),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        element_tag = self._diagram_element

        return asdict(element_tag)


class ShowFloatingLegendPlantUMLMacro(PlantUMLMacro[ShowFloatingLegend]):
    """
    PlantUML macro renderer for `SHOW_FLOATING_LEGEND`.
    """

    macro: ClassVar[str | None] = "SHOW_FLOATING_LEGEND"
    args: ClassVar[list[Argument]] = [
        Argument(name="alias", source="alias", format=quote),
        Argument.keyword(
            name="hideStereotype",
            source="hide_stereotype",
            format=quote_and_lower,
        ),
        Argument.keyword(
            name="details",
            source="details",
            format=macro_call,
        ),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        element_tag = self._diagram_element

        return asdict(element_tag)


class ShowPersonSpritePlantUMLMacro(PlantUMLMacro[ShowPersonSprite]):
    """
    PlantUML macro renderer for `SHOW_PERSON_SPRITE`.
    """

    macro: ClassVar[str | None] = "SHOW_PERSON_SPRITE"
    args: ClassVar[list[Argument]] = [
        Argument(name="alias", source="alias", format=quote),
    ]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts relevant attributes from the element for rendering.
        """
        element_tag = self._diagram_element

        return asdict(element_tag)


class TagPlantUMLMacro(
    PlantUMLMacro[_TDiagramElement], Generic[_TDiagramElement]
):
    """
    Base class for PlantUML macros that render diagram elements associated
    with tags.

    This class is generic over the type of tag it handles
    (a subclass of `BaseTag`), and uses subclass registration to associate
    specific tags with their corresponding macros.

    Subclasses must declare a single generic type argument
    (e.g. TagPlantUMLMacro[ImportantTag]), which is used for tag dispatch.
    """

    __macro_by_type: ClassVar[dict[type[Any], type[TagPlantUMLMacro[Any]]]] = {}

    @override
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """
        Automatically registers the macro subclass for its associated tag type.

        The tag type is inferred from the generic argument
        (e.g., TagPlantUMLMacro[ImportantTag]).

        Raises:
            TypeError: If the tag type is missing or already registered.
        """
        super().__init_subclass__(*args, **kwargs)

        tag_type = cls._get_tag_type()

        if tag_type in cls.__macro_by_type:
            raise TypeError(
                f"Macro for {tag_type.__name__!r} already registered"
            )

        cls.__macro_by_type[tag_type] = cls

    @classmethod
    def _get_tag_type(cls) -> type[BaseTag]:
        """
        Infers the tag type used as a generic argument to the macro class.

        Returns:
            The tag type subclassed from `BaseTag`.

        Raises:
            TypeError: If multiple or no tag types are found.
        """
        possible_tags: list[type[BaseTag]] = []

        for base in get_original_bases(cls):
            origin = get_origin(base)
            if origin and issubclass(origin, TagPlantUMLMacro):
                possible_tags.extend(arg for arg in get_args(base))

        if not possible_tags or len(possible_tags) > 1:
            raise TypeError(
                f"{cls.__name__} must specify exactly one generic tag type, "
                f"got: {possible_tags}"
            )
        return possible_tags[0]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts tag-relevant attributes from the associated diagram element.

        Assumes that the diagram element is a dataclass.

        Returns:
            A dictionary of the element's attributes for macro rendering.

        Raises:
            TypeError: If the diagram element is not a dataclass.
        """
        element = self._diagram_element

        if not is_dataclass(element):
            raise TypeError(
                f"{type(element).__name__} must be a dataclass to extract "
                f"macro data"
            )

        return asdict(element)  # type: ignore[arg-type]

    @classmethod
    def get_macro_by_tag(
        cls, tag: BaseTag
    ) -> TagPlantUMLMacro[_TDiagramElement]:
        """
        Retrieve the PlantUML macro associated with the given tag.

        This method looks up the appropriate macro class based on
        the type of the provided tag instance and returns an instance
        of that macro.

        Args:
            tag: A BaseTag object specifying how the element should be rendered.

        Returns:
            An instance of the corresponding `TagPlantUMLMacro` subclass.

        Raises:
            ValueError: If no macro is registered for the given tag type.
        """
        try:
            macro_class = cls.__macro_by_type[type(tag)]
            return macro_class(tag)
        except KeyError:
            raise ValueError(
                f"No macro registered for tag type {type(tag).__name__}"
            ) from None


class ElementTagArgsMixin:
    """
    Mixin providing common style-related arguments for `ElementTag`
    and its subclasses.
    """

    args: ClassVar[list[Argument]] = [
        Argument(
            name="tagStereo",
            source="tag_stereo",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="bgColor",
            source="bg_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="fontColor",
            source="font_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderColor",
            source="border_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shadowing",
            source="shadowing",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shape",
            source="shape",
            format=macro_call,
        ),
        Argument.keyword(
            name="sprite",
            source="sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="techn",
            source="technology",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendText",
            source="legend_text",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendSprite",
            source="legend_sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderStyle",
            source="border_style",
            format=macro_call,
        ),
        Argument.keyword(
            name="borderThickness",
            source="border_thickness",
            format=quote_and_escape,
        ),
    ]


class AddElementTagPlantUMLMacro(
    ElementTagArgsMixin, TagPlantUMLMacro[ElementTag]
):
    """
    PlantUML macro renderer for `AddElementTag`.
    """

    macro: ClassVar[str | None] = "AddElementTag"


class AddRelTagPlantUMLMacro(ElementTagArgsMixin, TagPlantUMLMacro[RelTag]):
    """
    PlantUML macro renderer for `AddRelTag`.
    """

    macro: ClassVar[str | None] = "AddRelTag"
    args: ClassVar[list[Argument]] = [
        Argument(
            name="tagStereo", source="tag_stereo", format=quote_and_escape
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
            name="lineStyle",
            source="line_style",
            format=macro_call,
        ),
        Argument.keyword(
            name="lineThickness",
            source="line_thickness",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="techn",
            source="technology",
            format=quote_and_escape,
        ),
    ]


class AddBoundaryTagPlantUMLMacro(
    ElementTagArgsMixin, TagPlantUMLMacro[BoundaryTag]
):
    """
    PlantUML macro renderer for `AddBoundaryTag`.
    """

    macro: ClassVar[str | None] = "AddBoundaryTag"


class AddComponentTagPlantUMLMacro(
    ElementTagArgsMixin, TagPlantUMLMacro[ComponentTag]
):
    """
    PlantUML macro renderer for `AddComponentTag`.
    """

    macro: ClassVar[str | None] = "AddComponentTag"


class AddExternalComponentTagPlantUMLMacro(
    ElementTagArgsMixin, TagPlantUMLMacro[ExternalComponentTag]
):
    """
    PlantUML macro renderer for `AddExternalComponentTag`.
    """

    macro: ClassVar[str | None] = "AddExternalComponentTag"


class AddContainerTagPlantUMLMacro(
    ElementTagArgsMixin, TagPlantUMLMacro[ContainerTag]
):
    """
    PlantUML macro renderer for `AddContainerTag`.
    """

    macro: ClassVar[str | None] = "AddContainerTag"


class AddExternalContainerTagPlantUMLMacro(
    ElementTagArgsMixin, TagPlantUMLMacro[ExternalContainerTag]
):
    """
    PlantUML macro renderer for `AddExternalContainerTag`.
    """

    macro: ClassVar[str | None] = "AddExternalContainerTag"


class AddNodeTagPlantUMLMacro(ElementTagArgsMixin, TagPlantUMLMacro[NodeTag]):
    """
    PlantUML macro renderer for `AddNodeTag`.
    """

    macro: ClassVar[str | None] = "AddNodeTag"


class PersonTagArgsMixin:
    """
    Mixin providing common style-related arguments for `PersonTag`
    and its subclasses.
    """

    args: ClassVar[list[Argument]] = [
        Argument(
            name="tagStereo",
            source="tag_stereo",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="bgColor",
            source="bg_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="fontColor",
            source="font_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderColor",
            source="border_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shadowing",
            source="shadowing",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shape",
            source="shape",
            format=macro_call,
        ),
        Argument.keyword(
            name="sprite",
            source="sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="type",
            source="type_",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendText",
            source="legend_text",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendSprite",
            source="legend_sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderStyle",
            source="border_style",
            format=macro_call,
        ),
        Argument.keyword(
            name="borderThickness",
            source="border_thickness",
            format=quote_and_escape,
        ),
    ]


class AddPersonTagPlantUMLMacro(
    PersonTagArgsMixin, TagPlantUMLMacro[PersonTag]
):
    """
    PlantUML macro renderer for `AddPersonTag`.
    """

    macro: ClassVar[str | None] = "AddPersonTag"


class AddExternalPersonTagPlantUMLMacro(
    PersonTagArgsMixin, TagPlantUMLMacro[ExternalPersonTag]
):
    """
    PlantUML macro renderer for `AddExternalPersonTag`.
    """

    macro: ClassVar[str | None] = "AddExternalPersonTag"


class SystemTagArgsMixin:
    """
    Mixin providing common style-related arguments for `SystemTag`
    and its subclasses.
    """

    args: ClassVar[list[Argument]] = [
        Argument(
            name="tagStereo",
            source="tag_stereo",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="bgColor",
            source="bg_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="fontColor",
            source="font_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderColor",
            source="border_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shadowing",
            source="shadowing",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shape",
            source="shape",
            format=macro_call,
        ),
        Argument.keyword(
            name="sprite",
            source="sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="type",
            source="type_",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendText",
            source="legend_text",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendSprite",
            source="legend_sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderStyle",
            source="border_style",
            format=macro_call,
        ),
        Argument.keyword(
            name="borderThickness",
            source="border_thickness",
            format=quote_and_escape,
        ),
    ]


class AddSystemTagPlantUMLMacro(
    SystemTagArgsMixin, TagPlantUMLMacro[SystemTag]
):
    """
    PlantUML macro renderer for `AddSystemTag`.
    """

    macro: ClassVar[str | None] = "AddSystemTag"


class AddExternalSystemTagPlantUMLMacro(
    SystemTagArgsMixin, TagPlantUMLMacro[ExternalSystemTag]
):
    """
    PlantUML macro renderer for `AddExternalSystemTag`.
    """

    macro: ClassVar[str | None] = "AddExternalSystemTag"


class StylePlantUMLMacro(
    PlantUMLMacro[_TDiagramElement], Generic[_TDiagramElement]
):
    """
    Base class for PlantUML macros that apply visual styles to diagram elements.

    This class is generic over the type of element it styles, and uses subclass
    registration to associate specific styles with their corresponding macros.

    Subclasses must declare a single generic type argument
    (e.g. StylePlantUMLMacro[RelStyle]), which is used for style dispatch.
    """

    __macro_by_type: ClassVar[
        dict[type[Any], type[StylePlantUMLMacro[Any]]]
    ] = {}

    @override
    def __init_subclass__(cls, *args: Any, **kwargs: Any) -> None:
        """
        Automatically registers the macro subclass for its associated
        style type.

        The style type is inferred from the generic argument
        (e.g., StylePlantUMLMacro[ContainerStyle]).

        Raises:
            TypeError: If the style type is missing or already registered.
        """
        super().__init_subclass__(*args, **kwargs)

        style_type = cls._get_style_type()

        if style_type in cls.__macro_by_type:
            raise TypeError(
                f"Macro for {style_type.__name__!r} already registered"
            )

        cls.__macro_by_type[style_type] = cls

    @classmethod
    def _get_style_type(cls) -> type[BaseStyle]:
        """
        Infers the style type used as a generic argument to the macro class.

        Returns:
            The style type subclassed from `BaseStyle`.

        Raises:
            TypeError: If multiple or no style types are found.
        """
        possible_tags: list[type[BaseStyle]] = []

        for base in get_original_bases(cls):
            origin = get_origin(base)
            if origin and issubclass(origin, StylePlantUMLMacro):
                possible_tags.extend(arg for arg in get_args(base))

        if not possible_tags or len(possible_tags) > 1:
            raise TypeError(
                f"{cls.__name__} must specify exactly one generic style type, "
                f"got: {possible_tags}"
            )
        return possible_tags[0]

    @override
    def get_data(self) -> dict[str, Any]:
        """
        Extracts style-relevant attributes from the associated diagram element.

        Assumes that the diagram element is a dataclass.

        Returns:
            A dictionary of the element's attributes for macro rendering.

        Raises:
            TypeError: If the diagram element is not a dataclass.
        """
        element = self._diagram_element

        if not is_dataclass(element):
            raise TypeError(
                f"{type(element).__name__} must be a dataclass to extract "
                f"macro data"
            )

        return asdict(element)  # type: ignore[arg-type]

    @classmethod
    def get_macro_by_style(
        cls, style: BaseStyle
    ) -> StylePlantUMLMacro[_TDiagramElement]:
        """
        Retrieve the PlantUML macro associated with the given style.

        This method looks up the appropriate macro class based on the type
        of the provided style instance and returns an instance of that macro.

        Args:
            style: A BaseStyle object specifying how the element
                should be rendered.

        Returns:
            An instance of the corresponding `StylePlantUMLMacro` subclass.

        Raises:
            ValueError: If no macro is registered for the given style type.
        """
        try:
            macro_class = cls.__macro_by_type[type(style)]
            return macro_class(style)
        except KeyError:
            raise ValueError(
                f"No macro registered for style type {type(style).__name__}"
            ) from None


class UpdateElementStylePlantUMLMacro(StylePlantUMLMacro[ElementStyle]):
    """
    PlantUML macro renderer for `UpdateElementStyle`.
    """

    macro: ClassVar[str | None] = "UpdateElementStyle"
    args: ClassVar[list[Argument]] = [
        Argument(
            name="elementName",
            source="element_name",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="bgColor",
            source="bg_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="fontColor",
            source="font_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderColor",
            source="border_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shadowing",
            source="shadowing",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shape",
            source="shape",
            format=macro_call,
        ),
        Argument.keyword(
            name="sprite",
            source="sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="techn",
            source="technology",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendText",
            source="legend_text",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendSprite",
            source="legend_sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderStyle",
            source="border_style",
            format=macro_call,
        ),
        Argument.keyword(
            name="borderThickness",
            source="border_thickness",
            format=quote_and_escape,
        ),
    ]


class UpdateRelStylePlantUMLMacro(StylePlantUMLMacro[RelStyle]):
    """
    PlantUML macro renderer for `UpdateRelStyle`.
    """

    macro: ClassVar[str | None] = "UpdateRelStyle"
    args: ClassVar[list[Argument]] = [
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
    ]


class BoundaryStyleArgsMixin:
    """
    Mixin providing common style-related arguments for `BoundaryStyle`
    and its subclasses.
    """

    args: ClassVar[list[Argument]] = [
        Argument(
            name="elementName", source="element_name", format=quote_and_escape
        ),
        Argument.keyword(
            name="bgColor",
            source="bg_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="fontColor",
            source="font_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderColor",
            source="border_color",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shadowing",
            source="shadowing",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="shape",
            source="shape",
            format=macro_call,
        ),
        Argument.keyword(
            name="type",
            source="type_",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="sprite",
            source="sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="techn",
            source="technology",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendText",
            source="legend_text",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="legendSprite",
            source="legend_sprite",
            format=quote_and_escape,
        ),
        Argument.keyword(
            name="borderStyle",
            source="border_style",
            format=macro_call,
        ),
        Argument.keyword(
            name="borderThickness",
            source="border_thickness",
            format=quote_and_escape,
        ),
    ]


class UpdateBoundaryStylePlantUMLMacro(
    BoundaryStyleArgsMixin, StylePlantUMLMacro[BoundaryStyle]
):
    """
    PlantUML macro renderer for `UpdateBoundaryStyle`.
    """

    macro: ClassVar[str | None] = "UpdateBoundaryStyle"


class UpdateContainerBoundaryStylePlantUMLMacro(
    BoundaryStyleArgsMixin, StylePlantUMLMacro[ContainerBoundaryStyle]
):
    """
    PlantUML macro renderer for `UpdateContainerBoundaryStyle`.
    """

    macro: ClassVar[str | None] = "UpdateContainerBoundaryStyle"


class UpdateSystemBoundaryStylePlantUMLMacro(
    BoundaryStyleArgsMixin, StylePlantUMLMacro[SystemBoundaryStyle]
):
    """
    PlantUML macro renderer for `UpdateSystemBoundaryStyle`.
    """

    macro: ClassVar[str | None] = "UpdateSystemBoundaryStyle"


class UpdateEnterpriseBoundaryStylePlantUMLMacro(
    BoundaryStyleArgsMixin, StylePlantUMLMacro[EnterpriseBoundaryStyle]
):
    """
    PlantUML macro renderer for `UpdateEnterpriseBoundaryStyle`.
    """

    macro: ClassVar[str | None] = "UpdateEnterpriseBoundaryStyle"

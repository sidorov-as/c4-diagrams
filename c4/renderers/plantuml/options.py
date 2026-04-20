from dataclasses import dataclass, field
from enum import unique
from typing import Any, Literal

from typing_extensions import Self

from c4.compat import StrEnum


@unique
class DiagramLayout(StrEnum):
    """
    Defines layout direction options for a PlantUML diagram.

    This enum controls how diagram elements are arranged visually using
    predefined PlantUML layout macros.
    """

    LAYOUT_TOP_DOWN = "LAYOUT_TOP_DOWN"
    LAYOUT_LEFT_RIGHT = "LAYOUT_LEFT_RIGHT"
    LAYOUT_LANDSCAPE = "LAYOUT_LANDSCAPE"


TagShape = Literal["EightSidedShape", "RoundedBoxShape"]
LineStyle = Literal["DashedLine", "DottedLine", "BoldLine", "SolidLine"]
Details = Literal["Small", "Normal", "None"]


@dataclass
class BaseTag:
    """
    Base class for C4-PlantUML tag macros.

    Represents shared attributes for tags applied to diagram elements or
    relationships, including optional visual enhancements and legend metadata.

    Attributes:
        tag_stereo: Stereotype name of the tag. Must match one of the tags
            declared in the `tags` field of a diagram component.
        legend_text: The text shown in the legend for this tag.
        legend_sprite: The sprite displayed in the legend.
        sprite: The sprite icon associated with the element or relationship.
    """

    tag_stereo: str | None = None
    legend_text: str | None = None
    legend_sprite: str | None = None
    sprite: str | None = None


@dataclass
class ElementTag(BaseTag):
    """
    Represents a tag for general diagram elements
    (e.g., containers, nodes, components).

    Defines color, border, shape, and optional technology metadata.

    Attributes:
        bg_color: Background color of the element.
        font_color: Font color used for labels.
        border_color: Color of the element border.
        shadowing: Shadow style or toggle (e.g., "true", "false").
        shape: Optional shape used for rendering.
        technology: Technology label shown in the element.
        border_style: Border style (e.g., solid, dashed).
        border_thickness: Thickness of the borderline.
    """

    bg_color: str | None = None
    font_color: str | None = None
    border_color: str | None = None
    shadowing: bool | None = None
    shape: TagShape | None = None
    technology: str | None = None
    border_style: LineStyle | None = None
    border_thickness: str | None = None


@dataclass
class RelTag(BaseTag):
    """
    Represents a tag for relationship styling in the diagram.

    Includes text and line formatting, plus optional technology
    and sprite metadata.

    Attributes:
        text_color: Color of the relationship label.
        line_color: Color of the relationship line.
        line_style: Line style (e.g., solid, dashed).
        line_thickness: Thickness of the line.
        technology: Technology label associated with the relationship.
    """

    text_color: str | None = None
    line_color: str | None = None
    line_style: LineStyle | None = None
    line_thickness: str | None = None
    technology: str | None = None


@dataclass
class BoundaryTag(ElementTag):
    """
    Represents a tag for diagram boundaries (e.g., containers or systems).

    Inherits common styling options from ElementTag.
    """


@dataclass
class ComponentTag(ElementTag):
    """
    Represents a tag for internal software components.

    Inherits common styling options from ElementTag.
    """


@dataclass
class ExternalComponentTag(ComponentTag):
    """
    Represents a tag for external software components.

    Inherits common styling options from ComponentTag.
    """


@dataclass
class ContainerTag(ElementTag):
    """
    Represents a tag for internal containers (e.g., microservices, databases).

    Inherits common styling options from ElementTag.
    """


@dataclass
class ExternalContainerTag(ContainerTag):
    """
    Represents a tag for external containers.

    Inherits common styling options from ContainerTag.
    """


@dataclass
class NodeTag(ElementTag):
    """
    Represents a tag for nodes, typically infrastructure elements.

    Inherits common styling options from ElementTag.
    """


@dataclass
class PersonTag(BaseTag):
    """
    Represents a tag for internal Person elements (actors, users, roles).

    Attributes:
        bg_color: Background color of the person symbol.
        font_color: Font color used in the label.
        border_color: Border color of the symbol.
        shadowing: Whether shadowing is applied.
        shape: Optional shape used for rendering.
        type_: Person type (e.g., "person", "group").
        border_style: Border style (e.g., solid, dashed).
        border_thickness: Border thickness.
    """

    bg_color: str | None = None
    font_color: str | None = None
    border_color: str | None = None
    shadowing: bool | None = None
    shape: TagShape | None = None
    type_: str | None = None
    border_style: LineStyle | None = None
    border_thickness: str | None = None


@dataclass
class ExternalPersonTag(PersonTag):
    """
    Represents a tag for external people (actors outside the system boundary).

    Inherits common styling options from PersonTag.
    """


@dataclass
class SystemTag(BaseTag):
    """
    Represents a tag for internal software systems.

    Attributes:
        bg_color: Background color.
        font_color: Font color used in text.
        border_color: Color of the system border.
        shadowing: Shadow effect toggle.
        shape: Optional rendering shape.
        type_: Type of system (e.g., "software system").
        border_style: Style of the system border line.
        border_thickness: Thickness of the border.
    """

    bg_color: str | None = None
    font_color: str | None = None
    border_color: str | None = None
    shadowing: bool | None = None
    shape: TagShape | None = None
    type_: str | None = None
    border_style: LineStyle | None = None
    border_thickness: str | None = None


@dataclass
class ExternalSystemTag(SystemTag):
    """
    Represents a tag for external software systems.

    Inherits common styling options from SystemTag.
    """


@dataclass
class BaseStyle:
    """
    Base class for C4-PlantUML style update macros.

    Represents macro configurations that update the visual style
    of diagram elements or relationships.
    """


@dataclass
class ElementStyle(BaseStyle):
    """
    Defines style overrides for an individual diagram element.

    Attributes:
        element_name: Alias of the element to style.
        bg_color: Background color.
        font_color: Font/text color.
        border_color: Borderline color.
        shadowing: Shadow effect toggle.
        shape: Shape type used for rendering.
        sprite: Optional sprite icon.
        technology: Optional technology label.
        legend_text: Label used in the legend.
        legend_sprite: Sprite shown in the legend.
        border_style: Borderline style (e.g. dashed, solid).
        border_thickness: Thickness of the borderline.
    """

    element_name: str | None = None
    bg_color: str | None = None
    font_color: str | None = None
    border_color: str | None = None
    shadowing: bool | None = None
    shape: TagShape | None = None
    sprite: str | None = None
    technology: str | None = None
    legend_text: str | None = None
    legend_sprite: str | None = None
    border_style: LineStyle | None = None
    border_thickness: str | None = None


@dataclass
class RelStyle(BaseStyle):
    """
    Defines style overrides for relationship lines.

    Attributes:
        text_color: Color of the relationship label.
        line_color: Color of the connecting line.
    """

    text_color: str | None = None
    line_color: str | None = None


@dataclass
class BoundaryStyle(ElementStyle):
    """
    Defines style overrides for a boundary element (e.g. container, system).

    Attributes:
        type_: The type of boundary (e.g., "System", "Container").
    """

    type_: str | None = None


@dataclass
class ContainerBoundaryStyle(BoundaryStyle):
    """
    Defines style overrides for container boundaries.

    Inherits common styling options from BoundaryStyle.
    """


@dataclass
class SystemBoundaryStyle(BoundaryStyle):
    """
    Defines style overrides for system boundaries.

    Inherits common styling options from BoundaryStyle.
    """


@dataclass
class EnterpriseBoundaryStyle(BoundaryStyle):
    """
    Defines style overrides for enterprise boundaries.

    Inherits common styling options from BoundaryStyle.
    """


@dataclass
class ShowLegend:
    """
    Configuration for the SHOW_LEGEND macro in PlantUML.

    Controls the visibility and detail level of the diagram legend,
    which explains the meaning of applied tags and stereotypes.

    Attributes:
        hide_stereotype: Whether to hide stereotype labels in the legend.
        details: Level of detail to display ("Small", "Normal", or "None").
    """

    hide_stereotype: bool | None = None
    details: Details | None = None


@dataclass
class ShowFloatingLegend(ShowLegend):
    """
    Configuration for the SHOW_FLOATING_LEGEND macro.

    Similar to ShowLegend but renders the legend in a floating box
    that can be referenced and positioned using an alias.

    Attributes:
        alias: Optional alias name for the floating legend box.
    """

    alias: str | None = None


@dataclass
class ShowPersonSprite:
    """
    Configuration for the SHOW_PERSON_SPRITE macro.

    Displays a visual sprite next to person elements using a given alias.

    Attributes:
        alias: Optional sprite alias to use for the person icon.
    """

    alias: str | None = None


@dataclass
class SetSketchStyle:
    """
    Configuration for the SET_SKETCH_STYLE macro.

    Applies global sketch-style theming to the diagram, mimicking
    a hand-drawn appearance.

    Attributes:
        bg_color: Background color of the diagram.
        font_color: Font color for all text.
        warning_color: Color used for warning messages in the footer.
        font_name: Font family name to use.
        footer_warning: Optional warning message shown in the footer.
        footer_text: Optional text message shown in the footer.
    """

    bg_color: str | None = None
    font_color: str | None = None
    warning_color: str | None = None
    font_name: str | None = None
    footer_warning: str | None = None
    footer_text: str | None = None


@dataclass
class PlantUMLRenderOptions:
    """
    Final render options for rendering a C4-PlantUML diagram.

    This class encapsulates all layout directives, macros, tag definitions,
    and visual styles that should be applied to a diagram at render time.

    Attributes:
        includes: A list of PlantUML `!include` directives
            to be injected at the beginning of the diagram.
        layout: Layout direction (e.g., top-down, left-right, landscape).
        layout_with_legend: Whether to apply the LAYOUT_WITH_LEGEND macro.
        layout_as_sketch: Whether to apply the LAYOUT_AS_SKETCH macro.
        set_sketch_style: Optional sketch-style visual customization.
        show_legend: Configuration for SHOW_LEGEND macro.
        show_floating_legend: Configuration for SHOW_FLOATING_LEGEND macro.
        hide_stereotype: Whether to hide stereotype labels globally.
        hide_person_sprite: Whether to hide person sprites globally.
        show_person_sprite: Configuration for SHOW_PERSON_SPRITE macro.
        show_person_portrait: Whether to enable person portraits.
        show_person_outline: Whether to enable person outlines.
        without_property_header: If no header is used, then the second column
            is bold.
        legend_title: Optional title for the diagram legend.
        tags: List of tag macros (e.g., AddElementTag, AddRelTag).
        styles: List of style update macros (e.g., UpdateElementStyle).
    """

    includes: list[str] = field(default_factory=list)
    layout: DiagramLayout | None = None
    layout_with_legend: bool = False
    layout_as_sketch: bool = False
    set_sketch_style: SetSketchStyle | None = None
    show_legend: ShowLegend | None = None
    show_floating_legend: ShowFloatingLegend | None = None
    hide_stereotype: bool = False
    hide_person_sprite: bool = False
    show_person_sprite: ShowPersonSprite | None = None
    show_person_portrait: bool = False
    show_person_outline: bool = False
    without_property_header: bool = False
    legend_title: str | None = None
    tags: list[BaseTag] = field(default_factory=list)
    styles: list[BaseStyle] = field(default_factory=list)


class PlantUMLRenderOptionsBuilder:
    """
    Builder class for constructing PlantUMLRenderOptions.

    Provides a fluent API for incrementally defining styles and layout
    configuration.
    """

    def __init__(
        self,
    ) -> None:
        """Initialize an empty render options."""
        self._layout: DiagramLayout | None = None
        self._layout_with_legend = False
        self._layout_as_sketch = False
        self._set_sketch_style = False
        self._set_sketch_style_defaults = {
            "bg_color": None,
            "font_color": None,
            "warning_color": None,
            "font_name": None,
            "footer_warning": None,
            "footer_text": None,
        }
        self._set_sketch_style_args: dict[str, Any] = {}
        self._show_legend = False
        self._show_legend_defaults = {
            "hide_stereotype": True,
            "details": "Small",
        }
        self._show_legend_args: dict[str, Any] = {}
        self._show_floating_legend = False
        self._show_floating_legend_defaults = {
            "alias": None,
            "hide_stereotype": True,
            "details": "Small",
        }
        self._show_floating_legend_args: dict[str, Any] = {}
        self._legend_title: str | None = None
        self._hide_stereotype = False
        self._hide_person_sprite = False
        self._show_person_portrait = False
        self._show_person_outline = False
        self._show_person_sprite = False
        self._show_person_sprite_defaults = {
            "alias": None,
        }
        self._show_person_sprite_args: dict[str, Any] = {}
        self._without_property_header = False
        self._tags: list[BaseTag] = []
        self._styles: list[BaseStyle] = []
        self._includes: list[str] = []

    @property
    def sketch_style_defaults(self) -> dict[str, Any]:
        return self._set_sketch_style_defaults

    @property
    def legend_defaults(self) -> dict[str, Any]:
        return self._show_legend_defaults

    @property
    def floating_legend_defaults(self) -> dict[str, Any]:
        return self._show_floating_legend_defaults

    @property
    def person_sprite_defaults(self) -> dict[str, Any]:
        return self._show_person_sprite_defaults

    def add_element_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddElementTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = ElementTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_boundary_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddBoundaryTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = BoundaryTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_includes(
        self,
        *includes: str,
    ) -> Self:
        """
        Adds a list of PlantUML `!include` directives to be injected
        at the beginning of the diagram.

        Returns:
            The updated render options.
        """
        self._includes.extend(includes)

        return self

    def add_rel_tag(
        self,
        tag_stereo: str | None = None,
        text_color: str | None = None,
        line_color: str | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        line_style: LineStyle | None = None,
        line_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddRelTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            text_color: Text color.
            line_color: Line color.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            line_style: Line style.
            line_thickness: Line thickness.

        Returns:
            The updated render options.
        """
        tag = RelTag(
            tag_stereo=tag_stereo,
            text_color=text_color,
            line_color=line_color,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            line_style=line_style,
            line_thickness=line_thickness,
        )
        self._tags.append(tag)

        return self

    def add_component_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddComponentTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = ComponentTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_external_component_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddExternalComponentTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = ExternalComponentTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_container_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddContainerTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = ContainerTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_external_container_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddExternalContainerTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = ExternalContainerTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_node_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddNodeTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = NodeTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_person_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        type_: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddPersonTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            type_: Person type.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = PersonTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            type_=type_,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_external_person_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        type_: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddExternalPersonTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            type_: Person type.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = ExternalPersonTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            type_=type_,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_system_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        type_: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddSystemTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            type_: System type.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = SystemTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            type_=type_,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def add_external_system_tag(
        self,
        tag_stereo: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        type_: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an AddExternalSystemTag() macro configuration.

        Args:
            tag_stereo: The tag stereotype name.
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            type_: System type.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        tag = ExternalSystemTag(
            tag_stereo=tag_stereo,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            type_=type_,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._tags.append(tag)

        return self

    def update_element_style(
        self,
        element_name: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an UpdateElementStyle() macro configuration.

        Args:
            element_name: C4 element type to style
                (e.g. 'person', 'system', 'container').
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        style = ElementStyle(
            element_name=element_name,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
        )
        self._styles.append(style)

        return self

    def update_boundary_style(
        self,
        element_name: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        type_: str | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an UpdateBoundaryStyle() macro configuration.

        Args:
            element_name: C4 element type to style
                (e.g. 'person', 'system', 'container').
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            type_: Element type.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        style = BoundaryStyle(
            element_name=element_name,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
            type_=type_,
        )
        self._styles.append(style)

        return self

    def update_rel_style(
        self,
        text_color: str | None = None,
        line_color: str | None = None,
    ) -> Self:
        """
        Adds an UpdateRelStyle() macro configuration.

        Args:
            text_color: Text color.
            line_color: Line color.

        Returns:
            The updated render options.
        """
        style = RelStyle(
            text_color=text_color,
            line_color=line_color,
        )
        self._styles.append(style)

        return self

    def update_container_boundary_style(
        self,
        element_name: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        type_: str | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an UpdateContainerBoundaryStyle() macro configuration.

        Args:
            element_name: C4 element type to style
                (e.g. 'person', 'system', 'container').
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            type_: Element type.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        style = ContainerBoundaryStyle(
            element_name=element_name,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
            type_=type_,
        )
        self._styles.append(style)

        return self

    def update_system_boundary_style(
        self,
        element_name: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        type_: str | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an UpdateSystemBoundaryStyle() macro configuration.

        Args:
            element_name: C4 element type to style
                (e.g. 'person', 'system', 'container').
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            type_: Container type.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        style = SystemBoundaryStyle(
            element_name=element_name,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
            type_=type_,
        )
        self._styles.append(style)

        return self

    def update_enterprise_boundary_style(
        self,
        element_name: str | None = None,
        bg_color: str | None = None,
        font_color: str | None = None,
        border_color: str | None = None,
        shadowing: bool | None = None,
        shape: TagShape | None = None,
        type_: str | None = None,
        sprite: str | None = None,
        technology: str | None = None,
        legend_text: str | None = None,
        legend_sprite: str | None = None,
        border_style: LineStyle | None = None,
        border_thickness: str | None = None,
    ) -> Self:
        """
        Adds an UpdateEnterpriseBoundaryStyle() macro configuration.

        Args:
            element_name: C4 element type to style
                (e.g. 'person', 'system', 'container').
            bg_color: Background color.
            font_color: Font color.
            border_color: Border color.
            shadowing: Shadow effect setting.
            shape: Optional shape modifier.
            type_: Container type.
            sprite: Optional sprite reference.
            technology: Technology metadata.
            legend_text: Legend label.
            legend_sprite: Legend sprite.
            border_style: Border style.
            border_thickness: Border thickness.

        Returns:
            The updated render options.
        """
        style = EnterpriseBoundaryStyle(
            element_name=element_name,
            bg_color=bg_color,
            font_color=font_color,
            border_color=border_color,
            shadowing=shadowing,
            shape=shape,
            sprite=sprite,
            technology=technology,
            legend_text=legend_text,
            legend_sprite=legend_sprite,
            border_style=border_style,
            border_thickness=border_thickness,
            type_=type_,
        )
        self._styles.append(style)

        return self

    def layout_top_down(self, *, with_legend: bool = False) -> Self:
        """
        Sets the diagram layout to top-down orientation.

        Args:
            with_legend: Whether to include LAYOUT_WITH_LEGEND.

        Returns:
            The updated render options.
        """
        return self._set_layout(DiagramLayout.LAYOUT_TOP_DOWN, with_legend)

    def layout_left_right(self, *, with_legend: bool = False) -> Self:
        """
        Sets the diagram layout to left-right orientation.

        Args:
            with_legend: Whether to include LAYOUT_WITH_LEGEND.

        Returns:
            The updated render options.
        """
        return self._set_layout(DiagramLayout.LAYOUT_LEFT_RIGHT, with_legend)

    def layout_landscape(self, *, with_legend: bool = False) -> Self:
        """
        Sets the diagram layout to PlantUML landscape mode.

        Args:
            with_legend: Whether to include LAYOUT_WITH_LEGEND.

        Returns:
            The updated render options.
        """
        return self._set_layout(DiagramLayout.LAYOUT_LANDSCAPE, with_legend)

    def layout_with_legend(self) -> Self:
        """
        Enables LAYOUT_WITH_LEGEND macro.

        Returns:
            The updated render options.
        """
        self._layout_with_legend = True

        return self

    def layout_as_sketch(self) -> Self:
        """
        Enables LAYOUT_AS_SKETCH macro.

        Returns:
            The updated render options.
        """
        self._layout_as_sketch = True

        return self

    def without_property_header(self) -> Self:
        """
        Enables WithoutPropertyHeader macro.

        Returns:
            The updated render options.
        """
        self._without_property_header = True

        return self

    def set_sketch_style(
        self,
        bg_color: str | None = None,
        font_color: str | None = None,
        warning_color: str | None = None,
        font_name: str | None = None,
        footer_warning: str | None = None,
        footer_text: str | None = None,
    ) -> Self:
        """
        Enables SET_SKETCH_STYLE macro with optional customization.

        Args:
            bg_color: Background color of the sketch.
            font_color: Font color.
            warning_color: Color for footer warnings.
            font_name: Font family name.
            footer_warning: Warning message in the footer.
            footer_text: Custom footer text.

        Returns:
            The updated render options.
        """
        self._set_sketch_style = True

        defaults = self._set_sketch_style_defaults

        args = {
            "bg_color": bg_color,
            "font_color": font_color,
            "warning_color": warning_color,
            "font_name": font_name,
            "footer_warning": footer_warning,
            "footer_text": footer_text,
        }

        for arg, value in args.items():
            if value != defaults[arg]:
                self._set_sketch_style_args[arg] = value

        return self

    def show_legend(
        self,
        hide_stereotype: bool = True,
        details: Details = "Small",
    ) -> Self:
        """
        Enables SHOW_LEGEND macro with custom options.

        Args:
            hide_stereotype: Whether to hide stereotypes in the legend.
            details: Level of detail to show.

        Returns:
            The updated render options.
        """
        self._show_legend = True

        if hide_stereotype != self._show_legend_defaults["hide_stereotype"]:
            self._show_legend_args["hide_stereotype"] = hide_stereotype

        if details != self._show_legend_defaults["details"]:
            self._show_legend_args["details"] = details

        return self

    def show_floating_legend(
        self,
        alias: str | None = None,
        hide_stereotype: bool = True,
        details: Details = "Small",
    ) -> Self:
        """
        Enables SHOW_FLOATING_LEGEND macro with custom options.

        Args:
            alias: Optional legend alias.
            hide_stereotype: Whether to hide stereotypes in the legend.
            details: Level of detail to show.

        Returns:
            The updated render options.
        """
        self._show_floating_legend = True
        defaults = self._show_floating_legend_defaults

        if hide_stereotype != defaults["hide_stereotype"]:
            self._show_floating_legend_args["hide_stereotype"] = hide_stereotype

        if alias != defaults["alias"]:
            self._show_floating_legend_args["alias"] = alias

        if details != defaults["details"]:
            self._show_floating_legend_args["details"] = details

        return self

    def update_legend_title(self, new_title: str | None = None) -> Self:
        """
        Sets a custom title for the legend.

        Args:
            new_title: The title to display above the legend.

        Returns:
            The updated render options.
        """
        self._legend_title = new_title

        return self

    def show_person_outline(self) -> Self:
        """
        Enables SHOW_PERSON_OUTLINE macro.

        Returns:
            The updated render options.
        """
        self._show_person_outline = True

        return self

    def show_person_sprite(
        self,
        alias: str | None = None,
    ) -> Self:
        """
        Enables SHOW_PERSON_SPRITE macro with custom options.

        Args:
            alias: Optional sprite alias.

        Returns:
            The updated render options.
        """
        self._show_person_sprite = True
        defaults = self._show_person_sprite_defaults

        if alias != defaults["alias"]:
            self._show_person_sprite_args["alias"] = alias

        return self

    def hide_stereotype(self) -> Self:
        """
        Enables HIDE_STEREOTYPE macro.

        Returns:
            The updated render options.
        """
        self._hide_stereotype = True

        return self

    def hide_person_sprite(self) -> Self:
        """
        Enables HIDE_PERSON_SPRITE macro.

        Returns:
            The updated render options.
        """
        self._hide_person_sprite = True

        return self

    def show_person_portrait(self) -> Self:
        """
        Enables SHOW_PERSON_PORTRAIT macro.

        Returns:
            The updated render options.
        """
        self._show_person_portrait = True

        return self

    def _set_layout(
        self, layout: DiagramLayout, with_legend: bool = False
    ) -> Self:
        """
        Internal helper to apply a layout mode with optional legend.

        Args:
            layout: The layout orientation or mode.
            with_legend: Whether to enable LAYOUT_WITH_LEGEND in addition.

        Returns:
            The updated render options.
        """
        self._layout = layout

        if with_legend:
            self.layout_with_legend()

        return self

    def build(self) -> PlantUMLRenderOptions:
        """
        Build and return the final PlantUMLRenderOptions instance.

        Returns:
            A fully populated `PlantUMLRenderOptions` instance that can be
            passed to renderers.
        """
        show_legend = None
        set_sketch_style = None
        show_floating_legend = None
        show_person_sprite = None

        if self._show_legend:
            show_legend = ShowLegend(**self._show_legend_args)

        if self._show_floating_legend:
            show_floating_legend = ShowFloatingLegend(
                **self._show_floating_legend_args
            )

        if self._set_sketch_style:
            set_sketch_style = SetSketchStyle(**self._set_sketch_style_args)

        if self._show_person_sprite:
            show_person_sprite = ShowPersonSprite(
                **self._show_person_sprite_args
            )

        return PlantUMLRenderOptions(
            includes=self._includes,
            layout=self._layout,
            layout_with_legend=self._layout_with_legend,
            layout_as_sketch=self._layout_as_sketch,
            set_sketch_style=set_sketch_style,
            legend_title=self._legend_title,
            hide_person_sprite=self._hide_person_sprite,
            show_person_sprite=show_person_sprite,
            show_person_portrait=self._show_person_portrait,
            show_person_outline=self._show_person_outline,
            tags=self._tags,
            styles=self._styles,
            show_legend=show_legend,
            show_floating_legend=show_floating_legend,
            hide_stereotype=self._hide_stereotype,
            without_property_header=self._without_property_header,
        )

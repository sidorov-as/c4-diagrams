from __future__ import annotations

from enum import unique
from typing import Annotated, Any, ClassVar, Literal

from pydantic import ConfigDict, Field

from c4.compat.strenum import StrEnum
from c4.converters.json.schemas.base import BaseSchemaItem
from c4.converters.json.schemas.renderers.common import RenderOptionsItem
from c4.renderers.plantuml.options import (
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
    PlantUMLRenderOptions,
    RelStyle,
    RelTag,
    SetSketchStyle,
    ShowFloatingLegend,
    ShowLegend,
    ShowPersonSprite,
    SystemBoundaryStyle,
    SystemTag,
)

TypeAny = type[Any]


@unique
class TagShape(StrEnum):
    """Defines PlantUML tag shape."""

    EIGHT_SIDED_SHAPE = "EightSidedShape"
    ROUNDED_BOX_SHAPE = "RoundedBoxShape"


@unique
class LineStyle(StrEnum):
    """Defines PlantUML line style."""

    DASHED_LINE = "DashedLine"
    DOTTED_LINE = "DottedLine"
    BOLD_LINE = "BoldLine"
    SOLID_LINE = "SolidLine"


@unique
class Details(StrEnum):
    """Defines PlantUML legend details."""

    SMALL = "Small"
    NORMAL = "Normal"
    NONE = "None"


class WithType:
    type_: str | None = Field(
        None,
        description="Optional custom type/stereotype label.",
        alias="stereotype",
    )


class BaseTagSchema(RenderOptionsItem):
    """
    Base class for C4-PlantUML tag macros.

    Represents shared attributes for tags applied to diagram elements or
    relationships, including optional visual enhancements and legend metadata.
    """

    model_config = ConfigDict(use_enum_values=True)

    __model__: ClassVar[TypeAny] = BaseTag

    type: str = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    tag_stereo: str = Field(
        description=(
            "Stereotype name of the tag. "
            "Must match one of the tags declared in the `tags` field "
            "of a diagram component."
        )
    )
    legend_text: str | None = Field(
        None, description="Text shown in the diagram legend for this tag."
    )
    legend_sprite: str | None = Field(
        None, description="Sprite displayed in the legend for this tag."
    )
    sprite: str | None = Field(
        None,
        description="Sprite icon associated with the element or relationship.",
    )


class ElementTagSchema(BaseTagSchema):
    """
    Represents a tag for general diagram elements
    (containers, nodes, components).

    Defines color, border, shape, and optional technology metadata.
    """

    __model__: ClassVar[TypeAny] = ElementTag

    type: Literal["ElementTag"] = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    bg_color: str | None = Field(
        None, description="Background color of the element."
    )
    font_color: str | None = Field(
        None, description="Font color used for labels."
    )
    border_color: str | None = Field(
        None, description="Color of the element border."
    )
    shadowing: bool | None = Field(False, description="Shadow style/toggle.")
    shape: TagShape | None = Field(
        None, description="Optional shape macro used for rendering."
    )
    technology: str | None = Field(
        None, description="Technology label shown on the element."
    )
    border_style: LineStyle | None = Field(
        None, description="Border line style macro."
    )
    border_thickness: str | None = Field(
        None, description="Thickness of the element border line."
    )


class RelTagSchema(BaseTagSchema):
    """
    Represents a tag for relationship styling in the diagram.

    Includes text and line formatting, plus optional technology
    and sprite metadata.
    """

    __model__: ClassVar[TypeAny] = RelTag

    type: Literal["RelTag"] = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    text_color: str | None = Field(
        None, description="Color of the relationship label text."
    )
    line_color: str | None = Field(
        None, description="Color of the relationship line."
    )
    line_style: LineStyle | None = Field(
        None, description="Relationship line style macro."
    )
    line_thickness: str | None = Field(
        None, description="Thickness of the relationship line."
    )
    technology: str | None = Field(
        None, description="Technology label associated with the relationship."
    )


class BoundaryTagSchema(ElementTagSchema):
    """Tag for diagram boundaries (containers/systems)."""

    __model__: ClassVar[TypeAny] = BoundaryTag

    type: Literal["BoundaryTag"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class ComponentTagSchema(ElementTagSchema):
    """Tag for internal software components."""

    __model__: ClassVar[TypeAny] = ComponentTag

    type: Literal["ComponentTag"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class ExternalComponentTagSchema(ComponentTagSchema):
    """Tag for external software components."""

    __model__: ClassVar[TypeAny] = ExternalComponentTag

    type: Literal["ExternalComponentTag"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class ContainerTagSchema(ElementTagSchema):
    """Tag for internal containers (microservices, databases, etc.)."""

    __model__: ClassVar[TypeAny] = ContainerTag

    type: Literal["ContainerTag"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class ExternalContainerTagSchema(ContainerTagSchema):
    """Tag for external containers."""

    __model__: ClassVar[TypeAny] = ExternalContainerTag

    type: Literal["ExternalContainerTag"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class NodeTagSchema(ElementTagSchema):
    """Tag for nodes (typically infrastructure elements)."""

    __model__: ClassVar[TypeAny] = NodeTag

    type: Literal["NodeTag"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class PersonTagSchema(BaseTagSchema, WithType):
    """
    Tag for internal Person elements (actors, users, roles).
    """

    __model__: ClassVar[TypeAny] = PersonTag

    type: Literal["PersonTag"] = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    bg_color: str | None = Field(
        None, description="Background color of the person symbol."
    )
    font_color: str | None = Field(
        None, description="Font color used in the label."
    )
    border_color: str | None = Field(
        None, description="Border color of the person symbol."
    )
    shadowing: bool | None = Field(False, description="Shadow style/toggle.")
    shape: TagShape | None = Field(
        None, description="Optional shape macro used for rendering."
    )
    border_style: LineStyle | None = Field(
        None, description="Border line style macro."
    )
    border_thickness: str | None = Field(
        None, description="Thickness of the person border line."
    )


class ExternalPersonTagSchema(PersonTagSchema):
    """Tag for external people (outside the system boundary)."""

    __model__: ClassVar[TypeAny] = ExternalPersonTag

    type: Literal["ExternalPersonTag"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class SystemTagSchema(BaseTagSchema, WithType):
    """
    Tag for internal software systems.
    """

    __model__: ClassVar[TypeAny] = SystemTag

    type: Literal["SystemTag"] = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    bg_color: str | None = Field(
        None, description="Background color of the system element."
    )
    font_color: str | None = Field(
        None, description="Font color used in system labels."
    )
    border_color: str | None = Field(
        None, description="Border color of the system element."
    )
    shadowing: bool | None = Field(False, description="Shadow style/toggle.")
    shape: TagShape | None = Field(
        None, description="Optional shape macro used for rendering."
    )
    border_style: LineStyle | None = Field(
        None, description="Border line style macro."
    )
    border_thickness: str | None = Field(
        None, description="Thickness of the system border line."
    )


class ExternalSystemTagSchema(SystemTagSchema):
    """Tag for external software systems."""

    __model__: ClassVar[TypeAny] = ExternalSystemTag

    type: Literal["ExternalSystemTag"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class BaseStyleSchema(RenderOptionsItem):
    """
    Base class for C4-PlantUML style update macros.

    Represents macro configurations that update the visual style
    of diagram elements or relationships.
    """

    model_config = ConfigDict(use_enum_values=True)

    __model__: ClassVar[TypeAny] = BaseStyle

    type: str = Field(
        ...,
        description="Discriminator identifying the element type.",
    )


class ElementStyleSchema(BaseStyleSchema):
    """
    Style update for an individual diagram element.
    """

    __model__: ClassVar[TypeAny] = ElementStyle

    type: Literal["ElementStyle"] = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    element_name: str = Field(
        description=(
            "C4 element type to style (e.g. 'person', 'system', 'container')."
            " This applies to all elements of the given type, not "
            "a specific instance."
        )
    )
    bg_color: str | None = Field(None, description="Background color.")
    font_color: str | None = Field(None, description="Font/text color.")
    border_color: str | None = Field(None, description="Border line color.")
    shadowing: bool | None = Field(None, description="Shadow style/toggle.")
    shape: TagShape | None = Field(
        None, description="Shape macro used for rendering."
    )
    sprite: str | None = Field(
        None, description="Sprite icon applied to the element."
    )
    technology: str | None = Field(
        None, description="Technology label shown on the element."
    )
    legend_text: str | None = Field(
        None, description="Legend label for this styled element."
    )
    legend_sprite: str | None = Field(
        None, description="Legend sprite for this styled element."
    )
    border_style: LineStyle | None = Field(
        None, description="Border line style macro."
    )
    border_thickness: str | None = Field(
        None, description="Thickness of the border line."
    )


class RelStyleSchema(BaseStyleSchema):
    """
    Style update for relationship lines.
    """

    __model__: ClassVar[TypeAny] = RelStyle

    type: Literal["RelStyle"] = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    text_color: str | None = Field(
        None, description="Color of the relationship label text."
    )
    line_color: str | None = Field(
        None, description="Color of the relationship line."
    )


class BoundaryStyleSchema(ElementStyleSchema, WithType):
    """
    Style update for a boundary element (container/system/enterprise boundary).
    """

    __model__: ClassVar[TypeAny] = BoundaryStyle

    type: Literal["BoundaryStyle"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class ContainerBoundaryStyleSchema(BoundaryStyleSchema):
    """Style update for container boundaries."""

    __model__: ClassVar[TypeAny] = ContainerBoundaryStyle

    type: Literal["ContainerBoundaryStyle"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class SystemBoundaryStyleSchema(BoundaryStyleSchema):
    """Style update for system boundaries."""

    __model__: ClassVar[TypeAny] = SystemBoundaryStyle

    type: Literal["SystemBoundaryStyle"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class EnterpriseBoundaryStyleSchema(BoundaryStyleSchema):
    """Style update for enterprise boundaries."""

    __model__: ClassVar[TypeAny] = EnterpriseBoundaryStyle

    type: Literal["EnterpriseBoundaryStyle"] = Field(  # type: ignore[assignment]
        ...,
        description="Discriminator identifying the element type.",
    )


class ShowLegendSchema(RenderOptionsItem):
    """
    Configuration for the SHOW_LEGEND macro in PlantUML.
    """

    model_config = ConfigDict(use_enum_values=True)

    __model__: ClassVar[TypeAny] = ShowLegend

    hide_stereotype: bool | None = Field(
        default=None,
        description="Whether to hide stereotype labels in the legend.",
    )
    details: Details = Field(
        default=Details.SMALL,
        description="Legend detail level.",
    )


class ShowFloatingLegendSchema(ShowLegendSchema):
    """
    Configuration for the SHOW_FLOATING_LEGEND macro.
    """

    __model__: ClassVar[TypeAny] = ShowFloatingLegend

    alias: str | None = Field(
        default=None, description="Optional alias for the floating legend box."
    )


class ShowPersonSpriteSchema(RenderOptionsItem):
    """
    Configuration for the SHOW_PERSON_SPRITE macro.
    """

    __model__: ClassVar[TypeAny] = ShowPersonSprite

    alias: str | None = Field(
        default=None,
        description="Optional sprite alias used for the person icon.",
    )


class SetSketchStyleSchema(RenderOptionsItem):
    """
    Configuration for the SET_SKETCH_STYLE macro.
    """

    __model__: ClassVar[TypeAny] = SetSketchStyle

    bg_color: str | None = Field(
        default=None, description="Background color of the diagram."
    )
    font_color: str | None = Field(
        default=None, description="Font color for all diagram text."
    )
    warning_color: str | None = Field(
        default=None,
        description="Color used for warning messages in the footer.",
    )
    font_name: str | None = Field(
        default=None, description="Font family name to use."
    )
    footer_warning: str | None = Field(
        default=None,
        description="Optional warning message shown in the footer.",
    )
    footer_text: str | None = Field(
        default=None, description="Optional footer text message."
    )


AnyTag = Annotated[
    (
        ElementTagSchema
        | BoundaryTagSchema
        | ComponentTagSchema
        | ExternalComponentTagSchema
        | ContainerTagSchema
        | ExternalContainerTagSchema
        | NodeTagSchema
        | RelTagSchema
        | PersonTagSchema
        | ExternalPersonTagSchema
        | SystemTagSchema
        | ExternalSystemTagSchema
    ),
    Field(discriminator="type"),
]

AnyStyle = Annotated[
    (
        ElementStyleSchema
        | BoundaryStyleSchema
        | ContainerBoundaryStyleSchema
        | SystemBoundaryStyleSchema
        | EnterpriseBoundaryStyleSchema
        | RelStyleSchema
    ),
    Field(discriminator="type"),
]


class PlantUMLRenderOptionsSchema(BaseSchemaItem):
    """
    Final layout configuration for rendering a C4-PlantUML diagram.

    Encapsulates layout directives, macros, tag definitions, and visual styles
    applied at render time.
    """

    includes: list[str] = Field(
        default_factory=list,
        description=(
            "A list of PlantUML `!include` directives "
            "to be injected at the beginning of the diagram."
        ),
    )
    layout: DiagramLayout | None = Field(
        default=None, description="Layout direction."
    )
    layout_with_legend: bool = Field(
        default=False,
        description="Whether to apply the LAYOUT_WITH_LEGEND macro.",
    )
    layout_as_sketch: bool = Field(
        default=False,
        description="Whether to apply the LAYOUT_AS_SKETCH macro.",
    )
    set_sketch_style: SetSketchStyleSchema | None = Field(
        default=None,
        description="Optional sketch-style visual customization.",
    )
    show_legend: ShowLegendSchema | None = Field(
        default=None,
        description="Configuration for the SHOW_LEGEND macro.",
    )
    show_floating_legend: ShowFloatingLegendSchema | None = Field(
        default=None,
        description="Configuration for the SHOW_FLOATING_LEGEND macro.",
    )
    hide_stereotype: bool = Field(
        default=False, description="Whether to hide stereotype labels globally."
    )
    hide_person_sprite: bool = Field(
        default=False, description="Whether to hide person sprites globally."
    )
    show_person_sprite: ShowPersonSpriteSchema | None = Field(
        default=None,
        description="Configuration for the SHOW_PERSON_SPRITE macro.",
    )
    show_person_portrait: bool = Field(
        default=False, description="Whether to enable person portraits."
    )
    show_person_outline: bool = Field(
        default=False, description="Whether to enable person outlines."
    )
    without_property_header: bool = Field(
        default=False,
        description=(
            "If true, omit the header row and render the second column in bold."
        ),
    )
    legend_title: str | None = Field(
        default=None, description="Optional title displayed above the legend."
    )
    tags: list[AnyTag] = Field(
        default_factory=list,
        description="List of tag macro configurations.",
    )
    styles: list[AnyStyle] = Field(
        default_factory=list,
        description="List of style update macro configurations.",
    )

    def to_render_options(self) -> PlantUMLRenderOptions:
        """
        Returns the render options object.
        """
        kwargs: dict[str, Any] = {
            "tags": [],
            "styles": [],
        }

        for field in self.__pydantic_fields__:
            if field in {"tags", "styles"}:
                continue

            value = getattr(self, field, None)
            if value and isinstance(value, RenderOptionsItem):
                kwargs[field] = value.to_model()
            else:
                kwargs[field] = value

        for tag in self.tags:
            kwargs["tags"].append(tag.to_model())

        for style in self.styles:
            kwargs["styles"].append(style.to_model())

        return PlantUMLRenderOptions(**kwargs)

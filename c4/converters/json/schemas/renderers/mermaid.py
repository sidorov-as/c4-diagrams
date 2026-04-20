from typing import Annotated, Any, ClassVar, Literal

from pydantic import Field

from c4.converters.json.schemas.base import BaseSchemaItem
from c4.converters.json.schemas.renderers.common import RenderOptionsItem
from c4.renderers import MermaidRenderOptions
from c4.renderers.mermaid.options import (
    BaseStyle,
    ElementStyle,
    RelStyle,
    UpdateLayoutConfig,
)

TypeAny = type[Any]


class BaseStyleSchema(RenderOptionsItem):
    """
    Base class for Mermaid C4 style update macros.

    Represents macro configurations that update the visual style
    of diagram elements.
    """

    __model__: ClassVar[TypeAny] = BaseStyle

    type: str = Field(
        ...,
        description="Discriminator identifying the element type.",
    )


class MermaidElementStyleSchema(BaseStyleSchema):
    """
    Style update for an individual diagram element.
    """

    __model__: ClassVar[TypeAny] = ElementStyle

    type: Literal["ElementStyle"] = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    element: str = Field(description="Alias of the element to style.")
    bg_color: str | None = Field(None, description="Background color.")
    font_color: str | None = Field(None, description="Font/text color.")
    border_color: str | None = Field(None, description="Border line color.")


class MermaidRelStyleSchema(BaseStyleSchema):
    """
    Style update for relationship lines.
    """

    __model__: ClassVar[TypeAny] = RelStyle

    type: Literal["RelStyle"] = Field(
        ...,
        description="Discriminator identifying the element type.",
    )

    from_element: str = Field(
        description="Alias of the source element to style."
    )
    to_element: str = Field(description="Alias of the target element to style.")
    text_color: str | None = Field(
        None, description="Color of the relationship label text."
    )
    line_color: str | None = Field(
        None, description="Color of the relationship line."
    )
    offset_x: int | None = Field(
        None, description="Optional horizontal offset for the label position."
    )
    offset_y: int | None = Field(
        None, description="Optional horizontal offset for the label position."
    )


AnyStyle = Annotated[
    MermaidElementStyleSchema | MermaidRelStyleSchema,
    Field(discriminator="type"),
]


class UpdateLayoutConfigSchema(RenderOptionsItem):
    """
    Configuration for updating default layout behavior in
    Mermaid C4 diagrams.
    """

    __model__: ClassVar[TypeAny] = UpdateLayoutConfig

    c4_shape_in_row: int | None = Field(
        None,
        description=(
            "Maximum number of non-boundary elements "
            "(e.g. systems, containers, components) per row."
        ),
    )
    c4_boundary_in_row: int | None = Field(
        None, description="Maximum number of boundaries per row."
    )


class MermaidRenderOptionsSchema(BaseSchemaItem):
    """
    Final layout configuration for rendering a Mermaid C4 diagram.

    Encapsulates layout directives, macros, tag definitions, and visual styles
    applied at render time.
    """

    styles: list[AnyStyle] = Field(
        default_factory=list,
        description="List of style update macro configurations.",
    )
    update_layout_config: UpdateLayoutConfigSchema | None = Field(
        None, description="Configuration for updating default layout behavior."
    )

    def to_render_options(self) -> MermaidRenderOptions:
        """
        Returns the render options object.
        """
        kwargs: dict[str, Any] = {
            "styles": [],
        }

        for field in self.__pydantic_fields__:
            if field in {"styles"}:
                continue

            value = getattr(self, field, None)
            if value and isinstance(value, RenderOptionsItem):
                kwargs[field] = value.to_model()

        for style in self.styles:
            kwargs["styles"].append(style.to_model())

        return MermaidRenderOptions(**kwargs)

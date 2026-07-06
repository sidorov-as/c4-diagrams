from __future__ import annotations

from typing import Any, ClassVar, Literal

from pydantic import ConfigDict, Field

from c4.contrib.d2.extensions import D2StyleValue
from c4.converters.json.schemas.base import BaseSchemaItem
from c4.renderers.d2.options import (
    D2Layout,
    D2Legend,
    D2LegendElement,
    D2LegendRel,
    D2NearPosition,
    D2RenderOptions,
)

TypeAny = type[Any]


class D2StyleSchema(BaseSchemaItem):
    """D2 style attributes used by D2 render options."""

    model_config = ConfigDict(extra="forbid")

    opacity: float | None = Field(None, ge=0, le=1)
    stroke: str | None = None
    fill: str | None = None
    fill_pattern: str | None = None
    stroke_width: int | None = None
    stroke_dash: int | None = None
    border_radius: int | None = None
    shadow: bool | None = None
    three_d: bool | None = None
    multiple: bool | None = None
    double_border: bool | None = None
    font: str | None = None
    font_size: int | None = None
    font_color: str | None = None
    animated: bool | None = None
    bold: bool | None = None
    italic: bool | None = None
    underline: bool | None = None
    text_transform: str | None = None

    def to_model(self) -> dict[str, D2StyleValue]:
        """Return style data using runtime extension key names."""
        return {  # pragma: no branch
            key: value
            for key, value in self.model_dump(mode="python").items()
            if value is not None
        }


class D2LegendItemSchema(BaseSchemaItem):
    """Base schema for structured D2 legend items."""

    model_config = ConfigDict(extra="forbid")

    __model__: ClassVar[TypeAny]

    type: str = Field(..., description="Legend item discriminator.")
    label: str = Field(..., description="Legend item label.")
    alias: str | None = Field(None, description="Optional D2 identifier.")
    style: D2StyleSchema | None = None
    classes: list[str] | None = None

    def to_model(self) -> Any:
        kwargs = self.model_dump(mode="python", exclude={"type", "style"})
        if self.style is not None:  # pragma: no branch
            kwargs["style"] = self.style.to_model()

        return self.__model__(**kwargs)


class D2LegendElementSchema(D2LegendItemSchema):
    """Schema for a D2 legend node sample."""

    __model__: ClassVar[TypeAny] = D2LegendElement

    type: Literal["element"] = Field(
        ..., description="Legend item discriminator."
    )
    shape: str | None = None
    icon: str | None = None


class D2LegendRelSchema(D2LegendItemSchema):
    """Schema for a D2 legend relationship sample."""

    __model__: ClassVar[TypeAny] = D2LegendRel

    type: Literal["relationship"] = Field(
        ..., description="Legend item discriminator."
    )
    source: str | None = None
    target: str | None = None
    bidirectional: bool = False
    hide_endpoints: bool | None = None


AnyD2LegendItemSchema = D2LegendElementSchema | D2LegendRelSchema


class D2LegendSchema(BaseSchemaItem):
    """Structured D2 legend render options."""

    model_config = ConfigDict(extra="forbid")

    label: str = "Legend"
    items: list[AnyD2LegendItemSchema] = Field(default_factory=list)

    def to_model(self) -> D2Legend:
        return D2Legend(
            label=self.label,
            items=[item.to_model() for item in self.items],  # pragma: no branch
        )


class D2RenderOptionsSchema(BaseSchemaItem):
    """Render options for the D2 renderer."""

    model_config = ConfigDict(extra="forbid")

    direction: Literal["up", "down", "left", "right"] | None = "right"
    layout: D2Layout = "dagre"
    theme: int | None = Field(None, ge=0)
    title_near: D2NearPosition | None = "top-center"
    sequence_diagram: bool = False
    auto_number_relationships: bool = False
    include_type_label: bool = True
    include_technology: bool = True
    include_properties: bool = False
    bidirectional_relationships: Literal["two_edges", "single_edge"] = (
        "two_edges"
    )
    fully_qualified_relationships: bool = True
    legend: D2LegendSchema | None = None

    def to_render_options(self) -> D2RenderOptions:
        """Return the D2 render options object."""
        kwargs: dict[str, Any] = self.model_dump(
            mode="python", exclude={"legend"}
        )
        if self.legend is not None:
            kwargs["legend"] = self.legend.to_model()

        return D2RenderOptions(**kwargs)

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, cast

from typing_extensions import Self

from c4.contrib.d2.extensions import D2StyleValue, StyleExtensions
from c4.renderers.d2.constants import (
    _D2_STYLE_BOOLEAN_KEYS,
    _D2_STYLE_INTEGER_KEYS,
    _D2_STYLE_KEYS,
    _D2_STYLE_STRING_KEYS,
)
from c4.renderers.d2.identifiers import D2IdentifierPolicy

D2Direction = Literal["up", "down", "left", "right"]
D2Layout = Literal["dagre", "elk"]
D2BidirectionalRelationshipStrategy = Literal["two_edges", "single_edge"]
D2NearPosition = Literal[
    "top-left",
    "top-center",
    "top-right",
    "center-left",
    "center-right",
    "bottom-left",
    "bottom-center",
    "bottom-right",
]

_D2_DIRECTIONS = ("up", "down", "left", "right")
_D2_LAYOUTS = ("dagre", "elk")
_D2_BIDIRECTIONAL_RELATIONSHIP_STRATEGIES = ("two_edges", "single_edge")
_D2_NEAR_POSITIONS = (
    "top-left",
    "top-center",
    "top-right",
    "center-left",
    "center-right",
    "bottom-left",
    "bottom-center",
    "bottom-right",
)


@dataclass(frozen=True)
class D2LegendElement:
    """A D2 legend node sample."""

    label: str
    alias: str | None = None
    shape: str | None = None
    style: StyleExtensions | dict[str, D2StyleValue] | None = None
    icon: str | None = None
    classes: list[str] | None = None


@dataclass(frozen=True)
class D2LegendRel:
    """A D2 legend relationship sample."""

    label: str
    alias: str | None = None
    source: str | None = None
    target: str | None = None
    bidirectional: bool = False
    style: StyleExtensions | dict[str, D2StyleValue] | None = None
    classes: list[str] | None = None
    hide_endpoints: bool | None = None


@dataclass(frozen=True)
class D2Legend:
    """Structured D2 legend render options."""

    label: str = "Legend"
    items: list[D2LegendElement | D2LegendRel] = field(default_factory=list)


@dataclass(frozen=True)
class D2RenderOptions:
    """
    Render options for the D2 renderer.

    Attributes:
        direction: Overall diagram layout direction. Set to `None` to omit the
            D2 direction directive.
        layout: D2 layout engine used by image export backends.
        theme: Optional D2 theme ID.
        title_near: Optional D2 `near` placement for generated title nodes.
            Set to `None` to preserve the title without forcing placement.
        sequence_diagram: Whether DynamicDiagram output should be emitted as a
            D2 sequence diagram.
        auto_number_relationships: Whether relationship labels should be
            prefixed with their render order.
        include_type_label: Whether element type labels appear in Markdown
            labels.
        include_technology: Whether element technology appears in labels.
        include_properties: Whether element properties are emitted.
        bidirectional_relationships: How bidirectional relationships are
            rendered. ``"two_edges"`` preserves the existing behavior;
            ``"single_edge"`` emits one D2 ``<->`` edge.
        fully_qualified_relationships: Whether relationship endpoints always
            use fully qualified D2 paths.
        legend: Optional structured D2 legend.
    """

    direction: D2Direction | None = "right"
    layout: D2Layout = "dagre"
    theme: int | None = None
    title_near: D2NearPosition | None = "top-center"
    sequence_diagram: bool = False
    auto_number_relationships: bool = False
    include_type_label: bool = True
    include_technology: bool = True
    include_properties: bool = False
    bidirectional_relationships: D2BidirectionalRelationshipStrategy = (
        "two_edges"
    )
    fully_qualified_relationships: bool = True
    legend: D2Legend | None = None

    def __post_init__(self) -> None:
        """Validate render option values."""
        if self.direction is not None and self.direction not in _D2_DIRECTIONS:
            directions = ", ".join(
                repr(direction) for direction in _D2_DIRECTIONS
            )
            raise ValueError(
                f"D2 direction must be one of {directions}, or None. "
                f"Got {self.direction!r}."
            )

        if self.layout not in _D2_LAYOUTS:
            layouts = ", ".join(repr(layout) for layout in _D2_LAYOUTS)
            raise ValueError(
                f"D2 layout must be one of {layouts}. Got {self.layout!r}."
            )

        if self.theme is not None:
            if isinstance(self.theme, bool) or not isinstance(self.theme, int):
                raise TypeError(
                    "D2 theme must be None or a non-negative integer theme ID. "
                    f"Got {self.theme!r}."
                )

            if self.theme < 0:
                raise ValueError(
                    "D2 theme must be None or a non-negative integer theme ID. "
                    f"Got {self.theme!r}."
                )

        if (
            self.title_near is not None
            and self.title_near not in _D2_NEAR_POSITIONS
        ):
            positions = ", ".join(
                repr(position) for position in _D2_NEAR_POSITIONS
            )
            raise ValueError(
                f"D2 title near position must be one of {positions}, or None. "
                f"Got {self.title_near!r}."
            )

        if (
            self.bidirectional_relationships
            not in _D2_BIDIRECTIONAL_RELATIONSHIP_STRATEGIES
        ):
            strategies = ", ".join(
                repr(strategy)
                for strategy in _D2_BIDIRECTIONAL_RELATIONSHIP_STRATEGIES
            )
            raise ValueError(
                "D2 bidirectional relationship strategy must be one of "
                f"{strategies}. Got {self.bidirectional_relationships!r}."
            )

        _validate_legend(self.legend)


class D2RenderOptionsBuilder:
    """Builder for constructing D2RenderOptions."""

    def __init__(self) -> None:
        """Initialize a builder with default D2 render options."""
        self._direction: D2Direction | None = "right"
        self._layout: D2Layout = "dagre"
        self._theme: int | None = None
        self._title_near: D2NearPosition | None = "top-center"
        self._sequence_diagram = False
        self._auto_number_relationships = False
        self._include_type_label = True
        self._include_technology = True
        self._include_properties = False
        self._bidirectional_relationships = cast(
            D2BidirectionalRelationshipStrategy,
            "two_edges",
        )
        self._fully_qualified_relationships = True
        self._legend: D2Legend | None = None

    def direction(self, direction: D2Direction | None) -> Self:
        """
        Set the D2 layout direction.

        Args:
            direction: One of `"up"`, `"down"`, `"left"`, `"right"`, or
                `None` to omit the directive.

        Returns:
            The updated render options builder.
        """
        D2RenderOptions(direction=direction)
        self._direction = direction

        return self

    def layout(self, layout: D2Layout) -> Self:
        """
        Set the D2 layout engine for image export.

        Args:
            layout: One of `"dagre"` or `"elk"`.

        Returns:
            The updated render options builder.
        """
        D2RenderOptions(layout=layout)
        self._layout = layout

        return self

    def theme(self, theme: int | None) -> Self:
        """
        Set the D2 theme ID.

        Args:
            theme: A non-negative integer D2 theme ID, or `None` to omit it.

        Returns:
            The updated render options builder.
        """
        D2RenderOptions(theme=theme)
        self._theme = theme

        return self

    def title_near(self, position: D2NearPosition | None) -> Self:
        """
        Set the generated diagram title placement.

        Args:
            position: One of the supported D2 `near` positions, or `None` to
                render the title node without forcing placement.

        Returns:
            The updated render options builder.
        """
        D2RenderOptions(title_near=position)
        self._title_near = position

        return self

    def sequence_diagram(self, enabled: bool = True) -> Self:
        """
        Render DynamicDiagram output as a D2 sequence diagram.

        Args:
            enabled: Whether DynamicDiagram output should include
                ``shape: sequence_diagram``.

        Returns:
            The updated render options builder.
        """
        self._sequence_diagram = enabled

        return self

    def auto_number_relationships(self, enabled: bool = True) -> Self:
        """
        Prefix relationship labels with their render order.

        Args:
            enabled: Whether relationship labels should be prefixed with
                ``"1. "``, ``"2. "``, etc.

        Returns:
            The updated render options builder.
        """
        self._auto_number_relationships = enabled

        return self

    def include_technology(self, enabled: bool = True) -> Self:
        """
        Include or omit technology from visible element labels.

        Args:
            enabled: Whether technology should be included.

        Returns:
            The updated render options builder.
        """
        self._include_technology = enabled

        return self

    def include_type_label(self, enabled: bool = True) -> Self:
        """
        Include or omit element type labels from Markdown labels.

        Args:
            enabled: Whether type labels should be included.

        Returns:
            The updated render options builder.
        """
        self._include_type_label = enabled

        return self

    def include_properties(self, enabled: bool = True) -> Self:
        """
        Include or omit element properties in D2 output.

        Args:
            enabled: Whether properties should be included.

        Returns:
            The updated render options builder.
        """
        self._include_properties = enabled

        return self

    def bidirectional_relationships(
        self,
        strategy: D2BidirectionalRelationshipStrategy,
    ) -> Self:
        """
        Set how bidirectional relationships are rendered.

        Args:
            strategy: ``"two_edges"`` or ``"single_edge"``.

        Returns:
            The updated render options builder.
        """
        D2RenderOptions(bidirectional_relationships=strategy)
        self._bidirectional_relationships = strategy

        return self

    def fully_qualified_relationships(self, enabled: bool = True) -> Self:
        """
        Use fully qualified D2 paths for relationship endpoints.

        Args:
            enabled: Whether relationship endpoints should always use full
                nested D2 paths.

        Returns:
            The updated render options builder.
        """
        self._fully_qualified_relationships = enabled

        return self

    def legend(self, legend: D2Legend | None) -> Self:
        """
        Set a structured D2 legend.

        Args:
            legend: Legend options, or `None` to omit the D2 legend block.

        Returns:
            The updated render options builder.
        """
        D2RenderOptions(legend=legend)
        self._legend = legend

        return self

    def build(self) -> D2RenderOptions:
        """Build and return the final D2RenderOptions instance."""
        return D2RenderOptions(
            direction=self._direction,
            layout=self._layout,
            theme=self._theme,
            title_near=self._title_near,
            sequence_diagram=self._sequence_diagram,
            auto_number_relationships=self._auto_number_relationships,
            include_type_label=self._include_type_label,
            include_technology=self._include_technology,
            include_properties=self._include_properties,
            bidirectional_relationships=self._bidirectional_relationships,
            fully_qualified_relationships=self._fully_qualified_relationships,
            legend=self._legend,
        )

    @classmethod
    def default(cls) -> Self:
        """Return a new builder with default D2 render options."""
        return cls()


def _validate_legend(legend: D2Legend | None) -> None:
    if legend is None:
        return

    if not isinstance(legend, D2Legend):
        raise TypeError(f"D2 legend must be D2Legend or None. Got {legend!r}.")

    if not isinstance(legend.label, str):
        raise TypeError("D2 legend label must be a string.")

    reserved_identifiers: set[str] = set()

    for index, item in enumerate(legend.items, start=1):
        if not isinstance(item, (D2LegendElement, D2LegendRel)):
            raise TypeError(
                "D2 legend items must be D2LegendElement or D2LegendRel. "
                f"Got {item!r}."
            )

        _validate_legend_item(item)
        item_identifier = item.alias or f"legend_{index}"
        _reserve_legend_identifier(reserved_identifiers, item_identifier)

        if isinstance(item, D2LegendRel):
            generated_endpoints = item.source is None and item.target is None
            if generated_endpoints:
                _reserve_legend_identifier(
                    reserved_identifiers,
                    f"{item_identifier}_source",
                )
                _reserve_legend_identifier(
                    reserved_identifiers,
                    f"{item_identifier}_target",
                )


def _validate_legend_item(item: D2LegendElement | D2LegendRel) -> None:
    if not isinstance(item.label, str):
        raise TypeError("D2 legend item label must be a string.")

    _validate_optional_identifier(item.alias, "D2 legend item alias")
    _validate_optional_classes(item.classes)
    _validate_style(item.style)

    if isinstance(item, D2LegendElement):
        _validate_optional_string(item.shape, "D2 legend element shape")
        _validate_optional_string(item.icon, "D2 legend element icon")
        return

    if (item.source is None) != (item.target is None):
        raise ValueError(
            "D2 legend relationship source and target must either both be "
            "provided or both be omitted."
        )

    _validate_optional_identifier(item.source, "D2 legend relationship source")
    _validate_optional_identifier(item.target, "D2 legend relationship target")

    if not isinstance(item.bidirectional, bool):
        raise TypeError(
            "D2 legend relationship bidirectional must be a boolean."
        )

    if item.hide_endpoints is not None and not isinstance(
        item.hide_endpoints,
        bool,
    ):
        raise TypeError(
            "D2 legend relationship hide_endpoints must be a boolean or None."
        )


def _validate_optional_identifier(value: str | None, name: str) -> None:
    if value is None:
        return

    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string or None.")

    if D2IdentifierPolicy.sanitize(value) != value:
        raise ValueError(
            f"{name} must be a valid D2 identifier. Got {value!r}."
        )


def _reserve_legend_identifier(
    reserved_identifiers: set[str],
    identifier: str,
) -> None:
    if identifier in reserved_identifiers:
        raise ValueError(
            "D2 legend identifiers must be unique inside one legend block. "
            f"Duplicate identifier: {identifier!r}."
        )

    reserved_identifiers.add(identifier)


def _validate_optional_string(value: str | None, name: str) -> None:
    if value is not None and not isinstance(value, str):
        raise TypeError(f"{name} must be a string or None.")


def _validate_optional_classes(classes: list[str] | None) -> None:
    if classes is None:
        return

    if not isinstance(classes, list) or any(
        not isinstance(item, str) for item in classes
    ):
        raise TypeError("D2 legend classes must be a list of strings or None.")


def _validate_style(
    style: StyleExtensions | dict[str, D2StyleValue] | None,
) -> None:
    if style is None:
        return

    if not isinstance(style, dict):
        raise TypeError("D2 legend style must be a mapping or None.")

    unknown_keys = set(style) - _D2_STYLE_KEYS
    if unknown_keys:
        keys = ", ".join(sorted(str(key) for key in unknown_keys))
        raise ValueError(f"D2 legend style contains unsupported keys: {keys}.")

    for key, value in style.items():
        _validate_style_value(str(key), value)


def _validate_style_value(key: str, value: Any) -> None:
    if value is None:
        return

    if key in _D2_STYLE_STRING_KEYS:
        if not isinstance(value, str):
            raise TypeError(f"D2 legend style.{key} must be a string or None.")
        return

    if key in _D2_STYLE_INTEGER_KEYS:
        if not isinstance(value, int) or isinstance(value, bool):
            raise TypeError(
                f"D2 legend style.{key} must be an integer or None."
            )
        return

    if key in _D2_STYLE_BOOLEAN_KEYS:
        if not isinstance(value, bool):
            raise TypeError(f"D2 legend style.{key} must be a boolean or None.")
        return

    if key == "opacity" and (
        not isinstance(value, (int, float))
        or isinstance(value, bool)
        or not 0 <= value <= 1
    ):
        raise TypeError(
            "D2 legend style.opacity must be a number between 0 and 1 or None."
        )

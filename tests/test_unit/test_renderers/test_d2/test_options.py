import pytest

from c4.renderers.d2 import (
    D2Legend,
    D2LegendElement,
    D2LegendRel,
    D2RenderOptionsBuilder,
)
from c4.renderers.d2.options import D2RenderOptions


def test_render_options_default():
    options_builder = D2RenderOptionsBuilder()
    expected_render_options = D2RenderOptions(
        direction="right",
        layout="dagre",
        theme=None,
        title_near="top-center",
        sequence_diagram=False,
        auto_number_relationships=False,
        include_type_label=True,
        include_technology=True,
        include_properties=False,
        bidirectional_relationships="two_edges",
        fully_qualified_relationships=True,
        legend=None,
    )

    render_options = options_builder.build()

    assert render_options == expected_render_options


def test_render_options_default_classmethod():
    options_builder = D2RenderOptionsBuilder.default()

    render_options = options_builder.build()

    assert render_options == D2RenderOptions()


@pytest.fixture()
def options_builder() -> D2RenderOptionsBuilder:
    return D2RenderOptionsBuilder()


@pytest.mark.parametrize(
    ("direction",),
    [
        ("up",),
        ("down",),
        ("left",),
        ("right",),
        (None,),
    ],
)
def test_render_options_direction_sets_value(
    options_builder: D2RenderOptionsBuilder,
    direction: str | None,
):
    result = options_builder.direction(direction)

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.direction == direction


def test_render_options_explicit_options(
    options_builder: D2RenderOptionsBuilder,
):
    result = (
        options_builder
        .direction("down")
        .layout("elk")
        .theme(101)
        .title_near("bottom-right")
        .sequence_diagram()
        .auto_number_relationships()
        .include_type_label(False)
        .include_technology(False)
        .include_properties()
        .bidirectional_relationships("single_edge")
        .fully_qualified_relationships(False)
        .legend(D2Legend())
    )

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg == D2RenderOptions(
        direction="down",
        layout="elk",
        theme=101,
        title_near="bottom-right",
        sequence_diagram=True,
        auto_number_relationships=True,
        include_type_label=False,
        include_technology=False,
        include_properties=True,
        bidirectional_relationships="single_edge",
        fully_qualified_relationships=False,
        legend=D2Legend(),
    )


def test_render_options_boolean_methods_accept_false(
    options_builder: D2RenderOptionsBuilder,
):
    result = (
        options_builder
        .sequence_diagram(False)
        .auto_number_relationships(False)
        .include_type_label(False)
        .include_technology(False)
        .include_properties(False)
        .fully_qualified_relationships(False)
    )

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.sequence_diagram is False
    assert cfg.auto_number_relationships is False
    assert cfg.include_type_label is False
    assert cfg.include_technology is False
    assert cfg.include_properties is False
    assert cfg.fully_qualified_relationships is False


@pytest.mark.parametrize(
    ("direction",),
    [
        ("north",),
        ("",),
        ("RIGHT",),
    ],
)
def test_render_options_reject_invalid_direction(direction: str):
    with pytest.raises(ValueError, match="D2 direction must be one of"):
        D2RenderOptions(direction=direction)


def test_render_options_builder_rejects_invalid_direction(
    options_builder: D2RenderOptionsBuilder,
):
    with pytest.raises(ValueError, match="D2 direction must be one of"):
        options_builder.direction("north")


@pytest.mark.parametrize(
    ("layout",),
    [
        ("dagre",),
        ("elk",),
    ],
)
def test_render_options_layout_sets_value(
    options_builder: D2RenderOptionsBuilder,
    layout: str,
):
    result = options_builder.layout(layout)

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.layout == layout


@pytest.mark.parametrize(
    ("layout",),
    [
        ("tala",),
        ("",),
        ("ELK",),
        (None,),
    ],
)
def test_render_options_reject_invalid_layout(layout: object):
    with pytest.raises(ValueError, match="D2 layout must be one of"):
        D2RenderOptions(layout=layout)


def test_render_options_builder_rejects_invalid_layout(
    options_builder: D2RenderOptionsBuilder,
):
    with pytest.raises(ValueError, match="D2 layout must be one of"):
        options_builder.layout("tala")


@pytest.mark.parametrize(
    ("theme",),
    [
        (0,),
        (1,),
        (101,),
        (None,),
    ],
)
def test_render_options_theme_accepts_valid_values(
    options_builder: D2RenderOptionsBuilder,
    theme: int | None,
):
    result = options_builder.theme(theme)

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.theme == theme


@pytest.mark.parametrize(
    ("theme", "exception_type"),
    [
        (-1, ValueError),
        (True, TypeError),
        ("101", TypeError),
    ],
)
def test_render_options_reject_invalid_theme(
    theme: object,
    exception_type: type[Exception],
):
    with pytest.raises(exception_type, match="D2 theme must be None"):
        D2RenderOptions(theme=theme)


def test_render_options_builder_rejects_invalid_theme(
    options_builder: D2RenderOptionsBuilder,
):
    with pytest.raises(ValueError, match="D2 theme must be None"):
        options_builder.theme(-1)


@pytest.mark.parametrize(
    ("position",),
    [
        ("top-left",),
        ("top-center",),
        ("top-right",),
        ("center-left",),
        ("center-right",),
        ("bottom-left",),
        ("bottom-center",),
        ("bottom-right",),
        (None,),
    ],
)
def test_render_options_title_near_sets_value(
    options_builder: D2RenderOptionsBuilder,
    position: str | None,
):
    result = options_builder.title_near(position)

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.title_near == position


def test_render_options_reject_invalid_title_near():
    with pytest.raises(ValueError, match="D2 title near position"):
        D2RenderOptions(title_near="center")


def test_render_options_builder_rejects_invalid_title_near(
    options_builder: D2RenderOptionsBuilder,
):
    with pytest.raises(ValueError, match="D2 title near position"):
        options_builder.title_near("center")


@pytest.mark.parametrize(
    ("strategy",),
    [
        ("two_edges",),
        ("single_edge",),
    ],
)
def test_render_options_bidirectional_relationships_sets_value(
    options_builder: D2RenderOptionsBuilder,
    strategy: str,
):
    result = options_builder.bidirectional_relationships(strategy)

    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.bidirectional_relationships == strategy


def test_render_options_reject_invalid_bidirectional_relationship_strategy():
    with pytest.raises(
        ValueError,
        match="D2 bidirectional relationship strategy must be one of",
    ):
        D2RenderOptions(bidirectional_relationships="both")


def test_render_options_builder_rejects_invalid_bidirectional_relationship_strategy(
    options_builder: D2RenderOptionsBuilder,
):
    with pytest.raises(
        ValueError,
        match="D2 bidirectional relationship strategy must be one of",
    ):
        options_builder.bidirectional_relationships("both")


def test_render_options_builder_sets_legend(
    options_builder: D2RenderOptionsBuilder,
):
    legend = D2Legend(
        items=[
            D2LegendElement(label="Banking", style={"fill": "#FFE4E1"}),
            D2LegendRel(label="Alerting", style={"stroke_dash": 5}),
        ],
    )

    result = options_builder.legend(legend)
    cfg = options_builder.build()

    assert result is options_builder
    assert cfg.legend == legend


def test_render_options_accepts_nullable_legend_style_values():
    legend = D2Legend(
        items=[
            D2LegendElement(
                label="Banking",
                style={
                    "fill": None,
                    "animated": True,
                    "opacity": 0.5,
                },
            ),
        ],
    )

    options = D2RenderOptions(legend=legend)

    assert options.legend == legend


def test_render_options_rejects_invalid_legend_type():
    with pytest.raises(TypeError, match="D2 legend must be D2Legend"):
        D2RenderOptions(legend="Legend")


@pytest.mark.parametrize(
    ("legend", "exception_type", "message"),
    [
        (
            D2Legend(label=1),
            TypeError,
            "legend label",
        ),
        (
            D2Legend(items=["Banking"]),
            TypeError,
            "legend items",
        ),
        (
            D2Legend(items=[D2LegendElement(label=1)]),
            TypeError,
            "item label",
        ),
        (
            D2Legend(items=[D2LegendElement(label="Banking", alias="")]),
            ValueError,
            "non-empty string",
        ),
        (
            D2Legend(items=[D2LegendElement(label="Banking", shape=1)]),
            TypeError,
            "element shape",
        ),
        (
            D2Legend(items=[D2LegendElement(label="Banking", icon=1)]),
            TypeError,
            "element icon",
        ),
        (
            D2Legend(items=[D2LegendElement(label="Banking", classes="c4")]),
            TypeError,
            "classes",
        ),
        (
            D2Legend(items=[D2LegendElement(label="Banking", style=["fill"])]),
            TypeError,
            "style must be a mapping",
        ),
        (
            D2Legend(
                items=[D2LegendElement(label="Banking", style={"custom": "x"})]
            ),
            ValueError,
            "unsupported keys: custom",
        ),
        (
            D2Legend(
                items=[D2LegendElement(label="Banking", style={"fill": 1})]
            ),
            TypeError,
            r"style\.fill",
        ),
        (
            D2Legend(
                items=[
                    D2LegendElement(
                        label="Banking", style={"stroke_width": True}
                    )
                ]
            ),
            TypeError,
            r"style\.stroke_width",
        ),
        (
            D2Legend(
                items=[
                    D2LegendElement(label="Banking", style={"animated": "yes"})
                ]
            ),
            TypeError,
            r"style\.animated",
        ),
        (
            D2Legend(
                items=[D2LegendElement(label="Banking", style={"opacity": 2})]
            ),
            TypeError,
            r"style\.opacity",
        ),
        (
            D2Legend(
                items=[D2LegendRel(label="Alerting", hide_endpoints="yes")]
            ),
            TypeError,
            "hide_endpoints",
        ),
        (
            D2Legend(
                items=[D2LegendRel(label="Alerting", bidirectional="yes")]
            ),
            TypeError,
            "bidirectional",
        ),
    ],
)
def test_render_options_rejects_invalid_legend_values(
    legend: D2Legend,
    exception_type: type[Exception],
    message: str,
):
    with pytest.raises(exception_type, match=message):
        D2RenderOptions(legend=legend)


def test_render_options_rejects_invalid_legend_identifier():
    legend = D2Legend(items=[D2LegendElement(label="Banking", alias="bad-id")])

    with pytest.raises(ValueError, match="valid D2 identifier"):
        D2RenderOptions(legend=legend)


def test_render_options_rejects_partial_legend_relationship_endpoints():
    legend = D2Legend(
        items=[D2LegendRel(label="Alerting", source="source")],
    )

    with pytest.raises(ValueError, match="source and target"):
        D2RenderOptions(legend=legend)


def test_render_options_rejects_duplicate_legend_identifiers():
    legend = D2Legend(
        items=[
            D2LegendElement(label="Banking", alias="legend_2_source"),
            D2LegendRel(label="Alerting"),
        ],
    )

    with pytest.raises(ValueError, match="Duplicate identifier"):
        D2RenderOptions(legend=legend)

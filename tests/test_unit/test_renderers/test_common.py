from c4.renderers import (
    D2RenderOptions,
    MermaidRenderOptions,
    PlantUMLRenderOptions,
    RenderOptions,
)


def test_render_options_is_empty_by_default():
    render_options = RenderOptions()

    assert render_options.is_empty is True
    assert bool(render_options) is False


def test_render_options_is_not_empty_with_plantuml_options():
    render_options = RenderOptions(plantuml=PlantUMLRenderOptions())

    assert render_options.is_empty is False
    assert bool(render_options) is True


def test_render_options_is_not_empty_with_mermaid_options():
    render_options = RenderOptions(mermaid=MermaidRenderOptions())

    assert render_options.is_empty is False
    assert bool(render_options) is True


def test_render_options_is_not_empty_with_d2_options():
    render_options = RenderOptions(d2=D2RenderOptions())

    assert render_options.is_empty is False
    assert bool(render_options) is True


def test_render_options_is_empty_after_clearing_d2_options():
    render_options = RenderOptions(d2=D2RenderOptions())

    render_options.d2 = None

    assert render_options.is_empty is True
    assert bool(render_options) is False

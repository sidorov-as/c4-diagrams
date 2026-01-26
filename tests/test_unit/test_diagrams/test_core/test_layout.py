import pytest

from c4.diagrams.core import (
    Diagram,
    Element,
    LayD,
    LayDown,
    LayL,
    LayLeft,
    Layout,
    LayoutType,
    LayR,
    LayRight,
    LayU,
    LayUp,
)


@pytest.mark.parametrize(
    ("layout_class", "expected_type"),
    [
        (
            LayD,
            LayoutType.LAY_D,
        ),
        (
            LayDown,
            LayoutType.LAY_DOWN,
        ),
        (
            LayU,
            LayoutType.LAY_U,
        ),
        (
            LayUp,
            LayoutType.LAY_UP,
        ),
        (
            LayR,
            LayoutType.LAY_R,
        ),
        (
            LayRight,
            LayoutType.LAY_RIGHT,
        ),
        (
            LayL,
            LayoutType.LAY_L,
        ),
        (
            LayLeft,
            LayoutType.LAY_LEFT,
        ),
    ],
)
def test_create_layout(
    diagram: Diagram,
    layout_class: type[Layout],
    expected_type: LayoutType,
):
    from_element = Element(label="from")
    to_element = Element(label="to")
    layout = layout_class(
        from_element=from_element,
        to_element=to_element,
    )

    assert diagram.layouts == [layout]
    assert layout.from_element == from_element
    assert layout.to_element == to_element
    assert layout.layout_type == expected_type


def test_create_layout_without_type_error(diagram: Diagram):
    from_element = Element(label="from")
    to_element = Element(label="to")
    expected_error = (
        "`layout_type` must be provided explicitly or defined as "
        "a class attribute"
    )

    with pytest.raises(ValueError, match=expected_error):
        Layout(
            from_element=from_element,
            to_element=to_element,
        )

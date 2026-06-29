from c4 import (
    Container,
    ContainerBoundary,
    ContainerDiagram,
    Person,
    Rel,
)
from c4.contrib.d2 import BiRel
from c4.renderers.d2 import D2Renderer


def test_typed_d2_kwargs_are_stored_under_canonical_extensions():
    with ContainerDiagram():
        person = Person("User", alias="user", d2={"shape": "c4-person"})

        with ContainerBoundary(
            "Backend",
            alias="backend",
            d2={"direction": "down"},
        ):
            api = Container("API", alias="api")

        relationship = Rel(
            "Uses",
            from_element=person,
            to_element=api,
            d2={"style": {"stroke": "red"}},
        )

    assert person.extensions == {"d2": {"shape": "c4-person"}}
    assert relationship.extensions == {"d2": {"style": {"stroke": "red"}}}
    assert api.extensions is None


def test_renderer_emits_supported_d2_extension_fields():
    with ContainerDiagram() as diagram:
        user = Person(
            "User",
            alias="user",
            d2={
                "shape": "c4-person",
                "style": {"fill": "#eef", "stroke_dash": 2},
                "icon": "https://example.com/user.svg",
                "tooltip": "External user",
                "link": "https://example.com/users",
                "classes": ["actor", "external"],
            },
        )

        with ContainerBoundary(
            "Backend",
            alias="backend",
            d2={"direction": "down", "style": {"fill_pattern": "dots"}},
        ):
            api = Container("API", alias="api")

        BiRel(
            "Syncs",
            from_element=user,
            to_element=api,
            d2={
                "style": {"animated": True, "stroke": "blue"},
                "classes": ["important"],
            },
        )

    result = D2Renderer().render(diagram)

    assert "shape: c4-person" in result
    assert 'icon: "https://example.com/user.svg"' in result
    assert 'tooltip: "External user"' in result
    assert 'link: "https://example.com/users"' in result
    assert 'style.fill: "#eef"' in result
    assert "style.stroke-dash: 2" in result
    assert 'class: ["actor"; "external"]' in result
    assert "direction: down" in result
    assert 'style.fill-pattern: "dots"' in result
    assert "style.animated: true" in result
    assert 'class: ["important"]' in result

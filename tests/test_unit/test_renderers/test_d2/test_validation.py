import pytest

from c4 import Person, Rel, System, SystemContextDiagram
from c4.contrib.c4_macros import RelDown
from c4.contrib.plantuml import LayDown
from c4.enums import STRICT
from c4.renderers.d2 import (
    D2ExtensionValidationError,
    D2UnresolvedRelationshipEndpointError,
    D2UnsupportedDeclarationError,
    validate_d2_diagram,
)


def test_validate_d2_diagram_accepts_supported_diagram():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        user >> Rel("Uses") >> system

    validate_d2_diagram(diagram)


def test_validate_d2_diagram_rejects_unresolved_endpoints_by_default():
    with SystemContextDiagram():
        missing = System("Missing", alias="missing")

    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        relationship = Rel("Uses")

    relationship.from_element = user
    relationship.to_element = missing
    diagram.add_ordered_element(relationship)

    with pytest.raises(D2UnresolvedRelationshipEndpointError, match="missing"):
        validate_d2_diagram(diagram)


def test_validate_d2_diagram_rejects_plantuml_layout_helpers_by_default():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        LayDown(user, system)

    with pytest.raises(ValueError, match="LayDown is not supported"):
        validate_d2_diagram(diagram)


def test_validate_d2_diagram_rejects_layout_relationships_by_default():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        RelDown("Uses", from_element=user, to_element=system)

    with pytest.raises(D2UnsupportedDeclarationError, match="REL_DOWN"):
        validate_d2_diagram(diagram)


def test_validate_d2_diagram_rejects_foreign_extensions_in_strict_mode():
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            extensions={"mermaid": {"shape": "hexagon"}},
        )

    with pytest.raises(ValueError, match="mermaid"):
        validate_d2_diagram(diagram, extension_validation_mode=STRICT)


def test_validate_d2_diagram_accepts_canonical_d2_extensions():
    with SystemContextDiagram() as diagram:
        user = Person(
            "User",
            alias="user",
            extensions={
                "d2": {
                    "shape": "person",
                    "style": {"fill": "#eef", "stroke_dash": 2},
                    "icon": "https://example.com/user.svg",
                    "near": "top-center",
                    "tooltip": "Uses the system",
                    "link": "https://example.com/users",
                    "classes": ["actor", "external"],
                    "direction": "down",
                }
            },
        )
        system = System("System", alias="system")
        Rel(
            "Uses",
            from_element=user,
            to_element=system,
            extensions={
                "d2": {
                    "style": {"animated": True},
                    "classes": ["important"],
                }
            },
        )

    validate_d2_diagram(diagram)


def test_validate_d2_diagram_accepts_typed_d2_kwargs():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user", d2={"shape": "person"})
        system = System("System", alias="system")
        Rel(
            "Uses",
            from_element=user,
            to_element=system,
            d2={"style": {"stroke": "blue"}},
        )

    validate_d2_diagram(diagram)


def test_validate_d2_diagram_accepts_nullable_d2_values():
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            d2={
                "shape": None,
                "style": {
                    "fill": None,
                    "opacity": 0.5,
                },
            },
        )

    validate_d2_diagram(diagram)


def test_validate_d2_diagram_accepts_empty_d2_style():
    with SystemContextDiagram() as diagram:
        System("System", alias="system", d2={"style": {}})

    validate_d2_diagram(diagram)


def test_validate_d2_diagram_rejects_unknown_d2_extension_keys():
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            extensions={"d2": {"unknown": "value"}},
        )

    with pytest.raises(D2ExtensionValidationError, match="unknown"):
        validate_d2_diagram(diagram)


def test_validate_d2_diagram_rejects_unknown_relationship_d2_keys():
    with SystemContextDiagram() as diagram:
        user = Person("User", alias="user")
        system = System("System", alias="system")
        Rel(
            "Uses",
            from_element=user,
            to_element=system,
            extensions={"d2": {"shape": "person"}},
        )

    with pytest.raises(D2ExtensionValidationError, match="shape"):
        validate_d2_diagram(diagram)


def test_validate_d2_diagram_rejects_unknown_d2_style_keys():
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            d2={"style": {"custom_style": "value"}},
        )

    with pytest.raises(D2ExtensionValidationError, match="custom_style"):
        validate_d2_diagram(diagram)


@pytest.mark.parametrize(
    ("d2", "message"),
    [
        (["not", "a", "mapping"], "must be a mapping"),
        ({"direction": "diagonal"}, "direction must be one of"),
        ({"classes": ["valid", 1]}, "classes must be a list"),
        ({"style": ["not", "a", "mapping"]}, "style must be a mapping"),
        ({"shape": 42}, "shape must be a string"),
        ({"style": {"stroke_width": "2"}}, "style.stroke_width"),
        ({"style": {"animated": "yes"}}, "style.animated"),
        ({"style": {"opacity": 2}}, "style.opacity"),
    ],
)
def test_validate_d2_diagram_rejects_malformed_d2_extension_values(
    d2: object,
    message: str,
):
    with SystemContextDiagram() as diagram:
        System("System", alias="system", extensions={"d2": d2})

    with pytest.raises(D2ExtensionValidationError, match=message):
        validate_d2_diagram(diagram)


def test_validate_d2_diagram_ignores_foreign_extensions_by_default():
    with SystemContextDiagram() as diagram:
        System(
            "System",
            alias="system",
            extensions={"mermaid": {"shape": "hexagon"}},
        )

    validate_d2_diagram(diagram)

import pytest

from c4.contrib.likec4._identifiers import is_valid_identifier
from c4.contrib.likec4.renderer import LikeC4IdentifierRegistry


def test_invalid_characters_are_normalized():
    identifier = LikeC4IdentifierRegistry().register("Payment API.v2")

    assert "." not in identifier.identifier
    assert identifier.identifier[0].isalpha()
    assert identifier.identifier == "Payment_API_v2"


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("api", "api"),
        ("payment-api", "payment-api"),
        ("_internal", "_internal"),
        ("1st", "el_1st"),
        ("---", "element"),
        ("", "element"),
        ("trail-", "trail"),
        ("a  b", "a_b"),
        ("a--b", "a--b"),
        ("a - b", "a_b"),
        ("style", "style_id"),
        ("model", "model"),
        ("ünï", "n"),
    ],
)
def test_sanitize(name, expected):
    result = LikeC4IdentifierRegistry.sanitize(name)

    assert result == expected
    assert is_valid_identifier(result)


def test_sibling_collision_is_deterministic():
    registry = LikeC4IdentifierRegistry()

    ids = [registry.register("API Gateway").identifier for _ in range(3)]
    ids.append(registry.register("API_Gateway").identifier)

    assert ids == [
        "API_Gateway",
        "API_Gateway_2",
        "API_Gateway_3",
        "API_Gateway_4",
    ]


def test_suffix_does_not_collide_with_existing_name():
    registry = LikeC4IdentifierRegistry()

    first = registry.register("a")
    explicit = registry.register("a_2")
    second = registry.register("a")

    assert (first.identifier, explicit.identifier, second.identifier) == (
        "a",
        "a_2",
        "a_3",
    )


def test_fqn_follows_parents_and_siblings_are_per_parent():
    registry = LikeC4IdentifierRegistry()
    cloud = registry.register("cloud")
    api_a = registry.register("api", parent_fqn=cloud.fqn)
    other = registry.register("other")
    api_b = registry.register("api", parent_fqn=other.fqn)
    nested = registry.register("db", parent_fqn=api_a.fqn)

    assert api_a.fqn == "cloud.api"
    assert api_b.fqn == "other.api"
    assert nested.fqn == "cloud.api.db"


def test_namespaces_are_separate():
    registry = LikeC4IdentifierRegistry()

    model_id = registry.register("prod")
    deployment_id = registry.register("prod", namespace="deployment")

    assert model_id.identifier == deployment_id.identifier == "prod"

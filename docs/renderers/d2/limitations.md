# D2 Limitations

D2 validation is intentionally strict for declarations owned by other backends.
If a diagram contains backend-only statements that D2 cannot represent
faithfully, D2 rendering fails before source is emitted.

## Validation Behavior

| Case | Behavior |
|------|----------|
| Unsupported backend-owned declarations | Fail validation by default. |
| Identifier collisions after D2 sanitization | Fail validation regardless of `extension_validation_mode`. |
| Malformed or unknown `d2=` fields | Fail validation by default. |
| Foreign backend extension data, such as `plantuml={...}` or `mermaid={...}` | Ignored by default and rejected when `extension_validation_mode=STRICT`. |
| Relationship endpoint cannot be resolved | Fail validation. |

D2 identifiers are based on element aliases, sanitized for D2 syntax, and kept
deterministic. Aliases that become the same D2 identifier after sanitization are
rejected instead of receiving generated suffixes.

## Backend Layout Helpers

PlantUML-only layout helpers, dynamic indexes, and directional relationship
suffixes are not supported by the D2 renderer. Use D2 render options and D2
extension fields for D2-owned layout hints.

The following deployment helper classes are treated as backend layout helpers:

- `NodeLeft`
- `NodeRight`
- `DeploymentNodeLeft`
- `DeploymentNodeRight`

D2 degrades these variants to normal `Node` or `DeploymentNode` containers,
without preserving the left/right placement hint.

## Properties

Element and relationship properties are rendered only when
`D2RenderOptions(include_properties=True)` is configured. With the default
`include_properties=False`, property tables are omitted from D2 labels.

## Supported Representations

D2 intentionally represents some backend-specific concepts in D2-native terms:

- Boundaries and deployment nodes render as D2 containers.
- External elements, people, databases, and queues use renderer-managed D2
  classes and shapes.
- Bidirectional relationships render as two directed edges by default, or as a
  single `<->` edge when `bidirectional_relationships="single_edge"`.
- `d2={"direction": ...}` on a boundary or element emits a local D2
  `direction` attribute.

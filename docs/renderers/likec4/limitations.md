# LikeC4 Limitations

## Not supported

- Image formats are PNG and JPG only. LikeC4 has no SVG export.
- There is no Kroki backend: LikeC4 images are exported only with the local
  `likec4` CLI.
- Dynamic views support flat steps only, with no parallel or alternative blocks.
- Deployment views take no `with { ... }` overrides.
- `navigateTo` cannot be set on an element (LikeC4 does not allow it inside an
  element body); use relationships, view predicates or dynamic-view steps.
- Features of the LikeC4 language the Python API does not model, such as
  `global` rules, `extends` and view `rank` rules, can only be written with
  [`RawPredicate`][c4.contrib.likec4.RawPredicate] where a predicate is accepted.

## Rules checked by the renderer

The project is validated before any source is produced, and a failure raises
[`LikeC4ValidationError`][c4.contrib.likec4.renderer.LikeC4ValidationError] naming the element, step or view. The full list is in
the [Reference](reference.md#validation-rules). The most common ones:

| Rule                                                                   |
|------------------------------------------------------------------------|
| A kind, relationship kind, deployment node kind, tag or custom color is used but not declared. |
| A relationship endpoint is not part of the project.                    |
| A relationship connects an element with its own ancestor or descendant. |
| A link has no scheme, no `./` or `../` prefix and no `@alias`, or contains whitespace. |
| View keys are not unique across all view types.                        |
| A view scope, predicate reference or instance does not resolve to a member of the project. |
| `navigate_to` does not name a view of the right kind.                  |
| A view style rule targets a relationship predicate.                    |

## Checked only by `likec4 validate`

The renderer cannot check these; run `likec4 validate` on the rendered source:

- An element view `of X` that includes elements outside `X`.
- The text of every `RawPredicate`.
- Icon references.
- Anything LikeC4 adds or changes in versions other than 1.60.0.

## JSON contract

The JSON format (`"backend": "likec4"`, see the
[project spec](../../converters/json/specs/likec4.project.md)) is a c4-diagrams
contract and is **not** compatible with `likec4 export json`.

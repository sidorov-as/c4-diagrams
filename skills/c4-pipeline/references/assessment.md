# Assessment

Rate every candidate source on four criteria (extraction is rated twice, for elements and for relationships). The ratings are judgments, not a score: write the evidence, not a number.

## Criteria

| Criterion      | Good                                                                                  | Poor                                                                              |
|----------------|---------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|
| **Formality**  | Schema-defined YAML in the repository; one file per system; names follow a convention | Free text, comments as documentation, files generated elsewhere, many near-copies |
| **Extraction: elements**   | Each service, workload or database is one entry with an image, a name and ports       | Entries are anonymous, or one entry hides several systems                         |
| **Extraction: relationships** | Stated outright: `depends_on`, a Service selector, an Ingress rule, a `c4.*` annotation | Inferred from environment variables, URLs, naming; or absent                      |
| **Stability**  | Changes with each feature; the diagram goes stale in weeks                            | Changes a few times a year                                                        |
| **Value**      | Read by a team or published; hand maintenance costs real time                         | Read once; nobody would notice it going stale                                     |

Rate elements and relationships separately: elements are usually extractable, relationships usually inferred.

Evidence to cite per rating: file paths, the count of services or workloads, three example entries, and for
relationships the exact field they came from (`depends_on` in `docker-compose.yml:12`, `DB_HOST` in `deploy.yaml:40`).
Ask the user for what files cannot show: how often the diagram is read, and who reads it.

## Verdicts

| Verdict          | When                                                                                                         |
|------------------|--------------------------------------------------------------------------------------------------------------|
| **Go**           | Formal sources; elements and relationships both extract with good confidence; the diagram is used often      |
| **Go partially** | Elements extract well, relationships are inferred or absent. Elements from sources; relationships from a small hand-written overlay or `c4.*` annotations in the sources |
| **No-go**        | Little formal data; or relationships are guesses and nobody will curate them; or the diagram changes rarely. Cost exceeds value |

How the ratings choose:

1. Poor formality, sources that rarely change, or low value: No-go.
2. Relationships rated inferred or absent: Go partially, never Go.
3. Everything good: Go.

A Go needs the relationship evidence to be stated fields, not guesses. When unsure between two verdicts, take the
lower one and say what would raise it.

No-go recommends one of: a one-off diagram with `c4-diagrams`, or hand maintenance of the Python file. Give the reason
in one sentence.

## Report template

```markdown
## Pipeline assessment

**Repository:** <path or name>

### Sources
| Source | Formality | Elements | Relationships | Stability | Value |
|--------|-----------|----------|---------------|-----------|-------|
| <path> | <good/poor> | <good/poor, n found> | <stated/inferred/absent> | <high/low> | <high/low> |

### Evidence
- <rating>: <file:line or field> — <what it shows>

### Verdict: <Go | Go partially | No-go>
<One paragraph: what supports it, and what would change it.>

### Next
- Go / Go partially: ask for agreement, then the target; Go partially names the overlay or annotations.
- No-go: <one-off diagram | hand maintenance>, and why.
```

Fill every heading. Wait for the user's answer after presenting it.

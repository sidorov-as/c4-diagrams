# Generator patterns

Read after a Go or Go partially verdict and the user's agreement. The generator is a script in the user's repository
(Python, any name, for example `tools/gen_c4.py`) that reads the manifests and writes one JSON file.

## Target

Ask which target the diagram should have, and recommend one:

| Wanted                                                         | Target                                   | `backend` value                           |
|----------------------------------------------------------------|------------------------------------------|-------------------------------------------|
| One diagram, or one diagram in PlantUML, Mermaid and D2        | portable `Diagram` (for example `ContainerDiagram`) | omit, or `plantuml`, `mermaid`, `d2`      |
| Context, containers and deployment from the same manifests     | Structurizr `Workspace`                  | `"backend": "structurizr"` (required)     |
| The same, rendered by LikeC4                                   | LikeC4 `Project`                         | `"backend": "likec4"` (required)          |

Manifests describe one system, so several views usually favour Structurizr or LikeC4. Start with one view and add
others on request.

Element kinds, views and nesting are in the `c4-diagrams` references: read them instead of copying from here.

- Portable classes: `../../c4-diagrams/references/python-dsl.md`
- Structurizr and LikeC4: `../../c4-diagrams/references/whole-architecture.md`
- Portable core versus backend fields: `../../c4-diagrams/references/backends.md`

Fields owned by one backend (such as `tags`) are accepted only with the matching `backend` value.

## Patterns

1. **Thin factories.** Two functions, `element(...)` and `relationship(...)`, each returning a plain `dict`. Parsing
   code calls them and never builds dicts by hand.
2. **Stable aliases.** Derive the alias from the source identity, not from order: `kind_<hex>` where `<hex>` is the
   first 8 characters of a SHA-1 of `kind/namespace/name`. Alias characters stay ASCII.
3. **Deterministic output.** Sort elements and relationships by alias, dump JSON with `indent=2, sort_keys=True`, end
   with a newline. Two runs on unchanged sources give identical bytes.
4. **Unresolved list.** A reference that matches no element (a `depends_on` entry, a Service selector without a
   workload) goes to a list printed on stderr, never dropped silently.
5. **Assumptions labeled.** An inferred relationship carries `"label"` text ending in `(assumed)`, appears in the
   unresolved report, and shows the field it came from.
6. **Thin parsing.** Read the fields in `sources.md`; ignore the rest. Do not parse every key of a manifest.

```python
import hashlib

def alias(kind: str, *parts: str) -> str:
    digest = hashlib.sha1("/".join((kind, *parts)).encode()).hexdigest()
    return f"{kind}_{digest[:8]}"

def element(kind: str, alias: str, label: str, **extra) -> dict:
    return {"type": kind, "alias": alias, "label": label, **{k: v for k, v in extra.items() if v}}

def relationship(src: str, dst: str, label: str, **extra) -> dict:
    return {"type": "REL", "from": src, "to": dst, "label": label, **{k: v for k, v in extra.items() if v}}
```

Structurizr and LikeC4 use their own field names (`id`, `name`, `title`): the factories change, the patterns do not.

### Annotations and overlay (Go partially)

Relationships come from one of two places. Offer both, let the user choose:

- **`c4.*` annotations** in the sources: Compose `labels` (`c4.type`, `c4.label`, `c4.technology`,
  `c4.rel.<dep>.label`), Kubernetes `metadata.annotations` with the same keys. They live next to the thing they describe.
- **Overlay file**, a small YAML or JSON in the repository (for example `c4-overlay.yaml`) listing relationships and
  labels by service or workload name.

Merge rule: overlay beats annotation, annotation beats inference. An overlay entry that matches no element goes to the
unresolved list. A relationship that survives only by inference keeps the `(assumed)` label.

## Validation

Load the output; the installed version's models do the checking.

```shell
c4 render diagram.json            # source text on success, field-path errors on failure
c4 render diagram.json --mermaid  # another renderer for a portable diagram
```

A failing load prints the path to the field: `root->ContainerDiagram->boundaries[0]->...->labl: Extra inputs are not
permitted`. Element unions list one line per candidate type; read the lines for the type you meant, and fix the
generator, not the JSON. Repeat until the load succeeds. From Python: `c4.converters.json.converter.diagram_from_dict`.

A Structurizr or LikeC4 file without its `backend` value fails to load or picks the wrong schema: add the field.

When a schema is needed, print it from the installed version. Do not copy one from a document.

```python
from c4.converters.json.schemas.diagrams.container import ContainerDiagramSchema          # portable core
from c4.contrib.plantuml.converters.json.schemas import PlantUMLContainerDiagramSchema    # a backend
from c4.contrib.structurizr.converters.json import StructurizrWorkspaceSchema             # whole-architecture
print(ContainerDiagramSchema.model_json_schema())
```

Minimal portable example (a `ContainerDiagram` that loads as is):

```json
{
  "type": "ContainerDiagram",
  "title": "Web App",
  "elements": [{"type": "Person", "alias": "user", "label": "User"}],
  "boundaries": [
    {
      "type": "SystemBoundary",
      "alias": "system",
      "label": "Simple System",
      "elements": [
        {"type": "Container", "alias": "web", "label": "Web App", "technology": "React"},
        {"type": "ContainerDb", "alias": "db", "label": "Database", "technology": "PostgreSQL"}
      ]
    }
  ],
  "relationships": [
    {"type": "REL", "from": "user", "to": "web", "label": "Uses"},
    {"type": "REL", "from": "web", "to": "db", "label": "Reads/Writes"}
  ]
}
```

Specs per diagram type and backend: https://sidorov-as.github.io/c4-diagrams/converters/json/json/

## Drift check

Commit the generated JSON. CI regenerates it and fails on any difference:

```shell
python tools/gen_c4.py > docs/architecture.json
git diff --exit-code docs/architecture.json
```

A manifest change without a regenerated file fails the job. Show the user the commands and leave the wiring to their
CI; do not edit CI files without a yes.

## Not covered

Terraform, Ansible and OpenAPI sources. Say so when they are the only candidates.

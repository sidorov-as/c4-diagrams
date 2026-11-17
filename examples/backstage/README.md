# Backstage catalog → C4 diagram

Build a C4 component diagram from a [Backstage](https://backstage.io) software
catalog. The demo runs a local Backstage with a seeded catalog, reads it through
the Catalog API, and exports a JSON document for the `c4` CLI.

```text
catalog/entities/*.yaml ─► Backstage ─► Catalog API ─► export script ─► JSON ─► c4 render / c4 export
```

Tested with Backstage 1.49.1 (`backstage/backstage.json`).

## Prerequisites

- Docker with Compose (the Backstage backend is built inside the image; the
  first build takes a few minutes)
- `curl` and [`jq`](https://jqlang.org) for the helper scripts
- Python 3.10+ for the export script (standard library only)
- `c4-diagrams` with the converters extra, to render the result:
  `pip install "c4-diagrams[converters]"`. PNG export also needs PlantUML.

## Quick start

Run everything from this directory.

```bash
# 1) Start Backstage (UI and API on http://localhost:7007; sign in as Guest)
docker compose up -d --build

# 2) Wait for the catalog to load and refresh the entities
./scripts/populate_catalog.sh

# 3) Optional: look at the raw entities and relations
./scripts/query_entities.sh

# 4) Export C4 JSON
./scripts/export_c4_from_backstage.py --pretty > order-processing.json

# 5) Render it
c4 render order-processing.json > order-processing.puml
c4 export order-processing.json -f png -o order-processing.png

# 6) Stop
docker compose down
```

Use `--backend core` in step 4 to get a portable document (no PlantUML-only
fields), which `c4 render` can also send to Mermaid or D2:

```bash
./scripts/export_c4_from_backstage.py --backend core > order-processing.json
c4 render order-processing.json --mermaid
```

## What is inside

| Path                                  | Purpose                                                                                       |
|---------------------------------------|-----------------------------------------------------------------------------------------------|
| `docker-compose.yml`                  | One service: Backstage with in-memory SQLite                                                  |
| `backstage/`                          | Trimmed Backstage app (catalog, auth, permissions only) and its `Dockerfile`                  |
| `backstage/app-config.demo.yaml`      | Catalog location, rules (Group allowed), static service token                                 |
| `catalog/entities/*.yaml`             | Demo entities: system `order-processing` with its components, resources, APIs and owner group |
| `scripts/populate_catalog.sh`         | Waits for the catalog and refreshes every entity                                              |
| `scripts/query_entities.sh`           | Prints entities and relations as JSON                                                         |
| `scripts/export_c4_from_backstage.py` | Catalog entities → C4 JSON                                                                    |
| `tests/`                              | Offline smoke test for the exporter                                                           |

## Authentication

**UI.** Open http://localhost:7007 and choose **Sign in as Guest**. The demo
enables Backstage's guest provider (`dangerouslyAllowOutsideDevelopment`), so
there is no password. Without signing in, the catalog stays empty because the
browser has no identity.

**Scripts.** The Catalog API requires credentials. The demo config defines a static service
token, `demo-c4-token`, limited to the catalog plugin. The scripts send it by
default; override it with `BACKSTAGE_TOKEN` (or `--token`). This token is for
the local demo only. Do not reuse it anywhere else.

Other settings: `BACKSTAGE_URL` (default `http://localhost:7007/api/catalog`),
`BACKSTAGE_SYSTEM` (default `order-processing`), `BACKSTAGE_NAMESPACE`.

## How entities map to C4

| Backstage   | C4 JSON                                                                                              |
|-------------|------------------------------------------------------------------------------------------------------|
| `System`    | `SystemBoundary` around the diagram; its `title` is the boundary label and the default diagram title |
| `Component` | element, `Component` by default                                                                      |
| `Resource`  | element, `ComponentDb` by default                                                                    |
| `API`       | not drawn; it supplies labels for relationships (see below)                                          |
| `Group`     | not drawn; owner only                                                                                |

Relationships come from standard catalog relations:

| Source                                               | Relationship                                                                                   |
|------------------------------------------------------|------------------------------------------------------------------------------------------------|
| `dependsOn` to a `Component`                         | `REL`, "Depends on"                                                                            |
| `dependsOn` to a `Resource` of type `ComponentDb`    | `REL`, "Reads and writes"                                                                      |
| `dependsOn` to a `Resource` of type `ComponentQueue` | `REL`, "Publishes events to"                                                                   |
| `consumesApis` an API with `c4.io/providerResource`  | consumer → provider resource, label from the API annotations                                   |
| API with `c4.io/sourceComponent`                     | every component that `dependsOn` the source component → source component, "Invokes" by default |

When two rules produce an edge between the same pair, the API rule wins. The
exporter emits one edge per pair.

## `c4.io/*` annotations

C4 details that Backstage has no field for are kept as annotations.

On `Component` and `Resource`:

| Annotation                                       | Meaning                                                                                 |
|--------------------------------------------------|-----------------------------------------------------------------------------------------|
| `c4.io/alias`                                    | Element alias (default: name with `-` replaced by `_`)                                  |
| `c4.io/type`                                     | C4 element type, such as `Component`, `ComponentDb`, `ComponentQueue`, `ComponentExt`   |
| `c4.io/label`                                    | Label (default: `metadata.title`, then the name)                                        |
| `c4.io/technology`                               | Technology                                                                              |
| `c4.io/tags`, `c4.io/sprite`, `c4.io/stereotype` | Comma-separated tags, sprite, stereotype (PlantUML only; dropped with `--backend core`) |

On `System`: `c4.io/alias`, `c4.io/label`, `c4.io/tags`.

On `API`:

| Annotation                                                  | Meaning                                                   |
|-------------------------------------------------------------|-----------------------------------------------------------|
| `c4.io/providerResource`                                    | Entity ref of the node that provides the API              |
| `c4.io/sourceComponent`                                     | Entity ref of the component that handles calls to the API |
| `c4.io/edgeLabel`, `c4.io/edgeTechnology`, `c4.io/edgeTags` | Label, technology and tags of the generated edge          |

## Smoke test

The test runs the exporter against a canned catalog response (no Docker, no
network) and checks that the output loads for the `plantuml` and `core` backends.
From the repository root:

```bash
python -m pytest examples/backstage
```

## Limits

This is a demo exporter, not a production tool:

- one system per run, selected with `--system`; no nested boundaries;
- only `Component` and `Resource` entities are drawn, and only in a component diagram;
- relationships are inferred from `dependsOn` and the API annotations above;
- the static token and the allow-all permission policy are for local use.

Extend `build_relationships` in `scripts/export_c4_from_backstage.py` to cover
other patterns.

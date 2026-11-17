#!/usr/bin/env python3
"""Export one Backstage system to C4 JSON (input of ``c4.diagram_from_dict``).

Stdlib only. Mapping and annotations are described in ../README.md.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

DEFAULT_TOKEN = "demo-c4-token"
PAGE_SIZE = 100
FIELDS = "kind,metadata,spec,relations"
PLANTUML_ONLY_FIELDS = ("sprite", "tags", "stereotype")
DEFAULT_C4_TYPES = {"Component": "Component", "Resource": "ComponentDb"}


def fetch_json(url: str, token: str | None = None) -> dict[str, Any]:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def fetch_system_entities(
    base_url: str, system: str, namespace: str, token: str | None
) -> list[dict[str, Any]]:
    """Read every entity of the system, following ``nextCursor`` pages."""
    filter_expr = f"spec.system={system},metadata.namespace={namespace}"
    query = {"filter": filter_expr, "fields": FIELDS, "limit": str(PAGE_SIZE)}
    items: list[dict[str, Any]] = []
    while True:
        payload = fetch_json(
            f"{base_url}/entities/by-query?{urllib.parse.urlencode(query)}",
            token,
        )
        items.extend(payload.get("items", []))
        cursor = (payload.get("pageInfo") or {}).get("nextCursor")
        if not cursor:
            return items
        query = {"cursor": cursor, "fields": FIELDS, "limit": str(PAGE_SIZE)}


def fetch_system_entity(
    base_url: str, system: str, namespace: str, token: str | None
) -> dict[str, Any] | None:
    """The System entity has no ``spec.system``, so it is looked up by name."""
    url = f"{base_url}/entities/by-name/system/{urllib.parse.quote(namespace)}/{urllib.parse.quote(system)}"
    try:
        return fetch_json(url, token)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def entity_ref(entity: dict[str, Any]) -> str:
    md = entity.get("metadata", {})
    return f"{entity['kind'].lower()}:{md.get('namespace', 'default').lower()}/{md['name'].lower()}"


def annotation(entity: dict[str, Any], key: str, default: str = "") -> str:
    return entity.get("metadata", {}).get("annotations", {}).get(key, default)


def csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def title_of(entity: dict[str, Any]) -> str:
    md = entity.get("metadata", {})
    return md.get("title") or md["name"]


def alias_for(entity: dict[str, Any]) -> str:
    return annotation(
        entity, "c4.io/alias", entity["metadata"]["name"].replace("-", "_")
    )


def make_element(entity: dict[str, Any]) -> dict[str, Any]:
    elem: dict[str, Any] = {
        "type": annotation(entity, "c4.io/type")
        or DEFAULT_C4_TYPES[entity["kind"]],
        "alias": alias_for(entity),
        "label": annotation(entity, "c4.io/label", title_of(entity)),
        "description": entity.get("metadata", {}).get("description", ""),
    }
    for key in ("sprite", "technology", "stereotype"):
        value = annotation(entity, f"c4.io/{key}")
        if value:
            elem[key] = value
    tags = csv(annotation(entity, "c4.io/tags"))
    if tags:
        elem["tags"] = tags
    return elem


def make_rel(
    src: dict[str, Any],
    dst: dict[str, Any],
    label: str,
    technology: str,
    tags: list[str],
) -> dict[str, Any]:
    rel: dict[str, Any] = {
        "type": "REL",
        "from": alias_for(src),
        "to": alias_for(dst),
        "label": label,
    }
    if technology:
        rel["technology"] = technology
    rel["tags"] = tags
    return rel


def api_edge_style(
    api: dict[str, Any], default_label: str, default_tags: str
) -> tuple[str, str, list[str]]:
    return (
        annotation(api, "c4.io/edgeLabel", default_label),
        annotation(api, "c4.io/edgeTechnology"),
        csv(annotation(api, "c4.io/edgeTags", default_tags)),
    )


def depends_on_style(target: dict[str, Any]) -> tuple[str, str, list[str]]:
    if target["kind"] == "Resource":
        target_type = annotation(target, "c4.io/type")
        if target_type == "ComponentDb":
            return (
                "Reads and writes",
                annotation(target, "c4.io/technology", "SQL"),
                ["DataAccess"],
            )
        if target_type == "ComponentQueue":
            return (
                "Publishes events to",
                annotation(target, "c4.io/technology", "Kafka"),
                ["AsyncFlow"],
            )
    return "Depends on", "", ["DependsOn"]


def build_relationships(
    entities: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """API annotations win over plain ``dependsOn``; one edge per (from, to) pair."""
    nodes = {
        ref: e for ref, e in entities.items() if e["kind"] in DEFAULT_C4_TYPES
    }
    components = [e for e in nodes.values() if e["kind"] == "Component"]
    apis = {ref: e for ref, e in entities.items() if e["kind"] == "API"}
    relationships: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    def add(
        src: dict[str, Any],
        dst: dict[str, Any],
        style: tuple[str, str, list[str]],
    ) -> None:
        key = (alias_for(src), alias_for(dst))
        if key not in seen:
            seen.add(key)
            relationships.append(make_rel(src, dst, *style))

    # 1) consumesApi: consumer -> the node named by c4.io/providerResource or c4.io/sourceComponent.
    for src in components:
        for rel in src.get("relations", []):
            api = (
                apis.get(rel.get("targetRef", ""))
                if rel.get("type") == "consumesApi"
                else None
            )
            if api is None:
                continue
            provider = nodes.get(
                annotation(api, "c4.io/providerResource")
                or annotation(api, "c4.io/sourceComponent")
            )
            if provider is not None:
                add(
                    src,
                    provider,
                    api_edge_style(api, "Consumes API", "ApiCall"),
                )

    # 2) c4.io/sourceComponent: components that depend on it call the API synchronously.
    for api in apis.values():
        handler_ref = annotation(api, "c4.io/sourceComponent")
        handler = nodes.get(handler_ref)
        if handler is None:
            continue
        for consumer in components:
            if any(
                r.get("type") == "dependsOn"
                and r.get("targetRef") == handler_ref
                for r in consumer.get("relations", [])
            ):
                add(
                    consumer,
                    handler,
                    api_edge_style(api, "Invokes", "SyncCall"),
                )

    # 3) Plain dependsOn between components and resources.
    for src in components:
        for rel in src.get("relations", []):
            target = (
                nodes.get(rel.get("targetRef", ""))
                if rel.get("type") == "dependsOn"
                else None
            )
            if target is not None:
                add(src, target, depends_on_style(target))

    return relationships


def strip_backend_fields(node: Any) -> None:
    """Remove PlantUML-only fields in place so the JSON fits the portable core schema."""
    if isinstance(node, dict):
        for key in PLANTUML_ONLY_FIELDS:
            node.pop(key, None)
        for value in node.values():
            strip_backend_fields(value)
    elif isinstance(node, list):
        for item in node:
            strip_backend_fields(item)


def build_diagram(
    items: list[dict[str, Any]],
    system_entity: dict[str, Any] | None,
    system: str,
    diagram_type: str,
    title: str | None,
    backend: str,
) -> dict[str, Any]:
    entities = {entity_ref(e): e for e in items}
    elements = [make_element(e) for e in items if e["kind"] in DEFAULT_C4_TYPES]

    system_title = title_of(system_entity) if system_entity else system
    boundary: dict[str, Any] = {
        "type": "SystemBoundary",
        "alias": alias_for(system_entity)
        if system_entity
        else system.replace("-", "_"),
        "label": annotation(system_entity, "c4.io/label", system_title)
        if system_entity
        else system_title,
        "description": system_entity.get("metadata", {}).get("description", "")
        if system_entity
        else "",
        "tags": csv(annotation(system_entity, "c4.io/tags", "SystemBoundary"))
        if system_entity
        else ["SystemBoundary"],
        "elements": elements,
        "boundaries": [],
        "relationships": [],
    }
    result: dict[str, Any] = {
        "type": diagram_type,
        "title": title or f"{system_title} - Component Diagram",
        "elements": [],
        "boundaries": [boundary],
        "relationships": build_relationships(entities),
    }
    if backend == "plantuml":
        # Backend-specific fields are accepted only when the document names its backend.
        return {"backend": "plantuml", **result}
    strip_backend_fields(result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Export a Backstage catalog slice to C4 JSON"
    )
    parser.add_argument(
        "--base-url",
        default=os.getenv("BACKSTAGE_URL", "http://localhost:7007/api/catalog"),
    )
    parser.add_argument(
        "--system",
        default=os.getenv("BACKSTAGE_SYSTEM", "order-processing"),
        help="Backstage system name",
    )
    parser.add_argument(
        "--namespace", default=os.getenv("BACKSTAGE_NAMESPACE", "default")
    )
    parser.add_argument(
        "--token", default=os.getenv("BACKSTAGE_TOKEN", DEFAULT_TOKEN)
    )
    parser.add_argument(
        "--title",
        default=None,
        help="Diagram title (default: '<System title> - Component Diagram')",
    )
    parser.add_argument("--diagram-type", default="ComponentDiagram")
    parser.add_argument(
        "--backend",
        choices=["plantuml", "core"],
        default="plantuml",
        help="plantuml: keep PlantUML-only fields (sprite, tags, stereotype) and set "
        '"backend": "plantuml"; core: drop them for a portable diagram (PlantUML, Mermaid, D2)',
    )
    parser.add_argument("--pretty", action="store_true")
    args = parser.parse_args(argv)

    items = fetch_system_entities(
        args.base_url, args.system, args.namespace, args.token
    )
    if not items:
        print(
            json.dumps(
                {"error": f"No entities found for system {args.system!r}"},
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1
    system_entity = fetch_system_entity(
        args.base_url, args.system, args.namespace, args.token
    )

    result = build_diagram(
        items,
        system_entity,
        args.system,
        args.diagram_type,
        args.title,
        args.backend,
    )
    print(json.dumps(result, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

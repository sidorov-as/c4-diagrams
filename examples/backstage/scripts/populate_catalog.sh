#!/usr/bin/env bash
# Wait until the demo catalog is loaded, then refresh every entity so that
# relations are stitched before exporting.
#
# The catalog itself is loaded from catalog/entities/all.yaml by the file
# location in backstage/app-config.demo.yaml; nothing is registered here.
set -euo pipefail

BACKSTAGE_URL="${BACKSTAGE_URL:-http://localhost:7007/api/catalog}"
TOKEN="${BACKSTAGE_TOKEN:-demo-c4-token}"
EXPECTED_MIN="${EXPECTED_MIN_ENTITIES:-12}"
TIMEOUT="${WAIT_TIMEOUT:-120}"

auth=(-H "Authorization: Bearer ${TOKEN}")

list_refs() {
  curl -fsS -G "${BACKSTAGE_URL}/entities/by-query" "${auth[@]}" \
    --data-urlencode "filter=kind=Component" \
    --data-urlencode "filter=kind=Resource" \
    --data-urlencode "filter=kind=API" \
    --data-urlencode "filter=kind=System" \
    --data-urlencode "filter=kind=Group" \
    --data-urlencode "fields=kind,metadata.name,metadata.namespace" \
    --data-urlencode "limit=100" |
    jq -r '.items[] | "\(.kind | ascii_downcase):\(.metadata.namespace // "default")/\(.metadata.name)"'
}

echo "Waiting for the catalog at ${BACKSTAGE_URL} ..."
deadline=$((SECONDS + TIMEOUT))
refs=""
while true; do
  refs="$(list_refs 2>/dev/null || true)"
  count=$(printf '%s' "$refs" | grep -c . || true)
  if [[ "$count" -ge "$EXPECTED_MIN" ]]; then
    break
  fi
  if (( SECONDS >= deadline )); then
    echo "Catalog not ready after ${TIMEOUT}s (found ${count} entities, need ${EXPECTED_MIN})." >&2
    exit 1
  fi
  sleep 3
done
echo "Found ${count} entities."

while IFS= read -r ref; do
  curl -fsS -X POST "${BACKSTAGE_URL}/refresh" "${auth[@]}" \
    -H 'Content-Type: application/json' \
    --data "$(jq -n --arg ref "$ref" '{entityRef: $ref}')" >/dev/null
done <<<"$refs"

echo "Refresh requested for ${count} entities."

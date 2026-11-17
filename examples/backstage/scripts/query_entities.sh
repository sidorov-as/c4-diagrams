#!/usr/bin/env bash
# Print the demo catalog entities (kind, metadata, spec, relations) as JSON.
set -euo pipefail

BACKSTAGE_URL="${BACKSTAGE_URL:-http://localhost:7007/api/catalog}"
TOKEN="${BACKSTAGE_TOKEN:-demo-c4-token}"

# Several `filter` parameters are OR-ed (a comma inside one filter would be AND).
curl -fsS -G "${BACKSTAGE_URL}/entities/by-query" \
  -H "Authorization: Bearer ${TOKEN}" \
  --data-urlencode "filter=kind=Component" \
  --data-urlencode "filter=kind=Resource" \
  --data-urlencode "filter=kind=API" \
  --data-urlencode "filter=kind=System" \
  --data-urlencode "filter=kind=Group" \
  --data-urlencode "fields=kind,metadata,spec,relations" \
  --data-urlencode "limit=100" | jq .

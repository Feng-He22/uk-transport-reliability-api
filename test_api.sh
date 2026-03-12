#!/usr/bin/env bash
set -eu

BASE_URL="https://meowcolate.pythonanywhere.com"

echo "== 1. Health =="
curl -sS "$BASE_URL/health"
echo -e "\n"

echo "== 2. OpenAPI =="
curl -sS "$BASE_URL/openapi.json" > /tmp/openapi.json
python -m json.tool /tmp/openapi.json | sed -n '1,20p'
echo -e "\n"

echo "== 3. List incidents =="
curl -sS "$BASE_URL/incidents"
echo -e "\n"

echo "== 4. Sync TfL =="
curl -sS -X POST "$BASE_URL/sync/tfl" -H "Content-Type: application/json"
echo -e "\n"

echo "== 5. Create incident =="
curl -sS -X POST "$BASE_URL/incidents" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "manual",
    "mode": "tube",
    "line_id": "central",
    "line_name": "Central",
    "station_id": null,
    "station_name": null,
    "occurred_at": "2026-03-12T16:00:00Z",
    "severity": 2,
    "delay_minutes": 10,
    "reason_code": "test_incident",
    "reason_text": "Manual API test incident",
    "status": "open",
    "geo_lat": null,
    "geo_lng": null,
    "raw_payload": { "test": true },
    "fingerprint": "manual-central-test-202603121600"
  }'
echo -e "\n"

echo "Done."

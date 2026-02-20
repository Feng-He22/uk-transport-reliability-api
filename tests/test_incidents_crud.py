from datetime import datetime, timezone
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_incident_crud_flow():
    payload = {
        "source": "user",
        "mode": "tube",
        "line_id": "victoria",
        "line_name": "Victoria",
        "station_id": "oxford-circus",
        "station_name": "Oxford Circus",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "severity": 3,
        "delay_minutes": 7,
        "reason_code": "signal",
        "reason_text": "Signal failure",
        "status": "open",
    }

    r = client.post("/incidents", json=payload)
    assert r.status_code == 201
    created = r.json()
    assert created["line_id"] == "victoria"
    incident_id = created["id"]

    r = client.get(f"/incidents/{incident_id}")
    assert r.status_code == 200
    assert r.json()["id"] == incident_id

    r = client.patch(f"/incidents/{incident_id}", json={"status": "resolved"})
    assert r.status_code == 200
    assert r.json()["status"] == "resolved"

    r = client.get("/incidents", params={"line_id": "victoria", "limit": 10})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.delete(f"/incidents/{incident_id}")
    assert r.status_code == 204

    r = client.get(f"/incidents/{incident_id}")
    assert r.status_code == 404
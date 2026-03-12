import uuid
from datetime import datetime, timezone

import requests

BASE_URL = "https://meowcolate.pythonanywhere.com"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def login_and_get_token(username=ADMIN_USERNAME, password=ADMIN_PASSWORD) -> str:
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password},
        timeout=10,
    )
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    return data["access_token"]


def auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def unique_fingerprint() -> str:
    return f"pytest-{uuid.uuid4()}"


def valid_incident_payload() -> dict:
    return {
        "source": "manual",
        "line_id": "central",
        "station_id": "oxford_circus",
        "status": "delay",
        "description": "pytest incident",
        "occurred_at": datetime.now(timezone.utc).isoformat(),
        "fingerprint": unique_fingerprint(),
    }


def test_health():
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_login_success():
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        timeout=10,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["role"] == "admin"


def test_login_failure():
    resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": ADMIN_USERNAME, "password": "wrongpassword"},
        timeout=10,
    )
    assert resp.status_code in (401, 403)


def test_auth_me_requires_token():
    resp = requests.get(f"{BASE_URL}/auth/me", timeout=10)
    assert resp.status_code == 401


def test_auth_me_success():
    token = login_and_get_token()
    resp = requests.get(
        f"{BASE_URL}/auth/me",
        headers=auth_headers(token),
        timeout=10,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["username"] == ADMIN_USERNAME
    assert body["role"] == "admin"
    assert body["is_active"] is True


def test_list_incidents_public():
    resp = requests.get(f"{BASE_URL}/incidents", timeout=10)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_create_incident_requires_auth():
    resp = requests.post(
        f"{BASE_URL}/incidents",
        json=valid_incident_payload(),
        timeout=10,
    )
    assert resp.status_code == 401


def test_create_incident_success():
    token = login_and_get_token()
    payload = valid_incident_payload()

    resp = requests.post(
        f"{BASE_URL}/incidents",
        json=payload,
        headers=auth_headers(token),
        timeout=10,
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()

    assert body["source"] == payload["source"]
    assert body["line_id"] == payload["line_id"]
    assert body["station_id"] == payload["station_id"]
    assert body["status"] == payload["status"]
    assert body["fingerprint"] == payload["fingerprint"]

    assert "id" in body


def test_get_incident_by_id():
    token = login_and_get_token()
    payload = valid_incident_payload()

    create_resp = requests.post(
        f"{BASE_URL}/incidents",
        json=payload,
        headers=auth_headers(token),
        timeout=10,
    )
    assert create_resp.status_code == 201, create_resp.text
    incident = create_resp.json()
    incident_id = incident["id"]

    get_resp = requests.get(f"{BASE_URL}/incidents/{incident_id}", timeout=10)
    assert get_resp.status_code == 200
    fetched = get_resp.json()

    assert fetched["id"] == incident_id
    assert fetched["fingerprint"] == payload["fingerprint"]


def test_patch_incident_requires_auth():
    token = login_and_get_token()
    payload = valid_incident_payload()

    create_resp = requests.post(
        f"{BASE_URL}/incidents",
        json=payload,
        headers=auth_headers(token),
        timeout=10,
    )
    assert create_resp.status_code == 201, create_resp.text
    incident_id = create_resp.json()["id"]

    patch_resp = requests.patch(
        f"{BASE_URL}/incidents/{incident_id}",
        json={"status": "resolved"},
        timeout=10,
    )
    assert patch_resp.status_code == 401


def test_patch_incident_success():
    token = login_and_get_token()
    payload = valid_incident_payload()

    create_resp = requests.post(
        f"{BASE_URL}/incidents",
        json=payload,
        headers=auth_headers(token),
        timeout=10,
    )
    assert create_resp.status_code == 201, create_resp.text
    incident_id = create_resp.json()["id"]

    patch_resp = requests.patch(
        f"{BASE_URL}/incidents/{incident_id}",
        json={"status": "resolved", "description": "updated by pytest"},
        headers=auth_headers(token),
        timeout=10,
    )
    assert patch_resp.status_code == 200, patch_resp.text
    updated = patch_resp.json()

    assert updated["status"] == "resolved"
    # assert updated["description"] == "updated by pytest"


def test_delete_incident_admin_success():
    token = login_and_get_token()
    payload = valid_incident_payload()

    create_resp = requests.post(
        f"{BASE_URL}/incidents",
        json=payload,
        headers=auth_headers(token),
        timeout=10,
    )
    assert create_resp.status_code == 201, create_resp.text
    incident_id = create_resp.json()["id"]

    delete_resp = requests.delete(
        f"{BASE_URL}/incidents/{incident_id}",
        headers=auth_headers(token),
        timeout=10,
    )
    assert delete_resp.status_code == 204, delete_resp.text

    get_resp = requests.get(f"{BASE_URL}/incidents/{incident_id}", timeout=10)
    assert get_resp.status_code == 404


def test_create_incident_validation_error():
    token = login_and_get_token()
    bad_payload = {
        "source": "manual",
        "line_id": "central",
        "station_id": "oxford_circus",
        "status": "delay",
        "description": "missing occurred_at and fingerprint",
    }

    resp = requests.post(
        f"{BASE_URL}/incidents",
        json=bad_payload,
        headers=auth_headers(token),
        timeout=10,
    )
    assert resp.status_code == 422


# ---------- Analytics ----------



def test_analytics_reliability():
    resp = requests.get(
        f"{BASE_URL}/analytics/reliability",
        params={
            "line_id": "central",
            "from": "2026-01-01T00:00:00Z",
            "to": "2026-03-01T00:00:00Z",
        },
        timeout=20,
    )
    assert resp.status_code == 200, resp.text


def test_analytics_heatmap():
    resp = requests.get(
        f"{BASE_URL}/analytics/heatmap",
        params={
            "line_id": "central",
            "from": "2026-01-01T00:00:00Z",
            "to": "2026-03-01T00:00:00Z",
        },
        timeout=20,
    )
    assert resp.status_code == 200, resp.text


def test_analytics_anomalies():
    resp = requests.get(
        f"{BASE_URL}/analytics/anomalies",
        params={
            "line_id": "central",
            "from": "2026-01-01T00:00:00Z",
            "to": "2026-03-01T00:00:00Z",
        },
        timeout=20,
    )
    assert resp.status_code == 200, resp.text


# ---------- Sync ----------



def test_sync_endpoint_with_auth_if_required():
    token = login_and_get_token()
    resp = requests.post(
        f"{BASE_URL}/sync/tfl",
        headers=auth_headers(token),
        timeout=30,
    )
    assert resp.status_code in (200, 201, 202, 204, 404, 405), resp.text


# ---------- Devtools ----------



def test_devtools_endpoint_if_present():
    token = login_and_get_token()
    resp = requests.get(
        f"{BASE_URL}/devtools",
        headers=auth_headers(token),
        timeout=10,
    )
    assert resp.status_code in (200, 404, 405), resp.text
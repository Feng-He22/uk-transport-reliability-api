import requests

BASE_URL = "http://localhost:8000"

username = "admin"
password = "admin123"

print("1. Testing login...")

login_resp = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "username": username,
        "password": password
    }
)

print("Login status:", login_resp.status_code)

if login_resp.status_code != 200:
    print(login_resp.text)
    exit()

data = login_resp.json()
token = data["access_token"]

print("Access token received")

headers = {
    "Authorization": f"Bearer {token}"
}

print("\n2. Testing protected endpoint /auth/me")

me_resp = requests.get(
    f"{BASE_URL}/auth/me",
    headers=headers
)

print("Status:", me_resp.status_code)
print(me_resp.json())

print("\n3. Testing public endpoint /incidents")

incidents_resp = requests.get(
    f"{BASE_URL}/incidents"
)

print("Status:", incidents_resp.status_code)

print("\n4. Testing protected create incident")

payload = {
    "source": "manual",
    "line_id": "central",
    "station_id": "oxford_circus",
    "status": "delay",
    "description": "test incident"
}

create_resp = requests.post(
    f"{BASE_URL}/incidents",
    json=payload,
    headers=headers
)

print("Create status:", create_resp.status_code)
print(create_resp.text)
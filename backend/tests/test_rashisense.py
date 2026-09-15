"""Rashisense backend API tests."""
import os
import time
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://cosmic-stones-2.preview.emergentagent.com").rstrip("/")
# Try backend/frontend .env order
try:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL"):
                BASE_URL = line.split("=", 1)[1].strip().strip('"').rstrip("/")
except Exception:
    pass

API = f"{BASE_URL}/api"

ADMIN_USER = "admin"
ADMIN_PASS = "Rashi@2026"


@pytest.fixture(scope="module")
def s():
    return requests.Session()


@pytest.fixture(scope="module")
def new_user(s):
    email = f"test_user_{uuid.uuid4().hex[:8]}@rashisense.com"
    r = s.post(f"{API}/auth/register", json={"name": "Test User", "email": email, "password": "User@2026"})
    assert r.status_code == 200, r.text
    data = r.json()
    assert "access_token" in data and "user" in data
    assert data["user"]["email"] == email
    assert data["user"]["role"] == "user"
    return {"email": email, "password": "User@2026", "token": data["access_token"], "id": data["user"]["id"]}


@pytest.fixture(scope="module")
def admin_token(s):
    r = s.post(f"{API}/auth/login", json={"email": ADMIN_USER, "password": ADMIN_PASS})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["user"]["role"] == "admin"
    return data["access_token"]


# --- Root & reference data ---
def test_root(s):
    r = s.get(f"{API}/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_rashis(s):
    r = s.get(f"{API}/rashis")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) == 12
    assert data[0]["sa"] == "Mesha"


def test_gemstones(s):
    r = s.get(f"{API}/gemstones")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and len(data) >= 9
    assert any(g["planet"] == "Sun" and g["name"] == "Ruby" for g in data)


# --- Auth ---
def test_register_duplicate(s, new_user):
    r = s.post(f"{API}/auth/register", json={"name": "x", "email": new_user["email"], "password": "abc"})
    assert r.status_code == 400


def test_login_with_email(s, new_user):
    r = s.post(f"{API}/auth/login", json={"email": new_user["email"], "password": new_user["password"]})
    assert r.status_code == 200
    assert r.json()["user"]["email"] == new_user["email"]


def test_login_admin_by_username(s):
    r = s.post(f"{API}/auth/login", json={"email": "admin", "password": ADMIN_PASS})
    assert r.status_code == 200
    assert r.json()["user"]["role"] == "admin"


def test_login_admin_by_email(s):
    r = s.post(f"{API}/auth/login", json={"email": "admin@rashisense.com", "password": ADMIN_PASS})
    assert r.status_code == 200


def test_login_bad(s):
    r = s.post(f"{API}/auth/login", json={"email": "nope@x.com", "password": "wrong"})
    assert r.status_code == 401


def test_me(s, new_user):
    r = s.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {new_user['token']}"})
    assert r.status_code == 200
    assert r.json()["email"] == new_user["email"]


def test_me_no_token(s):
    r = s.get(f"{API}/auth/me")
    assert r.status_code == 401


# --- Rashi calculate ---
BIRTH = {"name": "Ravi", "gender": "Male", "dob": "1992-05-15", "time": "14:30", "place": "Mumbai, India",
         "problem": "career growth"}


def test_calculate_anon(s):
    r = s.post(f"{API}/rashi/calculate", json=BIRTH)
    assert r.status_code == 200, r.text
    d = r.json()
    for k in ["chart", "gemstone", "reading", "input"]:
        assert k in d
    chart = d["chart"]
    for k in ["moon_sign", "sun_sign", "ascendant", "nakshatra", "pada", "ruling_planet", "planet_positions"]:
        assert k in chart
    assert chart["moon_sign"]["sa"] in [r["sa"] for r in requests.get(f"{API}/rashis").json()]
    gem = d["gemstone"]
    assert gem["planet"] and gem["name"]
    reading = d["reading"]
    for k in ["summary", "career", "love", "health", "wealth", "spiritual",
              "lucky_color", "lucky_number", "gemstone_reason"]:
        assert k in reading, f"missing reading key: {k}"
    assert isinstance(reading["lucky_number"], int)
    # Anonymous should NOT be saved
    assert not d.get("saved")


def test_calculate_bad_date(s):
    bad = dict(BIRTH, dob="not-a-date")
    r = s.post(f"{API}/rashi/calculate", json=bad)
    assert r.status_code == 400


def test_calculate_deterministic(s):
    r1 = s.post(f"{API}/rashi/calculate", json=BIRTH).json()
    r2 = s.post(f"{API}/rashi/calculate", json=BIRTH).json()
    assert r1["chart"]["moon_sign"]["sa"] == r2["chart"]["moon_sign"]["sa"]
    assert r1["chart"]["nakshatra"] == r2["chart"]["nakshatra"]


# --- Readings CRUD ---
def test_calculate_saves_for_user(s, new_user):
    r = s.post(f"{API}/rashi/calculate", json=BIRTH,
               headers={"Authorization": f"Bearer {new_user['token']}"})
    assert r.status_code == 200
    d = r.json()
    assert d.get("saved") is True
    assert "id" in d
    new_user["reading_id"] = d["id"]


def test_list_readings(s, new_user):
    r = s.get(f"{API}/readings", headers={"Authorization": f"Bearer {new_user['token']}"})
    assert r.status_code == 200
    lst = r.json()
    assert any(x["id"] == new_user["reading_id"] for x in lst)


def test_delete_reading(s, new_user):
    rid = new_user["reading_id"]
    r = s.delete(f"{API}/readings/{rid}", headers={"Authorization": f"Bearer {new_user['token']}"})
    assert r.status_code == 200
    # Verify removed
    r2 = s.get(f"{API}/readings", headers={"Authorization": f"Bearer {new_user['token']}"})
    assert not any(x["id"] == rid for x in r2.json())


# --- Admin ---
def test_admin_stats(s, admin_token):
    r = s.get(f"{API}/admin/stats", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    d = r.json()
    for k in ["total_users", "total_readings", "total_calculations"]:
        assert k in d and isinstance(d[k], int)


def test_admin_users(s, admin_token):
    r = s.get(f"{API}/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200
    assert isinstance(r.json(), list) and len(r.json()) >= 1


def test_admin_logs(s, admin_token):
    r = s.get(f"{API}/admin/logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert r.status_code == 200


def test_admin_forbidden_for_user(s, new_user):
    r = s.get(f"{API}/admin/stats", headers={"Authorization": f"Bearer {new_user['token']}"})
    assert r.status_code == 403
    r2 = s.get(f"{API}/admin/users", headers={"Authorization": f"Bearer {new_user['token']}"})
    assert r2.status_code == 403

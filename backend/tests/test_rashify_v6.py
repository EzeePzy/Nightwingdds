"""Rashify v6: cities autocomplete, match, dasha insights, settings, language."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")
try:
    with open("/app/frontend/.env") as f:
        for line in f:
            if line.startswith("REACT_APP_BACKEND_URL"):
                BASE_URL = line.split("=", 1)[1].strip().strip('"').rstrip("/")
except Exception:
    pass

API = f"{BASE_URL}/api"
ADMIN = {"email": "admin", "password": "Rashi@2026"}


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=10)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def h(t):
    return {"Authorization": f"Bearer {t}"}


# --- Cities autocomplete ---
def test_cities_short_query_empty():
    r = requests.get(f"{API}/cities", params={"q": "k"}, timeout=10)
    assert r.status_code == 200
    assert r.json()["results"] == []


def test_cities_query_returns_results():
    r = requests.get(f"{API}/cities", params={"q": "ko"}, timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["results"], list)
    assert len(data["results"]) >= 3
    for label in data["results"]:
        assert "," in label  # "City, Country"


# --- Guna Milan / Matching ---
def test_match_returns_valid_ashtakoot():
    payload = {
        "boy": {"name": "Ravi", "dob": "1995-08-20", "time": "14:30", "place": "Jaipur, India"},
        "girl": {"name": "Sita", "dob": "1997-05-12", "time": "09:15", "place": "Delhi, India"},
    }
    r = requests.post(f"{API}/match", json=payload, timeout=15)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "kootas" in data and len(data["kootas"]) == 8
    total_sum = 0
    for k in data["kootas"]:
        assert set(k.keys()) >= {"name", "obtained", "max", "meaning"}
        assert 0 <= k["obtained"] <= k["max"]
        total_sum += k["obtained"]
    assert data["max_total"] == 36
    assert 0 <= data["total"] <= 36
    assert abs(data["total"] - total_sum) < 0.05
    assert data["verdict"]
    for who in ("boy", "girl"):
        assert data[who]["rashi"] and data[who]["nakshatra"]


# --- Dasha insights ---
def test_dasha_insights_english():
    payload = {"rashi": "Vrishchika", "mahadasha": "Venus", "antardasha": "Rahu", "language": "en"}
    r = requests.post(f"{API}/dasha/insights", json=payload, timeout=30)
    assert r.status_code == 200, r.text
    d = r.json()
    for k in ("overview", "career", "love", "money"):
        assert k in d and isinstance(d[k], str) and len(d[k]) > 10


# --- Settings ---
def test_get_settings_defaults():
    r = requests.get(f"{API}/settings", timeout=10)
    assert r.status_code == 200
    d = r.json()
    assert "brand_name" in d
    assert "hero_title_gold" in d
    assert "hero_title_plain" in d
    assert "hero_subtitle" in d
    assert "pdf_price_inr" in d


def test_update_settings_admin_persists(admin_token):
    payload = {"brand_name": "Rashify", "pdf_price_inr": 249}
    r = requests.put(f"{API}/admin/settings", json=payload, headers=h(admin_token), timeout=10)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["brand_name"] == "Rashify"
    assert float(d["pdf_price_inr"]) == 249

    # GET again to verify persistence
    r2 = requests.get(f"{API}/settings", timeout=10)
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2["brand_name"] == "Rashify"
    assert float(d2["pdf_price_inr"]) == 249


def test_update_settings_non_admin_forbidden():
    # register a normal user
    email = f"TEST_settings_{uuid.uuid4().hex[:8]}@example.com"
    reg = requests.post(f"{API}/auth/register",
                        json={"name": "T", "email": email, "password": "User@2026"}, timeout=10)
    assert reg.status_code == 200
    tok = reg.json()["access_token"]
    r = requests.put(f"{API}/admin/settings", json={"brand_name": "Hacked"},
                     headers=h(tok), timeout=10)
    assert r.status_code == 403


# --- Language on calculate & horoscope ---
def test_rashi_calculate_hindi():
    r = requests.post(f"{API}/rashi/calculate", json={
        "name": "Aarav", "gender": "Male", "dob": "1990-01-15", "time": "10:00",
        "place": "Mumbai, India", "language": "hi"
    }, timeout=45)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["chart"]
    reading = d["reading"]
    for k in ("summary", "career", "love", "health", "wealth", "spiritual", "gemstone_reason"):
        assert k in reading and reading[k]


def test_horoscope_hindi():
    r = requests.get(f"{API}/horoscope/mesha", params={"period": "daily", "language": "hi"}, timeout=30)
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["forecast"]
    for k in ("overview", "career", "love", "health", "finance"):
        assert k in d["forecast"] and d["forecast"][k]

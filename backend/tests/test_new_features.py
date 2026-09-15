"""New feature tests: precise chart, horoscope, family profiles."""
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


@pytest.fixture(scope="module")
def s():
    return requests.Session()


@pytest.fixture(scope="module")
def user_token(s):
    email = f"test_user_{uuid.uuid4().hex[:8]}@rashisense.com"
    r = s.post(f"{API}/auth/register", json={"name": "Test User", "email": email, "password": "User@2026"})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def auth(t):
    return {"Authorization": f"Bearer {t}"}


# --- Precise Chart (Swiss Ephemeris) ---
def test_precise_chart_jaipur():
    r = requests.post(f"{API}/rashi/calculate", json={
        "name": "Arjun", "gender": "Male", "dob": "1995-08-20", "time": "14:30",
        "place": "Jaipur, India", "problem": ""
    })
    assert r.status_code == 200, r.text
    chart = r.json()["chart"]
    assert chart.get("accuracy") == "swiss_ephemeris_lahiri", f"got accuracy={chart.get('accuracy')}"
    loc = chart.get("birth_location")
    assert loc is not None, "no birth_location"
    assert 26.0 < loc["lat"] < 28.0, f"lat={loc['lat']}"
    assert 75.0 < loc["lon"] < 77.0, f"lon={loc['lon']}"
    assert loc["tz"] == "Asia/Kolkata"
    ay = chart.get("ayanamsa")
    assert isinstance(ay, (int, float)) and 23.0 < ay < 25.0, f"ayanamsa={ay}"
    assert "planet_degrees" in chart


def test_precise_chart_place_differs():
    payload = {"name": "X", "gender": "Male", "dob": "1995-08-20", "time": "14:30", "problem": ""}
    r1 = requests.post(f"{API}/rashi/calculate", json={**payload, "place": "Jaipur, India"})
    r2 = requests.post(f"{API}/rashi/calculate", json={**payload, "place": "New York, USA"})
    assert r1.status_code == 200 and r2.status_code == 200
    c1, c2 = r1.json()["chart"], r2.json()["chart"]
    # timezone or ascendant must differ
    tz_diff = c1["birth_location"]["tz"] != c2["birth_location"]["tz"]
    asc_diff = c1["ascendant"]["sa"] != c2["ascendant"]["sa"]
    assert tz_diff or asc_diff, "Different places should produce different tz or ascendant"


# --- Horoscope ---
@pytest.mark.parametrize("period", ["daily", "weekly", "yearly"])
def test_horoscope_periods(period):
    r = requests.get(f"{API}/horoscope/simha", params={"period": period})
    assert r.status_code == 200, r.text
    d = r.json()
    assert d["period"] == period
    assert d["rashi"]["key"] == "simha"
    assert "date_key" in d
    forecast = d["forecast"]
    for k in ["overview", "career", "love", "health", "finance", "lucky_color", "lucky_number"]:
        assert k in forecast, f"missing forecast key {k}"


def test_horoscope_cached():
    r1 = requests.get(f"{API}/horoscope/simha?period=daily").json()
    r2 = requests.get(f"{API}/horoscope/simha?period=daily").json()
    assert r1["date_key"] == r2["date_key"]
    assert r1["forecast"] == r2["forecast"]


def test_horoscope_unknown_rashi():
    r = requests.get(f"{API}/horoscope/notarashi?period=daily")
    assert r.status_code == 404


# --- Family Profiles ---
def test_profiles_unauth():
    r = requests.get(f"{API}/profiles")
    assert r.status_code == 401


def test_profiles_crud(s, user_token):
    # Create
    payload = {"name": "Dad", "relation": "Father", "gender": "Male",
               "dob": "1965-03-10", "time": "08:15", "place": "Delhi, India"}
    r = s.post(f"{API}/profiles", json=payload, headers=auth(user_token))
    assert r.status_code == 200, r.text
    p = r.json()
    assert p["name"] == "Dad" and "id" in p
    pid = p["id"]

    # List
    r = s.get(f"{API}/profiles", headers=auth(user_token))
    assert r.status_code == 200
    lst = r.json()
    assert any(x["id"] == pid for x in lst)

    # Isolation from another user
    email2 = f"other_{uuid.uuid4().hex[:8]}@rashisense.com"
    r2 = s.post(f"{API}/auth/register", json={"name": "Other", "email": email2, "password": "User@2026"})
    other_token = r2.json()["access_token"]
    r = s.get(f"{API}/profiles", headers=auth(other_token))
    assert r.status_code == 200
    assert not any(x["id"] == pid for x in r.json())

    # Delete
    r = s.delete(f"{API}/profiles/{pid}", headers=auth(user_token))
    assert r.status_code == 200
    r = s.get(f"{API}/profiles", headers=auth(user_token))
    assert not any(x["id"] == pid for x in r.json())

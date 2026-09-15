"""Vimshottari Dasha backend tests (Koushik chart)."""
import os
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

KOUSHIK = {
    "name": "Koushik",
    "gender": "Male",
    "dob": "2002-01-10",
    "time": "22:00",
    "place": "Kolkata, India",
}


@pytest.fixture(scope="module")
def koushik_chart():
    r = requests.post(f"{API}/rashi/calculate", json=KOUSHIK, timeout=60)
    assert r.status_code == 200, r.text
    return r.json()


def test_moon_sign_scorpio(koushik_chart):
    c = koushik_chart["chart"]
    assert c["moon_sign"]["sa"] == "Vrishchika"
    assert c["nakshatra"] == "Jyeshtha"
    assert abs(c["planet_degrees"]["Moon"] - 22.81) < 0.5


def test_dasha_first_period_mercury(koushik_chart):
    dasha = koushik_chart["chart"]["dasha"]
    assert isinstance(dasha, list) and len(dasha) > 0
    first = dasha[0]
    assert first["planet"] == "Mercury"
    assert 9.0 <= first["years"] <= 9.3, f"years={first['years']}"
    # end date around 2011-03-11 (±30 days)
    assert first["end"].startswith("2011-"), first["end"]


def test_dasha_contiguous(koushik_chart):
    dasha = koushik_chart["chart"]["dasha"]
    for i in range(1, len(dasha)):
        assert dasha[i]["start"] == dasha[i - 1]["end"], (i, dasha[i - 1], dasha[i])
    for p in dasha:
        for k in ("planet", "start", "end", "years"):
            assert k in p


def test_current_dasha_venus(koushik_chart):
    cur = koushik_chart["chart"]["current_dasha"]
    assert cur is not None
    assert cur.get("is_current") is True
    assert cur["planet"] == "Venus"


def test_regression_fields(koushik_chart):
    c = koushik_chart["chart"]
    for k in ["western_sun_sign", "sun_sign", "ascendant", "planet_positions",
              "planet_degrees", "ayanamsa"]:
        assert k in c
    assert c["accuracy"] == "swiss_ephemeris_lahiri"
    # All 9 planets
    for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        assert p in c["planet_degrees"]
        assert p in c["planet_positions"]
    assert "gemstone" in koushik_chart
    assert "reading" in koushik_chart

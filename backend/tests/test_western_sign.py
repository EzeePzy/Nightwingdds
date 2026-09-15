"""Tests for western_sun_sign feature in /api/rashi/calculate."""
import os
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL") or open("/app/frontend/.env").read().split("REACT_APP_BACKEND_URL=")[1].split("\n")[0].strip()
BASE_URL = BASE_URL.rstrip("/")
API = f"{BASE_URL}/api"


def _calc(payload):
    r = requests.post(f"{API}/rashi/calculate", json=payload, timeout=60)
    return r


def test_scorpio_western_sun_1992_11_10():
    r = _calc({"name": "Test", "dob": "1992-11-10", "time": "09:00", "place": "Mumbai, India"})
    assert r.status_code == 200, r.text
    data = r.json()
    chart = data["chart"]
    assert chart["western_sun_sign"]["en"] == "Scorpio"
    # Vedic (sidereal) Sun and Moon should differ from western sun
    assert chart["sun_sign"]["en"] != "Scorpio" or chart["moon_sign"]["en"] != "Scorpio"
    # Moon rashi (Vedic Rashi) should not equal the western sun sign here
    assert chart["moon_sign"]["en"] != chart["western_sun_sign"]["en"]


def test_aries_western_sun_1990_04_05():
    r = _calc({"name": "Test", "dob": "1990-04-05", "time": "09:00", "place": "Mumbai, India"})
    assert r.status_code == 200, r.text
    chart = r.json()["chart"]
    assert chart["western_sun_sign"]["en"] == "Aries"


def test_regression_response_fields():
    r = _calc({"name": "Test", "dob": "1992-11-10", "time": "09:00", "place": "Mumbai, India"})
    assert r.status_code == 200
    data = r.json()
    chart = data["chart"]
    for key in ["moon_sign", "sun_sign", "ascendant", "nakshatra", "pada", "planet_positions", "planet_degrees", "ayanamsa", "accuracy", "western_sun_sign"]:
        assert key in chart, f"missing {key}"
    assert chart["accuracy"] == "swiss_ephemeris_lahiri"
    assert "gemstone" in data
    assert "reading" in data
    # western_sun_sign structure
    ws = chart["western_sun_sign"]
    assert "en" in ws and "sa" in ws

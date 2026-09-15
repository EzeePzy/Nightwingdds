"""Tests for Antardasha, Navamsa (D9), Discount admin, and Paid PDF flow."""
import os
import time
import uuid
import pytest
import requests

BASE_URL = os.environ['REACT_APP_BACKEND_URL'].rstrip('/') if os.environ.get('REACT_APP_BACKEND_URL') else None
if not BASE_URL:
    # fallback to reading frontend .env
    with open('/app/frontend/.env') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                BASE_URL = line.split('=', 1)[1].strip().rstrip('/')
                break

API = f"{BASE_URL}/api"
ADMIN = {"email": "admin", "password": "Rashi@2026"}
KOUSHIK = {"name": "Koushik", "dob": "2002-01-10", "time": "22:00", "place": "Kolkata, India"}
TIMEOUT = 90


@pytest.fixture(scope="module")
def admin_token():
    r = requests.post(f"{API}/auth/login", json=ADMIN, timeout=30)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def user_token():
    email = f"TEST_pdfuser_{uuid.uuid4().hex[:10]}@example.com"
    r = requests.post(f"{API}/auth/register",
                      json={"name": "PDF Tester", "email": email, "password": "Passw0rd!"},
                      timeout=30)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def user2_token():
    email = f"TEST_pdfuser2_{uuid.uuid4().hex[:10]}@example.com"
    r = requests.post(f"{API}/auth/register",
                      json={"name": "PDF Tester2", "email": email, "password": "Passw0rd!"},
                      timeout=30)
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture(scope="module")
def calc_reading(user_token):
    r = requests.post(f"{API}/rashi/calculate", json=KOUSHIK,
                      headers={"Authorization": f"Bearer {user_token}"}, timeout=TIMEOUT)
    assert r.status_code == 200, r.text
    return r.json()


# ---------- Antardasha ----------
class TestAntardasha:
    def test_dasha_has_antardashas(self, calc_reading):
        dasha = calc_reading["chart"]["dasha"]
        assert isinstance(dasha, list) and len(dasha) > 0
        for period in dasha:
            assert "antardashas" in period, f"missing antardashas in {period.get('planet')}"
            ads = period["antardashas"]
            assert isinstance(ads, list) and len(ads) > 0
            for a in ads:
                assert {"planet", "start", "end"}.issubset(a.keys())
                assert "is_current" in a

    def test_current_dasha_has_antardasha(self, calc_reading):
        cd = calc_reading["chart"].get("current_dasha")
        assert cd is not None
        ad = cd.get("antardasha")
        assert ad and "planet" in ad

    def test_antardasha_sum_matches_mahadasha(self, calc_reading):
        from datetime import datetime
        dasha = calc_reading["chart"]["dasha"]
        for period in dasha[:3]:
            ads = period["antardashas"]
            m_start = datetime.fromisoformat(period["start"])
            m_end = datetime.fromisoformat(period["end"])
            a_start = datetime.fromisoformat(ads[0]["start"])
            a_end = datetime.fromisoformat(ads[-1]["end"])
            assert abs((a_start - m_start).total_seconds()) < 86400 * 2
            assert abs((a_end - m_end).total_seconds()) < 86400 * 2


# ---------- Navamsa ----------
class TestNavamsa:
    def test_navamsa_positions(self, calc_reading):
        nav = calc_reading["chart"].get("navamsa_positions")
        assert nav and isinstance(nav, dict)
        for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            assert p in nav and isinstance(nav[p], str) and len(nav[p]) > 0

    def test_navamsa_ascendant(self, calc_reading):
        na = calc_reading["chart"].get("navamsa_ascendant")
        assert na and "sa" in na and "en" in na


# ---------- Discount admin ----------
class TestDiscountAdmin:
    def test_non_admin_forbidden(self, user_token):
        r = requests.post(f"{API}/admin/discounts",
                          json={"code": "TEST50", "percent": 50},
                          headers={"Authorization": f"Bearer {user_token}"}, timeout=15)
        assert r.status_code == 403

    def test_admin_crud(self, admin_token):
        h = {"Authorization": f"Bearer {admin_token}"}
        # cleanup pre-existing
        existing = requests.get(f"{API}/admin/discounts", headers=h, timeout=15).json()
        for d in existing:
            if d["code"] in ("TEST50", "TESTFREE"):
                requests.delete(f"{API}/admin/discounts/{d['id']}", headers=h)

        # Create
        r = requests.post(f"{API}/admin/discounts", json={"code": "TEST50", "percent": 50},
                          headers=h, timeout=15)
        assert r.status_code == 200, r.text
        d = r.json()
        assert d["code"] == "TEST50" and d["percent"] == 50 and d["active"] is True
        did = d["id"]

        # List
        r = requests.get(f"{API}/admin/discounts", headers=h, timeout=15)
        assert r.status_code == 200
        assert any(x["code"] == "TEST50" for x in r.json())

        # Toggle off
        r = requests.patch(f"{API}/admin/discounts/{did}", headers=h, timeout=15)
        assert r.status_code == 200 and r.json()["active"] is False

        # Validate off => invalid
        r = requests.post(f"{API}/pdf/validate-discount", json={"code": "TEST50"}, timeout=15)
        assert r.status_code == 200 and r.json()["valid"] is False

        # Toggle on
        requests.patch(f"{API}/admin/discounts/{did}", headers=h, timeout=15)
        r = requests.post(f"{API}/pdf/validate-discount", json={"code": "TEST50"}, timeout=15)
        assert r.json()["valid"] is True and r.json()["percent"] == 50

        # Unknown
        r = requests.post(f"{API}/pdf/validate-discount", json={"code": "NOPE_ZZZ"}, timeout=15)
        assert r.json()["valid"] is False

        # Delete
        r = requests.delete(f"{API}/admin/discounts/{did}", headers=h, timeout=15)
        assert r.status_code == 200


# ---------- Paid PDF ----------
class TestPaidPdf:
    def test_free_path_downloads_pdf(self, admin_token, user_token, calc_reading):
        h_admin = {"Authorization": f"Bearer {admin_token}"}
        h_user = {"Authorization": f"Bearer {user_token}"}

        # cleanup
        for d in requests.get(f"{API}/admin/discounts", headers=h_admin).json():
            if d["code"] == "TESTFREE":
                requests.delete(f"{API}/admin/discounts/{d['id']}", headers=h_admin)

        r = requests.post(f"{API}/admin/discounts", json={"code": "TESTFREE", "percent": 100},
                          headers=h_admin, timeout=15)
        assert r.status_code == 200

        reading_id = calc_reading.get("id")
        assert reading_id, "reading must be saved"

        r = requests.post(f"{API}/pdf/checkout",
                          json={"reading_id": reading_id, "origin_url": BASE_URL,
                                "discount_code": "TESTFREE"},
                          headers=h_user, timeout=30)
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["free"] is True and "session_id" in j
        sid = j["session_id"]

        r = requests.get(f"{API}/pdf/download/{sid}", timeout=30)
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("application/pdf")
        assert r.content[:4] == b"%PDF"
        assert len(r.content) > 2000

    def test_stripe_path_returns_url(self, user_token, calc_reading):
        h = {"Authorization": f"Bearer {user_token}"}
        r = requests.post(f"{API}/pdf/checkout",
                          json={"reading_id": calc_reading["id"], "origin_url": BASE_URL},
                          headers=h, timeout=30)
        assert r.status_code == 200, r.text
        j = r.json()
        assert j["free"] is False
        assert j["amount"] == 199.0
        assert j["checkout_url"].startswith("https://checkout.stripe.com")
        sid = j["session_id"]

        # Status
        r = requests.get(f"{API}/payments/status/{sid}", timeout=30)
        assert r.status_code == 200
        assert r.json()["payment_status"] in ("pending", "unpaid", "initiated")

        # Unpaid download blocked
        r = requests.get(f"{API}/pdf/download/{sid}", timeout=15)
        assert r.status_code == 402

    def test_checkout_requires_auth(self, calc_reading):
        r = requests.post(f"{API}/pdf/checkout",
                          json={"reading_id": calc_reading["id"], "origin_url": BASE_URL},
                          timeout=15)
        assert r.status_code == 401

    def test_cannot_checkout_others_reading(self, user2_token, calc_reading):
        h = {"Authorization": f"Bearer {user2_token}"}
        r = requests.post(f"{API}/pdf/checkout",
                          json={"reading_id": calc_reading["id"], "origin_url": BASE_URL},
                          headers=h, timeout=15)
        assert r.status_code == 404

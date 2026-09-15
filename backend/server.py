from dotenv import load_dotenv
from pathlib import Path
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

import os
import logging
import secrets
from datetime import datetime, timezone, timedelta
from typing import List, Optional

import bcrypt
import jwt
from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr

from astro import compute_chart, recommend_gemstone, RASHIS, GEMSTONES, NAKSHATRAS
from geo import geocode, search_cities
from matchmaking import compute_guna_milan
from pdf_gen import generate_kundali_pdf
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionRequest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("rashisense")

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
STRIPE_API_KEY = os.environ.get('STRIPE_API_KEY', 'sk_test_emergent')
PDF_PRICE_INR = float(os.environ.get('PDF_PRICE_INR', '199'))

app = FastAPI(title="Rashisense API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer(auto_error=False)


# ---------- Auth helpers ----------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_access_token(user_id: str, email: str, role: str) -> str:
    payload = {"sub": user_id, "email": email, "role": role,
               "exp": datetime.now(timezone.utc) + timedelta(days=7), "type": "access"}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def serialize_user(u: dict) -> dict:
    return {"id": str(u["_id"]), "email": u["email"], "name": u.get("name", ""),
            "username": u.get("username"), "role": u.get("role", "user"),
            "created_at": u.get("created_at")}


async def get_current_user(request: Request,
                           creds: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> dict:
    token = None
    if creds:
        token = creds.credentials
    if not token:
        token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_admin_user(user: dict = Depends(get_current_user)) -> dict:
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


# ---------- Models ----------
class RegisterInput(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginInput(BaseModel):
    email: str  # accepts email or username
    password: str


class BirthDetails(BaseModel):
    name: str
    gender: Optional[str] = "Not specified"
    dob: str          # YYYY-MM-DD
    time: str         # HH:MM (24h)
    place: str
    problem: Optional[str] = ""
    language: Optional[str] = "en"


LANG_NAMES = {"en": "English", "hi": "Hindi", "bn": "Bengali"}


def lang_instruction(language: str) -> str:
    name = LANG_NAMES.get((language or "en").lower(), "English")
    return "" if name == "English" else f" Write ALL text values in {name} language (Devanagari/Bengali script as appropriate)."


class ProfileInput(BaseModel):
    name: str
    relation: Optional[str] = "Self"
    gender: Optional[str] = "Not specified"
    dob: str
    time: str
    place: str


# ---------- LLM ----------
async def generate_ai_reading(chart: dict, details: BirthDetails, gem: dict) -> dict:
    fallback = {
        "summary": f"As a {chart['moon_sign']['sa']} ({chart['moon_sign']['en']}) native ruled by {chart['ruling_planet']}, your path is shaped by {chart['moon_sign']['element'].lower()} energy. Your Nakshatra {chart['nakshatra']} lends you a distinctive inner rhythm.",
        "career": "Steady effort and disciplined focus bring recognition this cycle. Trust your instincts on new opportunities.",
        "love": "Warmth and honest communication strengthen your bonds. An emotional breakthrough is near.",
        "health": "Balance rest with activity. Your energy peaks when you honour a calm routine.",
        "wealth": "Financial stability improves through patience. Avoid impulsive spending under planetary tension.",
        "spiritual": f"Chanting {gem.get('mantra','your ruling mantra')} strengthens your ruling planet and calms the mind.",
        "lucky_color": chart['moon_sign'].get('element') and {"Fire": "Saffron", "Earth": "Green", "Air": "Sky Blue", "Water": "Pearl White"}.get(chart['moon_sign']['element'], "Gold"),
        "lucky_number": (sum(int(x) for x in details.dob.replace('-', '')) % 9) + 1,
        "gemstone_reason": f"{gem['name']} ({gem['name_sa']}) empowers {chart['ruling_planet']}, the lord of your rashi, helping with the concerns you described.",
    }
    if not EMERGENT_LLM_KEY:
        return fallback
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        system = ("You are an expert Vedic astrologer for Rashify. Respond ONLY with a compact JSON object, "
                  "no markdown, no prose outside JSON. Keys: summary, career, love, health, wealth, spiritual, "
                  "lucky_color, lucky_number (integer), gemstone_reason. Each text value 1-2 warm, specific sentences."
                  + lang_instruction(details.language))
        prompt = (f"Birth chart -> Moon Rashi: {chart['moon_sign']['sa']} ({chart['moon_sign']['en']}), "
                  f"Sun sign: {chart['sun_sign']['sa']}, Ascendant: {chart['ascendant']['sa']}, "
                  f"Nakshatra: {chart['nakshatra']} pada {chart['pada']}, Ruling planet: {chart['ruling_planet']}. "
                  f"Recommended gemstone: {gem['name']} ({gem['name_sa']}). "
                  f"Person: {details.name}, born {details.dob} {details.time} at {details.place}. "
                  f"Current problem/situation they want help with: '{details.problem or 'general life guidance'}'. "
                  f"Give a personalised horoscope reading and explain in gemstone_reason how the gemstone helps with their situation.")
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"reading-{secrets.token_hex(6)}",
                       system_message=system).with_model("anthropic", "claude-sonnet-4-6")
        resp = await chat.send_message(UserMessage(text=prompt))
        import json, re
        text = resp if isinstance(resp, str) else str(resp)
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            data = json.loads(match.group(0))
            for k, v in fallback.items():
                data.setdefault(k, v)
            return data
        return fallback
    except Exception as e:
        logger.warning(f"AI reading failed, using fallback: {e}")
        return fallback


# ---------- Auth routes ----------
@api_router.post("/auth/register")
async def register(inp: RegisterInput):
    email = inp.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    doc = {"email": email, "name": inp.name, "password_hash": hash_password(inp.password),
           "role": "user", "created_at": datetime.now(timezone.utc).isoformat()}
    res = await db.users.insert_one(doc)
    doc["_id"] = res.inserted_id
    token = create_access_token(str(res.inserted_id), email, "user")
    return {"access_token": token, "user": serialize_user(doc)}


@api_router.post("/auth/login")
async def login(inp: LoginInput):
    ident = inp.email.lower().strip()
    user = await db.users.find_one({"$or": [{"email": ident}, {"username": ident}]})
    if not user or not verify_password(inp.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(str(user["_id"]), user["email"], user.get("role", "user"))
    return {"access_token": token, "user": serialize_user(user)}


@api_router.get("/auth/me")
async def me(user: dict = Depends(get_current_user)):
    return serialize_user(user)


# ---------- Reference data ----------
@api_router.get("/rashis")
async def list_rashis():
    return RASHIS


@api_router.get("/gemstones")
async def list_gemstones():
    return [{"planet": k, **v} for k, v in GEMSTONES.items()]


# ---------- Core calculation ----------
@api_router.post("/rashi/calculate")
async def calculate(inp: BirthDetails, request: Request,
                    creds: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    try:
        dt = datetime.strptime(f"{inp.dob} {inp.time}", "%Y-%m-%d %H:%M")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format. Use YYYY-MM-DD and HH:MM (24h).")

    loc = geocode(inp.place)
    chart = compute_chart(dt, loc["lat"], loc["lon"], loc["tz"])
    chart["birth_location"] = loc
    gem = recommend_gemstone(chart, inp.problem or "")
    reading = await generate_ai_reading(chart, inp, gem)

    result = {
        "input": inp.model_dump(),
        "chart": chart,
        "gemstone": gem,
        "reading": reading,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Log for admin analytics
    await db.calc_logs.insert_one({
        "name": inp.name, "place": inp.place, "moon_sign": chart["moon_sign"]["sa"],
        "gemstone": gem["name"], "created_at": datetime.now(timezone.utc).isoformat(),
    })

    # Save to user history if authenticated
    user = None
    token = creds.credentials if creds else request.cookies.get("access_token")
    if token:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        except Exception:
            user = None
    if user:
        saved = {**result, "user_id": str(user["_id"])}
        ins = await db.readings.insert_one(saved)
        result["id"] = str(ins.inserted_id)
        result["saved"] = True
    return result


@api_router.get("/readings")
async def my_readings(user: dict = Depends(get_current_user)):
    docs = await db.readings.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(200)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@api_router.delete("/readings/{reading_id}")
async def delete_reading(reading_id: str, user: dict = Depends(get_current_user)):
    res = await db.readings.delete_one({"_id": ObjectId(reading_id), "user_id": str(user["_id"])})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Reading not found")
    return {"ok": True}


# ---------- Family profiles ----------
@api_router.get("/profiles")
async def list_profiles(user: dict = Depends(get_current_user)):
    docs = await db.profiles.find({"user_id": str(user["_id"])}).sort("created_at", -1).to_list(100)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@api_router.post("/profiles")
async def create_profile(inp: ProfileInput, user: dict = Depends(get_current_user)):
    doc = {**inp.model_dump(), "user_id": str(user["_id"]),
           "created_at": datetime.now(timezone.utc).isoformat()}
    res = await db.profiles.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return doc


@api_router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: str, user: dict = Depends(get_current_user)):
    res = await db.profiles.delete_one({"_id": ObjectId(profile_id), "user_id": str(user["_id"])})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"ok": True}


# ---------- Daily / Weekly / Yearly horoscope ----------
async def generate_horoscope(rashi: dict, period: str, date_key: str, language: str = "en") -> dict:
    fallback = {
        "overview": f"The cosmos turns in favour of {rashi['sa']} ({rashi['en']}) this {period}. Your ruling planet {rashi['planet']} lends steady momentum - trust your rhythm and act with intention.",
        "career": "Focus and consistency open a door you have been waiting on. A senior figure notices your effort.",
        "love": "Warmth flows in close relationships; express what you feel rather than assuming it is understood.",
        "health": "Energy is good when you protect your rest. Hydration and a short daily walk keep you balanced.",
        "finance": "Money matters stabilise. Avoid one impulsive purchase and a small saving grows meaningfully.",
        "lucky_color": {"Fire": "Saffron", "Earth": "Emerald Green", "Air": "Sky Blue", "Water": "Pearl White"}.get(rashi["element"], "Gold"),
        "lucky_number": (sum(ord(c) for c in date_key + rashi["key"]) % 9) + 1,
    }
    if not EMERGENT_LLM_KEY:
        return fallback
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        system = ("You are a warm, precise Vedic astrologer. Respond ONLY with a JSON object, no markdown. "
                  "Keys: overview, career, love, health, finance, lucky_color, lucky_number (integer). "
                  "Each text value 1-2 specific, encouraging sentences." + lang_instruction(language))
        prompt = (f"Write the {period} horoscope for rashi {rashi['sa']} ({rashi['en']}), ruling planet "
                  f"{rashi['planet']}, element {rashi['element']}, for the period identified as {date_key}. "
                  f"Make it feel fresh and specific to this {period}.")
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"horo-{rashi['key']}-{period}-{date_key}",
                       system_message=system).with_model("anthropic", "claude-sonnet-4-6")
        resp = await chat.send_message(UserMessage(text=prompt))
        import json, re
        text = resp if isinstance(resp, str) else str(resp)
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            for k, v in fallback.items():
                data.setdefault(k, v)
            return data
        return fallback
    except Exception as e:
        logger.warning(f"Horoscope AI failed, using fallback: {e}")
        return fallback


@api_router.get("/horoscope/{rashi_key}")
async def horoscope(rashi_key: str, period: str = "daily", language: str = "en"):
    rashi = next((r for r in RASHIS if r["key"] == rashi_key), None)
    if not rashi:
        raise HTTPException(status_code=404, detail="Unknown rashi")
    if period not in ("daily", "weekly", "yearly"):
        period = "daily"
    language = (language or "en").lower()
    now = datetime.now(timezone.utc)
    if period == "daily":
        date_key = now.strftime("%Y-%m-%d")
    elif period == "weekly":
        date_key = now.strftime("%Y-W%U")
    else:
        date_key = now.strftime("%Y")

    cached = await db.horoscopes.find_one({"rashi": rashi_key, "period": period, "date_key": date_key, "language": language})
    if cached:
        return {"rashi": rashi, "period": period, "date_key": date_key, "forecast": cached["forecast"]}

    forecast = await generate_horoscope(rashi, period, date_key, language)
    await db.horoscopes.insert_one({"rashi": rashi_key, "period": period, "date_key": date_key, "language": language,
                                    "forecast": forecast, "created_at": now.isoformat()})
    return {"rashi": rashi, "period": period, "date_key": date_key, "forecast": forecast}


# ---------- City autocomplete ----------
@api_router.get("/cities")
async def cities(q: str = ""):
    return {"results": search_cities(q)}


# ---------- Kundali Matching (Guna Milan) ----------
class PersonInput(BaseModel):
    name: Optional[str] = ""
    dob: str
    time: str
    place: str


class MatchInput(BaseModel):
    boy: PersonInput
    girl: PersonInput


def _moon_details(p: PersonInput):
    dt = datetime.strptime(f"{p.dob} {p.time}", "%Y-%m-%d %H:%M")
    loc = geocode(p.place)
    c = compute_chart(dt, loc["lat"], loc["lon"], loc["tz"])
    return c["nakshatra_index"], c["moon_rashi_index"], c


@api_router.post("/match")
async def match(inp: MatchInput):
    try:
        nb, rb, cb = _moon_details(inp.boy)
        ng, rg, cg = _moon_details(inp.girl)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date or time format (use YYYY-MM-DD and HH:MM).")
    result = compute_guna_milan(nb, rb, ng, rg)
    result["boy"] = {"name": inp.boy.name, "rashi": cb["moon_sign"]["sa"], "nakshatra": cb["nakshatra"]}
    result["girl"] = {"name": inp.girl.name, "rashi": cg["moon_sign"]["sa"], "nakshatra": cg["nakshatra"]}
    await db.calc_logs.insert_one({"name": f"Match: {inp.boy.name or 'Boy'} & {inp.girl.name or 'Girl'}",
                                   "place": "-", "moon_sign": f"{cb['moon_sign']['sa']}/{cg['moon_sign']['sa']}",
                                   "gemstone": f"Guna {result['total']}/36",
                                   "created_at": datetime.now(timezone.utc).isoformat()})
    return result


# ---------- AI Dasha insights ----------
class DashaInsightInput(BaseModel):
    rashi: str
    mahadasha: str
    antardasha: Optional[str] = ""
    language: Optional[str] = "en"


@api_router.post("/dasha/insights")
async def dasha_insights(inp: DashaInsightInput):
    fallback = {
        "overview": f"You are in the {inp.mahadasha} Mahadasha" + (f" with {inp.antardasha} Antardasha" if inp.antardasha else "") + f". This period shapes the themes of your {inp.rashi} moon with the qualities of {inp.mahadasha}.",
        "career": f"{inp.mahadasha}'s influence favours steady, disciplined progress. Align effort with long-term goals for recognition.",
        "love": "Relationships deepen through patience and honest communication during this period.",
        "money": "Finances stabilise with mindful planning; avoid speculative risks while this period runs.",
    }
    if not EMERGENT_LLM_KEY:
        return fallback
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        system = ("You are a Vedic astrologer explaining Vimshottari Dasha. Respond ONLY with JSON, no markdown. "
                  "Keys: overview, career, love, money. Each 2-3 practical, encouraging sentences."
                  + lang_instruction(inp.language))
        prompt = (f"Explain the current period for a {inp.rashi} moon-sign native running {inp.mahadasha} Mahadasha"
                  + (f" and {inp.antardasha} Antardasha" if inp.antardasha else "")
                  + ". Cover what it means for career, love and money right now.")
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"dasha-{secrets.token_hex(5)}",
                       system_message=system).with_model("anthropic", "claude-sonnet-4-6")
        resp = await chat.send_message(UserMessage(text=prompt))
        import json, re
        m = re.search(r"\{.*\}", resp if isinstance(resp, str) else str(resp), re.DOTALL)
        if m:
            data = json.loads(m.group(0))
            for k, v in fallback.items():
                data.setdefault(k, v)
            return data
        return fallback
    except Exception as e:
        logger.warning(f"Dasha insights failed: {e}")
        return fallback


# ---------- Site settings (admin-editable) ----------
DEFAULT_SETTINGS = {
    "brand_name": "Rashify",
    "hero_title_gold": "Discover Your Cosmic",
    "hero_title_plain": "Alignment & True Rashi",
    "hero_subtitle": "Enter your birth date, exact time and place. Rashify reveals your real Vedic Rashi, a personalised horoscope, and the precise gemstone that can turn your situation around.",
    "pdf_price_inr": PDF_PRICE_INR,
}


@api_router.get("/settings")
async def get_settings():
    doc = await db.settings.find_one({"_id": "site"})
    if not doc:
        return DEFAULT_SETTINGS
    doc.pop("_id", None)
    return {**DEFAULT_SETTINGS, **doc}


@api_router.put("/admin/settings")
async def update_settings(payload: dict, admin: dict = Depends(get_admin_user)):
    allowed = {"brand_name", "hero_title_gold", "hero_title_plain", "hero_subtitle", "pdf_price_inr"}
    clean = {k: v for k, v in payload.items() if k in allowed}
    if "pdf_price_inr" in clean:
        try:
            clean["pdf_price_inr"] = float(clean["pdf_price_inr"])
        except (TypeError, ValueError):
            clean.pop("pdf_price_inr")
    await db.settings.update_one({"_id": "site"}, {"$set": clean}, upsert=True)
    doc = await db.settings.find_one({"_id": "site"})
    doc.pop("_id", None)
    return {**DEFAULT_SETTINGS, **doc}


# ---------- Discount codes + Paid PDF ----------
class DiscountInput(BaseModel):
    code: str
    percent: int  # 0-100


class DiscountCodeIn(BaseModel):
    code: str


class PdfCheckoutInput(BaseModel):
    reading_id: str
    origin_url: str
    discount_code: Optional[str] = ""


async def _find_active_discount(code: str):
    if not code:
        return None
    doc = await db.discount_codes.find_one({"code": code.strip().upper(), "active": True})
    return doc


@api_router.post("/pdf/validate-discount")
async def validate_discount(inp: DiscountCodeIn):
    doc = await _find_active_discount(inp.code)
    if not doc:
        return {"valid": False, "percent": 0}
    return {"valid": True, "code": doc["code"], "percent": doc["percent"]}


@api_router.post("/pdf/checkout")
async def pdf_checkout(inp: PdfCheckoutInput, request: Request, user: dict = Depends(get_current_user)):
    reading = await db.readings.find_one({"_id": ObjectId(inp.reading_id), "user_id": str(user["_id"])})
    if not reading:
        raise HTTPException(status_code=404, detail="Reading not found")
    reading["_id"] = str(reading["_id"])

    percent = 0
    disc = await _find_active_discount(inp.discount_code)
    if disc:
        percent = disc["percent"]
    settings_doc = await db.settings.find_one({"_id": "site"}) or {}
    base_price = float(settings_doc.get("pdf_price_inr", PDF_PRICE_INR))
    amount = round(base_price * (1 - percent / 100.0), 2)

    # Free (100% off) -> unlock without Stripe
    if amount <= 0:
        session_id = f"free_{secrets.token_hex(10)}"
        await db.payment_transactions.insert_one({
            "session_id": session_id, "user_id": str(user["_id"]), "reading_id": inp.reading_id,
            "reading_snapshot": reading, "amount": 0.0, "currency": "inr",
            "discount_code": (disc or {}).get("code"), "discount_percent": percent,
            "status": "completed", "payment_status": "paid",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        return {"free": True, "session_id": session_id, "amount": 0.0, "discount_percent": percent}

    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=webhook_url)
    success_url = f"{inp.origin_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{inp.origin_url}/payment/cancel"
    req = CheckoutSessionRequest(
        amount=amount, currency="inr", success_url=success_url, cancel_url=cancel_url,
        metadata={"user_id": str(user["_id"]), "reading_id": inp.reading_id, "product": "kundali_pdf"},
    )
    session = await stripe_checkout.create_checkout_session(req)
    await db.payment_transactions.insert_one({
        "session_id": session.session_id, "user_id": str(user["_id"]), "reading_id": inp.reading_id,
        "reading_snapshot": reading, "amount": amount, "currency": "inr",
        "discount_code": (disc or {}).get("code"), "discount_percent": percent,
        "status": "initiated", "payment_status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    return {"free": False, "checkout_url": session.url, "session_id": session.session_id,
            "amount": amount, "discount_percent": percent}


@api_router.get("/payments/status/{session_id}")
async def payment_status(session_id: str, request: Request):
    record = await db.payment_transactions.find_one({"session_id": session_id})
    if not record:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if record.get("payment_status") != "paid" and not session_id.startswith("free_"):
        try:
            host_url = str(request.base_url)
            stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}api/webhook/stripe")
            status = await stripe_checkout.get_checkout_status(session_id)
            if status.payment_status == "paid" or status.status == "complete":
                await db.payment_transactions.update_one(
                    {"session_id": session_id, "payment_status": {"$ne": "paid"}},
                    {"$set": {"status": "completed", "payment_status": "paid",
                              "updated_at": datetime.now(timezone.utc).isoformat()}})
                record = await db.payment_transactions.find_one({"session_id": session_id})
        except Exception as e:
            logger.warning(f"Stripe status check failed: {e}")
    return {"session_id": record["session_id"], "status": record["status"],
            "payment_status": record["payment_status"]}


@api_router.get("/pdf/download/{session_id}")
async def pdf_download(session_id: str):
    record = await db.payment_transactions.find_one({"session_id": session_id})
    if not record:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if record.get("payment_status") != "paid":
        raise HTTPException(status_code=402, detail="Payment not completed")
    reading = record.get("reading_snapshot")
    if not reading:
        reading = await db.readings.find_one({"_id": ObjectId(record["reading_id"])})
    pdf_bytes = generate_kundali_pdf(reading)
    name = (reading.get("input", {}).get("name") or "kundali").replace(" ", "_")
    return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf",
                             headers={"Content-Disposition": f'attachment; filename="Rashisense_{name}.pdf"'})


@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    sig = request.headers.get("Stripe-Signature", "")
    try:
        host_url = str(request.base_url)
        stripe_checkout = StripeCheckout(api_key=STRIPE_API_KEY, webhook_url=f"{host_url}api/webhook/stripe")
        resp = await stripe_checkout.handle_webhook(body, sig)
        if resp.session_id and resp.payment_status == "paid":
            await db.payment_transactions.update_one(
                {"session_id": resp.session_id, "payment_status": {"$ne": "paid"}},
                {"$set": {"status": "completed", "payment_status": "paid",
                          "updated_at": datetime.now(timezone.utc).isoformat()}})
    except Exception as e:
        logger.warning(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook error")
    return {"status": "ok"}


# ---------- Admin ----------
@api_router.get("/admin/stats")
async def admin_stats(admin: dict = Depends(get_admin_user)):
    total_users = await db.users.count_documents({"role": "user"})
    total_readings = await db.readings.count_documents({})
    total_calcs = await db.calc_logs.count_documents({})
    return {"total_users": total_users, "total_readings": total_readings, "total_calculations": total_calcs}


@api_router.get("/admin/users")
async def admin_users(admin: dict = Depends(get_admin_user)):
    docs = await db.users.find({}).sort("created_at", -1).to_list(500)
    return [serialize_user(d) for d in docs]


@api_router.get("/admin/logs")
async def admin_logs(admin: dict = Depends(get_admin_user)):
    docs = await db.calc_logs.find({}).sort("created_at", -1).to_list(200)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@api_router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, admin: dict = Depends(get_admin_user)):
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if target and target.get("role") == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete an admin account")
    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.readings.delete_many({"user_id": user_id})
    return {"ok": True}


@api_router.get("/admin/discounts")
async def admin_list_discounts(admin: dict = Depends(get_admin_user)):
    docs = await db.discount_codes.find({}).sort("created_at", -1).to_list(200)
    for d in docs:
        d["id"] = str(d.pop("_id"))
    return docs


@api_router.post("/admin/discounts")
async def admin_create_discount(inp: DiscountInput, admin: dict = Depends(get_admin_user)):
    code = inp.code.strip().upper()
    if not code:
        raise HTTPException(status_code=400, detail="Code required")
    percent = max(0, min(100, inp.percent))
    if await db.discount_codes.find_one({"code": code}):
        raise HTTPException(status_code=400, detail="Code already exists")
    doc = {"code": code, "percent": percent, "active": True,
           "created_at": datetime.now(timezone.utc).isoformat()}
    res = await db.discount_codes.insert_one(doc)
    doc["id"] = str(res.inserted_id)
    doc.pop("_id", None)
    return doc


@api_router.patch("/admin/discounts/{discount_id}")
async def admin_toggle_discount(discount_id: str, admin: dict = Depends(get_admin_user)):
    doc = await db.discount_codes.find_one({"_id": ObjectId(discount_id)})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    new_active = not doc.get("active", True)
    await db.discount_codes.update_one({"_id": ObjectId(discount_id)}, {"$set": {"active": new_active}})
    return {"id": discount_id, "active": new_active}


@api_router.delete("/admin/discounts/{discount_id}")
async def admin_delete_discount(discount_id: str, admin: dict = Depends(get_admin_user)):
    await db.discount_codes.delete_one({"_id": ObjectId(discount_id)})
    return {"ok": True}


@api_router.get("/")
async def root():
    return {"message": "Rashisense API", "status": "ok"}


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await db.users.create_index("email", unique=True)
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@rashisense.com").lower()
    admin_username = os.environ.get("ADMIN_USERNAME", "admin").lower()
    admin_password = os.environ.get("ADMIN_PASSWORD", "Rashi@2026")
    existing = await db.users.find_one({"email": admin_email})
    if not existing:
        await db.users.insert_one({
            "email": admin_email, "username": admin_username, "name": "Administrator",
            "password_hash": hash_password(admin_password), "role": "admin",
            "created_at": datetime.now(timezone.utc).isoformat(),
        })
        logger.info("Admin account seeded")
    else:
        upd = {"username": admin_username, "role": "admin"}
        if not verify_password(admin_password, existing["password_hash"]):
            upd["password_hash"] = hash_password(admin_password)
        await db.users.update_one({"_id": existing["_id"]}, {"$set": upd})


@app.on_event("shutdown")
async def shutdown():
    client.close()

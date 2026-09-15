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
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr

from astro import compute_chart, recommend_gemstone, RASHIS, GEMSTONES, NAKSHATRAS
from geo import geocode

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("rashisense")

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

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
        system = ("You are an expert Vedic astrologer for Rashisense. Respond ONLY with a compact JSON object, "
                  "no markdown, no prose outside JSON. Keys: summary, career, love, health, wealth, spiritual, "
                  "lucky_color, lucky_number (integer), gemstone_reason. Each text value 1-2 warm, specific sentences.")
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
async def generate_horoscope(rashi: dict, period: str, date_key: str) -> dict:
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
                  "Each text value 1-2 specific, encouraging sentences.")
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
async def horoscope(rashi_key: str, period: str = "daily"):
    rashi = next((r for r in RASHIS if r["key"] == rashi_key), None)
    if not rashi:
        raise HTTPException(status_code=404, detail="Unknown rashi")
    if period not in ("daily", "weekly", "yearly"):
        period = "daily"
    now = datetime.now(timezone.utc)
    if period == "daily":
        date_key = now.strftime("%Y-%m-%d")
    elif period == "weekly":
        date_key = now.strftime("%Y-W%U")
    else:
        date_key = now.strftime("%Y")

    cached = await db.horoscopes.find_one({"rashi": rashi_key, "period": period, "date_key": date_key})
    if cached:
        return {"rashi": rashi, "period": period, "date_key": date_key, "forecast": cached["forecast"]}

    forecast = await generate_horoscope(rashi, period, date_key)
    await db.horoscopes.insert_one({"rashi": rashi_key, "period": period, "date_key": date_key,
                                    "forecast": forecast, "created_at": now.isoformat()})
    return {"rashi": rashi, "period": period, "date_key": date_key, "forecast": forecast}


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

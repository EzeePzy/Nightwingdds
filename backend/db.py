"""SQLite persistence layer for Rashify.

Replaces the original MongoDB dependency with a single local SQLite file so the
app can run on a single free Render service without external services.
"""
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = os.environ.get(
    "SQLITE_PATH",
    str(Path(__file__).parent / "data" / "rashify.db"),
)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return uuid.uuid4().hex


def _connect() -> sqlite3.Connection:
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL DEFAULT '',
    username TEXT,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username
    ON users(username) WHERE username IS NOT NULL;

CREATE TABLE IF NOT EXISTS readings (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_readings_user ON readings(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    relation TEXT NOT NULL DEFAULT 'Self',
    gender TEXT NOT NULL DEFAULT 'Not specified',
    dob TEXT NOT NULL,
    time TEXT NOT NULL,
    place TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_profiles_user ON profiles(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS horoscopes (
    id TEXT PRIMARY KEY,
    rashi TEXT NOT NULL,
    period TEXT NOT NULL,
    date_key TEXT NOT NULL,
    language TEXT NOT NULL,
    forecast TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(rashi, period, date_key, language)
);

CREATE TABLE IF NOT EXISTS calc_logs (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    place TEXT NOT NULL,
    moon_sign TEXT NOT NULL,
    gemstone TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_calc_logs_created ON calc_logs(created_at DESC);

CREATE TABLE IF NOT EXISTS settings (
    id TEXT PRIMARY KEY,
    data TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS discount_codes (
    id TEXT PRIMARY KEY,
    code TEXT NOT NULL UNIQUE,
    percent INTEGER NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS payment_transactions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    reading_id TEXT NOT NULL,
    reading_snapshot TEXT,
    amount REAL NOT NULL DEFAULT 0,
    currency TEXT NOT NULL DEFAULT 'inr',
    discount_code TEXT,
    discount_percent INTEGER NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    payment_status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_payments_user ON payment_transactions(user_id, created_at DESC);
"""


def init_db() -> None:
    conn = _connect()
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


# ---------- Users ----------
def _user_row(row: sqlite3.Row) -> dict:
    return dict(row)


def create_user(email: str, name: str, password_hash: str, role: str = "user",
                username: str | None = None) -> dict:
    doc = {
        "id": new_id(),
        "email": email,
        "name": name,
        "username": username,
        "password_hash": password_hash,
        "role": role,
        "created_at": now_iso(),
    }
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO users (id, email, name, username, password_hash, role, created_at) "
            "VALUES (:id, :email, :name, :username, :password_hash, :role, :created_at)",
            doc,
        )
        conn.commit()
    finally:
        conn.close()
    return doc


def get_user_by_email(email: str) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return _user_row(row) if row else None
    finally:
        conn.close()


def get_user_by_identifier(ident: str) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? OR username = ? LIMIT 1",
            (ident, ident),
        ).fetchone()
        return _user_row(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: str) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return _user_row(row) if row else None
    finally:
        conn.close()


def update_user(user_id: str, **fields) -> None:
    if not fields:
        return
    keys = ", ".join(f"{k} = :{k}" for k in fields)
    fields["id"] = user_id
    conn = _connect()
    try:
        conn.execute(f"UPDATE users SET {keys} WHERE id = :id", fields)
        conn.commit()
    finally:
        conn.close()


def list_users() -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC LIMIT 500").fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def count_users(role: str | None = None) -> int:
    conn = _connect()
    try:
        if role:
            row = conn.execute("SELECT COUNT(*) AS n FROM users WHERE role = ?", (role,)).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
        return int(row["n"])
    finally:
        conn.close()


def delete_user(user_id: str) -> None:
    conn = _connect()
    try:
        conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.execute("DELETE FROM readings WHERE user_id = ?", (user_id,))
        conn.execute("DELETE FROM profiles WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()


# ---------- Readings ----------
def create_reading(user_id: str, data: dict) -> str:
    reading_id = new_id()
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO readings (id, user_id, data, created_at) VALUES (?, ?, ?, ?)",
            (reading_id, user_id, json.dumps(data, default=str), now_iso()),
        )
        conn.commit()
    finally:
        conn.close()
    return reading_id


def list_readings(user_id: str, limit: int = 200) -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, data FROM readings WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        out = []
        for row in rows:
            data = json.loads(row["data"])
            data["id"] = row["id"]
            out.append(data)
        return out
    finally:
        conn.close()


def get_reading(reading_id: str, user_id: str | None = None) -> dict | None:
    conn = _connect()
    try:
        if user_id is None:
            row = conn.execute("SELECT id, data FROM readings WHERE id = ?", (reading_id,)).fetchone()
        else:
            row = conn.execute(
                "SELECT id, data FROM readings WHERE id = ? AND user_id = ?",
                (reading_id, user_id),
            ).fetchone()
        if not row:
            return None
        data = json.loads(row["data"])
        data["id"] = row["id"]
        return data
    finally:
        conn.close()


def delete_reading(reading_id: str, user_id: str) -> bool:
    conn = _connect()
    try:
        cur = conn.execute(
            "DELETE FROM readings WHERE id = ? AND user_id = ?",
            (reading_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def count_readings() -> int:
    conn = _connect()
    try:
        return int(conn.execute("SELECT COUNT(*) AS n FROM readings").fetchone()["n"])
    finally:
        conn.close()


# ---------- Profiles ----------
def create_profile(user_id: str, data: dict) -> dict:
    doc = {
        "id": new_id(),
        "user_id": user_id,
        "name": data.get("name", ""),
        "relation": data.get("relation") or "Self",
        "gender": data.get("gender") or "Not specified",
        "dob": data["dob"],
        "time": data["time"],
        "place": data["place"],
        "created_at": now_iso(),
    }
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO profiles (id, user_id, name, relation, gender, dob, time, place, created_at) "
            "VALUES (:id, :user_id, :name, :relation, :gender, :dob, :time, :place, :created_at)",
            doc,
        )
        conn.commit()
    finally:
        conn.close()
    return doc


def list_profiles(user_id: str, limit: int = 100) -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, name, relation, gender, dob, time, place, created_at "
            "FROM profiles WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def delete_profile(profile_id: str, user_id: str) -> bool:
    conn = _connect()
    try:
        cur = conn.execute(
            "DELETE FROM profiles WHERE id = ? AND user_id = ?",
            (profile_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# ---------- Horoscopes ----------
def get_horoscope(rashi: str, period: str, date_key: str, language: str) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT forecast FROM horoscopes WHERE rashi = ? AND period = ? AND date_key = ? AND language = ?",
            (rashi, period, date_key, language),
        ).fetchone()
        return json.loads(row["forecast"]) if row else None
    finally:
        conn.close()


def save_horoscope(rashi: str, period: str, date_key: str, language: str, forecast: dict) -> None:
    conn = _connect()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO horoscopes "
            "(id, rashi, period, date_key, language, forecast, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (new_id(), rashi, period, date_key, language, json.dumps(forecast), now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


# ---------- Calculation logs ----------
def add_calc_log(name: str, place: str, moon_sign: str, gemstone: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO calc_logs (id, name, place, moon_sign, gemstone, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (new_id(), name, place, moon_sign, gemstone, now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


def list_calc_logs(limit: int = 200) -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT id, name, place, moon_sign, gemstone, created_at "
            "FROM calc_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def count_calc_logs() -> int:
    conn = _connect()
    try:
        return int(conn.execute("SELECT COUNT(*) AS n FROM calc_logs").fetchone()["n"])
    finally:
        conn.close()


# ---------- Settings ----------
def get_settings() -> dict | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT data FROM settings WHERE id = 'site'").fetchone()
        return json.loads(row["data"]) if row else None
    finally:
        conn.close()


def save_settings(settings: dict) -> None:
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO settings (id, data, updated_at) VALUES ('site', ?, ?) "
            "ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at",
            (json.dumps(settings), now_iso()),
        )
        conn.commit()
    finally:
        conn.close()


# ---------- Discounts ----------
def _discount_row(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "code": row["code"],
        "percent": row["percent"],
        "active": bool(row["active"]),
        "created_at": row["created_at"],
    }


def get_active_discount(code: str) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM discount_codes WHERE code = ? AND active = 1",
            (code.strip().upper(),),
        ).fetchone()
        return _discount_row(row) if row else None
    finally:
        conn.close()


def get_discount_by_code(code: str) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM discount_codes WHERE code = ?", (code,)).fetchone()
        return _discount_row(row) if row else None
    finally:
        conn.close()


def get_discount_by_id(discount_id: str) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute("SELECT * FROM discount_codes WHERE id = ?", (discount_id,)).fetchone()
        return _discount_row(row) if row else None
    finally:
        conn.close()


def list_discounts() -> list[dict]:
    conn = _connect()
    try:
        rows = conn.execute("SELECT * FROM discount_codes ORDER BY created_at DESC LIMIT 200").fetchall()
        return [_discount_row(r) for r in rows]
    finally:
        conn.close()


def create_discount(code: str, percent: int) -> dict:
    doc = {
        "id": new_id(),
        "code": code,
        "percent": percent,
        "active": True,
        "created_at": now_iso(),
    }
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO discount_codes (id, code, percent, active, created_at) "
            "VALUES (:id, :code, :percent, 1, :created_at)",
            doc,
        )
        conn.commit()
    finally:
        conn.close()
    return doc


def toggle_discount(discount_id: str) -> bool | None:
    doc = get_discount_by_id(discount_id)
    if not doc:
        return None
    new_active = not doc["active"]
    conn = _connect()
    try:
        conn.execute(
            "UPDATE discount_codes SET active = ? WHERE id = ?",
            (1 if new_active else 0, discount_id),
        )
        conn.commit()
    finally:
        conn.close()
    return new_active


def delete_discount(discount_id: str) -> None:
    conn = _connect()
    try:
        conn.execute("DELETE FROM discount_codes WHERE id = ?", (discount_id,))
        conn.commit()
    finally:
        conn.close()


# ---------- Payment transactions ----------
def create_transaction(doc: dict) -> None:
    payload = {
        "session_id": doc["session_id"],
        "user_id": doc["user_id"],
        "reading_id": doc["reading_id"],
        "reading_snapshot": json.dumps(doc.get("reading_snapshot") or {}, default=str),
        "amount": float(doc.get("amount", 0)),
        "currency": doc.get("currency", "inr"),
        "discount_code": doc.get("discount_code"),
        "discount_percent": int(doc.get("discount_percent", 0)),
        "status": doc.get("status", "completed"),
        "payment_status": doc.get("payment_status", "paid"),
        "created_at": doc.get("created_at") or now_iso(),
        "updated_at": doc.get("updated_at"),
    }
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO payment_transactions "
            "(session_id, user_id, reading_id, reading_snapshot, amount, currency, "
            " discount_code, discount_percent, status, payment_status, created_at, updated_at) "
            "VALUES (:session_id, :user_id, :reading_id, :reading_snapshot, :amount, :currency, "
            " :discount_code, :discount_percent, :status, :payment_status, :created_at, :updated_at)",
            payload,
        )
        conn.commit()
    finally:
        conn.close()


def get_transaction(session_id: str) -> dict | None:
    conn = _connect()
    try:
        row = conn.execute(
            "SELECT * FROM payment_transactions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if not row:
            return None
        doc = dict(row)
        doc["reading_snapshot"] = json.loads(doc["reading_snapshot"]) if doc["reading_snapshot"] else None
        return doc
    finally:
        conn.close()


def mark_transaction_paid(session_id: str) -> None:
    conn = _connect()
    try:
        conn.execute(
            "UPDATE payment_transactions SET status = 'completed', payment_status = 'paid', "
            "updated_at = ? WHERE session_id = ?",
            (now_iso(), session_id),
        )
        conn.commit()
    finally:
        conn.close()

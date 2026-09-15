# Rashisense — PRD

## Original Problem Statement
Astrology website "Rashisense" where users know their horoscope and true Vedic Rashi from date of birth, place and time (24h), and get the gemstone (stone) that helps their situation. User wanted: both calculation + AI, login with accounts, gemstone based on rashi + described problem, an admin panel with username/password, mystical dark + Indian traditional theme.

## Architecture
- Frontend: React (CRA + craco), Tailwind, framer-motion, sonner, lucide-react. JWT stored in localStorage, sent as Bearer header.
- Backend: FastAPI (/api prefix). astro.py = deterministic Vedic chart + gemstone engine. server.py = auth (bcrypt + PyJWT), calculate, readings, admin.
- AI: Claude Sonnet 4.6 via emergentintegrations (EMERGENT_LLM_KEY) for personalized reading, with deterministic fallback.
- DB: MongoDB (users, readings, calc_logs).

## User Personas
- Seeker: enters birth details, gets rashi + horoscope + gemstone remedy.
- Registered user: saves readings, views history in dashboard.
- Admin: manages users, views calculation logs + gemstone catalog.

## Core Requirements (static)
- Rashi calculation from DOB + 24h time + place.
- AI + rule-based horoscope across life pillars.
- Gemstone recommendation tied to ruling planet + user's problem.
- Auth with user + admin roles; admin login by username/password.

## Implemented (2026-06)
- Landing (hero, rashi ticker, features, CTA), Auth (login/signup, username-aware), Calculator (form + full result view), Gemstones catalog, Dashboard (history view/delete), Admin (stats, users, logs, gemstone catalog).
- Backend: /api/auth/register|login|me, /api/rashi/calculate, /api/readings CRUD, /api/admin/stats|users|logs, /api/gemstones, /api/rashis.
- Admin seeded: admin / Rashi@2026. Tested 20/20 backend + all frontend flows pass.

## Implemented (later 2026)
- Precise charts: Swiss Ephemeris (pyswisseph) + Lahiri ayanamsa + offline geocoding (geonamescache) with IANA timezone -> UTC. Verified to match a professional Rainbow Gems chart exactly (all 9 planets, Moon rashi Scorpio 22.81°, nakshatra Jyeshtha).
- Western (tropical) Sun sign added alongside Vedic Moon Rashi to resolve the "my sign is Scorpio" confusion; result view explains Rashi = Moon sign.
- Daily/Weekly/Yearly AI horoscope (Claude) cached per rashi+period+date. Family Profiles CRUD (save/switch birth details).
- Vimshottari Dasha timeline computed from Moon nakshatra (matches professional chart's Mercury balance 9.16y); planetary degrees shown in Kundali.

## Backlog (P1/P2)
- P1: Email the PDF after purchase (NOT yet built — needs an email provider key e.g. Resend/SendGrid).
- P2: Navamsa full nested divisional set (D3/D10), one-time-use signed PDF download tokens.
- P2: Gemstone catalog editing from admin (currently read-only), password reset flow.

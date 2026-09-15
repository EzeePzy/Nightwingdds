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

## Backlog (P1/P2)
- P1: Real ephemeris (Swiss Ephemeris) + timezone-by-place for astronomically accurate charts.
- P1: Daily/Weekly/Yearly horoscope refresh (currently one personalized reading).
- P2: Saved multiple birth profiles (family/friends), PDF export of reading.
- P2: Gemstone catalog editing from admin (currently read-only), password reset flow.

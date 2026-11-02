# Rashify

Vedic astrology web app: true Rashi (Moon sign), Lagna, Nakshatra, Vimshottari
Dasha, Guna Milan matching, daily/weekly/yearly horoscopes, gemstone remedies,
accounts and an admin panel.

This repository has been adapted to deploy as **one service** with **SQLite**
instead of MongoDB, so it needs no external database, AI key or payment key.

## Stack

- Frontend: React 19, CRA + Craco, Tailwind, framer-motion, lucide-react.
- Backend: FastAPI, SQLite (`backend/db.py`), Swiss Ephemeris (`pyswisseph`),
  offline geocoding (`geonamescache`), ReportLab PDF generation.
- Deployment: Docker on Render (`render.yaml`).

## Local development

Backend (Python 3.11/3.12 recommended):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn server:app --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install --legacy-peer-deps
REACT_APP_BACKEND_URL=http://localhost:8000 npm start
```

Default admin login after the backend starts: **admin / Rashi@2026**
(or `admin@rashisense.com`). Override with `ADMIN_USERNAME` / `ADMIN_PASSWORD`.

## Deploy to Render

1. Push this repo to GitHub.
2. In Render: **New > Web Service**, connect the repo, choose **Docker**.
3. Render reads `render.yaml`; if creating manually, keep the defaults:
   - Health check path: `/api/`
   - Plan: Free
   - Env: `JWT_SECRET` (generate), `SQLITE_PATH=/tmp/rashify.db`,
     `ADMIN_EMAIL`, `ADMIN_USERNAME`, `ADMIN_PASSWORD`, `PDF_PRICE_INR=0`,
     `CORS_ORIGINS=*`.
4. Deploy. The app is served at the service root; the API lives under `/api`.

### Free-plan behaviour

- The service sleeps after inactivity and has an ephemeral filesystem.
- SQLite data (`users`, `readings`, `profiles`, logs) **resets on restart or
  deploy**. Use a paid disk or a hosted SQLite (Turso) if persistence is needed.
- AI readings use the built-in deterministic fallbacks. Payments are disabled;
  the Kundali PDF is generated free for saved readings.

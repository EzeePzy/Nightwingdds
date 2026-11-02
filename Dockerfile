# ---------- Build the React frontend ----------
FROM node:22-alpine AS web
WORKDIR /app/frontend
COPY frontend/package.json ./
RUN npm install --legacy-peer-deps --no-audit --no-fund
COPY frontend/ ./
ENV CI=false
ENV REACT_APP_BACKEND_URL=""
RUN npm run build

# ---------- Runtime: FastAPI + SQLite + static React ----------
FROM python:3.12-slim
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./
COPY --from=web /app/frontend/build ./static

RUN mkdir -p /app/data
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]

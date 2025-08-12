# AIR-scrappy (Airbnb → Rentals United)

Production‑grade scraper skeleton:
- FastAPI backend with Playwright‑ready rendering, robust HTML/JSON extraction, rate limiting, CORS, and Prometheus metrics
- React + Vite single‑page admin UI for testing and inspecting outputs
- Docker Compose with Prometheus + Grafana for basic monitoring

## Quickstart (local dev)

Backend (Python 3.11+):

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# optional for dynamic content rendering:
# python -m playwright install chromium --with-deps
pytest -q
uvicorn app:APP --reload --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Docker Compose (backend, frontend, Prometheus, Grafana):

```bash
docker compose up --build
```

Frontend will be served on http://localhost:5173 and proxy API requests to the backend.

## Environment variables

Backend (set via shell or an `.env` file in repo root referenced by `compose.yaml`):

- `API_KEY` (optional): Require clients to send `X-API-Key: <value>` header
- `ALLOWED_ORIGINS` (CSV): CORS allowlist. Default: `http://localhost:5173,http://localhost:5174,http://localhost:5175`
- `RATE_LIMIT` (SlowAPI format): Default `60/minute`
- `PLAYWRIGHT_TIMEOUT` (int seconds): Navigation/render timeout. Default `15`
- `MAX_IMAGES` (int): Upper bound for image enrichment. Default `25`
- `USER_AGENT_POOL` (JSON array, optional): Custom UA rotation, e.g. `["Mozilla/5.0 ...", "Mozilla/5.0 ..."]`
- `HTTP_PROXY` / `HTTPS_PROXY` (optional): Proxy settings passed to Playwright

Frontend:

- `VITE_API_BASE`: Base URL for API. Defaults to `/api` (works with dev proxy and Nginx in Docker)

> Tip: If you don’t keep an `.env` in the repo, export these in your shell or your CI variables.

## API

- `GET /healthz` → `{ status, browser, contexts }` (reports Playwright/browser readiness)
- `GET /metrics` → Prometheus metrics (via `prometheus-fastapi-instrumentator`)
- `GET /robots-check?url=` → Fetches and previews `robots.txt` for a host
- `POST /api/extract` with body `{ "url": "..." }` → Extracts raw listing data
- `POST /api/map/rentals-united` with body `{ "url": "..." }` → Normalized Rentals United shaped output

Send `X-API-Key` header when `API_KEY` is set.

## Monitoring

- Prometheus runs at http://localhost:9090 and scrapes backend `/metrics`
- Grafana runs at http://localhost:3000 (admin/admin by default) with a Prometheus datasource pre‑provisioned

## Testing

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Build production images (optional)

```bash
docker compose build
# or single services
docker build -t air-scrappy-backend ./backend
docker build -t air-scrappy-frontend ./frontend
```

## Notes & guidelines

- Respect site TOS and robots; do not use this for unauthorized scraping
- Playwright is used selectively when dynamic rendering is required
- Rate limiting and CORS are enabled; tune via env vars above
- Metrics are exposed for minimal observability; extend as needed

## Sample URL

Try: `https://www.airbnb.com/rooms/780210484211628646`

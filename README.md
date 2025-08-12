# AIR-scrappy (Airbnb -> Rentals United)

Production-grade scraper skeleton: FastAPI backend with Playwright-ready extractor and amenity normalization + minimal React test UI.

## Quickstart (dev)

Backend:

```bash
cd AIR-scrappy/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest
uvicorn app:APP --reload --port 8000
```

Frontend:

```bash
cd AIR-scrappy/frontend
npm install
npm run dev
```

Compose:

```bash
docker compose up --build
```

Environment: see `.env.example`.

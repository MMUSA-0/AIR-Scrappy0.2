# AIR-scrappy Backend

FastAPI + Playwright-ready backend that extracts Airbnb listing data and maps to Rentals United taxonomy.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
# optional browsers (not needed for unit tests):
# python -m playwright install chromium
pytest
```

## Run

```bash
uvicorn app:APP --reload --port 8000
```

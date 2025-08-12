import json
import os
import time
from typing import Any, Dict

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from ru_mapper.mapping import map_to_ru
from ru_mapper.schema import ExtractedListing, RUListing, Photo
from scraper.extractor import extract_from_html
from scraper.enrich import collect_images, collect_amenities
from scraper.utils import (
    find_first_listing_like,
    normalize_airbnb_url,
    canonicalize_airbnb_url,
)

APP = FastAPI(title="AIR-scrappy API", version="0.1.0")

# Env
API_KEY = os.getenv("API_KEY")
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:5174,http://localhost:5175").split(",") if o.strip()]
RATE_LIMIT = os.getenv("RATE_LIMIT", "60/minute")
PLAYWRIGHT_TIMEOUT = int(os.getenv("PLAYWRIGHT_TIMEOUT", "15"))

# CORS
APP.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting
limiter = Limiter(key_func=get_remote_address)
APP.state.limiter = limiter
APP.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
APP.add_middleware(SlowAPIMiddleware)

# Metrics
Instrumentator().instrument(APP).expose(APP, endpoint="/metrics", include_in_schema=False)


class UrlInput(BaseModel):
    url: str


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")


@APP.get("/healthz")
async def healthz() -> Dict[str, Any]:
    # Report Playwright/browser status if available
    browser_ok = False
    contexts = 0
    try:
        from scraper.browser import BrowserManager  # type: ignore

        mgr = BrowserManager.instance()
        browser = getattr(mgr, "_browser", None)
        if browser is not None:
            browser_ok = True
            try:
                contexts = len(browser.contexts)
            except Exception:
                contexts = 0
    except Exception:
        # Playwright not installed or browser not started
        browser_ok = False
        contexts = 0
    return {"status": "ok", "browser": browser_ok, "contexts": contexts}


# Alias under /api for frontend proxy convenience
@APP.get("/api/healthz")
async def healthz_api() -> Dict[str, Any]:
    return await healthz()


@APP.get("/robots-check")
async def robots_check(url: str) -> Dict[str, Any]:
    # Warn-only compliance helper
    try:
        from urllib.parse import urlparse

        p = urlparse(url)
        robots = f"{p.scheme}://{p.netloc}/robots.txt"
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(robots)
            return {"robots_url": robots, "status": r.status_code, "snippet": r.text[:500]}
    except Exception as e:
        return {"error": str(e)}


# Alias under /api for frontend proxy convenience
@APP.get("/api/robots-check")
async def robots_check_api(url: str) -> Dict[str, Any]:
    return await robots_check(url)


async def fetch_html_with_playwright(url: str) -> str | None:
    try:
        from scraper.browser import render_and_get_next_data, render_and_get_html
    except Exception:
        return None
    try:
        # First try NEXT_DATA
        json_text = await render_and_get_next_data(url, timeout_s=PLAYWRIGHT_TIMEOUT)
        if json_text:
            try:
                nd = json.loads(json_text)
                if find_first_listing_like(nd):
                    return f'<script id="__NEXT_DATA__" type="application/json">{json_text}</script>'
            except Exception:
                pass

        # Fallback to HTML and attempt to find a PDP link if needed
        html = await render_and_get_html(url, timeout_s=PLAYWRIGHT_TIMEOUT)
        if '/rooms/' not in url:
            import re
            m = re.search(r'https?://[^"\s]+/rooms/\d+', html)
            if m:
                next_url = m.group(0)
                jt2 = await render_and_get_next_data(next_url, timeout_s=PLAYWRIGHT_TIMEOUT)
                if jt2:
                    try:
                        nd2 = json.loads(jt2)
                        if find_first_listing_like(nd2):
                            return f'<script id="__NEXT_DATA__" type="application/json">{jt2}</script>'
                    except Exception:
                        pass
                # As last resort, return the HTML of the PDP
                html2 = await render_and_get_html(next_url, timeout_s=PLAYWRIGHT_TIMEOUT)
                return html2
        return html
    except Exception:
        return None


async def fetch_html_with_httpx(url: str) -> str:
    async with httpx.AsyncClient(timeout=PLAYWRIGHT_TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


@APP.post("/api/extract")
@limiter.limit(RATE_LIMIT)
async def api_extract(payload: UrlInput, request: Request, _: None = Depends(require_api_key)) -> ExtractedListing:
    start = time.time()
    url = normalize_airbnb_url(payload.url)
    if "/rooms/" not in url:
        try:
            url = await canonicalize_airbnb_url(url)
        except Exception:
            pass

    html = await fetch_html_with_playwright(url)
    if not html:
        html = await fetch_html_with_httpx(url)

    listing = extract_from_html(html, url=url)
    # Enrichment: collect images and amenities via Playwright when initial parse is weak
    try:
        if len(listing.photos) < 5:
            imgs = await collect_images(url, max_images=int(os.getenv("MAX_IMAGES", "25")), wait_seconds=1.0)
            if imgs:
                listing.photos = [
                    Photo(url=i) for i in imgs[: int(os.getenv("MAX_IMAGES", "25"))]
                ]
        if not listing.amenities_raw and not listing.amenities_normalized:
            ams = await collect_amenities(url, wait_seconds=1.0)
            if ams:
                listing.amenities_raw = ams
                from ru_mapper.amenities import normalize_amenities as _norm

                listing.amenities_normalized = _norm(ams)
    except Exception:
        pass
    duration_ms = int((time.time() - start) * 1000)
    return listing


@APP.get("/api/extract")
@limiter.limit(RATE_LIMIT)
async def api_extract_get(url: str, request: Request, _: None = Depends(require_api_key)) -> ExtractedListing:
    # Convenience GET endpoint for manual testing
    start = time.time()
    url = normalize_airbnb_url(url)
    if "/rooms/" not in url:
        try:
            url = await canonicalize_airbnb_url(url)
        except Exception:
            pass
    html = await fetch_html_with_playwright(url)
    if not html:
        html = await fetch_html_with_httpx(url)
    listing = extract_from_html(html, url=url)
    _ = int((time.time() - start) * 1000)
    return listing


@APP.post("/api/map/rentals-united")
@limiter.limit(RATE_LIMIT)
async def api_map_ru(payload: UrlInput, request: Request, _: None = Depends(require_api_key)) -> RUListing:
    url = normalize_airbnb_url(payload.url)
    if "/rooms/" not in url:
        try:
            url = await canonicalize_airbnb_url(url)
        except Exception:
            pass
    html = await fetch_html_with_playwright(url)
    if not html:
        html = await fetch_html_with_httpx(payload.url)

    listing = extract_from_html(html, url=url)
    # Enrichment similar to /api/extract
    try:
        if len(listing.photos) < 5:
            imgs = await collect_images(payload.url, max_images=int(os.getenv("MAX_IMAGES", "25")), wait_seconds=1.0)
            if imgs:
                listing.photos = [Photo(url=i) for i in imgs[: int(os.getenv("MAX_IMAGES", "25"))]]
        if not listing.amenities_raw and not listing.amenities_normalized:
            ams = await collect_amenities(payload.url, wait_seconds=1.0)
            if ams:
                listing.amenities_raw = ams
                from ru_mapper.amenities import normalize_amenities as _norm

                listing.amenities_normalized = _norm(ams)
    except Exception:
        pass
    return map_to_ru(listing)


@APP.get("/api/map/rentals-united")
@limiter.limit(RATE_LIMIT)
async def api_map_ru_get(url: str, request: Request, _: None = Depends(require_api_key)) -> RUListing:
    url = normalize_airbnb_url(url)
    if "/rooms/" not in url:
        try:
            url = await canonicalize_airbnb_url(url)
        except Exception:
            pass
    html = await fetch_html_with_playwright(url)
    if not html:
        html = await fetch_html_with_httpx(url)
    listing = extract_from_html(html, url=url)
    return map_to_ru(listing)

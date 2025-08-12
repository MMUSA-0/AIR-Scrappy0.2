from __future__ import annotations

import asyncio
import json
import os
import random
from typing import Any, Dict, List, Optional


_DEFAULT_UAS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
]


def get_user_agent_pool() -> List[str]:
    raw = os.getenv("USER_AGENT_POOL", "")
    if raw:
        try:
            arr = json.loads(raw)
            if isinstance(arr, list) and arr:
                return [str(x) for x in arr]
        except Exception:
            pass
    return _DEFAULT_UAS


def choose_user_agent() -> str:
    pool = get_user_agent_pool()
    return random.choice(pool)


def get_proxy_config() -> Optional[Dict[str, Any]]:
    proxy = os.getenv("HTTP_PROXY") or os.getenv("HTTPS_PROXY")
    if proxy:
        return {"server": proxy}
    return None


def build_context_kwargs() -> Dict[str, Any]:
    ua = choose_user_agent()
    opts: Dict[str, Any] = {
        "user_agent": ua,
        "viewport": {"width": 1280, "height": 800},
        "java_script_enabled": True,
        "ignore_https_errors": True,
        "bypass_csp": True,
        "locale": "en-US",
        "extra_http_headers": {
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com/",
        },
    }
    proxy = get_proxy_config()
    if proxy:
        opts["proxy"] = proxy
    return opts


async def jitter_delay(min_ms: int = 600, max_ms: int = 1500) -> None:
    await asyncio.sleep(random.uniform(min_ms, max_ms) / 1000.0)


async def enable_request_blocking(page) -> None:
    # Best-effort blocking of analytics/ads that are not required for rendering
    blocked = (
        "googletagmanager", "google-analytics", "doubleclick", "facebook", "adsystem",
        "segment", "amplitude", "mixpanel", "hotjar", "optimizely", "criteo",
    )

    async def on_route(route):
        url = route.request.url.lower()
        if any(b in url for b in blocked):
            return await route.abort()
        return await route.continue_()

    try:
        await page.route("**/*", on_route)
    except Exception:
        pass

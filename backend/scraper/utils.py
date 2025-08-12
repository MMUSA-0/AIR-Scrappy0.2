from __future__ import annotations

import re
import unicodedata
from typing import Any, Iterable, List, Optional


def normalize_text(text: Optional[str]) -> str:
    if text is None:
        return ""
    s = unicodedata.normalize("NFKC", str(text))
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def deep_get(data: Any, path: Iterable[str], default: Any = None) -> Any:
    cur = data
    try:
        for key in path:
            if isinstance(cur, dict) and key in cur:
                cur = cur[key]
            else:
                return default
        return cur
    except Exception:
        return default


def find_first_listing_like(next_data: dict) -> Optional[dict]:
    # Known paths
    candidates = [
        deep_get(next_data, ["props", "pageProps", "listing"]),
        deep_get(
            next_data,
            [
                "props",
                "pageProps",
                "bootstrapData",
                "reduxData",
                "homePDP",
                "listingInfo",
                "listing",
            ],
        ),
    ]

    for c in candidates:
        if isinstance(c, dict) and c:
            return c

    # Apollo cache heuristic
    apollo = deep_get(next_data, ["props", "pageProps", "__APOLLO_STATE__"]) or deep_get(
        next_data, ["__APOLLO_STATE__"]
    )
    if isinstance(apollo, dict):
        for k, v in apollo.items():
            if isinstance(k, str) and k.lower().startswith("listing:") and isinstance(v, dict):
                return v
    return None


def dedupe_photos(urls: Iterable[dict], min_side_px: int = 0, max_items: int = 25) -> List[dict]:
    seen = set()
    out: List[dict] = []
    for p in urls:
        url = p.get("url") or p.get("large") or p.get("xl_picture_url") or p.get("picture")
        if not url or url.startswith("data:"):
            continue
        # Filter obvious non-listing assets and sprites
        lowered = url.lower()
        if "airbnb-platform-assets" in lowered or "search-bar-icons" in lowered:
            continue
        width = p.get("width") or p.get("w")
        height = p.get("height") or p.get("h")
        if width and height and min(width, height) < min_side_px:
            continue
        if url in seen:
            continue
        seen.add(url)
        out.append({
            "url": url,
            "width": width,
            "height": height,
            "caption": p.get("caption") or p.get("title") or p.get("alt"),
        })
        if len(out) >= max_items:
            break
    return out


def is_airbnb_listing_url(url: str) -> bool:
    if not url:
        return False
    u = url.lower()
    return "/rooms/" in u or "/p/" in u  # PDP canonical paths


def normalize_airbnb_url(input_url: str) -> str:
    """Return a sanitized URL string that the backend can safely fetch.

    This is intentionally conservative and does not attempt network lookups.
    It handles:
      - leading/trailing whitespace and stray leading '@'
      - missing scheme (assumes https)
      - surrounding angle brackets or quotes
      - common markdown copy artifacts (trailing ')' or '.')
    """
    if input_url is None:
        return ""
    s = str(input_url).strip()
    # Drop leading '@' often used in chat mentions
    if s.startswith("@"):
        s = s.lstrip("@").strip()
    # Remove surrounding angle brackets or quotes
    if (s.startswith("<") and s.endswith(">")) or (s.startswith("\"") and s.endswith("\"")):
        s = s[1:-1].strip()
    # Trim trailing punctuation that is not part of URL
    while s and s[-1] in ")].,":
        s = s[:-1]
    # Ensure scheme
    if not s.startswith("http://") and not s.startswith("https://"):
        s = "https://" + s
    return s


async def canonicalize_airbnb_url(url: str, timeout_s: int = 8) -> str:
    """Attempt a lightweight network canonicalization.

    - Follows redirects using a plain HTTP client
    - If HTML is returned and contains a canonical link or a rooms path,
      prefer that as the canonical target
    - Never raises; returns the original URL on failure
    """
    try:
        import re
        import httpx

        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout_s) as client:
            resp = await client.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            })
            final_url = str(resp.url)
            # If we landed on a rooms URL already, return it
            if "/rooms/" in final_url:
                return final_url
            # Try to parse canonical
            text = resp.text or ""
            m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)["\']', text, re.I)
            if m:
                href = m.group(1)
                if "/rooms/" in href or "/h/" in href:
                    return href if href.startswith("http") else ("https://www.airbnb.com" + href)
            # Heuristic: look for a rooms link
            m2 = re.search(r'https?://[^"\s]+/rooms/\d+', text)
            if m2:
                return m2.group(0)
            m3 = re.search(r'(/rooms/\d+)', text)
            if m3:
                return "https://www.airbnb.com" + m3.group(1)
            return final_url or url
    except Exception:
        return url

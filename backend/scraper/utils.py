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

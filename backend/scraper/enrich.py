from __future__ import annotations

import asyncio
import re
from typing import List, Optional, Set

from .browser import BrowserManager


def _looks_like_photo(url: str) -> bool:
    if not isinstance(url, str):
        return False
    u = url.lower()
    if "airbnbplatformassets" in u or "search-bar-icons" in u:
        return False
    return (
        u.startswith("http")
        and ("muscache.com/im/pictures" in u or "/photos/" in u or ".jpg" in u or ".jpeg" in u or ".png" in u)
    )


async def collect_images(url: str, max_images: int = 30, wait_seconds: float = 1.5) -> List[str]:
    mgr = BrowserManager.instance()
    await mgr.start()
    images: List[str] = []
    seen: Set[str] = set()

    async with mgr.page() as page:
        net_urls: List[str] = []

        async def on_response(resp):
            try:
                req = resp.request
                if req.resource_type == "image":
                    u = resp.url
                    if u and _looks_like_photo(u):
                        net_urls.append(u)
            except Exception:
                pass

        try:
            page.on("response", on_response)
        except Exception:
            pass

        await page.goto(url, wait_until="domcontentloaded")
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)

        # Scroll to trigger lazy loads
        try:
            for _ in range(3):
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
                await asyncio.sleep(0.4)
                await page.evaluate("window.scrollTo(0, 0);")
                await asyncio.sleep(0.2)
        except Exception:
            pass

        # Collect from DOM
        try:
            dom_imgs = await page.evaluate(
                """
                () => {
                  const out = [];
                  const imgs = Array.from(document.querySelectorAll('img'));
                  for (const img of imgs) {
                    if (img.src) out.push(img.src);
                    const srcset = img.getAttribute('srcset');
                    if (srcset) {
                      const parts = srcset.split(',').map(s => s.trim().split(' ')[0]);
                      for (const p of parts) if (p) out.push(p);
                    }
                  }
                  const sources = Array.from(document.querySelectorAll('source[srcset]'));
                  for (const s of sources) {
                    const parts = s.getAttribute('srcset').split(',').map(x => x.trim().split(' ')[0]);
                    for (const p of parts) if (p) out.push(p);
                  }
                  return out;
                }
                """
            )
            for u in dom_imgs or []:
                if isinstance(u, str) and _looks_like_photo(u) and u not in seen:
                    seen.add(u)
                    images.append(u)
                    if len(images) >= max_images:
                        return images
        except Exception:
            pass

        # Add network-captured images
        for u in net_urls:
            if _looks_like_photo(u) and u not in seen:
                seen.add(u)
                images.append(u)
                if len(images) >= max_images:
                    return images

        # Try photo tour modal variant
        sep = '&' if '?' in url else '?'
        modal_url = f"{url}{sep}modal=PHOTO_TOUR_SCROLLABLE"
        try:
            await page.goto(modal_url, wait_until="domcontentloaded")
            if wait_seconds > 0:
                await asyncio.sleep(wait_seconds)
            # Collect again
            dom_imgs2 = await page.evaluate(
                """
                () => Array.from(document.querySelectorAll('img')).map(i => i.src).filter(Boolean)
                """
            )
            for u in dom_imgs2 or []:
                if isinstance(u, str) and _looks_like_photo(u) and u not in seen:
                    seen.add(u)
                    images.append(u)
                    if len(images) >= max_images:
                        break
        except Exception:
            pass

    return images[:max_images]


async def collect_amenities(url: str, wait_seconds: float = 1.0) -> List[str]:
    mgr = BrowserManager.instance()
    await mgr.start()
    items: List[str] = []
    seen: Set[str] = set()

    def _push(s: Optional[str]):
        if not s:
            return
        s2 = re.sub(r"\s+", " ", s).strip()
        low = s2.lower()
        if not s2 or len(s2) > 120:
            return
        if any(x in low for x in [
            "translation", "translated", "calendar", "reviews", "rating", "unavailable:",
            "where you'll", "where you’ll", "things to know", "meet your host", "show all", "see all",
        ]):
            return
        if s2 not in seen:
            seen.add(s2)
            items.append(s2)

    async with mgr.page() as page:
        await page.goto(url, wait_until="domcontentloaded")
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)

        # Try opening amenities modal
        selectors = [
            "button:has-text('Show all amenities')",
            "button:has-text('See all amenities')",
            "text=/Show\\s+all\\s+\\d+\\s+amenities/i",
            "button:has-text('Show all')",
        ]
        for sel in selectors:
            try:
                locator = page.locator(sel)
                if await locator.count() > 0:
                    await locator.first.click(timeout=1200)
                    await asyncio.sleep(0.5)
                    break
            except Exception:
                continue

        # Scope to modal if any
        modal_scope = None
        for sel in ["div[role='dialog']", "section[aria-label*='Amenities' i]", "[data-testid*='amenities']"]:
            try:
                loc = page.locator(sel)
                if await loc.count() > 0 and await loc.first.is_visible():
                    modal_scope = sel
                    break
            except Exception:
                continue

        # Extract amenity texts
        try:
            elements = await page.evaluate(
                """
                (sel) => {
                  const root = sel ? document.querySelector(sel) : document;
                  if (!root) return [];
                  const out = [];
                  const nodes = root.querySelectorAll('li,div,span');
                  nodes.forEach(n => {
                    const t = (n.innerText || n.textContent || '').trim();
                    if (t) out.push(t);
                  });
                  return out;
                }
                """,
                modal_scope,
            )
            for t in elements or []:
                if isinstance(t, str):
                    _push(t)
        except Exception:
            pass

    return items[:100]





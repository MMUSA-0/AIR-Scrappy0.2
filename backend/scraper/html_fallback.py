from __future__ import annotations

import json
from typing import List

from bs4 import BeautifulSoup

from ru_mapper.amenities import normalize_amenities
from ru_mapper.schema import Address, ExtractedListing, Photo


def extract_from_html_fallback(html: str, url: str = "") -> ExtractedListing:
    soup = BeautifulSoup(html or "", "html.parser")

    # Try to parse __NEXT_DATA__ if present
    next_data_script = soup.find("script", id="__NEXT_DATA__")
    if next_data_script and next_data_script.string:
        try:
            next_data = json.loads(next_data_script.string)
            from .extractor import extract_from_next_data  # late import to avoid cycle

            return extract_from_next_data(next_data, url=url)
        except Exception:
            pass

    title = (soup.title.string or "").strip() if soup.title else None
    desc_meta = soup.find("meta", attrs={"name": "description"})
    description = desc_meta["content"].strip() if desc_meta and desc_meta.has_attr("content") else None

    imgs = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src")
        if not src:
            continue
        imgs.append({
            "url": src,
            "width": None,
            "height": None,
            "caption": img.get("alt"),
        })

    amenity_texts: List[str] = []
    for elem in soup.select('[data-testid*="amenity"], .amenity, .amenities li'):
        text = (elem.get_text(" ") or "").strip()
        if text:
            amenity_texts.append(text)

    return ExtractedListing(
        title=title,
        description=description,
        address=Address(),
        photos=[Photo(**p) for p in imgs],
        amenities_raw=amenity_texts,
        amenities_normalized=normalize_amenities(amenity_texts),
        canonical_url=url,
    )

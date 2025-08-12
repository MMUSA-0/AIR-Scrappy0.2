from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from ru_mapper.amenities import normalize_amenities
from ru_mapper.schema import Address, ExtractedListing, Host, Photo

from .utils import dedupe_photos, find_first_listing_like


def _safe_float(v: Any) -> Optional[float]:
    try:
        return float(v)
    except Exception:
        return None


def _safe_int(v: Any) -> Optional[int]:
    try:
        return int(v)
    except Exception:
        try:
            f = float(v)
            return int(f)
        except Exception:
            return None


def extract_from_next_data(next_data: Dict[str, Any], url: str = "") -> ExtractedListing:
    listing = find_first_listing_like(next_data) or {}

    title = listing.get("name") or listing.get("title") or (listing.get("seoDetails") or {}).get("listingName")
    description = (
        listing.get("description")
        or (listing.get("sectionedDescription") or {}).get("body")
        or (listing.get("sectionedDescription") or {}).get("overview")
        or (listing.get("seoDetails") or {}).get("description")
    )

    # Address
    raw_addr = listing.get("address") or listing.get("location") or {}
    address = Address(
        full=raw_addr.get("full") or raw_addr.get("public") or None,
        street=raw_addr.get("street") or raw_addr.get("streetAddress") or None,
        city=raw_addr.get("city") or None,
        state=raw_addr.get("state") or raw_addr.get("stateProvince") or None,
        postal_code=raw_addr.get("postalCode") or raw_addr.get("zipcode") or None,
        country=raw_addr.get("country") or None,
        lat=_safe_float(raw_addr.get("lat") or raw_addr.get("latitude")),
        lng=_safe_float(raw_addr.get("lng") or raw_addr.get("longitude")),
    )

    # Photos
    raw_photos: List[dict] = []
    photos_candidates = [
        listing.get("photos"),
        listing.get("images"),
        listing.get("media"),
        (listing.get("photoData") or {}).get("allPhotos"),
    ]
    for cand in photos_candidates:
        if isinstance(cand, list):
            raw_photos.extend(cand)

    photos = [Photo(**p) for p in dedupe_photos(raw_photos, min_side_px=300, max_items=25)]

    # Amenities
    amenities_raw: List[str] = (
        listing.get("amenities")
        or listing.get("amenityNames")
        or (listing.get("structuredContent") or {}).get("amenities")
        or []
    )
    amenities_normalized = normalize_amenities(amenities_raw)

    # Capacity
    bedrooms = _safe_int(listing.get("bedrooms"))
    beds = _safe_int(listing.get("beds"))
    bathrooms = _safe_float(listing.get("bathrooms"))
    max_guests = _safe_int(listing.get("maxGuests") or listing.get("personCapacity"))

    # Types
    property_type_raw = (
        listing.get("propertyType") or listing.get("propertyTypeLabel") or listing.get("property_type")
    )
    room_type_raw = (
        listing.get("roomTypeCategory") or listing.get("roomType") or listing.get("room_type")
    )

    # Rating
    rating = _safe_float(listing.get("starRating") or listing.get("avgRating") or listing.get("overallRating"))

    # Pricing
    currency = None
    base_price = None
    quote = listing.get("pricingQuote") or listing.get("price") or {}
    if isinstance(quote, dict):
        price = quote.get("price") or quote.get("rate") or quote
        currency = price.get("currency") or price.get("currencyCode")
        base_price = _safe_float(price.get("amount") or price.get("total") or price.get("nightly"))

    # Host
    raw_host = listing.get("host") or {}
    host = Host(
        name=raw_host.get("name") or raw_host.get("hostName"),
        superhost=raw_host.get("isSuperhost") or raw_host.get("is_superhost"),
        response_rate=_safe_int(raw_host.get("responseRate")),
        response_time=raw_host.get("responseTime"),
    )

    return ExtractedListing(
        title=title,
        description=description,
        address=address,
        photos=photos,
        amenities_raw=amenities_raw,
        amenities_normalized=amenities_normalized,
        bedrooms=bedrooms,
        beds=beds,
        bathrooms=bathrooms,
        max_guests=max_guests,
        property_type_raw=property_type_raw,
        room_type_raw=room_type_raw,
        rating=rating,
        currency=currency,
        base_price=base_price,
        host=host,
        source="airbnb",
        canonical_url=url,
        fetched_at=datetime.utcnow(),
    )


def extract_from_html(html: str, url: str = "") -> ExtractedListing:
    # Attempt to find __NEXT_DATA__ first
    try:
        import re

        m = re.search(r"<script[^>]+id=\"__NEXT_DATA__\"[^>]*>(.*?)</script>", html, re.S | re.I)
        if m:
            data = json.loads(m.group(1))
            return extract_from_next_data(data, url=url)
    except Exception:
        pass

    # Fallback to DOM parsing
    from .html_fallback import extract_from_html_fallback

    return extract_from_html_fallback(html, url=url)

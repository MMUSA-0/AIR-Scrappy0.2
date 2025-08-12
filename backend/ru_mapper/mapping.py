from __future__ import annotations

from typing import Optional

from .amenities import normalize_amenities
from .schema import (
    Address,
    ExtractedListing,
    RUListing,
    RUPropertyType,
    RURoomType,
)


_ROOM_TYPE_MAP = {
    "entire_place": RURoomType.ENTIRE_PLACE,
    "entire home/apt": RURoomType.ENTIRE_PLACE,
    "private_room": RURoomType.PRIVATE_ROOM,
    "private room": RURoomType.PRIVATE_ROOM,
    "shared_room": RURoomType.SHARED_ROOM,
    "shared room": RURoomType.SHARED_ROOM,
    "hotel_room": RURoomType.HOTEL_ROOM,
    "hotel room": RURoomType.HOTEL_ROOM,
}


def map_room_type_to_ru(room_type_raw: Optional[str]) -> Optional[RURoomType]:
    if not room_type_raw:
        return None
    key = room_type_raw.strip().lower()
    return _ROOM_TYPE_MAP.get(key)


def map_property_type_to_ru(property_type_raw: Optional[str]) -> RUPropertyType:
    if not property_type_raw:
        return RUPropertyType.OTHER
    key = property_type_raw.strip().lower()
    if any(k in key for k in ["apartment", "apt", "flat"]):
        return RUPropertyType.APARTMENT
    # Check more specific types before broader ones to avoid false matches
    if any(k in key for k in ["townhouse", "townhome"]):
        return RUPropertyType.TOWNHOUSE
    if any(k in key for k in ["house", "home"]):
        return RUPropertyType.HOUSE
    if "villa" in key:
        return RUPropertyType.VILLA
    if any(k in key for k in ["bungalow"]):
        return RUPropertyType.BUNGALOW
    if any(k in key for k in ["condo", "condominium"]):
        return RUPropertyType.CONDO
    if any(k in key for k in ["hotel"]):
        return RUPropertyType.HOTEL
    if any(k in key for k in ["hostel"]):
        return RUPropertyType.HOSTEL
    if any(k in key for k in ["guesthouse", "guest house"]):
        return RUPropertyType.GUESTHOUSE
    return RUPropertyType.OTHER


def map_to_ru(extracted: ExtractedListing) -> RUListing:
    return RUListing(
        property_name=extracted.title,
        description=extracted.description,
        property_type=map_property_type_to_ru(extracted.property_type_raw),
        room_type=map_room_type_to_ru(extracted.room_type_raw),
        bedrooms=extracted.bedrooms,
        beds=extracted.beds,
        bathrooms=extracted.bathrooms,
        max_guests=extracted.max_guests,
        address=Address(**extracted.address.model_dump()),
        photos=list(extracted.photos),
        amenities=normalize_amenities(extracted.amenities_raw or extracted.amenities_normalized),
        amenities_raw=list(extracted.amenities_raw),
        currency=extracted.currency,
        base_price=extracted.base_price,
        host=extracted.host,
        source=extracted.source,
        canonical_url=extracted.canonical_url,
        fetched_at=extracted.fetched_at,
    )

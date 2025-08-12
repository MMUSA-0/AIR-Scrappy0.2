from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Photo(BaseModel):
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    caption: Optional[str] = None


class Address(BaseModel):
    full: Optional[str] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class Host(BaseModel):
    name: Optional[str] = None
    superhost: Optional[bool] = None
    response_rate: Optional[int] = None
    response_time: Optional[str] = None


class ExtractedListing(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    address: Address = Field(default_factory=Address)
    photos: List[Photo] = Field(default_factory=list)
    amenities_raw: List[str] = Field(default_factory=list)
    amenities_normalized: List[str] = Field(default_factory=list)
    bedrooms: Optional[int] = None
    beds: Optional[int] = None
    bathrooms: Optional[float] = None
    max_guests: Optional[int] = None
    property_type_raw: Optional[str] = None
    room_type_raw: Optional[str] = None
    rating: Optional[float] = None
    currency: Optional[str] = None
    base_price: Optional[float] = None
    host: Host = Field(default_factory=Host)
    source: str = "airbnb"
    canonical_url: Optional[str] = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.utcnow())


class RUPropertyType(str, Enum):
    APARTMENT = "Apartment"
    HOUSE = "House"
    VILLA = "Villa"
    BUNGALOW = "Bungalow"
    CONDO = "Condominium"
    TOWNHOUSE = "Townhouse"
    HOTEL = "Hotel"
    HOSTEL = "Hostel"
    GUESTHOUSE = "Guesthouse"
    OTHER = "Other"


class RURoomType(str, Enum):
    ENTIRE_PLACE = "Entire place"
    PRIVATE_ROOM = "Private room"
    SHARED_ROOM = "Shared room"
    HOTEL_ROOM = "Hotel room"


class RUListing(BaseModel):
    property_name: Optional[str] = None
    description: Optional[str] = None
    property_type: Optional[RUPropertyType] = None
    room_type: Optional[RURoomType] = None
    bedrooms: Optional[int] = None
    beds: Optional[int] = None
    bathrooms: Optional[float] = None
    max_guests: Optional[int] = None
    address: Address = Field(default_factory=Address)
    photos: List[Photo] = Field(default_factory=list)
    amenities: List[str] = Field(default_factory=list)
    amenities_raw: List[str] = Field(default_factory=list)
    currency: Optional[str] = None
    base_price: Optional[float] = None
    host: Host = Field(default_factory=Host)
    source: str = "airbnb"
    canonical_url: Optional[str] = None
    fetched_at: datetime = Field(default_factory=lambda: datetime.utcnow())

from ru_mapper.mapping import map_property_type_to_ru, map_room_type_to_ru, map_to_ru
from ru_mapper.schema import ExtractedListing, RUPropertyType, RURoomType


def test_map_room_type_enum():
    assert map_room_type_to_ru("entire_place") == RURoomType.ENTIRE_PLACE
    assert map_room_type_to_ru("private_room") == RURoomType.PRIVATE_ROOM
    assert map_room_type_to_ru("shared_room") == RURoomType.SHARED_ROOM
    assert map_room_type_to_ru("hotel_room") == RURoomType.HOTEL_ROOM


def test_map_property_type_keywords():
    assert map_property_type_to_ru("apartment") == RUPropertyType.APARTMENT
    assert map_property_type_to_ru("Villa") == RUPropertyType.VILLA
    assert map_property_type_to_ru("Townhouse") == RUPropertyType.TOWNHOUSE
    assert map_property_type_to_ru("unknown type") == RUPropertyType.OTHER


essential = {
    "title": "Test listing",
    "description": "Nice place",
    "amenities_raw": ["wifi", "A/C", "Fridge"],
    "bedrooms": 2,
    "beds": 3,
    "bathrooms": 1.5,
    "max_guests": 4,
    "property_type_raw": "Apartment",
    "room_type_raw": "entire_place",
}


def test_map_to_ru_basic():
    ex = ExtractedListing(**essential)
    ru = map_to_ru(ex)
    assert ru.property_name == ex.title
    assert ru.property_type == RUPropertyType.APARTMENT
    assert ru.room_type == RURoomType.ENTIRE_PLACE
    assert "Wifi" in ru.amenities

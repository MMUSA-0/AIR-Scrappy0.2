from ru_mapper.amenities import normalize_amenities


def test_amenity_synonyms_wifi():
    items = ["wi-fi", "WLAN", "wireless internet"]
    normalized = normalize_amenities(items)
    assert "Wifi" in normalized


def test_amenity_synonyms_ac():
    items = ["A/C", "aircon", "ac"]
    normalized = normalize_amenities(items)
    assert "Air conditioning" in normalized


def test_amenity_synonyms_fridge():
    items = ["Fridge", "Refrigerator", "mini fridge"]
    normalized = normalize_amenities(items)
    assert "Fridge" in normalized

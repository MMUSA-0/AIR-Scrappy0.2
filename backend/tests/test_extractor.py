import json
from pathlib import Path

from scraper.extractor import extract_from_html, extract_from_next_data
from scraper.utils import normalize_airbnb_url

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def _load_json(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _load_text(name: str):
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_extract_from_next_data_minimal():
    nd = _load_json("sample_next_data.json")
    listing = extract_from_next_data(nd, url="https://example.test/rooms/1")
    assert listing.title == "Charming loft in city center"
    assert listing.address.city == "Lisbon"
    assert listing.max_guests == 3
    assert "Wifi" in listing.amenities_normalized


def test_extract_from_html_with_next_data_script():
    html = _load_text("sample_listing.html")
    listing = extract_from_html(html, url="https://example.test/rooms/1")
    assert listing.title == "Charming loft in city center"
    assert listing.address.country == "Portugal"
    assert listing.currency == "EUR"


def test_normalize_airbnb_url_variants():
    cases = {
        "@https://www.airbnb.com/rooms/123": "https://www.airbnb.com/rooms/123",
        "https://airbnb.com/h/irtahal-apartment57": "https://airbnb.com/h/irtahal-apartment57",
        "airbnb.com/rooms/999)": "https://airbnb.com/rooms/999",
        "  https://www.airbnb.com/rooms/1211031564000709008  ": "https://www.airbnb.com/rooms/1211031564000709008",
        "www.airbnb.com/rooms/42": "https://www.airbnb.com/rooms/42",
    }
    for raw, expected in cases.items():
        assert normalize_airbnb_url(raw) == expected

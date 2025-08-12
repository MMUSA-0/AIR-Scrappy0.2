from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Dict, Iterable, List

from rapidfuzz import fuzz, process

DATA_DIR = Path(__file__).resolve().parent / "data"
TAXONOMY_FILE = DATA_DIR / "amenities_taxonomy.json"
SYNONYMS_FILE = DATA_DIR / "amenities_synonyms.json"


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


_WHITESPACE_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[\u0000-\u001F\u007F]+")


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    text = unicodedata.normalize("NFKC", str(value)).strip().lower()
    text = _PUNCT_RE.sub(" ", text)
    text = _WHITESPACE_RE.sub(" ", text)
    return text


def taxonomy() -> Dict[str, List[str]]:
    return _load_json(TAXONOMY_FILE)


def synonyms_table() -> Dict[str, str]:
    # Store keys normalized for lookups
    raw = _load_json(SYNONYMS_FILE)
    return {normalize_text(k): v for k, v in raw.items()}


def canonical_flat_list() -> List[str]:
    flat: List[str] = []
    for group_values in taxonomy().values():
        flat.extend(group_values)
    # Deduplicate while preserving order
    seen = set()
    ordered_unique = []
    for item in flat:
        if item not in seen:
            ordered_unique.append(item)
            seen.add(item)
    return ordered_unique


_CANONICAL = canonical_flat_list()
_SYNONYMS = synonyms_table()


def _pre_map_synonyms(raw_items: Iterable[str]) -> List[str]:
    mapped: List[str] = []
    for item in raw_items:
        key = normalize_text(item)
        if key in _SYNONYMS:
            mapped.append(_SYNONYMS[key])
        else:
            mapped.append(item)
    return mapped


def normalize_amenities(raw_list: Iterable[str]) -> List[str]:
    if raw_list is None:
        return []

    # First, apply explicit synonyms mapping
    pre_mapped = _pre_map_synonyms(raw_list)

    # Then fuzzy-match leftovers to canonical list
    results = set()
    for item in pre_mapped:
        # If already canonical, accept
        if item in _CANONICAL:
            results.add(item)
            continue
        key = normalize_text(item)
        if key in _SYNONYMS:
            results.add(_SYNONYMS[key])
            continue
        match = process.extractOne(
            key,
            _CANONICAL,
            scorer=fuzz.token_set_ratio,
            score_cutoff=88,
        )
        if match:
            best, score, _ = match
            if score >= 88:
                results.add(best)
    return sorted(results)

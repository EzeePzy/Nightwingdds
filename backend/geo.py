"""Offline geocoding: birth place string -> latitude, longitude, IANA timezone."""
from functools import lru_cache
from geonamescache import GeonamesCache

_gc = GeonamesCache()
_CITIES = _gc.get_cities()
_COUNTRIES = _gc.get_countries()

# Build lookup indexes once
_NAME_INDEX = {}
for _c in _CITIES.values():
    _NAME_INDEX.setdefault(_c["name"].lower(), []).append(_c)

_COUNTRY_NAME_TO_CODE = {v["name"].lower(): code for code, v in _COUNTRIES.items()}
# common aliases
_COUNTRY_NAME_TO_CODE.update({"usa": "US", "uk": "GB", "uae": "AE", "united states": "US"})

_DEFAULT = {"lat": 23.1765, "lon": 75.7885, "tz": "Asia/Kolkata",
            "matched": "Ujjain, India", "confidence": "low"}


def search_cities(q: str, limit: int = 8):
    q = (q or "").strip().lower()
    if len(q) < 2:
        return []
    scored = []
    for c in _CITIES.values():
        name = c["name"]
        nl = name.lower()
        if nl.startswith(q):
            country = _COUNTRIES.get(c.get("countrycode", ""), {}).get("name", c.get("countrycode", ""))
            scored.append((c.get("population", 0) or 0, f"{name}, {country}"))
    scored.sort(reverse=True)
    out, seen = [], set()
    for _, label in scored:
        if label in seen:
            continue
        seen.add(label)
        out.append(label)
        if len(out) >= limit:
            break
    return out


@lru_cache(maxsize=512)
def geocode(place: str):
    if not place or not place.strip():
        return dict(_DEFAULT)
    parts = [p.strip() for p in place.split(",") if p.strip()]
    city_part = parts[0].lower() if parts else place.strip().lower()

    # detect country hint from any trailing part
    country_code = None
    for p in parts[1:]:
        cc = _COUNTRY_NAME_TO_CODE.get(p.lower())
        if cc:
            country_code = cc
            break

    candidates = _NAME_INDEX.get(city_part)
    if not candidates:
        # try progressive token match (e.g. "New Delhi Airport")
        for name, cities in _NAME_INDEX.items():
            if name and (name in city_part or city_part in name):
                candidates = cities
                break

    if not candidates:
        return dict(_DEFAULT)

    filtered = [c for c in candidates if c.get("countrycode") == country_code] if country_code else candidates
    if not filtered:
        filtered = candidates

    best = max(filtered, key=lambda c: c.get("population", 0) or 0)
    country = _COUNTRIES.get(best.get("countrycode", ""), {}).get("name", best.get("countrycode", ""))
    return {
        "lat": float(best["latitude"]),
        "lon": float(best["longitude"]),
        "tz": best.get("timezone") or "Asia/Kolkata",
        "matched": f"{best['name']}, {country}",
        "confidence": "high",
    }

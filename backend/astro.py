"""Vedic astrology calculation engine and reference data for Rashisense.

Uses the Swiss Ephemeris (pyswisseph) with the Lahiri (Chitrapaksha) ayanamsa
for astronomically precise sidereal positions, plus birth-place latitude,
longitude and timezone for an accurate Ascendant (Lagna).
"""
from datetime import datetime
import pytz
import swisseph as swe

RASHIS = [
    {"key": "mesha", "en": "Aries", "sa": "Mesha", "symbol": "Ram", "element": "Fire", "planet": "Mars", "planet_sa": "Mangal"},
    {"key": "vrishabha", "en": "Taurus", "sa": "Vrishabha", "symbol": "Bull", "element": "Earth", "planet": "Venus", "planet_sa": "Shukra"},
    {"key": "mithuna", "en": "Gemini", "sa": "Mithuna", "symbol": "Twins", "element": "Air", "planet": "Mercury", "planet_sa": "Budh"},
    {"key": "karka", "en": "Cancer", "sa": "Karka", "symbol": "Crab", "element": "Water", "planet": "Moon", "planet_sa": "Chandra"},
    {"key": "simha", "en": "Leo", "sa": "Simha", "symbol": "Lion", "element": "Fire", "planet": "Sun", "planet_sa": "Surya"},
    {"key": "kanya", "en": "Virgo", "sa": "Kanya", "symbol": "Maiden", "element": "Earth", "planet": "Mercury", "planet_sa": "Budh"},
    {"key": "tula", "en": "Libra", "sa": "Tula", "symbol": "Scales", "element": "Air", "planet": "Venus", "planet_sa": "Shukra"},
    {"key": "vrishchika", "en": "Scorpio", "sa": "Vrishchika", "symbol": "Scorpion", "element": "Water", "planet": "Mars", "planet_sa": "Mangal"},
    {"key": "dhanu", "en": "Sagittarius", "sa": "Dhanu", "symbol": "Archer", "element": "Fire", "planet": "Jupiter", "planet_sa": "Guru"},
    {"key": "makara", "en": "Capricorn", "sa": "Makara", "symbol": "Crocodile", "element": "Earth", "planet": "Saturn", "planet_sa": "Shani"},
    {"key": "kumbha", "en": "Aquarius", "sa": "Kumbha", "symbol": "Water-Bearer", "element": "Air", "planet": "Saturn", "planet_sa": "Shani"},
    {"key": "meena", "en": "Pisces", "sa": "Meena", "symbol": "Fishes", "element": "Water", "planet": "Jupiter", "planet_sa": "Guru"},
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu",
    "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]

# Gemstone reference keyed by ruling planet
GEMSTONES = {
    "Sun": {"name": "Ruby", "name_sa": "Manik", "planet": "Sun", "color": "Deep Red", "metal": "Gold", "finger": "Ring finger", "day": "Sunday", "weight": "3-6 carats", "mantra": "Om Suryaya Namah", "benefits": "Confidence, leadership, vitality, authority and recovery from low self-esteem.", "caution": "Avoid if Sun is malefic in the birth chart; test-wear for 3 days first."},
    "Moon": {"name": "Pearl", "name_sa": "Moti", "planet": "Moon", "color": "White", "metal": "Silver", "finger": "Little finger", "day": "Monday", "weight": "4-7 carats", "mantra": "Om Chandraya Namah", "benefits": "Emotional balance, calm mind, relief from anxiety, better sleep and intuition.", "caution": "Keep it clean; remove during periods of heavy grief for re-energising."},
    "Mars": {"name": "Red Coral", "name_sa": "Moonga", "planet": "Mars", "color": "Vermilion Red", "metal": "Gold or Copper", "finger": "Ring finger", "day": "Tuesday", "weight": "6-9 carats", "mantra": "Om Angarakaya Namah", "benefits": "Courage, energy, protection from debts, victory over enemies and drive.", "caution": "Not advised together with Blue Sapphire or Diamond."},
    "Mercury": {"name": "Emerald", "name_sa": "Panna", "planet": "Mercury", "color": "Green", "metal": "Gold", "finger": "Little finger", "day": "Wednesday", "weight": "3-6 carats", "mantra": "Om Budhaya Namah", "benefits": "Sharp intellect, communication, business success, focus and clarity in studies.", "caution": "Avoid flawed/cracked stones; they can reverse the effect."},
    "Jupiter": {"name": "Yellow Sapphire", "name_sa": "Pukhraj", "planet": "Jupiter", "color": "Golden Yellow", "metal": "Gold", "finger": "Index finger", "day": "Thursday", "weight": "5-8 carats", "mantra": "Om Gurave Namah", "benefits": "Wisdom, wealth, marriage prospects, good fortune and spiritual growth.", "caution": "One of the safest stones; still test-wear before permanent wear."},
    "Venus": {"name": "Diamond", "name_sa": "Heera", "planet": "Venus", "color": "Clear/White", "metal": "Platinum or Silver", "finger": "Middle finger", "day": "Friday", "weight": "0.5-1 carat", "mantra": "Om Shukraya Namah", "benefits": "Love, luxury, artistic talent, charm, marital harmony and prosperity.", "caution": "Opaque white sapphire is a budget substitute; avoid black spots."},
    "Saturn": {"name": "Blue Sapphire", "name_sa": "Neelam", "planet": "Saturn", "color": "Deep Blue", "metal": "Silver or Panchdhatu", "finger": "Middle finger", "day": "Saturday", "weight": "5-7 carats", "mantra": "Om Shanaischaraya Namah", "benefits": "Fast results, career growth, discipline, protection and removal of obstacles.", "caution": "Most powerful stone - MUST be tested for 3 nights before permanent wear."},
    "Rahu": {"name": "Hessonite", "name_sa": "Gomed", "planet": "Rahu", "color": "Honey Brown", "metal": "Silver", "finger": "Middle finger", "day": "Saturday", "weight": "6-9 carats", "mantra": "Om Rahave Namah", "benefits": "Removes confusion, protects from hidden enemies, sudden gains and mental peace.", "caution": "Wear only during Rahu dasha/antardasha after consultation."},
    "Ketu": {"name": "Cat's Eye", "name_sa": "Lehsunia", "planet": "Ketu", "color": "Greyish Green", "metal": "Silver", "finger": "Middle finger", "day": "Saturday", "weight": "5-7 carats", "mantra": "Om Ketave Namah", "benefits": "Protection, spiritual insight, sudden wealth and relief from unknown fears.", "caution": "Effects are intense and sudden; wear cautiously."},
}


swe.set_sid_mode(swe.SIDM_LAHIRI)
_SID_FLAG = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
_PLANET_CODES = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
}


def _rashi_of(longitude: float):
    return RASHIS[int(longitude % 360 // 30)]


def compute_chart(birth_dt: datetime, lat: float, lon: float, tz_name: str = "Asia/Kolkata"):
    """Astronomically precise sidereal (Lahiri) Vedic chart.

    birth_dt: naive local datetime at the birth place.
    lat/lon: birth place coordinates. tz_name: IANA timezone of the place.
    """
    try:
        tz = pytz.timezone(tz_name)
    except Exception:
        tz = pytz.timezone("Asia/Kolkata")
    utc_dt = tz.localize(birth_dt).astimezone(pytz.utc)
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                    utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)

    ayanamsa = swe.get_ayanamsa_ut(jd)

    # Sidereal planetary longitudes
    positions = {}
    for name, code in _PLANET_CODES.items():
        positions[name] = swe.calc_ut(jd, code, _SID_FLAG)[0][0] % 360.0
    positions["Ketu"] = (positions["Rahu"] + 180.0) % 360.0

    moon_long = positions["Moon"]
    sun_long = positions["Sun"]

    # Western / tropical Sun sign (what most people casually call their "sign")
    trop_sun = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)[0][0] % 360.0
    western_sun = _rashi_of(trop_sun)

    # Ascendant (Lagna) from lat/lon + sidereal time
    ascmc = swe.houses_ex(jd, lat, lon, b"W", _SID_FLAG)[1]
    asc_long = ascmc[0] % 360.0

    moon_rashi = _rashi_of(moon_long)
    sun_rashi = _rashi_of(sun_long)
    asc_rashi = _rashi_of(asc_long)

    # Nakshatra + pada from sidereal moon
    nak_span = 360.0 / 27.0
    nak_index = int(moon_long // nak_span)
    within = moon_long - nak_index * nak_span
    pada = int(within // (nak_span / 4.0)) + 1

    planet_positions = {p: _rashi_of(lng)["sa"] for p, lng in positions.items()}
    planet_degrees = {p: round(lng % 30.0, 2) for p, lng in positions.items()}

    dasha = compute_vimshottari(birth_dt, nak_index, within, nak_span)

    return {
        "moon_sign": moon_rashi,
        "sun_sign": sun_rashi,
        "western_sun_sign": western_sun,
        "ascendant": asc_rashi,
        "nakshatra": NAKSHATRAS[nak_index],
        "pada": pada,
        "ruling_planet": moon_rashi["planet"],
        "ruling_planet_sa": moon_rashi["planet_sa"],
        "planet_positions": planet_positions,
        "planet_degrees": planet_degrees,
        "ayanamsa": round(ayanamsa, 4),
        "accuracy": "swiss_ephemeris_lahiri",
        "dasha": dasha["periods"],
        "current_dasha": dasha["current"],
    }


# Vimshottari Dasha: 120-year cycle. Nakshatra lords repeat every 9 nakshatras.
_DASHA_SEQ = [
    ("Ketu", 7), ("Venus", 20), ("Sun", 6), ("Moon", 10), ("Mars", 7),
    ("Rahu", 18), ("Jupiter", 16), ("Saturn", 19), ("Mercury", 17),
]
_DAYS_PER_YEAR = 365.2425


def compute_vimshottari(birth_dt: datetime, nak_index: int, within: float, nak_span: float):
    """Vimshottari Mahadasha timeline anchored to the Moon's nakshatra at birth."""
    from datetime import timedelta

    start_idx = nak_index % 9
    remaining_fraction = (nak_span - within) / nak_span

    periods = []
    cursor = birth_dt
    today = datetime.now()
    current = None
    for i in range(10):  # one full 120-yr cycle + balance
        lord, years = _DASHA_SEQ[(start_idx + i) % 9]
        span_years = years * remaining_fraction if i == 0 else float(years)
        end = cursor + timedelta(days=span_years * _DAYS_PER_YEAR)
        entry = {
            "planet": lord,
            "start": cursor.strftime("%Y-%m-%d"),
            "end": end.strftime("%Y-%m-%d"),
            "years": round(span_years, 2),
        }
        if cursor <= today < end:
            entry["is_current"] = True
            current = entry
        periods.append(entry)
        cursor = end
    return {"periods": periods, "current": current}


def recommend_gemstone(chart, problem_hint: str = ""):
    """Pick a gemstone based on the ruling planet of the moon-sign (Vedic rashi)."""
    planet = chart["ruling_planet"]
    gem = GEMSTONES.get(planet, GEMSTONES["Jupiter"]).copy()
    gem["for_rashi"] = chart["moon_sign"]["sa"]
    return gem

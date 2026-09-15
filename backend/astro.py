"""Vedic astrology calculation engine and reference data for Rashisense."""
from datetime import datetime, timezone
import math

# Sidereal ayanamsa (Lahiri approx for modern era)
AYANAMSA = 24.1

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


def _julian_day(dt: datetime) -> float:
    y, m = dt.year, dt.month
    d = dt.day + (dt.hour + dt.minute / 60.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    jd = math.floor(365.25 * (y + 4716)) + math.floor(30.6001 * (m + 1)) + d + b - 1524.5
    return jd


def _norm(deg: float) -> float:
    return deg % 360.0


def _sidereal(tropical_long: float) -> float:
    return _norm(tropical_long - AYANAMSA)


def compute_chart(birth_dt: datetime):
    """Deterministic simplified Vedic chart from a UTC-naive local birth datetime."""
    jd = _julian_day(birth_dt)
    d = jd - 2451545.0

    # Mean longitudes (tropical, degrees)
    moon_long = _norm(218.316 + 13.176396 * d)
    sun_long = _norm(280.460 + 0.9856474 * d)

    moon_sid = _sidereal(moon_long)
    sun_sid = _sidereal(sun_long)

    moon_index = int(moon_sid // 30)
    sun_index = int(sun_sid // 30)

    # Ascendant (Lagna): rough model advancing one sign every ~2 sidereal hours from sun sign
    hour_frac = birth_dt.hour + birth_dt.minute / 60.0
    asc_index = int((sun_index + math.floor(hour_frac / 2.0)) % 12)

    # Nakshatra + pada from sidereal moon
    nak_span = 360.0 / 27.0
    nak_index = int(moon_sid // nak_span)
    within = moon_sid - nak_index * nak_span
    pada = int(within // (nak_span / 4.0)) + 1

    moon_rashi = RASHIS[moon_index]
    sun_rashi = RASHIS[sun_index]
    asc_rashi = RASHIS[asc_index]

    # Approximate planetary sign placements (deterministic mean-motion model)
    planets = {}
    speeds = {"Mars": 0.524, "Mercury": 1.383, "Jupiter": 0.0831, "Venus": 1.602, "Saturn": 0.0334}
    epochs = {"Mars": 355.43, "Mercury": 252.25, "Jupiter": 34.35, "Venus": 181.98, "Saturn": 50.08}
    for p in speeds:
        lon = _sidereal(_norm(epochs[p] + speeds[p] * d))
        planets[p] = RASHIS[int(lon // 30)]["sa"]
    planets["Sun"] = sun_rashi["sa"]
    planets["Moon"] = moon_rashi["sa"]
    rahu_long = _sidereal(_norm(125.04 - 0.0529539 * d))
    planets["Rahu"] = RASHIS[int(rahu_long // 30)]["sa"]
    planets["Ketu"] = RASHIS[int(_norm(rahu_long + 180) // 30)]["sa"]

    return {
        "moon_sign": moon_rashi,
        "sun_sign": sun_rashi,
        "ascendant": asc_rashi,
        "nakshatra": NAKSHATRAS[nak_index],
        "pada": pada,
        "ruling_planet": moon_rashi["planet"],
        "ruling_planet_sa": moon_rashi["planet_sa"],
        "planet_positions": planets,
    }


def recommend_gemstone(chart, problem_hint: str = ""):
    """Pick a gemstone based on the ruling planet of the moon-sign (Vedic rashi)."""
    planet = chart["ruling_planet"]
    gem = GEMSTONES.get(planet, GEMSTONES["Jupiter"]).copy()
    gem["for_rashi"] = chart["moon_sign"]["sa"]
    return gem

"""Ashtakoot Guna Milan (Kundali Matching) - 36-point Vedic compatibility."""

# Nakshatra-indexed reference data (0..26 in standard order)
_YONI = ["Horse", "Elephant", "Goat", "Snake", "Snake", "Dog", "Cat", "Goat", "Cat",
         "Rat", "Rat", "Cow", "Buffalo", "Tiger", "Buffalo", "Tiger", "Deer", "Deer",
         "Dog", "Monkey", "Mongoose", "Monkey", "Lion", "Horse", "Lion", "Cow", "Elephant"]
_YONI_ENEMIES = {
    frozenset(["Cow", "Tiger"]), frozenset(["Horse", "Buffalo"]),
    frozenset(["Elephant", "Lion"]), frozenset(["Dog", "Deer"]),
    frozenset(["Snake", "Mongoose"]), frozenset(["Cat", "Rat"]),
    frozenset(["Monkey", "Goat"]),
}
_GANA = ["D", "M", "R", "M", "D", "M", "D", "D", "R", "R", "M", "M", "D", "R", "D",
         "R", "D", "R", "R", "M", "M", "D", "R", "R", "M", "M", "D"]  # Deva/Manushya/Rakshasa
_NADI = ["A", "M", "E", "E", "M", "A", "A", "M", "E", "E", "M", "A", "A", "E", "E",
         "E", "M", "A", "A", "M", "E", "E", "M", "A", "A", "M", "E"]  # Aadi/Madhya/Antya

# Rashi-indexed (0=Aries..11=Pisces)
_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars",
          "Jupiter", "Saturn", "Saturn", "Jupiter"]
_VARNA = [3, 2, 1, 4, 3, 2, 1, 4, 3, 2, 1, 4]  # Kshatriya3 Vaishya2 Shudra1 Brahmin4
_VASHYA = ["C", "C", "N", "J", "V", "N", "N", "K", "C", "J", "N", "J"]  # Chatushpada/Nara/Jalachar/Vanachar/Keeta

_FRIENDS = {
    "Sun": {"Moon", "Mars", "Jupiter"}, "Moon": {"Sun", "Mercury"},
    "Mars": {"Sun", "Moon", "Jupiter"}, "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"}, "Venus": {"Mercury", "Saturn"},
    "Saturn": {"Mercury", "Venus"},
}
_ENEMIES = {
    "Sun": {"Venus", "Saturn"}, "Moon": set(), "Mars": {"Mercury"},
    "Mercury": {"Moon"}, "Jupiter": {"Mercury", "Venus"},
    "Venus": {"Sun", "Moon"}, "Saturn": {"Sun", "Moon", "Mars"},
}


def _rel(a, b):
    if a == b or b in _FRIENDS.get(a, set()):
        return "friend"
    if b in _ENEMIES.get(a, set()):
        return "enemy"
    return "neutral"


def _varna(b, g):
    return 1 if _VARNA[b] >= _VARNA[g] else 0


def _vashya(b, g):
    vb, vg = _VASHYA[b], _VASHYA[g]
    if vb == vg:
        return 2
    pair = {vb, vg}
    if pair in ({"N", "C"}, {"C", "J"}):
        return 1
    if pair == {"V", "K"}:
        return 0
    return 0.5


def _tara(nb, ng):
    def good(a, b):
        rem = (((b - a) % 27) + 1) % 9
        rem = rem or 9
        return rem not in (3, 5, 7)
    return (1.5 if good(nb, ng) else 0) + (1.5 if good(ng, nb) else 0)


def _yoni(nb, ng):
    yb, yg = _YONI[nb], _YONI[ng]
    if yb == yg:
        return 4
    if frozenset([yb, yg]) in _YONI_ENEMIES:
        return 0
    return 2


def _graha_maitri(rb, rg):
    r1, r2 = _rel(_LORDS[rb], _LORDS[rg]), _rel(_LORDS[rg], _LORDS[rb])
    s = {"friend": 2, "neutral": 1, "enemy": 0}
    table = {(2, 2): 5, (2, 1): 4, (1, 2): 4, (1, 1): 3,
             (2, 0): 1, (0, 2): 1, (1, 0): 0.5, (0, 1): 0.5, (0, 0): 0}
    return table.get((s[r1], s[r2]), 0)


def _gana(nb, ng):
    gb, gg = _GANA[nb], _GANA[ng]
    if gb == gg:
        return 6
    pair = {gb, gg}
    if pair == {"D", "M"}:
        return 5
    if pair == {"D", "R"}:
        return 1
    return 0  # Manushya-Rakshasa


def _bhakoot(rb, rg):
    n = (rg - rb) % 12
    return 0 if n in (1, 11, 4, 8, 5, 7) else 7


def _nadi(nb, ng):
    return 0 if _NADI[nb] == _NADI[ng] else 8


def compute_guna_milan(nak_b, rashi_b, nak_g, rashi_g):
    kootas = [
        ("Varna", _varna(rashi_b, rashi_g), 1, "Spiritual & ego compatibility"),
        ("Vashya", _vashya(rashi_b, rashi_g), 2, "Mutual attraction & control"),
        ("Tara", _tara(nak_b, nak_g), 3, "Health & well-being (destiny)"),
        ("Yoni", _yoni(nak_b, nak_g), 4, "Physical & intimate compatibility"),
        ("Graha Maitri", _graha_maitri(rashi_b, rashi_g), 5, "Mental & intellectual bond"),
        ("Gana", _gana(nak_b, nak_g), 6, "Temperament & nature"),
        ("Bhakoot", _bhakoot(rashi_b, rashi_g), 7, "Love, family & prosperity"),
        ("Nadi", _nadi(nak_b, nak_g), 8, "Health & progeny (most important)"),
    ]
    total = sum(k[1] for k in kootas)
    if total >= 32:
        verdict = "Excellent match"
    elif total >= 24:
        verdict = "Very good match"
    elif total >= 18:
        verdict = "Acceptable match"
    else:
        verdict = "Not recommended"
    return {
        "kootas": [{"name": n, "obtained": round(float(o), 1), "max": m, "meaning": d} for n, o, m, d in kootas],
        "total": round(float(total), 1),
        "max_total": 36,
        "verdict": verdict,
    }

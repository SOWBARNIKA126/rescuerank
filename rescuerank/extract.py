"""Rule-based extraction of structured facts from a raw distress message.

This is the offline, no-API-key baseline. It understands English, Tanglish
(Tamil written in Latin letters) and a few Tamil-script keywords. The planned
LLM extractor (see README roadmap) should return the same `Extraction` object,
so the rest of the pipeline does not change.
"""
from __future__ import annotations

import re

from .gazetteer import PLACES
from .models import Extraction

ELDERLY = ["paati", "paatti", "thatha", "thaatha", "grandmother", "grandfather",
           "grandma", "grandpa", "elderly", "old", "aged", "vayasana", "பாட்டி", "தாத்தா", "முதியவர்"]
CHILD = ["kulandhai", "kolandhai", "kuzhandhai", "baby", "child", "children", "kids",
         "kid", "infant", "pasanga", "குழந்தை"]
PREGNANT = ["pregnant", "pregnancy", "garbam", "garbha", "கர்ப்பிணி"]
DISABLED = ["disabled", "wheelchair", "bedridden", "paralysed", "paralyzed"]

CONDITIONS = {
    "diabetic": ["sugar", "diabetic", "diabetes", "insulin", "சர்க்கரை"],
    "heart/BP": ["heart", "bp"],
    "oxygen/dialysis": ["oxygen", "dialysis", "ventilator"],
    "injured": ["injured", "bleeding", "fracture", "accident"],
}

WATER_WORDS = ["thanni", "water", "neer", "flood", "flooded", "தண்ணீர்", "வெள்ளம்"]
ENTRY_WORDS = ["vandhu", "vanthu", "entered", "inside", "ulla", "floor", "நுழைந்து",
               "வீட்டுக்குள்", "உள்ளே", "வந்து"]
RISING_WORDS = ["rising", "increasing", "ethuruthu", "athigam", "அதிகரிக்க"]

RESCUE_WORDS = ["rescue", "boat", "stuck", "trapped", "maatti", "maattikittom", "evacuate", "terrace"]
MEDICAL_WORDS = ["medicine", "ambulance", "doctor", "hospital", "marundhu"]
FOOD_WORDS = ["food", "saapadu", "sapadu", "biscuit", "milk", "paal", "hungry", "bread"]

FORWARD_PATTERNS = re.compile(
    r"\b(forwarded|fwd|share this|please share|viral|heard that|someone said)\b", re.I)

NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10}
PEOPLE_DIGITS = re.compile(r"\b(\d{1,3})\s*(?:perr|per|peru|people|persons|members|ppl|pesr)\b")
PEOPLE_WORDS = re.compile(
    r"\b(" + "|".join(NUM_WORDS) + r")\s+(?:person|people|persons|members)\b")
STREET = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(cross|main)\b(?:\s+(?:st|street|road|rd))?")


def _tokens(text: str) -> list:
    return re.findall(r"[a-z0-9]+|[\u0b80-\u0bff]+", text.lower())


def _has(tokens: list, words: list) -> bool:
    """Token starts with a keyword (so 'paatiku' matches 'paati')."""
    for t in tokens:
        for w in words:
            if t.startswith(w):
                return True
    return False


def _ordinal(n: int) -> str:
    if 10 <= n % 100 <= 20:
        return f"{n}th"
    return f"{n}" + {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")


def _find_place(text: str):
    best = None  # (alias_length, canonical_name)
    for name, (_, _, aliases) in PLACES.items():
        for a in aliases:
            if re.search(r"(?<![a-z])" + re.escape(a) + r"(?![a-z])", text):
                if best is None or len(a) > best[0]:
                    best = (len(a), name)
    return best[1] if best else None


def extract(text: str) -> Extraction:
    low = text.lower()
    toks = _tokens(text)
    ex = Extraction()

    ex.place = _find_place(low)
    if ex.place:
        ex.lat, ex.lon = PLACES[ex.place][0], PLACES[ex.place][1]

    m = STREET.search(low)
    if m:
        n, kind = int(m.group(1)), m.group(2)
        ex.street = f"{_ordinal(n)} {kind.capitalize()} St"
        ex.street_key = f"{n} {kind}"

    m = PEOPLE_DIGITS.search(low)
    if m:
        ex.people = int(m.group(1))
    else:
        m = PEOPLE_WORDS.search(low)
        if m:
            ex.people = NUM_WORDS[m.group(1)]

    if _has(toks, ELDERLY):
        ex.at_risk.append("elderly")
    if _has(toks, CHILD):
        ex.at_risk.append("child")
    if _has(toks, PREGNANT):
        ex.at_risk.append("pregnant")
        ex.conditions.append("pregnant")
    if _has(toks, DISABLED):
        ex.at_risk.append("disabled")
    for label, words in CONDITIONS.items():
        if _has(toks, words):
            ex.conditions.append(label)

    if _has(toks, WATER_WORDS):
        if _has(toks, ENTRY_WORDS):
            ex.water = "indoors"
        elif _has(toks, RISING_WORDS):
            ex.water = "rising"
        else:
            ex.water = "outside"

    if ex.water in ("indoors", "rising") or _has(toks, RESCUE_WORDS):
        ex.needs.append("rescue")
    if ex.conditions or _has(toks, MEDICAL_WORDS):
        ex.needs.append("medical")
    if _has(toks, FOOD_WORDS):
        ex.needs.append("food")

    ex.forwarded = bool(FORWARD_PATTERNS.search(text))
    return ex

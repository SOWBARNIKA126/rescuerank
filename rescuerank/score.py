"""Explainable urgency score, 0 to 100.

Every point has a reason. The weights below are EXAMPLE values chosen to
demonstrate the idea. They are not clinically or operationally validated;
a real deployment must tune them with disaster-management officers.
"""
from __future__ import annotations

from datetime import datetime

from .models import Case

BANDS = [(75, "CRITICAL"), (50, "HIGH"), (25, "MEDIUM"), (0, "LOW")]
LIFE_THREATENING = {"oxygen/dialysis", "injured"}


def _round(x: float) -> int:
    return int(x + 0.5)


def score_case(case: Case, now: datetime) -> Case:
    reasons = []

    if case.at_risk:
        reasons.append({"label": "Vulnerable person (" + ", ".join(case.at_risk) + ")", "points": 15})
    if case.conditions:
        severe = bool(LIFE_THREATENING & set(case.conditions))
        reasons.append({"label": "Medical condition (" + ", ".join(case.conditions) + ")",
                        "points": 25 if severe else 15})

    water_points = {"indoors": 25, "rising": 15, "outside": 10}
    if case.water:
        label = {"indoors": "Water inside the home", "rising": "Water rising nearby",
                 "outside": "Water around the area"}[case.water]
        reasons.append({"label": label, "points": water_points[case.water]})

    minutes = max(0, (now - case.first_reported).total_seconds() / 60)
    wait = min(25, _round(minutes * 0.5))
    if wait:
        reasons.append({"label": f"Waiting {int(minutes)} min", "points": wait})

    if case.people:
        reasons.append({"label": f"Group of {case.people}", "points": min(15, _round(2.5 * case.people))})

    total = min(100, sum(r["points"] for r in reasons))
    case.score = total
    case.reasons = reasons
    case.band = next(name for floor, name in BANDS if total >= floor)
    return case

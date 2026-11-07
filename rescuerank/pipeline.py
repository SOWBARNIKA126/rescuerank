"""Messages in, ranked cases out."""
from __future__ import annotations

from datetime import datetime
from typing import List

from .dedup import same_incident
from .extract import extract
from .models import Case, Extraction, Message
from .score import score_case

_WATER_RANK = {None: 0, "outside": 1, "rising": 2, "indoors": 3}


def _union(a: list, b: list) -> list:
    return a + [x for x in b if x not in a]


def trust_for(case: Case) -> float:
    """0 to 1. More independent senders = more trust; chain forwards = less."""
    t = 0.5 if case.place else 0.2
    t += min(0.3, 0.15 * (len(set(case.senders)) - 1))
    if case.forwarded_only:
        t -= 0.3
    return round(max(0.0, min(1.0, t)), 2)


def build_queue(messages: List[Message], now: datetime) -> List[Case]:
    ordered = sorted(messages, key=lambda m: m.received_at)
    parsed = [(m, extract(m.text)) for m in ordered]

    cases: List[Case] = []
    anchors: List[tuple] = []  # (message, extraction) the case was opened with

    for msg, ex in parsed:
        target = None
        for case, (a_msg, a_ex) in zip(cases, anchors):
            if same_incident(a_ex, a_msg, ex, msg):
                target = case
                break
        if target is None:
            cases.append(Case(
                id=f"case-{len(cases) + 1}", place=ex.place, street=ex.street,
                street_key=ex.street_key, lat=ex.lat, lon=ex.lon, people=ex.people,
                needs=list(ex.needs), at_risk=list(ex.at_risk), conditions=list(ex.conditions),
                water=ex.water, first_reported=msg.received_at, report_ids=[msg.id],
                senders=[msg.sender], forwarded_only=ex.forwarded))
            anchors.append((msg, ex))
        else:
            target.report_ids.append(msg.id)
            target.senders.append(msg.sender)
            target.people = max(target.people or 0, ex.people or 0) or None
            target.needs = _union(target.needs, ex.needs)
            target.at_risk = _union(target.at_risk, ex.at_risk)
            target.conditions = _union(target.conditions, ex.conditions)
            target.street = target.street or ex.street
            if _WATER_RANK[ex.water] > _WATER_RANK[target.water]:
                target.water = ex.water
            target.forwarded_only = target.forwarded_only and ex.forwarded

    for case in cases:
        case.trust = trust_for(case)
        case.needs_review = case.trust < 0.4
        score_case(case, now)

    cases.sort(key=lambda c: (-c.score, c.first_reported))
    return cases

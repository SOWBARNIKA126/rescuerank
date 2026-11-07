"""Merge repeat reports of the same incident.

Rule of thumb used here (simple and explainable on purpose):
  * same locality, AND
  * same street if both reports name one, otherwise similar wording, AND
  * reported within a time window.
The roadmap replaces the wording check with multilingual embeddings (LaBSE).
"""
from __future__ import annotations

import re

from .models import Extraction, Message

STOP = {"the", "a", "an", "is", "are", "we", "in", "on", "at", "to", "and", "of", "for",
        "please", "help", "la", "ku", "irukku", "irukkom", "my", "our", "near", "send"}


def content_tokens(text: str) -> set:
    toks = re.findall(r"[a-z0-9]+|[\u0b80-\u0bff]+", text.lower())
    return {t for t in toks if len(t) > 2 and t not in STOP}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def same_incident(ex_a: Extraction, msg_a: Message, ex_b: Extraction, msg_b: Message,
                  window_minutes: int = 90) -> bool:
    if not ex_a.place or ex_a.place != ex_b.place:
        return False
    gap = abs((msg_a.received_at - msg_b.received_at).total_seconds()) / 60
    if gap > window_minutes:
        return False
    if ex_a.street_key and ex_b.street_key:
        return ex_a.street_key == ex_b.street_key
    return jaccard(content_tokens(msg_a.text), content_tokens(msg_b.text)) >= 0.3

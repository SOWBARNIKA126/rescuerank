from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Message:
    id: str
    sender: str
    text: str
    received_at: datetime


@dataclass
class Extraction:
    """Structured facts pulled out of one raw message."""
    place: Optional[str] = None
    street: Optional[str] = None          # display form, e.g. "3rd Cross St"
    street_key: Optional[str] = None      # normalised, e.g. "3 cross"
    lat: Optional[float] = None
    lon: Optional[float] = None
    people: Optional[int] = None
    needs: list = field(default_factory=list)        # rescue / medical / food
    at_risk: list = field(default_factory=list)      # elderly / child / pregnant / disabled
    conditions: list = field(default_factory=list)   # diabetic / oxygen / injured ...
    water: Optional[str] = None                      # indoors / rising / outside
    forwarded: bool = False                          # looks like a chain forward


@dataclass
class Case:
    """One real-world incident = one or more merged reports."""
    id: str
    place: Optional[str]
    street: Optional[str]
    street_key: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    people: Optional[int]
    needs: list
    at_risk: list
    conditions: list
    water: Optional[str]
    first_reported: datetime
    report_ids: list
    senders: list
    forwarded_only: bool
    trust: float = 0.0
    needs_review: bool = False
    score: int = 0
    band: str = "LOW"
    reasons: list = field(default_factory=list)      # [{"label": str, "points": int}]

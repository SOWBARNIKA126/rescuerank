"""Minimal REST API.

    uvicorn rescuerank.api:app --reload

POST /messages   submit one raw message
GET  /queue      ranked cases with reasons
POST /reset      clear everything (demo use)
"""
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

from .extract import extract
from .models import Message
from .pipeline import build_queue

app = FastAPI(title="RescueRank", version="0.1.0",
              description="AI-assisted triage for disaster distress messages")
_STORE: List[Message] = []


class MessageIn(BaseModel):
    sender: str
    text: str
    received_at: Optional[datetime] = None


@app.get("/health")
def health():
    return {"status": "ok", "messages": len(_STORE)}


@app.post("/messages")
def add_message(body: MessageIn):
    msg = Message(id=f"m{len(_STORE) + 1:03d}", sender=body.sender, text=body.text,
                  received_at=body.received_at or datetime.now())
    _STORE.append(msg)
    return {"id": msg.id, "extraction": asdict(extract(msg.text))}


@app.get("/queue")
def queue(now: Optional[datetime] = None):
    cases = build_queue(_STORE, now or datetime.now())
    out = []
    for c in cases:
        d = asdict(c)
        d["first_reported"] = c.first_reported.isoformat()
        out.append(d)
    return {"count": len(out), "cases": out}


@app.post("/reset")
def reset():
    _STORE.clear()
    return {"status": "cleared"}

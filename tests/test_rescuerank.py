from datetime import datetime
from pathlib import Path

from fastapi.testclient import TestClient

from rescuerank.api import app
from rescuerank.extract import extract
from rescuerank.io import load_messages
from rescuerank.pipeline import build_queue

DATA = Path(__file__).resolve().parent.parent / "data" / "sample_messages.json"
TANGLISH = ("Velachery 3rd cross st, ground floor la thanni vandhuduchu. "
            "4 perr irukkom, paatiku sugar irukku. Help pannunga!")


def queue():
    msgs, now = load_messages(DATA)
    return build_queue(msgs, now)


def test_extracts_tanglish_message():
    ex = extract(TANGLISH)
    assert ex.place == "Velachery"
    assert ex.street == "3rd Cross St"
    assert ex.people == 4
    assert ex.water == "indoors"
    assert "elderly" in ex.at_risk
    assert "diabetic" in ex.conditions
    assert {"rescue", "medical"} <= set(ex.needs)


def test_understands_tamil_script():
    ex = extract("வேளச்சேரி 2வது தெருவில் தண்ணீர் வீட்டுக்குள் வந்துவிட்டது. பாட்டி இருக்காங்க")
    assert ex.place == "Velachery"
    assert ex.water == "indoors"
    assert "elderly" in ex.at_risk


def test_duplicates_are_merged():
    cases = queue()
    velachery = [c for c in cases if c.street_key == "3 cross"]
    assert len(velachery) == 1
    assert len(velachery[0].report_ids) == 3


def test_top_case_matches_slide_example():
    top = queue()[0]
    assert top.place == "Velachery"
    assert top.score == 88
    assert top.band == "CRITICAL"
    assert sum(r["points"] for r in top.reasons) == 88


def test_chain_forward_is_flagged_for_review():
    flagged = [c for c in queue() if c.needs_review]
    assert any(c.place == "Besant Nagar" for c in flagged)


def test_ranking_is_sorted_by_score():
    scores = [c.score for c in queue()]
    assert scores == sorted(scores, reverse=True)


def test_api_roundtrip():
    client = TestClient(app)
    client.post("/reset")
    r = client.post("/messages", json={"sender": "t1", "text": TANGLISH,
                                       "received_at": "2026-11-06T09:14:00"})
    assert r.status_code == 200
    assert r.json()["extraction"]["place"] == "Velachery"
    q = client.get("/queue", params={"now": "2026-11-06T10:00:00"}).json()
    assert q["count"] == 1
    assert q["cases"][0]["score"] == 88

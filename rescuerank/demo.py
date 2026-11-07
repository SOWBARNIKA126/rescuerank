"""Run the full pipeline on the sample messages and print the ranked queue.

    python -m rescuerank.demo
"""
from __future__ import annotations

import argparse
from pathlib import Path

from .io import load_messages
from .pipeline import build_queue

DEFAULT = Path(__file__).resolve().parent.parent / "data" / "sample_messages.json"


def label(case) -> str:
    place = case.place or "Unknown place"
    return f"{place}, {case.street}" if case.street else place


def main() -> None:
    ap = argparse.ArgumentParser(description="RescueRank demo")
    ap.add_argument("--data", default=str(DEFAULT), help="path to a messages JSON file")
    args = ap.parse_args()

    msgs, now = load_messages(args.data)
    cases = build_queue(msgs, now)

    print(f"\nRescueRank: {len(msgs)} raw messages -> {len(cases)} cases\n")
    print(f"{'#':<3}{'SCORE':<7}{'BAND':<10}{'PLACE':<30}{'REPORTS':<9}FLAGS")
    print("-" * 72)
    for i, c in enumerate(cases, 1):
        flag = "NEEDS REVIEW (low trust)" if c.needs_review else ""
        print(f"{i:<3}{c.score:<7}{c.band:<10}{label(c):<30}{len(c.report_ids):<9}{flag}")

    top = cases[0]
    print(f"\nWhy is '{label(top)}' ranked #1?  (score {top.score}/100, {top.band})")
    for r in top.reasons:
        print(f"  +{r['points']:<3}{r['label']}")
    print(f"  merged {len(top.report_ids)} reports from {len(set(top.senders))} senders: {', '.join(top.report_ids)}\n")


if __name__ == "__main__":
    main()

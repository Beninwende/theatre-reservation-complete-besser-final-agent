#!/usr/bin/env python3
"""Offline smoke tests (no OpenAI key required)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_store_booking_and_conflict() -> None:
    os.environ["THEATRE_PERSIST"] = "1"
    os.environ["THEATRE_DB"] = str(ROOT / "data" / "_smoke_test.db")
    db = Path(os.environ["THEATRE_DB"])
    if db.exists():
        db.unlink()

    from reservation_store import build_store

    store = build_store(ROOT)
    shows = store.list_shows()
    assert len(shows) >= 3
    hamlet = next(s for s in shows if s["id"] == "hamlet")
    cap = hamlet["capacity"]

    rec = store.book("hamlet", 2, "Smoke Test", "front", "none")
    assert rec.confirmation_code.startswith("BK-")
    assert store.remaining("hamlet") == cap - 2

    try:
        store.book("hamlet", cap, "Too Many", "rear", "none")
        raise AssertionError("expected NOT_ENOUGH_SEATS")
    except ValueError as e:
        assert str(e) == "NOT_ENOUGH_SEATS"

    db.unlink(missing_ok=True)
    print("OK reservation_store")


def test_wme_json() -> None:
    data = json.loads((ROOT / "wme-theatre-reservation-bot.json").read_text(encoding="utf-8"))
    p = data["project"]
    assert p["diagrams"]["ClassDiagram"][0]["model"]["elements"]
    agent = p["diagrams"]["AgentDiagram"][0]["model"]
    names = {el["name"] for el in agent["elements"].values() if el.get("type") == "AgentState"}
    for required in ("hub", "confirm_do", "faq_llm", "seat_count"):
        assert required in names, f"missing agent state {required}"
    print("OK wme-theatre-reservation-bot.json")


def test_api_import() -> None:
    from backend.main_api import app  # noqa: F401

    assert app.title == "Theatre Reservation API"
    print("OK backend.main_api")


if __name__ == "__main__":
    test_store_booking_and_conflict()
    test_wme_json()
    test_api_import()
    print("All smoke tests passed.")

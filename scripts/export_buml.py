#!/usr/bin/env python3
"""Export WME project payload to buml/ (BESSER agent repo layout)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WME = ROOT / "wme-theatre-reservation-bot.json"
BUML = ROOT / "buml"


def main() -> None:
    data = json.loads(WME.read_text(encoding="utf-8"))
    project = data["project"]
    BUML.mkdir(exist_ok=True)
    (BUML / "diagrams.json").write_text(
        json.dumps(project, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    agent_model = BUML / "agent_model_theatre_reservation_agent.py"
    agent_model.write_text(
        '''"""
B-UML traceability stub — agent implementation lives in theatre_bot.py.

Regenerate diagrams.json:
  python scripts/build_wme_export.py && python scripts/export_buml.py
"""
AGENT_NAME = "theatre_reservation_bot"
IMPLEMENTATION = "theatre_bot.py"

STATES = [
    "initial_state", "profile_pick", "set_profile_standard", "set_profile_access",
    "hub", "cancel_reset", "show_select", "ready_hamlet", "ready_jazz", "ready_comedy",
    "seat_count", "seat_set_1", "seat_set_2", "seat_set_3", "seat_set_4",
    "zone_pick", "name_collect_front", "name_collect_rear", "a11y_ask",
    "a11y_done_none", "a11y_done_wheel", "a11y_done_hear", "confirm_do", "faq_llm",
]
''',
        encoding="utf-8",
    )
    print(f"Wrote {BUML / 'diagrams.json'}")
    print(f"Wrote {agent_model}")


if __name__ == "__main__":
    main()

"""
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

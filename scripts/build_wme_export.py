#!/usr/bin/env python3
"""Build wme-theatre-reservation-bot.json (domain + agent + object + GUI + user diagrams)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "wme-theatre-reservation-bot.json"


def _uid(prefix: str, n: int) -> str:
    return f"{prefix}{n:04d}-0000-4000-8000-000000000{n:03d}"


# ---------------------------------------------------------------------------
# Class diagram helpers
# ---------------------------------------------------------------------------
def _class_diagram_domain() -> dict[str, Any]:
    e: dict[str, Any] = {}
    r: dict[str, Any] = {}

    def cls(cid: int, name: str, x: int, y: int, w: int, h: int, attr_ids: list[int]) -> None:
        e[_uid("a", cid)] = {
            "id": _uid("a", cid),
            "name": name,
            "type": "Class",
            "owner": None,
            "bounds": {"x": x, "y": y, "width": w, "height": h},
            "attributes": [_uid("b", i) for i in attr_ids],
            "methods": [],
        }

    def attr(aid: int, owner: int, label: str, y_off: float) -> None:
        oid = _uid("a", owner)
        e[_uid("b", aid)] = {
            "id": _uid("b", aid),
            "name": label,
            "type": "ClassAttribute",
            "owner": oid,
            "bounds": {
                "x": e[oid]["bounds"]["x"] + 0.5,
                "y": e[oid]["bounds"]["y"] + y_off,
                "width": e[oid]["bounds"]["width"] - 1,
                "height": 30,
            },
        }

    cls(1, "Theatre", 40, 40, 200, 100, [101])
    attr(101, 1, "+ name: str", 55)
    cls(2, "Show", 300, 40, 240, 190, [201, 202, 203, 204, 205, 206])
    attr(201, 2, "+ id: str", 55)
    attr(202, 2, "+ title: str", 85)
    attr(203, 2, "+ datetime: str", 115)
    attr(204, 2, "+ price_eur: int", 145)
    attr(205, 2, "+ capacity: int", 175)
    attr(206, 2, "+ pmr_entrance: str", 205)
    cls(3, "Reservation", 620, 40, 260, 160, [301, 302, 303, 304, 305])
    attr(301, 3, "+ confirmation_code: str", 55)
    attr(302, 3, "+ customer_name: str", 85)
    attr(303, 3, "+ seats: int", 115)
    attr(304, 3, "+ zone: str", 145)
    attr(305, 3, "+ accessibility: str", 175)
    cls(4, "StandardSpectator", 40, 280, 280, 100, [401])
    attr(401, 4, "+ boxOfficeStyle: short", 55)
    cls(5, "AccessibilitySpectator", 380, 260, 300, 130, [501, 502])
    attr(501, 5, "+ guidance: detailed", 55)
    attr(502, 5, "+ boxOfficeTone: ACCESS", 85)

    def assoc(rid: int, src: int, tgt: int, label: str, mult_s: str, mult_t: str) -> None:
        r[_uid("r", rid)] = {
            "id": _uid("r", rid),
            "name": label,
            "type": "ClassBidirectional",
            "owner": None,
            "bounds": {"x": 240, "y": 120, "width": 60, "height": 40},
            "path": [{"x": 0, "y": 20}, {"x": 60, "y": 20}],
            "source": {
                "direction": "Right",
                "element": _uid("a", src),
                "multiplicity": mult_s,
                "role": "",
                "bounds": {"x": 0, "y": 0, "width": 0, "height": 0},
            },
            "target": {
                "direction": "Left",
                "element": _uid("a", tgt),
                "multiplicity": mult_t,
                "role": "",
                "bounds": {"x": 0, "y": 0, "width": 0, "height": 0},
            },
            "isManuallyLayouted": False,
        }

    assoc(1, 1, 2, "programme", "1", "1..*")
    assoc(2, 2, 3, "bookings", "1", "0..*")
    assoc(3, 4, 3, "places", "1", "0..*")
    assoc(4, 5, 3, "places", "1", "0..*")

    return {
        "version": "3.0.0",
        "type": "ClassDiagram",
        "size": {"width": 1400, "height": 740},
        "interactive": {"elements": {}, "relationships": {}},
        "elements": e,
        "relationships": r,
        "assessments": {},
    }


def _object_diagram_example() -> dict[str, Any]:
    e = {
        _uid("o", 1): {
            "id": _uid("o", 1),
            "name": "hamletShow:Show",
            "type": "ObjectName",
            "owner": None,
            "bounds": {"x": 120, "y": 100, "width": 280, "height": 130},
            "underline": True,
            "attributes": [_uid("o", 2), _uid("o", 3)],
            "methods": [],
        },
        _uid("o", 2): {
            "id": _uid("o", 2),
            "name": "title = Hamlet",
            "type": "ObjectAttribute",
            "owner": _uid("o", 1),
            "bounds": {"x": 120.5, "y": 145.5, "width": 279, "height": 30},
        },
        _uid("o", 3): {
            "id": _uid("o", 3),
            "name": "capacity = 80",
            "type": "ObjectAttribute",
            "owner": _uid("o", 1),
            "bounds": {"x": 120.5, "y": 175.5, "width": 279, "height": 30},
        },
        _uid("o", 4): {
            "id": _uid("o", 4),
            "name": "res1:Reservation",
            "type": "ObjectName",
            "owner": None,
            "bounds": {"x": 520, "y": 120, "width": 300, "height": 100},
            "underline": True,
            "attributes": [_uid("o", 5)],
            "methods": [],
        },
        _uid("o", 5): {
            "id": _uid("o", 5),
            "name": "confirmation_code = BK-00001",
            "type": "ObjectAttribute",
            "owner": _uid("o", 4),
            "bounds": {"x": 520.5, "y": 165.5, "width": 299, "height": 30},
        },
    }
    return {
        "version": "3.0.0",
        "type": "ObjectDiagram",
        "size": {"width": 1400, "height": 740},
        "interactive": {"elements": {}, "relationships": {}},
        "elements": e,
        "relationships": {},
        "assessments": {},
    }


def _agent_diagram() -> dict[str, Any]:
    """Full agent model aligned with theatre_bot.py / docs/STATE_MAP.md."""
    e: dict[str, Any] = {}
    rel: dict[str, Any] = {}
    tid = 0

    def nid() -> str:
        nonlocal tid
        tid += 1
        return f"ag{tid:04d}-0000-4000-8000-00000000{tid:04d}"

    def add_state(name: str, x: int, y: int, bodies: list[str]) -> str:
        sid = nid()
        body_ids = []
        by = y + 45
        for i, text in enumerate(bodies):
            bid = nid()
            body_ids.append(bid)
            e[bid] = {
                "id": bid,
                "name": text[:120],
                "type": "AgentStateBody",
                "owner": sid,
                "bounds": {"x": x + 0.5, "y": by + i * 30, "width": 219, "height": 30},
                "replyType": "text",
            }
        h = 40 + 30 * max(1, len(bodies))
        e[sid] = {
            "id": sid,
            "name": name,
            "type": "AgentState",
            "owner": None,
            "bounds": {"x": x, "y": y, "width": 220, "height": h},
            "bodies": body_ids,
            "fallbackBodies": [],
        }
        return sid

    def add_intent(name: str, x: int, y: int, samples: list[str], desc: str) -> str:
        iid = nid()
        bodies = []
        for j, s in enumerate(samples):
            bid = nid()
            bodies.append(bid)
            e[bid] = {
                "id": bid,
                "name": s,
                "type": "AgentIntentBody",
                "owner": iid,
                "bounds": {"x": x + 0.5, "y": y + 45 + j * 30, "width": 229, "height": 30},
            }
        e[iid] = {
            "id": iid,
            "name": name,
            "type": "AgentIntent",
            "owner": None,
            "bounds": {"x": x, "y": y, "width": 240, "height": 40 + 30 * len(samples)},
            "bodies": bodies,
            "intent_description": desc,
        }
        return iid

    def trans(src: str, tgt: str, condition: str, value: str = "", is_init: bool = False) -> None:
        rid = nid()
        rel[rid] = {
            "id": rid,
            "name": "",
            "type": "AgentStateTransitionInit" if is_init else "AgentStateTransition",
            "owner": None,
            "bounds": {"x": 0, "y": 0, "width": 80, "height": 1},
            "path": [{"x": 0, "y": 0}, {"x": 80, "y": 0}],
            "source": {"direction": "Right", "element": src},
            "target": {"direction": "Left", "element": tgt},
            "isManuallyLayouted": False,
        }
        if not is_init:
            rel[rid]["condition"] = condition
            if value:
                rel[rid]["conditionValue"] = value

    init_node = nid()
    e[init_node] = {
        "id": init_node,
        "name": "",
        "type": "StateInitialNode",
        "owner": None,
        "bounds": {"x": -1200, "y": 200, "width": 45, "height": 45},
    }

    # Layout: columns x= -1100 .. 900, rows stepped by 120
    s: dict[str, str] = {}
    s["initial_state"] = add_state("initial_state", -1100, 200, [])
    s["profile_pick"] = add_state("profile_pick", -900, 200, ["Pick STANDARD or ACCESS"])
    s["set_profile_standard"] = add_state("set_profile_standard", -900, 360, ["Store standard profile"])
    s["set_profile_access"] = add_state("set_profile_access", -700, 360, ["Store access profile"])
    s["hub"] = add_state("hub", -500, 200, ["BOOK | FAQ | CANCEL", "Dynamic shows menu"])
    s["cancel_reset"] = add_state("cancel_reset", -500, 400, ["Clear booking draft"])
    s["faq_llm"] = add_state("faq_llm", -300, 400, ["LLM FAQ — profile-aware tone"])
    s["show_select"] = add_state("show_select", -100, 80, ["Hamlet / Jazz / Comedy"])
    s["ready_hamlet"] = add_state("ready_hamlet", 120, 0, ["show_id = hamlet"])
    s["ready_jazz"] = add_state("ready_jazz", 120, 120, ["show_id = jazz_night"])
    s["ready_comedy"] = add_state("ready_comedy", 120, 240, ["show_id = comedy_club"])
    s["seat_count"] = add_state("seat_count", 360, 120, ["Wait seats 1–4"])
    for i in range(1, 5):
        s[f"seat_set_{i}"] = add_state(f"seat_set_{i}", 580, 40 + (i - 1) * 90, [f"seats = {i}"])
    s["zone_pick"] = add_state("zone_pick", 800, 120, ["FRONT or REAR"])
    s["name_collect_front"] = add_state("name_collect_front", 1020, 40, ["NAME: … (front zone)"])
    s["name_collect_rear"] = add_state("name_collect_rear", 1020, 200, ["NAME: … (rear zone)"])
    s["a11y_ask"] = add_state("a11y_ask", 1240, 120, ["NONE | WHEELCHAIR | HEARING"])
    s["a11y_done_none"] = add_state("a11y_done_none", 1460, 0, ["accessibility = none"])
    s["a11y_done_wheel"] = add_state("a11y_done_wheel", 1460, 120, ["wheelchair"])
    s["a11y_done_hear"] = add_state("a11y_done_hear", 1460, 240, ["hearing loop"])
    s["confirm_do"] = add_state(
        "confirm_do",
        1680,
        120,
        ["ReservationStore.book()", "NOT_ENOUGH_SEATS", "confirmation code"],
    )

    # Intents (palette above diagram)
    iy = -280
    intents = [
        ("profile_standard", -1100, iy, ["STANDARD"], "Standard profile"),
        ("profile_access", -900, iy, ["ACCESS"], "Accessibility profile"),
        ("start_booking", -500, iy, ["BOOK"], "Start booking"),
        ("ask_faq", -300, iy, ["FAQ", "prices?"], "FAQ question"),
        ("cancel_booking", -100, iy, ["CANCEL"], "Cancel draft"),
        ("pick_hamlet", 0, iy, ["Hamlet"], "Pick Hamlet"),
        ("pick_jazz", 200, iy, ["Jazz"], "Pick Jazz Night"),
        ("pick_comedy", 400, iy, ["Comedy"], "Pick Comedy"),
        ("seats_1", 600, iy, ["1"], "One seat"),
        ("seats_2", 720, iy, ["2", "two seats"], "Two seats"),
        ("seats_3", 880, iy, ["3"], "Three seats"),
        ("seats_4", 1000, iy, ["4"], "Four seats"),
        ("zone_front", 1200, iy, ["FRONT"], "Front zone"),
        ("zone_rear", 1360, iy, ["REAR"], "Rear zone"),
        ("name_line", 1520, iy, ["NAME:"], "Customer name line"),
        ("a11y_none", 1680, iy, ["NONE"], "No accessibility"),
        ("a11y_wheelchair", 1840, iy, ["WHEELCHAIR"], "Wheelchair"),
        ("a11y_hearing", 2000, iy, ["HEARING"], "Hearing loop"),
    ]
    for spec in intents:
        add_intent(*spec)

    trans(init_node, s["initial_state"], "init", is_init=True)
    trans(s["initial_state"], s["profile_pick"], "auto")
    trans(s["profile_pick"], s["set_profile_standard"], "when_intent_matched", "profile_standard")
    trans(s["profile_pick"], s["set_profile_access"], "when_intent_matched", "profile_access")
    trans(s["set_profile_standard"], s["hub"], "auto")
    trans(s["set_profile_access"], s["hub"], "auto")
    trans(s["hub"], s["show_select"], "when_intent_matched", "start_booking")
    trans(s["hub"], s["faq_llm"], "when_intent_matched", "ask_faq")
    trans(s["hub"], s["cancel_reset"], "when_intent_matched", "cancel_booking")
    trans(s["cancel_reset"], s["hub"], "auto")
    trans(s["show_select"], s["ready_hamlet"], "when_intent_matched", "pick_hamlet")
    trans(s["show_select"], s["ready_jazz"], "when_intent_matched", "pick_jazz")
    trans(s["show_select"], s["ready_comedy"], "when_intent_matched", "pick_comedy")
    for show in ("ready_hamlet", "ready_jazz", "ready_comedy"):
        trans(s[show], s["seat_count"], "auto")
    trans(s["seat_count"], s["seat_set_1"], "when_intent_matched", "seats_1")
    trans(s["seat_count"], s["seat_set_2"], "when_intent_matched", "seats_2")
    trans(s["seat_count"], s["seat_set_3"], "when_intent_matched", "seats_3")
    trans(s["seat_count"], s["seat_set_4"], "when_intent_matched", "seats_4")
    for i in range(1, 5):
        trans(s[f"seat_set_{i}"], s["zone_pick"], "auto")
    trans(s["zone_pick"], s["name_collect_front"], "when_intent_matched", "zone_front")
    trans(s["zone_pick"], s["name_collect_rear"], "when_intent_matched", "zone_rear")
    trans(s["name_collect_front"], s["a11y_ask"], "when_intent_matched", "name_line")
    trans(s["name_collect_rear"], s["a11y_ask"], "when_intent_matched", "name_line")
    trans(s["a11y_ask"], s["a11y_done_none"], "when_intent_matched", "a11y_none")
    trans(s["a11y_ask"], s["a11y_done_wheel"], "when_intent_matched", "a11y_wheelchair")
    trans(s["a11y_ask"], s["a11y_done_hear"], "when_intent_matched", "a11y_hearing")
    for done in ("a11y_done_none", "a11y_done_wheel", "a11y_done_hear"):
        trans(s[done], s["confirm_do"], "auto")
    trans(s["confirm_do"], s["hub"], "auto")
    trans(s["faq_llm"], s["hub"], "auto")

    return {
        "version": "3.0.0",
        "type": "AgentDiagram",
        "size": {"width": 2400, "height": 720},
        "interactive": {"elements": {}, "relationships": {}},
        "elements": e,
        "relationships": rel,
        "assessments": {},
    }


def _gui_model() -> dict[str, Any]:
    return {
        "pages": [
            {
                "name": "Shows",
                "frames": [
                    {
                        "component": {
                            "type": "wrapper",
                            "stylable": ["background", "background-color"],
                            "attributes": {"id": "theatre-root"},
                            "components": [
                                {
                                    "tagName": "section",
                                    "attributes": {"id": "shows-page"},
                                    "components": [
                                        {
                                            "type": "text",
                                            "tagName": "h1",
                                            "attributes": {"id": "shows-title"},
                                            "components": [
                                                {"type": "textnode", "content": "Theatre — Shows"}
                                            ],
                                        },
                                        {
                                            "type": "text",
                                            "tagName": "p",
                                            "attributes": {"id": "shows-hint"},
                                            "components": [
                                                {
                                                    "type": "textnode",
                                                    "content": "Table bound to Show (class diagram). "
                                                    "Use Generate → Web Application or the bundled webapp/.",
                                                }
                                            ],
                                        },
                                        {
                                            "type": "text",
                                            "tagName": "p",
                                            "attributes": {"id": "agent-hint"},
                                            "components": [
                                                {
                                                    "type": "textnode",
                                                    "content": "Chatbot: theatre reservation agent (Agent diagram). "
                                                    "Run python theatre_bot.py or Docker agent service.",
                                                }
                                            ],
                                        },
                                    ],
                                }
                            ],
                            "head": {"type": "head"},
                            "docEl": {"tagName": "html"},
                        }
                    }
                ],
            },
            {
                "name": "Reservations",
                "frames": [
                    {
                        "component": {
                            "type": "wrapper",
                            "components": [
                                {
                                    "type": "text",
                                    "tagName": "h1",
                                    "components": [
                                        {"type": "textnode", "content": "Reservations"}
                                    ],
                                },
                                {
                                    "type": "text",
                                    "tagName": "p",
                                    "components": [
                                        {
                                            "type": "textnode",
                                            "content": "Lists bookings from REST API GET /reservations",
                                        }
                                    ],
                                },
                            ],
                            "head": {"type": "head"},
                            "docEl": {"tagName": "html"},
                        }
                    }
                ],
            },
        ],
        "styles": [],
        "assets": [],
        "symbols": [],
        "version": "0.21.13",
    }


def _user_diagrams() -> list[dict[str, Any]]:
    """Preserve Lab 7-style user profile tabs from existing export."""
    path = OUT
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        tabs = data.get("project", {}).get("diagrams", {}).get("UserDiagram")
        if tabs:
            return tabs
    return []


def build_project() -> dict[str, Any]:
    user_tabs = _user_diagrams()
    if not user_tabs:
        user_tabs = [
            {
                "id": "user_diagram_standard_spectator",
                "title": "Standard spectator",
                "lastUpdate": "2026-06-04T12:00:00.000Z",
                "model": {
                    "version": "3.0.0",
                    "type": "UserDiagram",
                    "size": {"width": 1400, "height": 740},
                    "interactive": {"elements": {}, "relationships": {}},
                    "elements": {
                        "c0010000-0000-4000-8000-000000000001": {
                            "id": "c0010000-0000-4000-8000-000000000001",
                            "name": "Standard spectator",
                            "type": "UserModelName",
                            "owner": None,
                            "bounds": {"x": 120, "y": 120, "width": 320, "height": 100},
                            "underline": True,
                            "italic": False,
                            "stereotype": None,
                            "attributes": ["c0010000-0000-4000-8000-000000000002"],
                            "methods": [],
                        },
                        "c0010000-0000-4000-8000-000000000002": {
                            "id": "c0010000-0000-4000-8000-000000000002",
                            "name": "Prefers short factual answers at the box office.",
                            "type": "UserModelAttribute",
                            "owner": "c0010000-0000-4000-8000-000000000001",
                            "bounds": {"x": 120.5, "y": 165.5, "width": 319, "height": 30},
                            "attributeOperator": "==",
                        },
                    },
                    "relationships": {},
                    "assessments": {},
                },
            }
        ]

    return {
        "project": {
            "id": "project_theatre_reservation_final",
            "type": "Project",
            "schemaVersion": 3,
            "name": "Theatre reservation (complete BESSER final)",
            "description": "Domain model, agent, user profiles, GUI; code in theatre_bot.py + webapp/",
            "owner": "BESSER Education",
            "createdAt": "2026-06-04T12:00:00.000Z",
            "currentDiagramType": "ClassDiagram",
            "currentDiagramIndices": {
                "ClassDiagram": 0,
                "ObjectDiagram": 0,
                "StateMachineDiagram": 0,
                "AgentDiagram": 0,
                "UserDiagram": 0,
                "GUINoCodeDiagram": 0,
                "QuantumCircuitDiagram": 0,
            },
            "diagrams": {
                "ClassDiagram": [
                    {
                        "id": "theatre_domain_class",
                        "title": "Theatre domain",
                        "lastUpdate": "2026-06-04T12:00:00.000Z",
                        "model": _class_diagram_domain(),
                    }
                ],
                "ObjectDiagram": [
                    {
                        "id": "theatre_object_example",
                        "title": "Example booking",
                        "lastUpdate": "2026-06-04T12:00:00.000Z",
                        "model": _object_diagram_example(),
                    }
                ],
                "StateMachineDiagram": [
                    {
                        "id": "empty_sm",
                        "title": "State Machine (optional)",
                        "lastUpdate": "2026-06-04T12:00:00.000Z",
                        "model": {
                            "version": "3.0.0",
                            "type": "StateMachineDiagram",
                            "size": {"width": 1400, "height": 740},
                            "elements": {},
                            "relationships": {},
                            "interactive": {"elements": {}, "relationships": {}},
                            "assessments": {},
                        },
                    }
                ],
                "AgentDiagram": [
                    {
                        "id": "theatre_agent",
                        "title": "Theatre reservation agent",
                        "lastUpdate": "2026-06-04T12:00:00.000Z",
                        "model": _agent_diagram(),
                    }
                ],
                "UserDiagram": user_tabs,
                "GUINoCodeDiagram": [
                    {
                        "id": "theatre_gui",
                        "title": "Theatre web GUI",
                        "lastUpdate": "2026-06-04T12:00:00.000Z",
                        "model": _gui_model(),
                    }
                ],
                "QuantumCircuitDiagram": [
                    {
                        "id": "qc_empty",
                        "title": "Quantum Circuit",
                        "lastUpdate": "2026-06-04T12:00:00.000Z",
                        "model": {
                            "cols": [],
                            "gates": [],
                            "gateMetadata": {},
                            "initialStates": [],
                            "version": "1.0.0",
                        },
                    }
                ],
            },
            "settings": {
                "defaultDiagramType": "ClassDiagram",
                "autoSave": True,
                "collaborationEnabled": False,
            },
        },
        "exportedAt": "2026-06-04T12:00:00.000Z",
        "version": "2.0.0",
    }


def main() -> None:
    payload = build_project()
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

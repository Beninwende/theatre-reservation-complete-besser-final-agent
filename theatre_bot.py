"""
Theatre reservation chatbot — final BESSER education project.

Flow: profile (STANDARD / ACCESS) → hub → BOOK → pick show → seats (1–4)
→ zone (front / rear) → NAME: … → accessibility → confirm (in-memory store).

Run from this directory:
  python theatre_bot.py

Optional shared bookings DB (same as API):
  export THEATRE_PERSIST=1

Requires: pip install 'besser-agentic-framework[all]' PyYAML
Set OPENAI_API_KEY or edit config.yaml.
"""
import logging
import os
from dataclasses import dataclass
from pathlib import Path

import yaml
from baf.core.agent import Agent
from baf.core.session import Session
from baf.exceptions.logger import logger
from baf.nlp import OPENAI_API_KEY
from baf.nlp.intent_classifier.intent_classifier_configuration import LLMIntentClassifierConfiguration
from baf.nlp.llm.llm_openai_api import LLMOpenAI

from reservation_store import ReservationStore, build_store, load_shows_yaml

_BASE = Path(__file__).resolve().parent
_CONFIG = None

logger.setLevel(logging.INFO)


def _load_config() -> dict:
    global _CONFIG
    if _CONFIG is None:
        with open(_BASE / "config.yaml", encoding="utf-8") as f:
            _CONFIG = yaml.safe_load(f) or {}
    return _CONFIG


def _llm_model() -> str:
    return (_load_config().get("llm") or {}).get("model", "gpt-4o-mini")


def _load_openai_key() -> str:
    env_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if env_key and env_key not in ("YOUR-API-KEY", "sk-..."):
        return env_key
    cfg = _load_config()
    key = (cfg.get("nlp") or {}).get("openai", {}).get("api_key", "")
    key = (key or "").strip()
    if not key or key in ("YOUR-API-KEY", "sk-..."):
        raise ValueError(
            "Set OPENAI_API_KEY or nlp.openai.api_key in config.yaml (not YOUR-API-KEY)."
        )
    return key


_SHOWS: list = []
_STORE: ReservationStore | None = None


def _shows() -> list:
    global _SHOWS
    if not _SHOWS:
        _SHOWS = load_shows_yaml(_BASE)
    return _SHOWS


def _store() -> ReservationStore:
    global _STORE
    if _STORE is None:
        _STORE = build_store(_BASE)
    return _STORE


@dataclass
class BookingDraft:
    profile: str = "standard"
    show_id: str | None = None
    seats: int | None = None
    zone: str | None = None
    customer_name: str | None = None
    accessibility: str | None = None

    def reset_booking(self) -> None:
        self.show_id = None
        self.seats = None
        self.zone = None
        self.customer_name = None
        self.accessibility = None


_DRAFTS: dict[int, BookingDraft] = {}


def _draft(session: Session) -> BookingDraft:
    k = id(session)
    if k not in _DRAFTS:
        _DRAFTS[k] = BookingDraft()
    return _DRAFTS[k]


def _menu_text(session: Session) -> str:
    d = _draft(session)
    prof = "Standard" if d.profile == "standard" else "Accessibility-focused"
    lines = [
        f"**Venue assistant** — profile: *{prof}*.",
        "",
        "Commands:",
        "- **BOOK** — start a seat reservation",
        "- **FAQ** — ask about times, prices, PMR access, late arrival",
        "- **CANCEL** — abort the current booking draft",
        "",
        "Shows on sale:",
    ]
    for s in _shows():
        rem = _store().remaining(s["id"])
        lines.append(
            f"  • **{s['title']}** (`{s['id']}`) — {s['datetime']} — "
            f"{s['price_eur']} € — {rem} seats left"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------
agent = Agent("theatre_reservation_bot")
agent.load_properties(str(_BASE / "config.yaml"))
_openai_key = _load_openai_key()
agent.set_property(OPENAI_API_KEY, _openai_key)
_llm = _llm_model()

agent.use_websocket_platform(use_ui=True)

gpt = LLMOpenAI(
    agent=agent,
    name=_llm,
    parameters={},
    num_previous_messages=0,
)

ic_config = LLMIntentClassifierConfiguration(
    llm_name=_llm,
    parameters={},
    use_intent_descriptions=True,
    use_training_sentences=False,
    use_entity_descriptions=True,
    use_entity_synonyms=False,
)
agent.set_default_ic_config(ic_config)

# ---------------------------------------------------------------------------
# Intents
# ---------------------------------------------------------------------------
profile_standard = agent.new_intent(
    "profile_standard",
    description="User chooses the standard profile (STANDARD, normal, default).",
)
profile_access = agent.new_intent(
    "profile_access",
    description="User chooses the accessibility-focused profile (ACCESS, accessibility).",
)
start_booking = agent.new_intent(
    "start_booking",
    description="User wants to book seats (book, reserve, tickets).",
)
ask_faq = agent.new_intent(
    "ask_faq",
    description="User asks an informational FAQ (prices, hours, PMR, wheelchair, late).",
)
cancel_booking = agent.new_intent(
    "cancel_booking",
    description="User cancels the booking flow (cancel, stop, abort).",
)
pick_hamlet = agent.new_intent(
    "pick_hamlet",
    description="User selects Hamlet or hamlet.",
)
pick_jazz = agent.new_intent(
    "pick_jazz",
    description="User selects Jazz Night or jazz.",
)
pick_comedy = agent.new_intent(
    "pick_comedy",
    description="User selects Stand-up Comedy or comedy.",
)
seats_1 = agent.new_intent("seats_1", description="User wants exactly 1 seat.")
seats_2 = agent.new_intent("seats_2", description="User wants exactly 2 seats.")
seats_3 = agent.new_intent("seats_3", description="User wants exactly 3 seats.")
seats_4 = agent.new_intent("seats_4", description="User wants exactly 4 seats.")
zone_front = agent.new_intent(
    "zone_front",
    description="User picks front stalls / front.",
)
zone_rear = agent.new_intent(
    "zone_rear",
    description="User picks rear stalls / rear / back.",
)
name_line = agent.new_intent(
    "name_line",
    description="User sends their name as a line starting with NAME: (example NAME: Ada Lovelace).",
)
a11y_none = agent.new_intent(
    "a11y_none",
    description="User says no special accessibility needs (none, no).",
)
a11y_wheelchair = agent.new_intent(
    "a11y_wheelchair",
    description="User needs wheelchair or step-free access.",
)
a11y_hearing = agent.new_intent(
    "a11y_hearing",
    description="User needs hearing loop / magnetic loop.",
)

# ---------------------------------------------------------------------------
# States
# ---------------------------------------------------------------------------
initial_state = agent.new_state("initial_state", initial=True)
profile_pick = agent.new_state("profile_pick")
set_profile_standard = agent.new_state("set_profile_standard")
set_profile_access = agent.new_state("set_profile_access")
hub = agent.new_state("hub")
cancel_reset = agent.new_state("cancel_reset")
show_select = agent.new_state("show_select")
ready_hamlet = agent.new_state("ready_hamlet")
ready_jazz = agent.new_state("ready_jazz")
ready_comedy = agent.new_state("ready_comedy")
seat_count = agent.new_state("seat_count")
seat_set_1 = agent.new_state("seat_set_1")
seat_set_2 = agent.new_state("seat_set_2")
seat_set_3 = agent.new_state("seat_set_3")
seat_set_4 = agent.new_state("seat_set_4")
zone_pick = agent.new_state("zone_pick")
name_collect_front = agent.new_state("name_collect_front")
name_collect_rear = agent.new_state("name_collect_rear")
a11y_ask = agent.new_state("a11y_ask")
a11y_done_none = agent.new_state("a11y_done_none")
a11y_done_wheel = agent.new_state("a11y_done_wheel")
a11y_done_hear = agent.new_state("a11y_done_hear")
confirm_do = agent.new_state("confirm_do")
faq_llm = agent.new_state("faq_llm")


def initial_body(session: Session) -> None:
    pass


initial_state.set_body(initial_body)
initial_state.go_to(profile_pick)


def profile_pick_body(session: Session) -> None:
    session.reply(
        "Welcome to the **small theatre** booking assistant.\n\n"
        "Pick a **profile** (see also User diagrams / `data/user_profiles.yaml`):\n"
        "- **STANDARD** — short answers.\n"
        "- **ACCESS** — clearer, more detailed accessibility-friendly answers.\n"
    )


profile_pick.set_body(profile_pick_body)
profile_pick.when_intent_matched(profile_standard).go_to(set_profile_standard)
profile_pick.when_intent_matched(profile_access).go_to(set_profile_access)
profile_pick.when_no_intent_matched().go_to(profile_pick)


def set_profile_standard_body(session: Session) -> None:
    _draft(session).profile = "standard"
    session.reply("Profile **STANDARD**.\n\n" + _menu_text(session))


set_profile_standard.set_body(set_profile_standard_body)
set_profile_standard.go_to(hub)


def set_profile_access_body(session: Session) -> None:
    _draft(session).profile = "access"
    session.reply("Profile **ACCESS**.\n\n" + _menu_text(session))


set_profile_access.set_body(set_profile_access_body)
set_profile_access.go_to(hub)


def hub_body(session: Session) -> None:
    session.reply(_menu_text(session))


hub.set_body(hub_body)
hub.when_intent_matched(start_booking).go_to(show_select)
hub.when_intent_matched(ask_faq).go_to(faq_llm)
hub.when_intent_matched(cancel_booking).go_to(cancel_reset)
hub.when_no_intent_matched().go_to(hub)


def cancel_reset_body(session: Session) -> None:
    _draft(session).reset_booking()
    session.reply("Draft cleared.\n\n" + _menu_text(session))


cancel_reset.set_body(cancel_reset_body)
cancel_reset.go_to(hub)


def show_select_body(session: Session) -> None:
    session.reply(
        "**Booking — step 1 — Pick a show**\n"
        "Say **Hamlet**, **Jazz**, or **Comedy** (or use the show ids from the menu). "
        "Or **CANCEL**."
    )


show_select.set_body(show_select_body)
show_select.when_intent_matched(pick_hamlet).go_to(ready_hamlet)
show_select.when_intent_matched(pick_jazz).go_to(ready_jazz)
show_select.when_intent_matched(pick_comedy).go_to(ready_comedy)
show_select.when_intent_matched(cancel_booking).go_to(cancel_reset)
show_select.when_no_intent_matched().go_to(show_select)


def _ready_show(session: Session, show_id: str) -> None:
    _draft(session).show_id = show_id
    show = next(s for s in _shows() if s["id"] == show_id)
    rem = _store().remaining(show_id)
    session.reply(
        f"**{show['title']}** — **{rem}** seats still available.\n\n"
        "**Step 2 — How many seats?** Reply **1**, **2**, **3**, or **4** (or CANCEL)."
    )


def ready_hamlet_body(session: Session) -> None:
    _ready_show(session, "hamlet")


ready_hamlet.set_body(ready_hamlet_body)
ready_hamlet.go_to(seat_count)


def ready_jazz_body(session: Session) -> None:
    _ready_show(session, "jazz_night")


ready_jazz.set_body(ready_jazz_body)
ready_jazz.go_to(seat_count)


def ready_comedy_body(session: Session) -> None:
    _ready_show(session, "comedy_club")


ready_comedy.set_body(ready_comedy_body)
ready_comedy.go_to(seat_count)


def seat_count_body(session: Session) -> None:
    session.reply("Waiting for a seat count **1–4**… (or CANCEL.)")


seat_count.set_body(seat_count_body)
seat_count.when_intent_matched(seats_1).go_to(seat_set_1)
seat_count.when_intent_matched(seats_2).go_to(seat_set_2)
seat_count.when_intent_matched(seats_3).go_to(seat_set_3)
seat_count.when_intent_matched(seats_4).go_to(seat_set_4)
seat_count.when_intent_matched(cancel_booking).go_to(cancel_reset)
seat_count.when_no_intent_matched().go_to(seat_count)


def _seat_set_body(session: Session, n: int) -> None:
    _draft(session).seats = n
    session.reply(
        "**Step 3 — Zone**\n"
        "Reply **FRONT** or **REAR** (rear = back of the hall). Or CANCEL."
    )


def seat_set_1_body(session: Session) -> None:
    _seat_set_body(session, 1)


seat_set_1.set_body(seat_set_1_body)
seat_set_1.go_to(zone_pick)


def seat_set_2_body(session: Session) -> None:
    _seat_set_body(session, 2)


seat_set_2.set_body(seat_set_2_body)
seat_set_2.go_to(zone_pick)


def seat_set_3_body(session: Session) -> None:
    _seat_set_body(session, 3)


seat_set_3.set_body(seat_set_3_body)
seat_set_3.go_to(zone_pick)


def seat_set_4_body(session: Session) -> None:
    _seat_set_body(session, 4)


seat_set_4.set_body(seat_set_4_body)
seat_set_4.go_to(zone_pick)


def zone_pick_body(session: Session) -> None:
    session.reply("Waiting for **FRONT** or **REAR**…")


zone_pick.set_body(zone_pick_body)
zone_pick.when_intent_matched(zone_front).go_to(name_collect_front)
zone_pick.when_intent_matched(zone_rear).go_to(name_collect_rear)
zone_pick.when_intent_matched(cancel_booking).go_to(cancel_reset)
zone_pick.when_no_intent_matched().go_to(zone_pick)


def name_collect_front_body(session: Session) -> None:
    d = _draft(session)
    raw = (session.event.message or "").strip()
    if d.zone != "front":
        d.zone = "front"
        session.reply(
            "**Step 4 — Your name**\n"
            "Send exactly: `NAME: Firstname Lastname`\n"
            "Or CANCEL."
        )
    elif not raw.upper().startswith("NAME:"):
        session.reply("Please send `NAME: First Last` (one line) or CANCEL.")


name_collect_front.set_body(name_collect_front_body)
name_collect_front.when_intent_matched(name_line).go_to(a11y_ask)
name_collect_front.when_intent_matched(cancel_booking).go_to(cancel_reset)
name_collect_front.when_no_intent_matched().go_to(name_collect_front)


def name_collect_rear_body(session: Session) -> None:
    d = _draft(session)
    raw = (session.event.message or "").strip()
    if d.zone != "rear":
        d.zone = "rear"
        session.reply(
            "**Step 4 — Your name**\n"
            "Send exactly: `NAME: Firstname Lastname`\n"
            "Or CANCEL."
        )
    elif not raw.upper().startswith("NAME:"):
        session.reply("Please send `NAME: First Last` (one line) or CANCEL.")


name_collect_rear.set_body(name_collect_rear_body)
name_collect_rear.when_intent_matched(name_line).go_to(a11y_ask)
name_collect_rear.when_intent_matched(cancel_booking).go_to(cancel_reset)
name_collect_rear.when_no_intent_matched().go_to(name_collect_rear)


def a11y_ask_body(session: Session) -> None:
    raw = (session.event.message or "").strip()
    if raw.upper().startswith("NAME:"):
        name = raw.split(":", 1)[1].strip()
        if len(name) < 2:
            session.reply("That name looks too short. Use `NAME: Your Full Name`.")
            return
        _draft(session).customer_name = name
    if not _draft(session).customer_name:
        session.reply("Use the format **NAME: Your Full Name**.")
        return
    session.reply(
        "**Step 5 — Accessibility**\n"
        "Reply **NONE**, **WHEELCHAIR**, or **HEARING** (hearing loop). Or CANCEL."
    )


a11y_ask.set_body(a11y_ask_body)
a11y_ask.when_intent_matched(a11y_none).go_to(a11y_done_none)
a11y_ask.when_intent_matched(a11y_wheelchair).go_to(a11y_done_wheel)
a11y_ask.when_intent_matched(a11y_hearing).go_to(a11y_done_hear)
a11y_ask.when_intent_matched(cancel_booking).go_to(cancel_reset)
a11y_ask.when_no_intent_matched().go_to(a11y_ask)


def a11y_done_none_body(session: Session) -> None:
    _draft(session).accessibility = "none"


a11y_done_none.set_body(a11y_done_none_body)
a11y_done_none.go_to(confirm_do)


def a11y_done_wheel_body(session: Session) -> None:
    _draft(session).accessibility = "wheelchair"


a11y_done_wheel.set_body(a11y_done_wheel_body)
a11y_done_wheel.go_to(confirm_do)


def a11y_done_hear_body(session: Session) -> None:
    _draft(session).accessibility = "hearing_loop"


a11y_done_hear.set_body(a11y_done_hear_body)
a11y_done_hear.go_to(confirm_do)


def confirm_do_body(session: Session) -> None:
    d = _draft(session)
    show = next((s for s in _shows() if s["id"] == d.show_id), None)
    if not show or not d.seats or not d.zone or not d.customer_name:
        session.reply("Incomplete draft. Say **BOOK** to start again.")
        d.reset_booking()
        return
    try:
        rec = _store().book(
            d.show_id,
            d.seats,
            d.customer_name,
            d.zone,
            d.accessibility or "none",
        )
    except ValueError as e:
        code = str(e)
        if code == "NOT_ENOUGH_SEATS":
            session.reply(
                "**Conflict:** not enough seats left for that show. "
                "Try fewer seats or another show (**BOOK**)."
            )
        else:
            session.reply(f"**Error:** {code}. Say **BOOK** to retry.")
        d.reset_booking()
        return

    pmr = show.get("pmr_entrance", "")
    extra = ""
    if d.profile == "access":
        extra = f"\n\n**PMR / access:** {pmr}"
    session.reply(
        f"**Confirmed** — `{rec.confirmation_code}`\n"
        f"- **{show['title']}**\n"
        f"- **{rec.seats}** seat(s), zone **{rec.zone}**\n"
        f"- **{rec.customer_name}**\n"
        f"- Accessibility: **{rec.accessibility}**"
        f"{extra}\n\n"
        + _menu_text(session)
    )
    d.reset_booking()


confirm_do.set_body(confirm_do_body)
confirm_do.go_to(hub)


def faq_llm_body(session: Session) -> None:
    d = _draft(session)
    ctx_lines = ["Facts (use only if relevant):"]
    for s in _shows():
        ctx_lines.append(
            f"- {s['title']} @ {s['datetime']}, {s['price_eur']} EUR, "
            f"PMR: {s.get('pmr_entrance', '')}"
        )
    ctx = "\n".join(ctx_lines)
    tone = (
        "Answer with clear, reassuring detail; repeat PMR / hearing information when asked."
        if d.profile == "access"
        else "Answer briefly and neutrally."
    )
    question = session.event.message or ""
    prompt = (
        f"{tone}\n{ctx}\n"
        "Late policy: doors close 10 minutes after start; late seating at intermission only.\n"
        f"Question: {question}"
    )
    answer = gpt.predict(prompt)
    session.reply(answer)


faq_llm.set_body(faq_llm_body)
faq_llm.go_to(hub)


if __name__ == "__main__":
    agent.run()

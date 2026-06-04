# Theatre reservation bot — state map (WME Agent diagram ↔ `theatre_bot.py`)

Regenerate WME export after diagram edits: `python scripts/build_wme_export.py`.

| Code state | Role |
|------------|------|
| `initial_state` | Entry |
| `profile_pick` | Choose STANDARD vs ACCESS |
| `set_profile_standard` / `set_profile_access` | Store profile → `hub` |
| `hub` | Menu: BOOK / FAQ / CANCEL |
| `cancel_reset` | Clear draft → `hub` |
| `show_select` | Pick Hamlet / Jazz / Comedy |
| `ready_hamlet` / `ready_jazz` / `ready_comedy` | Fix `show_id` → `seat_count` |
| `seat_count` | Wait 1–4 seats |
| `seat_set_1` … `seat_set_4` | Store seat count → `zone_pick` |
| `zone_pick` | Wait FRONT / REAR |
| `name_collect_front` / `name_collect_rear` | Store zone, wait `NAME: …` |
| `a11y_ask` | NONE / WHEELCHAIR / HEARING |
| `a11y_done_*` | Store accessibility → `confirm_do` |
| `confirm_do` | Call `ReservationStore.book` → `hub` |
| `faq_llm` | LLM FAQ → `hub` |

Intents are declared in `theatre_bot.py` next to `agent.new_intent(...)`.

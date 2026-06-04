Theatre reservation — complete BESSER education deliverable.

Agent (full logic):  python Theatre_reservation_agent.py
WME import file:     wme-theatre-reservation-bot.json
API:                 THEATRE_PERSIST=1 uvicorn backend.main_api:app --port 8000
Web UI:              webapp/index.html
Regenerate models:   python scripts/build_wme_export.py && python scripts/export_buml.py
Tests:               python tests/smoke_test.py

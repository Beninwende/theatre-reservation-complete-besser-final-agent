# Livrable complet — checklist

## Modélisation WME

- [x] Diagramme de classes domaine (Theatre, Show, Reservation, profils)
- [x] Diagramme Agent complet (`docs/STATE_MAP.md` — tous les états)
- [x] User diagrams Lab 7 (2 onglets)
- [x] GUI Shows + Reservations
- [x] Object diagram exemple
- [x] Fichier import : `wme-theatre-reservation-bot.json`
- [x] Régénération : `python scripts/build_wme_export.py`

## Code

- [x] `theatre_bot.py` — BAF complet (store, LLM FAQ, profils, conflits)
- [x] `Theatre_reservation_agent.py` — entrée compatible export BESSER
- [x] `models/domain_model.py` — B-UML
- [x] `backend/main_api.py` + `webapp/index.html`
- [x] `buml/` via `python scripts/export_buml.py`
- [x] `tests/smoke_test.py`

## Déploiement

- [x] `docker-compose.yml` (api + web + agent)
- [x] `render.yaml` (API) + `render-agent.yaml` (agent)

## À faire dans l’éditeur (une fois)

- [ ] Importer `wme-theatre-reservation-bot.json`
- [ ] Quality check class + agent
- [ ] (Optionnel) **Generate → Web Application** pour ZIP Lab 6 officiel
- [ ] Pousser vers GitHub (remplacer le squelette agent par ce dossier)

## Scénarios de démo

1. `STANDARD` → `BOOK` → `Hamlet` → `2` → `FRONT` → `NAME: …` → `NONE` → code BK-*
2. FAQ depuis hub (ton selon profil)
3. Remplir un spectacle → `NOT_ENOUGH_SEATS`
4. `THEATRE_PERSIST=1` + API + recharger `webapp/index.html`

---
name: Battleship game implementation
description: Two-player text-mode Battleship game with REST server, CLI clients, BDD tests, and DreamHost deployment
type: project
---

Python implementation of a full Battleship game.

**Why:** User wanted a two-player game running in two separate command windows, communicating through a REST API. Server is deployed to boardgame.this-is-only-a-test.com on DreamHost shared hosting.

**How to apply:** Run `python server.py` locally (port 5000). Run `python client.py` for local play or `python client.py --server https://boardgame.this-is-only-a-test.com` for the live server. Run `python -m behave` for tests (8 scenarios, 81 steps).

## Fleet (5 ships)
| Ship       | Length | Symbol |
|------------|--------|--------|
| Carrier    | 5      | A      |
| Battleship | 4      | B      |
| Cruiser    | 3      | C      |
| Submarine  | 3      | S      |
| Destroyer  | 2      | D      |

## Coordinate format
Column letter (A–J) + row number (1–10), e.g. `C5` = column C, row 5. NOT row,col anymore.

## Move results
Hit → `"Hit"`, Miss → `"Miss"`, ship sunk → `"<ShipType> Destroyed"` (e.g. `"Cruiser Destroyed"`).

## Key files
- `server.py` — Flask REST API; `GameStore` class uses in-memory dict locally or SQLite when `GAME_DB` env var is set; port 5000
- `client.py` — text-mode client, defaults to `http://localhost:5000`
- `webclient.html` — single-file browser client; dark ocean theme; vanilla JS polling every 2s; ship placement UI; Quit button
- `app.cgi` — CGI entry point for DreamHost (sets `GAME_DB=/home/kenpugh/battleship.db`)
- `.htaccess` — Apache rewrite rules routing all requests through app.cgi
- `deploy/do_deploy.py` — upload + setup script; run with `python deploy/do_deploy.py '<password>'`
- `deploy/setup_dreamhost.sh` — one-time SSH setup (installs Flask, patches shebang)
- `requirements.txt`, `behave.ini`, `features/boardgame.feature`, `features/boardgame_message.feature`, `features/environment.py`, `features/steps/game_steps.py`

## Key API endpoints
`POST /games`, `GET /games/{id}`, `DELETE /games/{id}`, `POST /games/{id}/ships/{player}`, `POST /games/{id}/moves`

## Game cancellation / timeout
- `DELETE /games/{id}` with `{"player": name}` sets `status="Cancelled"`, `cancelled_by=name`
- `GET /games/{id}` auto-cancels (sets `cancelled_by="timeout"`) if no activity for 10 minutes
- Both clients detect `status="Cancelled"` on next poll and show an overlay with the reason

## DreamHost deployment
- SSH: kenpugh@boardgame.this-is-only-a-test.com port 22
- SQLite DB: `/home/kenpugh/battleship.db`
- Web root: `/home/kenpugh/boardgame.this-is-only-a-test.com/`
- Python: `/usr/bin/python3` (3.10.12), Flask installed `--user`
- Redeploy: `python deploy/do_deploy.py '<password>'`

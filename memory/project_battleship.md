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
- `webclient.html` — single-file browser client; dark ocean theme; vanilla JS polling every 2s; ship placement UI with Undo button; click-to-select fire mechanic; Quit button
- `mobile.html` — mobile-optimized client; tab-based board switching (Opponent | My Fleet); 30px cells fit 375px iPhone SE; served at `/mobile`
- `player.html` — terminal-style browser client served at `/player`
- `app.cgi` — CGI entry point for DreamHost (sets `GAME_DB=/home/<user>/battleship.db`)
- `.htaccess` — Apache rewrite rules routing all requests through app.cgi
- `deploy/do_deploy.py` — upload + setup script; run with `python deploy/do_deploy.py '<password>'`
- `deploy/setup_dreamhost.sh` — one-time SSH setup (installs Flask, patches shebang)
- `requirements.txt`, `behave.ini`, `features/boardgame.feature`, `features/boardgame_message.feature`, `features/environment.py`, `features/steps/game_steps.py`

## Key API endpoints
`POST /games`, `GET /games/{id}`, `DELETE /games/{id}`, `POST /games/{id}/ships/{player}`, `POST /games/{id}/moves`

## webclient.html layout (game phase)
- Two boards side by side: **Opponent's Board (left) | Your Board (right)**
- Fire row (input + Fire button + Quit) below the boards
- Single last-message line below fire row (no message log/history)
- Ship health panel as horizontal strip below last-message line

## client.py board layout
Side-by-side in terminal: **Opponent's Board (left) | Your Board (right)**
Each board is 38 chars wide with 2-char padding between.

## webclient.html fire mechanic
Click a cell on the opponent board → highlights it and fills the location input. Click **Fire!** (or press Enter) to actually fire. The `selectedLoc` state variable tracks the highlighted cell.

## webclient.html ship placement
- Ships placed one at a time by clicking the grid
- **↩ Undo** button removes the last placed ship (rebuilds grid and repaints remaining ships)
- **🎲 Random** places all ships randomly and immediately submits
- Orientation toggled with ↔/↕ button

## Game cancellation / timeout
- `DELETE /games/{id}` with `{"player": name}` sets `status="Cancelled"`, `cancelled_by=name`
- `GET /games/{id}` auto-cancels (sets `cancelled_by="timeout"`) based on inactivity:
  - **Setup phase**: 2 minutes (120 s)
  - **In Progress**: 20 seconds
- Timer resets on every GET /games poll (not on moves or ship placement)
- Both clients detect `status="Cancelled"` on next poll and show an overlay with the reason

## Board rendering (webclient.html)
- `cache: 'no-store'` on all fetch calls prevents browser from caching GET /games responses
- Hits (`@`) → `.cell.hit` (red background, ✕ marker)
- Misses (`X`) → `.cell.miss` (dark blue, lighter border, ○ marker)
- Own ships → `.cell.ship` (blue)
- Selected target → `.cell.selected` (bright blue glow)
- Targetable cells → `.cell.targetable` (crosshair cursor, hover highlight)

## DreamHost deployment
- SSH: $DEPLOY_USER@boardgame.this-is-only-a-test.com port 22
- SQLite DB: `/home/$DEPLOY_USER/battleship.db`
- Web root: `/home/$DEPLOY_USER/boardgame.this-is-only-a-test.com/`
- Python: `/usr/bin/python3` (3.10.12), Flask installed `--user`
- Redeploy: `python deploy/do_deploy.py '<password>'`
- `DEPLOY_USER` env var must be set — stored in `.claude/settings.local.json` (gitignored); never hardcode the username in tracked files
- Use `<user>` placeholder in any docs/memory that reference the DreamHost username

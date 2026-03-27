---
name: Battleship game implementation
description: Two-player text-mode Battleship game with REST server and two CLI clients
type: project
---

Python implementation of the Battleship game defined in the .featurex specification files.

**Why:** User wanted a two-player game running in two separate command windows, communicating through a REST API at boardgame.this-is-only-a-test.com (placeholder domain, not yet live).

**How to apply:** The server (server.py) is meant to eventually be deployed to boardgame.this-is-only-a-test.com. For local play, run server.py on localhost:5000 (the client default). Use `--server` flag on the client to point at a remote host.

Files created:
- `server.py` — Flask REST API, in-memory game state, port 5000
- `client.py` — text-mode client, defaults to http://localhost:5000
- `requirements.txt` — flask, requests, behave
- `behave.ini` — points behave at features/
- `features/boardgame.feature` — cleaned up from boardgame.featurex
- `features/boardgame_message.feature` — cleaned up from boardgame-message.featurex
- `features/environment.py` — resets server state, sets up Flask test client per scenario
- `features/steps/game_steps.py` — all BDD step definitions (no running server needed)

Key API endpoints: POST /games, POST /games/{id}/ships/{player}, POST /games/{id}/moves, GET /games/{id}

Run tests: `python -m behave` (8 scenarios, 60 steps)

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

**Install dependencies** (Flask + requests already available in this environment):
```
pip install -r requirements.txt
```

**Start the server** (one terminal):
```
python server.py
```

**Start each client** (two separate terminals — one per player):
```
# Against local server:
python client.py --server http://localhost:5000

# Against hosted server (when deployed):
python client.py
```

Player 1 chooses option `1`, enters both player names, gets a Game ID.
Player 2 chooses option `2`, enters the Game ID and their name.
Both place ships, then take turns. The server defaults to port 5000.

---

## Project Overview

This is a **Battleship game** project currently in the specification phase. The repository contains BDD/ATDD feature specifications written in FeatureX (Gherkin-style) format. No implementation exists yet.

## Planned Implementations

Per `boardgame - overview.featurex`, three client implementations are planned:
1. **CLI** — text input for locations, side-by-side board display
2. **Qt desktop** — cross-platform (macOS, Windows, Linux)
3. **Web browser** — click-based location selection

All clients connect to a REST API at `boardgame.this-is-only-a-test.com` using a **2-second polling** pattern.

## Game Domain Model

### Ships
| Type       | Length | Board Symbol |
|------------|--------|--------------|
| Battleship | 4      | B            |
| Cruiser    | 3      | C            |

Ship statuses: `Not Placed` → `Placed` → `Hit` → `Destroyed`

### Board
- 10×10 grid, coordinates as `row,col` (e.g., `1,1` is top-left)
- Display symbols: `B`/`C` = ship, `@` = hit, `X` = miss
- Both player board and opponent board are shown simultaneously

### Coordinate System
Orientation affects how ships extend from their starting location:
- `Vertical`: extends down (increasing row)
- `Horizontal`: extends right (increasing column)

### Game Status
`Not Started` → `In Progress` → `Over`

## API Protocol (`boardgame-message.featurex`)

Game ID format: `{Player1}-{Player2}` (e.g., `Ken-George`)

Message schema:
```
Game ID | Turn (number) | Status | Turn (whose turn) | Move | Previous Move | Result
```

Move flow:
1. Current player selects location → sends move with the **result of the previous move** included
2. Game increments turn number and switches whose turn it is
3. Opponent polls and receives the move; responds with their move + result of the received move

End-of-game: when all of a player's ships are destroyed, status becomes `Over` with a `Winner` field.

## Validation Rules (`boardgame.featurex`)
- **Off board**: ship placement must fit entirely within the 10×10 grid
- **Overlap**: ships cannot occupy the same cell
- **Duplicate launch**: a player cannot target the same location twice

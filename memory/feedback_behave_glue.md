---
name: Behave glue code patterns
description: How behave parses tables and how turn management works in the BDD step definitions
type: feedback
---

Key patterns used in the Battleship behave glue code that future work should follow:

**Table parsing:** Behave always treats the first row as column headers. A 2-column vertical key-value table like `| Ship | Battleship |` has `headings[0]='Ship'`, `headings[1]='Battleship'`; subsequent rows are data. The `kv()` helper handles this. A single-value table like `| Miss |` has `headings[0]='Miss'` and no data rows.

**Turn management:** The server enforces strict turn alternation. `ensure_opp_turn()` makes a dummy my-move to pass the turn to the opponent; `ensure_my_turn()` makes a dummy opp-move. Dummy my-moves use rows 1-4 cols 5-10 (safe from default opp ships at rows 6/8). Dummy opp-moves use rows 5-10 (safe from test ships in rows 1-4).

**Why:** Without turn bridging, consecutive `When opponent launches` steps fail because the server requires alternating turns. The dummy move pools are pre-computed in `environment.py`.

**How to apply:** Any new step that needs to fire a move should call `ensure_my_turn` or `ensure_opp_turn` first. Keep dummy location pools away from positions used in test scenarios.

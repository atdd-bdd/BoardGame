import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app, games

def before_scenario(context, scenario):
    games.clear()
    app.config['TESTING'] = True
    context.client = app.test_client()

    context.my_name  = 'Player'
    context.opp_name = 'Opponent'
    context.game_id  = 'Player-Opponent'

    context.placed_ships = []   # ships submitted to server for my player
    context.last_result  = None
    context.last_error   = None

    # Pools of dummy locations used to bridge turn gaps without disturbing test state.
    # My dummy attacks: rows 1-4, cols 5-10  (safe — default opp ships are at rows 6/9-10)
    context.dummy_my_locs  = [f'{r},{c}' for r in range(1, 5)  for c in range(5, 11)]
    # Opp dummy attacks: rows 5-10 (safe — test ship positions stay in rows 1-4)
    context.dummy_opp_locs = [f'{r},{c}' for r in range(5, 11) for c in range(1, 11)]

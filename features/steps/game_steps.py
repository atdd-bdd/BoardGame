"""
Glue code (step definitions) for boardgame.feature and boardgame_message.feature.
Uses Flask's test client so no running server is required.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from behave import given, when, then, step

# ── Constants ──────────────────────────────────────────────────────────────────

DEFAULT_OPP_SHIPS = [
    {'type': 'Battleship', 'location': '6,6', 'orientation': 'Horizontal'},  # (6,6)-(6,9)
    {'type': 'Cruiser',    'location': '8,7', 'orientation': 'Horizontal'},  # (8,7)-(8,9)
]
DEFAULT_MY_SHIPS = [
    {'type': 'Battleship', 'location': '1,1', 'orientation': 'Vertical'},
    {'type': 'Cruiser',    'location': '2,2', 'orientation': 'Horizontal'},
]

STATUS_ALIASES = {
    'Ready to Play': 'In Progress',
}

# ── Table parsers ──────────────────────────────────────────────────────────────

def kv(table):
    """
    Parse a 2-column vertical key-value table.
    Behave treats the first row as headings, so:
        | Ship     | Battleship |   → headings[0]='Ship', headings[1]='Battleship'
        | Location | 1,1        |   → row.cells = ['Location', '1,1']
    Returns {'Ship': 'Battleship', 'Location': '1,1', ...}
    """
    d = {table.headings[0]: table.headings[1]}
    for row in table:
        d[row.cells[0]] = row.cells[1]
    return d


def parse_ships(table):
    return [
        {
            'type':        row['Type'],
            'length':      int(row['Length']),
            'status':      row['Status'],
            'location':    row['Location'],
            'orientation': row['Orientation'],
        }
        for row in table
    ]


def parse_board(table):
    board = [[' '] * 10 for _ in range(10)]
    col_hdrs = table.headings[1:]   # skip the row-label column
    for row in table:
        r = int(row[table.headings[0]]) - 1
        for ch in col_hdrs:
            cell = row[ch].strip()
            board[r][int(ch) - 1] = cell if cell else ' '
    return board


# ── Game helpers ───────────────────────────────────────────────────────────────

def get_game(context):
    resp = context.client.get(f'/games/{context.game_id}')
    assert resp.status_code == 200, f"Game not found: {context.game_id}"
    return resp.get_json()


def ensure_game_exists(context):
    """Create game if it doesn't exist; always pre-place opponent ships."""
    resp = context.client.get(f'/games/{context.game_id}')
    if resp.status_code != 200:
        resp = context.client.post('/games', json={
            'player1': context.my_name,
            'player2': context.opp_name,
        })
        assert resp.status_code == 200, resp.get_json()
        resp = context.client.post(
            f'/games/{context.game_id}/ships/{context.opp_name}',
            json={'ships': DEFAULT_OPP_SHIPS},
        )
        assert resp.status_code == 200, resp.get_json()


def ensure_opp_turn(context):
    """If it's my turn, make one dummy my-move to pass the turn to the opponent."""
    game = get_game(context)
    if game['status'] != 'In Progress':
        return
    if game['current_turn'] == context.my_name:
        loc = context.dummy_my_locs.pop(0)
        resp = context.client.post(
            f'/games/{context.game_id}/moves',
            json={'player': context.my_name, 'location': loc},
        )
        assert resp.status_code == 200, f"Dummy my-move at {loc} failed: {resp.get_json()}"


def ensure_my_turn(context):
    """If it's the opponent's turn, make one dummy opponent-move to pass the turn to me."""
    game = get_game(context)
    if game['status'] != 'In Progress':
        return
    if game['current_turn'] == context.opp_name:
        loc = context.dummy_opp_locs.pop(0)
        resp = context.client.post(
            f'/games/{context.game_id}/moves',
            json={'player': context.opp_name, 'location': loc},
        )
        assert resp.status_code == 200, f"Dummy opp-move at {loc} failed: {resp.get_json()}"


def ship_cells(location, orientation, length):
    r, c = map(int, location.split(','))
    if orientation.lower().startswith('v'):
        return [(r + i, c) for i in range(length)]
    return [(r, c + i) for i in range(length)]


# ── Given steps ───────────────────────────────────────────────────────────────

@given('my ships are')
@given('ships are')
def step_given_my_ships_are(context):
    ships = parse_ships(context.table)
    placed = [s for s in ships if s['status'] == 'Placed']
    context.placed_ships = [
        {'type': s['type'], 'location': s['location'], 'orientation': s['orientation']}
        for s in placed
    ]
    if context.placed_ships:
        ensure_game_exists(context)
        resp = context.client.post(
            f'/games/{context.game_id}/ships/{context.my_name}',
            json={'ships': context.placed_ships},
        )
        assert resp.status_code == 200, resp.get_json()


@given('my ship display is')
def step_given_display_is(context):
    expected = parse_board(context.table)
    game = get_game(context)
    actual = game['boards'][context.my_name]
    for r in range(10):
        for c in range(10):
            exp = expected[r][c]
            if exp:
                assert actual[r][c] == exp, \
                    f"Initial board mismatch at ({r+1},{c+1}): expected {exp!r}, got {actual[r][c]!r}"


@given('I am')
def step_given_i_am(context):
    context.my_name = context.table.headings[0].strip()


@given('game is')
def step_given_game_is(context):
    row = context.table[0]
    headings = context.table.headings

    if 'Game ID' in headings:
        context.game_id = row['Game ID']
        parts = context.game_id.split('-')
        context.my_name  = parts[0]   # player1, always goes first
        context.opp_name = parts[1]

    ensure_game_exists(context)

    # Place my (player1) ships if not yet placed so game reaches In Progress
    game = get_game(context)
    if not game['ships_placed'].get(context.my_name):
        resp = context.client.post(
            f'/games/{context.game_id}/ships/{context.my_name}',
            json={'ships': DEFAULT_MY_SHIPS},
        )
        assert resp.status_code == 200, resp.get_json()
        context.placed_ships = list(DEFAULT_MY_SHIPS)

    # Advance turns until the expected Current Turn is active
    if 'Current Turn' in headings:
        target = row['Current Turn']
        for _ in range(20):   # safety cap
            g = get_game(context)
            if g['current_turn'] == target or g['status'] != 'In Progress':
                break
            player = g['current_turn']
            pool = context.dummy_my_locs if player == context.my_name else context.dummy_opp_locs
            loc = pool.pop(0)
            resp = context.client.post(
                f'/games/{context.game_id}/moves',
                json={'player': player, 'location': loc},
            )
            assert resp.status_code == 200, f"Turn-advance move failed: {resp.get_json()}"


@step('game does not exist')
def step_game_does_not_exist(context):
    game_id = context.table[0]['Game ID']
    context.game_id = game_id
    resp = context.client.get(f'/games/{game_id}')
    assert resp.status_code == 404, \
        f"Expected game {game_id!r} to not exist but got status {resp.status_code}"


# ── When steps ────────────────────────────────────────────────────────────────

@when('placed')
def step_when_placed(context):
    d = kv(context.table)
    new_ship = {
        'type':        d['Ship'],
        'location':    d['Location'],
        'orientation': d['Orientation'],
    }
    ensure_game_exists(context)
    trial = [s for s in context.placed_ships if s['type'] != new_ship['type']] + [new_ship]
    resp = context.client.post(
        f'/games/{context.game_id}/ships/{context.my_name}',
        json={'ships': trial},
    )
    if resp.status_code == 200:
        context.placed_ships = trial
        context.last_error = None
    else:
        context.last_error = resp.get_json().get('error')


@when('opponent launches')
def step_when_opponent_launches(context):
    location = kv(context.table)['Location']
    ensure_opp_turn(context)
    resp = context.client.post(
        f'/games/{context.game_id}/moves',
        json={'player': context.opp_name, 'location': location},
    )
    if resp.status_code == 200:
        context.last_result = resp.get_json()['result']
        context.last_error  = None
    else:
        context.last_result = None
        context.last_error  = resp.get_json().get('error')


@when('I launch')
def step_when_i_launch(context):
    location = kv(context.table)['Location']
    ensure_my_turn(context)
    resp = context.client.post(
        f'/games/{context.game_id}/moves',
        json={'player': context.my_name, 'location': location},
    )
    if resp.status_code == 200:
        context.last_result = resp.get_json()['result']
        context.last_error  = None
    else:
        context.last_result = None
        context.last_error  = resp.get_json().get('error')


@when('player enters')
def step_when_player_enters(context):
    d = kv(context.table)
    if 'My Name' in d:
        context.my_name  = d['My Name']
        context.opp_name = d['Your Name']
        context.game_id  = f"{context.my_name}-{context.opp_name}"
        resp = context.client.post('/games', json={
            'player1': context.my_name,
            'player2': context.opp_name,
        })
        assert resp.status_code == 200, resp.get_json()
        # Place ships for both so game is In Progress
        for player, ships in [(context.my_name, DEFAULT_MY_SHIPS), (context.opp_name, DEFAULT_OPP_SHIPS)]:
            resp = context.client.post(
                f'/games/{context.game_id}/ships/{player}',
                json={'ships': ships},
            )
            assert resp.status_code == 200, f"Place ships for {player}: {resp.get_json()}"
    else:
        location = d['Location']
        ensure_my_turn(context)
        resp = context.client.post(
            f'/games/{context.game_id}/moves',
            json={'player': context.my_name, 'location': location},
        )
        if resp.status_code == 200:
            context.last_result = resp.get_json()['result']
            context.last_error  = None
        else:
            context.last_result = None
            context.last_error  = resp.get_json().get('error')


@when('other player enters')
def step_when_other_player_enters(context):
    location = kv(context.table)['Location']
    ensure_opp_turn(context)
    resp = context.client.post(
        f'/games/{context.game_id}/moves',
        json={'player': context.opp_name, 'location': location},
    )
    if resp.status_code == 200:
        context.last_result = resp.get_json()['result']
        context.last_error  = None
    else:
        context.last_result = None
        context.last_error  = resp.get_json().get('error')


# ── Then steps ────────────────────────────────────────────────────────────────

@then('my ships are now')
def step_then_my_ships_are_now(context):
    expected = parse_ships(context.table)
    srv = get_game(context)['ships'].get(context.my_name, {})
    for s in expected:
        if s['status'] == 'Not Placed':
            assert s['type'] not in srv, \
                f"{s['type']} should be Not Placed but found in server ships"
        else:
            assert s['type'] in srv, \
                f"{s['type']} not found in server ships (have: {list(srv)})"
            assert srv[s['type']]['status'] == s['status'], \
                f"{s['type']} status: expected {s['status']!r}, got {srv[s['type']]['status']!r}"
            if s['location']:
                assert srv[s['type']]['location'] == s['location'], \
                    f"{s['type']} location: expected {s['location']!r}, got {srv[s['type']]['location']!r}"


@then('my ship display is now')
def step_then_display_is_now(context):
    expected = parse_board(context.table)
    actual   = get_game(context)['boards'][context.my_name]
    for r in range(10):
        for c in range(10):
            exp = expected[r][c]
            if exp:
                assert actual[r][c] == exp, \
                    f"Board ({r+1},{c+1}): expected {exp!r}, got {actual[r][c]!r}"


@then('game is')
def step_then_game_is(context):
    row    = context.table[0]
    game   = get_game(context)
    hdgs   = context.table.headings

    if 'Status' in hdgs:
        expected = STATUS_ALIASES.get(row['Status'], row['Status'])
        assert game['status'] == expected, \
            f"Status: expected {expected!r}, got {game['status']!r}"

    if 'Winner' in hdgs:
        winner = row['Winner']
        if winner == 'TBD':
            assert game['winner'] is None, f"Expected no winner, got {game['winner']!r}"
        elif winner == 'I Lost':
            assert game['winner'] == context.opp_name, \
                f"Expected {context.opp_name!r} to win, got {game['winner']!r}"
        elif winner == 'I Won':
            assert game['winner'] == context.my_name, \
                f"Expected {context.my_name!r} to win, got {game['winner']!r}"
        elif winner:
            assert game['winner'] == winner, \
                f"Winner: expected {winner!r}, got {game['winner']!r}"


@then('game is now')
def step_then_game_is_now(context):
    if not context.table:
        return
    row  = context.table[0]
    game = get_game(context)
    hdgs = context.table.headings

    if 'Game ID' in hdgs:
        assert game['game_id'] == row['Game ID'], \
            f"Game ID: expected {row['Game ID']!r}, got {game['game_id']!r}"

    if 'Status' in hdgs:
        expected = STATUS_ALIASES.get(row['Status'], row['Status'])
        assert game['status'] == expected, \
            f"Status: expected {expected!r}, got {game['status']!r}"

    if 'Current Turn' in hdgs:
        assert game['current_turn'] == row['Current Turn'], \
            f"Current turn: expected {row['Current Turn']!r}, got {game['current_turn']!r}"

    if 'Winner' in hdgs and row['Winner']:
        assert game['winner'] == row['Winner'], \
            f"Winner: expected {row['Winner']!r}, got {game['winner']!r}"


@then('result is')
def step_then_result_is(context):
    expected = context.table.headings[0].strip()
    assert context.last_result == expected, \
        f"Result: expected {expected!r}, got {context.last_result!r}"


@then('error is')
def step_then_error_is(context):
    expected = context.table.headings[0].strip()
    assert context.last_error == expected, \
        f"Error: expected {expected!r}, got {context.last_error!r}"


@then('message sent')
def step_then_message_sent(context):
    row  = context.table[0]
    game = get_game(context)
    hdgs = context.table.headings

    if 'Status' in hdgs:
        expected = STATUS_ALIASES.get(row['Status'], row['Status'])
        assert game['status'] == expected, \
            f"Status: expected {expected!r}, got {game['status']!r}"

    if 'Move' in hdgs and row['Move'] not in ('None', ''):
        player = row['Player'] if 'Player' in hdgs else context.my_name
        move   = row['Move']
        found  = any(m['location'] == move and m['player'] == player for m in game['moves'])
        assert found, f"Move {move!r} by {player!r} not found in moves: {game['moves']}"

    if 'Result' in hdgs and row['Result'] not in ('None', ''):
        player = row['Player'] if 'Player' in hdgs else context.my_name
        move   = row['Move']   if 'Move'   in hdgs else None
        match  = [m for m in game['moves']
                  if m['player'] == player and (move is None or m['location'] == move)]
        assert match, f"No move found for player {player!r}"
        assert match[-1]['result'] == row['Result'], \
            f"Result: expected {row['Result']!r}, got {match[-1]['result']!r}"

    if 'Winner' in hdgs and row['Winner'] not in ('', 'TBD'):
        assert game['winner'] == row['Winner'], \
            f"Winner: expected {row['Winner']!r}, got {game['winner']!r}"


@step('my ships are all destroyed')
def step_my_ships_all_destroyed(context):
    """Place my ships then simulate opponent destroying each one."""
    ship_data = [
        {'type': row['Type'], 'location': row['Location'], 'orientation': row['Orientation']}
        for row in context.table
    ]
    ensure_game_exists(context)
    resp = context.client.post(
        f'/games/{context.game_id}/ships/{context.my_name}',
        json={'ships': ship_data},
    )
    assert resp.status_code == 200, resp.get_json()

    for row in context.table:
        cells = ship_cells(row['Location'], row['Orientation'], int(row['Length']))
        for r, c in cells:
            ensure_opp_turn(context)
            resp = context.client.post(
                f'/games/{context.game_id}/moves',
                json={'player': context.opp_name, 'location': f'{r},{c}'},
            )
            assert resp.status_code == 200, \
                f"Attack ({r},{c}) failed: {resp.get_json()}"
            if get_game(context)['status'] == 'Over':
                return   # game ended, no more moves possible

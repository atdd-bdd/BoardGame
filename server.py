"""
Battleship REST API server.
Run with: python server.py
Listens on port 5000 by default.

For CGI deployment set the GAME_DB environment variable to a writable SQLite
path, e.g. GAME_DB=/home/user/battleship.db
"""

import json
import os
import sqlite3
import time
from flask import Flask, request, jsonify
from werkzeug.exceptions import HTTPException

app = Flask(__name__)


class GameStore:
    """Dict-like store backed by SQLite when GAME_DB env var is set."""

    def __init__(self):
        self._mem = {}
        self._db_path = os.environ.get('GAME_DB')
        if self._db_path:
            self._init_db()

    def _init_db(self):
        con = sqlite3.connect(self._db_path)
        con.execute(
            'CREATE TABLE IF NOT EXISTS games (gid TEXT PRIMARY KEY, data TEXT)'
        )
        con.commit()
        con.close()

    def _con(self):
        return sqlite3.connect(self._db_path)

    def __contains__(self, gid):
        if not self._db_path:
            return gid in self._mem
        con = self._con()
        row = con.execute('SELECT 1 FROM games WHERE gid=?', (gid,)).fetchone()
        con.close()
        return row is not None

    def __getitem__(self, gid):
        if not self._db_path:
            return self._mem[gid]
        con = self._con()
        row = con.execute('SELECT data FROM games WHERE gid=?', (gid,)).fetchone()
        con.close()
        if row is None:
            raise KeyError(gid)
        return json.loads(row[0])

    def __setitem__(self, gid, value):
        if not self._db_path:
            self._mem[gid] = value
            return
        con = self._con()
        con.execute(
            'INSERT OR REPLACE INTO games (gid, data) VALUES (?, ?)',
            (gid, json.dumps(value)),
        )
        con.commit()
        con.close()

    def clear(self):
        self._mem.clear()
        if self._db_path:
            con = self._con()
            con.execute('DELETE FROM games')
            con.commit()
            con.close()


games = GameStore()


@app.errorhandler(Exception)
def handle_error(e):
    code = e.code if isinstance(e, HTTPException) else 500
    return jsonify({'error': str(e)}), code

SHIP_INFO = {
    'Carrier':    {'length': 5, 'symbol': 'A'},
    'Battleship': {'length': 4, 'symbol': 'B'},
    'Cruiser':    {'length': 3, 'symbol': 'C'},
    'Submarine':  {'length': 3, 'symbol': 'S'},
    'Destroyer':  {'length': 2, 'symbol': 'D'},
}


def empty_board():
    return [[' '] * 10 for _ in range(10)]


def parse_loc(loc):
    loc = loc.strip().upper()
    c = ord(loc[0]) - ord('A') + 1
    r = int(loc[1:])
    return r, c


def ship_cells(location, orientation, length):
    r, c = parse_loc(location)
    if orientation.lower().startswith('v'):
        return [[r + i, c] for i in range(length)]
    else:
        return [[r, c + i] for i in range(length)]


@app.route('/')
@app.route('/index.html')
def index_page():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'index.html')
    with open(path) as f:
        return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}


@app.route('/player')
def player_page():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'player.html')
    with open(path) as f:
        return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}


@app.route('/mobile')
@app.route('/mobile.html')
def mobile_page():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mobile.html')
    with open(path) as f:
        return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}


@app.route('/games', methods=['POST'])
def create_game():
    d = request.get_json(force=True, silent=True)
    if not d or 'player1' not in d or 'player2' not in d:
        return jsonify({'error': 'Required fields: player1, player2'}), 400
    p1, p2 = d['player1'], d['player2']
    gid = f"{p1}-{p2}"
    if gid in games and games[gid]['status'] not in ('Cancelled', 'Over'):
        return jsonify({'error': 'Game already exists'}), 409
    games[gid] = {
        'game_id': gid, 'player1': p1, 'player2': p2,
        'status': 'Setup', 'turn': 1, 'current_turn': p1, 'winner': None,
        'ships': {p1: {}, p2: {}},
        'boards': {p1: empty_board(), p2: empty_board()},
        'ships_placed': {p1: False, p2: False},
        'moves': [],
        'last_activity': time.time(),
        'cancelled_by': None,
    }
    return jsonify({'game_id': gid})


@app.route('/games/<gid>', methods=['GET'])
def get_game(gid):
    if gid not in games:
        return jsonify({'error': 'Not found'}), 404
    g = games[gid]
    if g['status'] in ('Setup', 'In Progress'):
        now = time.time()
        limit = 120 if g['status'] == 'Setup' else 20
        if now - g.get('last_activity', now) > limit:
            g['status'] = 'Cancelled'
            g['cancelled_by'] = 'timeout'
        else:
            g['last_activity'] = now
        games[gid] = g
    return jsonify(g)


@app.route('/games/<gid>', methods=['DELETE'])
def cancel_game(gid):
    if gid not in games:
        return jsonify({'error': 'Not found'}), 404
    g = games[gid]
    d = request.get_json(force=True, silent=True) or {}
    g['status'] = 'Cancelled'
    g['cancelled_by'] = d.get('player', 'unknown')
    games[gid] = g
    return jsonify({'ok': True})


@app.route('/games/<gid>/ships/<player>', methods=['POST'])
def place_ships(gid, player):
    if gid not in games:
        return jsonify({'error': 'Not found'}), 404
    g = games[gid]
    if player not in (g['player1'], g['player2']):
        return jsonify({'error': 'Player not in game'}), 403

    d = request.get_json(force=True, silent=True)
    if not d or 'ships' not in d:
        return jsonify({'error': 'Required field: ships'}), 400
    ships_data = d['ships']
    board = empty_board()
    ships = {}

    for s in ships_data:
        stype, loc, orient = s['type'], s['location'], s['orientation']
        if stype not in SHIP_INFO:
            return jsonify({'error': f'Unknown ship type: {stype}'}), 400
        info = SHIP_INFO[stype]
        try:
            cells = ship_cells(loc, orient, info['length'])
        except Exception:
            return jsonify({'error': 'Invalid location format'}), 400

        for (r, c) in cells:
            if not (1 <= r <= 10 and 1 <= c <= 10):
                return jsonify({'error': 'Off board'}), 400
        for (r, c) in cells:
            if board[r-1][c-1] != ' ':
                return jsonify({'error': 'Overlap'}), 400
        for (r, c) in cells:
            board[r-1][c-1] = info['symbol']

        ships[stype] = {
            'type': stype, 'length': info['length'], 'status': 'Placed',
            'location': loc, 'orientation': orient,
            'cells': cells, 'hits': [],
        }

    g['ships'][player] = ships
    g['boards'][player] = board
    g['ships_placed'][player] = True
    if all(g['ships_placed'].values()):
        g['status'] = 'In Progress'
    games[gid] = g
    return jsonify({'success': True})


@app.route('/games/<gid>/moves', methods=['POST'])
def make_move(gid):
    if gid not in games:
        return jsonify({'error': 'Not found'}), 404
    g = games[gid]
    d = request.get_json(force=True, silent=True)
    if not d or 'player' not in d or 'location' not in d:
        return jsonify({'error': 'Required fields: player, location'}), 400
    player, location = d['player'], d['location']

    if player not in (g['player1'], g['player2']):
        return jsonify({'error': 'Player not in game'}), 403
    if g['status'] != 'In Progress':
        return jsonify({'error': 'Game not in progress'}), 400
    if g['current_turn'] != player:
        return jsonify({'error': 'Not your turn'}), 400

    for m in g['moves']:
        if m['player'] == player and m['location'] == location:
            return jsonify({'error': 'Duplicate launch'}), 400

    try:
        r, c = parse_loc(location)
    except Exception:
        return jsonify({'error': 'Invalid location format'}), 400

    if not (1 <= r <= 10 and 1 <= c <= 10):
        return jsonify({'error': 'Off board'}), 400

    opp = g['player2'] if player == g['player1'] else g['player1']
    cell = g['boards'][opp][r-1][c-1]
    result = 'Miss'

    if cell in {info['symbol'] for info in SHIP_INFO.values()}:
        for stype, ship in g['ships'][opp].items():
            if [r, c] in ship['cells']:
                ship['hits'].append([r, c])
                if len(ship['hits']) == ship['length']:
                    ship['status'] = 'Destroyed'
                    result = f'{stype} Destroyed'
                    for (sr, sc) in ship['cells']:
                        g['boards'][opp][sr-1][sc-1] = '@'
                else:
                    ship['status'] = 'Hit'
                    result = 'Hit'
                    g['boards'][opp][r-1][c-1] = '@'
                break
    else:
        g['boards'][opp][r-1][c-1] = 'X'

    g['moves'].append({'player': player, 'location': location, 'result': result, 'turn': g['turn']})

    if all(s['status'] == 'Destroyed' for s in g['ships'][opp].values()):
        g['status'] = 'Over'
        g['winner'] = player
    else:
        g['turn'] += 1
        g['current_turn'] = opp

    games[gid] = g
    return jsonify({'result': result})


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Battleship game server')
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    print(f"Battleship server running on http://localhost:{args.port}")
    app.run(port=args.port, debug=False)

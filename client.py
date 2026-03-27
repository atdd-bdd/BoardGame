"""
Battleship text-mode client.

Usage:
  python client.py                                                   # connects to local server
  python client.py --server http://boardgame.this-is-only-a-test.com  # connects to remote server
"""

import requests
import time
import os
import sys
import argparse

DEFAULT_SERVER = 'http://localhost:5000'

SHIP_TYPES = [
    ('Carrier',    5),
    ('Battleship', 4),
    ('Cruiser',    3),
    ('Submarine',  3),
    ('Destroyer',  2),
]
SHIP_SYMBOLS = {'Carrier': 'A', 'Battleship': 'B', 'Cruiser': 'C', 'Submarine': 'S', 'Destroyer': 'D'}


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def api_json(resp):
    """Decode a response as JSON, printing a helpful message on failure."""
    try:
        return resp.json()
    except Exception as e:
        print(f"\nServer returned a non-JSON response (status {resp.status_code}): {e}")
        print("Make sure the server is running:  python server.py")
        print(f"Response body: {resp.text[:300]}")
        sys.exit(1)


def parse_loc(s):
    try:
        s = s.strip().upper()
        c = ord(s[0]) - ord('A') + 1
        r = int(s[1:])
        return r, c
    except Exception:
        return None, None


def get_cells(loc, orient, length):
    r, c = parse_loc(loc)
    if r is None:
        return None
    if orient == 'Vertical':
        return [(r + i, c) for i in range(length)]
    else:
        return [(r, c + i) for i in range(length)]


def validate_local(board, loc, orient, length):
    cells = get_cells(loc, orient, length)
    if cells is None:
        return "Invalid format — use letter + number (e.g. C5)"
    for r, c in cells:
        if not (1 <= r <= 10 and 1 <= c <= 10):
            return "Off board"
    for r, c in cells:
        if board[r-1][c-1] != ' ':
            return "Overlap with existing ship"
    return None


def board_lines(board, hide_ships=False, label=''):
    sym = {' ': '.', 'A': 'A', 'B': 'B', 'C': 'C', 'S': 'S', 'D': 'D', '@': '@', 'X': 'X'}
    if hide_ships:
        for k in ['A', 'B', 'C', 'S', 'D']:
            sym[k] = '.'
    col_hdrs = ''.join(f'{chr(ord("A")+i):3}' for i in range(10))
    lines = [f'  {label}', f'    {col_hdrs}']
    for r in range(10):
        row = ''.join(f'{sym.get(board[r][c], "."):3}' for c in range(10))
        lines.append(f'{r+1:2}  {row}')
    return lines


def show_boards(game, my_name):
    opp = game['player2'] if my_name == game['player1'] else game['player1']
    left  = board_lines(game['boards'][my_name], hide_ships=False, label=f'YOUR BOARD  ({my_name})')
    right = board_lines(game['boards'][opp],     hide_ships=True,  label=f'OPPONENT    ({opp})')
    for l, r in zip(left, right):
        print(f'{l:<38} {r}')


def show_ships(ships):
    print(f"\n  {'Ship':<12} {'Len':<5} {'Status'}")
    print('  ' + '-' * 28)
    for s in ships.values():
        print(f"  {s['type']:<12} {s['length']:<5} {s['status']}")


def place_ships_phase(server, game_id, my_name):
    local_board = [[' '] * 10 for _ in range(10)]
    placed = []

    clear()
    print(f"=== Ship Placement — {my_name} ===\n")
    print("Coordinates: row,col  (1,1 = top-left, 10,10 = bottom-right)")
    print("Vertical = extends downward   Horizontal = extends rightward\n")

    for ship_type, length in SHIP_TYPES:
        while True:
            for line in board_lines(local_board, label='YOUR BOARD'):
                print(line)
            print(f"\nPlace {ship_type} (length {length}):")
            loc = input("  Location (e.g. A3): ").strip().upper()
            raw = input("  Orientation (V/H): ").strip().upper()
            orient = 'Vertical' if raw == 'V' else 'Horizontal'

            err = validate_local(local_board, loc, orient, length)
            if err:
                clear()
                print(f"  *** {err} *** Try again.\n")
                continue

            cells = get_cells(loc, orient, length)
            sym = SHIP_SYMBOLS[ship_type]
            for r, c in cells:
                local_board[r-1][c-1] = sym
            placed.append({'type': ship_type, 'location': loc, 'orientation': orient})
            clear()
            print(f"  {ship_type} placed!\n")
            break

    resp = requests.post(f'{server}/games/{game_id}/ships/{my_name}', json={'ships': placed})
    if resp.status_code != 200:
        print(f"Server rejected ship placement: {api_json(resp).get('error')}")
        sys.exit(1)

    print("All ships placed and confirmed by server!\n")
    for line in board_lines(local_board, label='YOUR FLEET'):
        print(line)


def game_loop(server, game_id, my_name):
    while True:
        try:
            resp = requests.get(f'{server}/games/{game_id}', timeout=5)
        except requests.RequestException:
            print("Connection error, retrying...")
            time.sleep(2)
            continue

        if resp.status_code != 200:
            print("Game not found on server.")
            sys.exit(1)

        game = api_json(resp)
        clear()

        # Header
        print(f"=== BATTLESHIP  {game_id} ===")
        if game['status'] == 'Over':
            print(f"Status: GAME OVER  |  Winner: {game['winner']}")
        else:
            print(f"Status: {game['status']}  |  Turn {game['turn']}  |  Now playing: {game['current_turn']}")
        print()

        show_boards(game, my_name)

        if game['ships'].get(my_name):
            show_ships(game['ships'][my_name])

        # Recent moves
        moves = game.get('moves', [])
        if moves:
            last = moves[-1]
            print(f"\n  Last move: {last['player']} fired at {last['location']} — {last['result']}")

        if game['status'] == 'Over':
            print()
            if game['winner'] == my_name:
                print("*** YOU WIN!  Congratulations! ***")
            else:
                print("*** YOU LOST.  Better luck next time! ***")
            break

        if game['current_turn'] == my_name:
            print()
            while True:
                target = input("Your move (e.g. C5): ").strip().upper()
                r, c = parse_loc(target)
                if r is None or not (1 <= r <= 10 and 1 <= c <= 10):
                    print("  Invalid — use letter A-J followed by number 1-10 (e.g. C5)")
                    continue
                try:
                    resp = requests.post(
                        f'{server}/games/{game_id}/moves',
                        json={'player': my_name, 'location': target},
                        timeout=5,
                    )
                except requests.RequestException:
                    print("  Connection error, try again.")
                    continue
                if resp.status_code == 200:
                    print(f"  Result: {api_json(resp)['result']}!")
                    time.sleep(1)
                    break
                else:
                    print(f"  Error: {api_json(resp).get('error', 'Unknown error')}")
        else:
            print(f"\n  Waiting for {game['current_turn']} to move...", end='', flush=True)
            time.sleep(2)


def main():
    parser = argparse.ArgumentParser(description='Battleship text client')
    parser.add_argument('--server', default=DEFAULT_SERVER,
                        help=f'Server URL (default: {DEFAULT_SERVER})')
    args = parser.parse_args()
    server = args.server.rstrip('/')

    clear()
    print("=== BATTLESHIP ===\n")
    print(f"Server: {server}\n")
    print("1. Create new game  (you go first)")
    print("2. Join existing game")
    choice = input("\nChoice (1/2): ").strip()

    if choice == '1':
        my_name  = input("Your name: ").strip()
        opp_name = input("Opponent's name: ").strip()
        try:
            resp = requests.post(f'{server}/games', json={'player1': my_name, 'player2': opp_name}, timeout=5)
        except requests.RequestException as e:
            print(f"Cannot reach server: {e}")
            sys.exit(1)
        if resp.status_code != 200:
            print(f"Error: {api_json(resp).get('error')}")
            sys.exit(1)
        game_id = api_json(resp)['game_id']
        print(f"\nGame created!  Game ID: {game_id}")
        print(f"Tell your opponent: python client.py --server {server}")
        print(f"They should choose option 2 and enter Game ID: {game_id}")
        input("\nPress Enter to continue to ship placement...")

    elif choice == '2':
        game_id = input("Game ID: ").strip()
        my_name  = input("Your name: ").strip()
        try:
            resp = requests.get(f'{server}/games/{game_id}', timeout=5)
        except requests.RequestException as e:
            print(f"Cannot reach server: {e}")
            sys.exit(1)
        if resp.status_code != 200:
            print("Game not found on server.")
            sys.exit(1)
        game = api_json(resp)
        if my_name not in (game['player1'], game['player2']):
            print(f"Name '{my_name}' is not part of game '{game_id}'.")
            print(f"  Players: {game['player1']} and {game['player2']}")
            sys.exit(1)
    else:
        print("Invalid choice.")
        sys.exit(1)

    place_ships_phase(server, game_id, my_name)

    print("\nWaiting for opponent to place ships", end='', flush=True)
    while True:
        try:
            resp = requests.get(f'{server}/games/{game_id}', timeout=5)
            if resp.status_code == 200 and api_json(resp)['status'] == 'In Progress':
                break
        except requests.RequestException:
            pass
        print('.', end='', flush=True)
        time.sleep(2)

    print("\nBoth players ready — game on!\n")
    time.sleep(1)
    game_loop(server, game_id, my_name)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nExited.")

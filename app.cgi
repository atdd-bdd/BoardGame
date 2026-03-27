#!/home/boardgame/venv/bin/python3
"""CGI entry point for DreamHost shared hosting."""

import sys
import os

# Add the directory containing server.py to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Point at the SQLite database for persistent storage
os.environ.setdefault('GAME_DB', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'battleship.db'))

from server import app
from wsgiref.handlers import CGIHandler

CGIHandler().run(app)

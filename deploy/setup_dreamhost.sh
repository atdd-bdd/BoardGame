#!/usr/bin/env bash
# Setup script for DreamHost shared hosting.
# Run once via SSH after uploading the repo files.
#
# Usage:
#   ssh user@boardgame.this-is-only-a-test.com
#   cd ~/boardgame.this-is-only-a-test.com
#   bash deploy/setup_dreamhost.sh

set -e

SITE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="$HOME/venv"
PYTHON="python3"

echo "=== Site dir: $SITE_DIR"

# 1. Create virtualenv in the home directory (not inside the web root)
if [ ! -d "$VENV_DIR" ]; then
    echo "=== Creating virtualenv at $VENV_DIR"
    $PYTHON -m venv "$VENV_DIR"
fi

# 2. Install dependencies
echo "=== Installing Python packages"
"$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$VENV_DIR/bin/pip" install --quiet flask>=3.0 requests>=2.32

# 3. Patch the shebang in app.cgi to use the virtualenv Python
PYTHON_PATH="$VENV_DIR/bin/python3"
echo "=== Setting shebang in app.cgi to $PYTHON_PATH"
sed -i "1s|.*|#!$PYTHON_PATH|" "$SITE_DIR/app.cgi"

# 4. Make app.cgi executable
chmod 755 "$SITE_DIR/app.cgi"

# 5. Ensure the SQLite database directory is writable
DB_DIR="$HOME"
echo "=== SQLite database will be at $DB_DIR/battleship.db"

# 6. Patch GAME_DB path in app.cgi to use absolute home path
DB_PATH="$DB_DIR/battleship.db"
sed -i "s|os.path.join(os.path.dirname.*|'$DB_PATH')|" "$SITE_DIR/app.cgi"

echo ""
echo "=== Setup complete."
echo "    Test with: curl -s -X POST https://boardgame.this-is-only-a-test.com/games \\"
echo "         -H 'Content-Type: application/json' \\"
echo "         -d '{\"player1\":\"Alice\",\"player2\":\"Bob\"}'"

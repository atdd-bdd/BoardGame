"""
One-shot deployment script: uploads server files and runs setup on DreamHost.
"""
import os
import sys
import paramiko
from pathlib import Path

HOST = 'boardgame.this-is-only-a-test.com'
PORT = 22
USER = os.environ.get('DEPLOY_USER', '')
PASS = sys.argv[1] if len(sys.argv) > 1 else ''

REMOTE_DIR = f'/home/{USER}/boardgame.this-is-only-a-test.com'

REPO = Path(__file__).parent.parent

FILES = [
    ('server.py',                 f'{REMOTE_DIR}/server.py'),
    ('app.cgi',                   f'{REMOTE_DIR}/app.cgi'),
    ('.htaccess',                 f'{REMOTE_DIR}/.htaccess'),
    ('requirements.txt',          f'{REMOTE_DIR}/requirements.txt'),
    ('index.html',                f'{REMOTE_DIR}/index.html'),
    ('webclient.html',            f'{REMOTE_DIR}/webclient.html'),
    ('player.html',               f'{REMOTE_DIR}/player.html'),
    ('mobile.html',               f'{REMOTE_DIR}/mobile.html'),
    ('deploy/setup_dreamhost.sh', f'{REMOTE_DIR}/deploy/setup_dreamhost.sh'),
]

def run(ssh, cmd):
    print(f'  $ {cmd}')
    _, stdout, stderr = ssh.exec_command(cmd)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip():
        print(out, end='')
    if err.strip():
        print('[stderr]', err, end='', file=sys.stderr)
    return out.strip()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
print(f'Connecting to {HOST}...')
ssh.connect(HOST, port=PORT, username=USER, password=PASS)

sftp = ssh.open_sftp()
for d in [REMOTE_DIR, f'{REMOTE_DIR}/deploy']:
    try:
        sftp.stat(d)
    except FileNotFoundError:
        sftp.mkdir(d)
        print(f'Created {d}')

print('\nUploading files...')
for local, remote in FILES:
    print(f'  {local}')
    sftp.put(str(REPO / local), remote)
sftp.close()

print('\nProbing server environment...')
run(ssh, 'which python3 && python3 --version')
run(ssh, 'which python && python --version 2>&1 || true')
run(ssh, 'which pip3 || which pip || echo "no pip"')
run(ssh, 'which virtualenv || echo "no virtualenv"')
run(ssh, 'ls /usr/local/bin/python* 2>/dev/null || true')
run(ssh, 'python3 -m pip --version 2>&1 || true')

print('\nTrying to install Flask with pip3 --user...')
run(ssh, 'python3 -m pip install --user --quiet flask>=3.0 2>&1 || pip3 install --user --quiet flask>=3.0 2>&1 || echo "pip install failed"')

print('\nChecking if Flask installed...')
run(ssh, 'python3 -c "import flask; print(flask.__version__)"')

print('\nPatching app.cgi shebang and permissions...')
python_path = run(ssh, 'which python3').strip()
run(ssh, f'sed -i "1s|.*|#!{python_path}|" {REMOTE_DIR}/app.cgi')
run(ssh, f'chmod 755 {REMOTE_DIR}/app.cgi')

DB_PATH = f'/home/{USER}/battleship.db'
run(ssh, f"sed -i \"s|os.environ.setdefault.*|os.environ.setdefault('GAME_DB', '{DB_PATH}')|\" {REMOTE_DIR}/app.cgi")

print('\nSmoke test (import server)...')
run(ssh, f'cd {REMOTE_DIR} && python3 -c "from server import app; print(\'ok\')"')

print('\nCurl test...')
run(ssh, (
    "curl -s -X POST https://boardgame.this-is-only-a-test.com/games "
    "-H 'Content-Type: application/json' "
    "-d '{\"player1\":\"Alice\",\"player2\":\"Bob\"}'"
))

ssh.close()
print('\nDone.')

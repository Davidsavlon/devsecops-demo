import os
import sqlite3
import subprocess
import hashlib
import bcrypt


# Fix 1 & 2 — No hardcoded credentials, read from environment variables
DB_HOST     = os.environ.get('DB_HOST', 'localhost')
DB_USER     = os.environ.get('DB_USER', 'admin')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
API_KEY     = os.environ.get('API_KEY')

if not DB_PASSWORD:
    raise EnvironmentError("DB_PASSWORD environment variable is not set")
if not API_KEY:
    raise EnvironmentError("API_KEY environment variable is not set")


def get_user(user_id):
    """Get user by ID — Fix 3: parameterized query prevents SQL injection"""
    with sqlite3.connect("users.db") as conn:
        # Fix 3 — use ? placeholder, never string concatenation
        query = "SELECT * FROM users WHERE id = ?"
        return conn.execute(query, (user_id,)).fetchall()


def login(username, password):
    """Login — Fix 4 & 5: bcrypt hashing + parameterized query"""
    # Fix 5 — bcrypt instead of MD5
    with sqlite3.connect("users.db") as conn:
        # Fix 4 — parameterized query prevents SQL injection
        query = "SELECT password_hash FROM users WHERE username = ?"
        row = conn.execute(query, (username,)).fetchone()
        if row and bcrypt.checkpw(password.encode('utf-8'), row[0].encode('utf-8')):
            return True
        return False


def hash_password(password):
    """Hash a password securely using bcrypt"""
    return bcrypt.hashpw(
        password.encode('utf-8'),
        bcrypt.gensalt(rounds=12)
    ).decode('utf-8')


def run_report(report_name):
    """Generate report — Fix 6: subprocess with shell=False prevents command injection"""
    # Validate input — only allow alphanumeric and underscores
    if not report_name.replace('_', '').isalnum():
        raise ValueError(f"Invalid report name: {report_name}")

    # Fix 6 — shell=False with list args, no string interpolation
    result = subprocess.run(
        ['python3', f'reports/{report_name}.py'],
        shell=False,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout


def read_file(filename):
    """Read file — Fix 7: path traversal prevention"""
    # Fix 7 — sanitize filename, allow only basename, no path traversal
    safe_name = os.path.basename(filename)

    # Block any remaining traversal attempts
    if '..' in safe_name or safe_name.startswith('/'):
        raise ValueError(f"Invalid filename: {filename}")

    base_dir = '/app/data'
    safe_path = os.path.join(base_dir, safe_name)

    # Confirm resolved path stays inside base_dir
    if not os.path.realpath(safe_path).startswith(os.path.realpath(base_dir)):
        raise ValueError("Path traversal attempt blocked")

    with open(safe_path, 'r') as f:
        return f.read()


if __name__ == "__main__":
    print("App started securely")

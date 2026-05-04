import os
import sqlite3
import hashlib

# Hardcoded credentials - security issue
DB_HOST     = "localhost"
DB_USER     = "admin"
DB_PASSWORD = "SuperSecret123"
API_KEY     = "sk-prod-abc123xyz789"

def get_user(user_id):
    """Get user by ID - has SQL injection vulnerability"""
    conn = sqlite3.connect("users.db")
    # Vulnerable: string concatenation in SQL query
    query = "SELECT * FROM users WHERE id = " + user_id
    result = conn.execute(query).fetchall()
    conn.close()
    return result

def login(username, password):
    """Login function - weak password hashing"""
    # Vulnerable: MD5 is cryptographically broken
    hashed = hashlib.md5(password.encode()).hexdigest()
    conn = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{hashed}'"
    return conn.execute(query).fetchone()

def run_report(report_name):
    """Generate report - command injection vulnerability"""
    # Vulnerable: user input passed directly to shell
    os.system(f"python3 reports/{report_name}.py")

def read_file(filename):
    """Read file - path traversal vulnerability"""
    # Vulnerable: no path validation
    with open(f"/app/data/{filename}", "r") as f:
        return f.read()

if __name__ == "__main__":
    print("App started")

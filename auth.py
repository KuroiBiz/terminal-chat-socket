import sqlite3
import hashlib

DB = "users.db"


# ------------------------
# DB INIT
# ------------------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


# ------------------------
# HASH
# ------------------------
def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# ------------------------
# USER OPS
# ------------------------
def user_exists(username):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
    result = cur.fetchone()

    conn.close()
    return result is not None


def register_user(username, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, hash_pw(password))
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()


def verify_user(username, password):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT password FROM users WHERE username=?",
        (username,)
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    return row[0] == hash_pw(password)


# ------------------------
# AUTH FLOW
# ------------------------
def authenticate(client, send):
    send(client, "[AUTH] Use: /login user pass OR /register user pass")

    while True:
        data = client.recv(1024)
        if not data:
            return None

        cmd = data.decode().strip()
        parts = cmd.split()

        if len(parts) < 3:
            send(client, "[!] use: /login user pass")
            continue

        action = parts[0]
        username = parts[1]
        password = " ".join(parts[2:])

        if action == "/register":
            if user_exists(username):
                send(client, "[-] username exists")
                continue

            if register_user(username, password):
                send(client, "[+] registered. now login")
            else:
                send(client, "[-] register failed")

        elif action == "/login":
            if not verify_user(username, password):
                send(client, "[-] invalid credentials")
                continue

            send(client, "[+] login success")
            return username

        else:
            send(client, "[!] unknown command")
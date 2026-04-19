import sqlite3
from datetime import datetime

DB = "chat.db"


# ------------------------
# INIT DB
# ------------------------
def init_msg_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        message TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


# ------------------------
# SAVE MESSAGE
# ------------------------
def save_message(username, message):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cur.execute(
        "INSERT INTO messages (username, message, timestamp) VALUES (?, ?, ?)",
        (username, message, ts)
    )

    conn.commit()
    conn.close()


# ------------------------
# LOAD LAST N MESSAGES
# ------------------------
def get_last_messages(limit=20):
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        "SELECT username, message, timestamp FROM messages ORDER BY id DESC LIMIT ?",
        (limit,)
    )

    rows = cur.fetchall()
    conn.close()

    return rows[::-1]  # reverse for correct order

import os
import sqlite3
from datetime import datetime
from config import DB_PATH, DATA_DIR
from bot.logger import LOG

# Ensure DB directory exists
os.makedirs(DATA_DIR, exist_ok=True)


# ----------------------- DB INIT -----------------------
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        persona TEXT DEFAULT 'professional',
        ts TEXT
    )
    """)

    # EVENTS LOG
    cur.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT,
        user_id TEXT,
        username TEXT,
        action TEXT,
        detail TEXT
    )
    """)

    # CONVERSATIONS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS convs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        role TEXT,
        content TEXT,
        ts TEXT
    )
    """)

    # TASKS
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        task TEXT,
        ts TEXT
    )
    """)

    # PERMANENT MEMORY
    cur.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        user_id TEXT PRIMARY KEY,
        memory TEXT
    )
    """)

    con.commit()
    con.close()
    LOG.info("Database initialized.")


# ----------------------- USER MGMT -----------------------
def save_user(user):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, persona, ts)
    VALUES (?, ?, ?, ?, COALESCE((SELECT persona FROM users WHERE user_id=?), 'professional'), datetime('now'))
    """, (str(user.id), user.username, user.first_name, user.last_name, str(user.id)))
    con.commit()
    con.close()


# ----------------------- EVENTS LOG -----------------------
def log_event(user_id, username, action, detail=""):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    INSERT INTO events (ts, user_id, username, action, detail)
    VALUES (?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), str(user_id), username or "", action, detail))
    con.commit()
    con.close()


# ----------------------- CONVERSATIONS -----------------------
def append_conv(user_id, role, content):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    INSERT INTO convs (user_id, role, content, ts)
    VALUES (?, ?, ?, ?)
    """, (str(user_id), role, content, datetime.utcnow().isoformat()))
    con.commit()
    con.close()


def get_conv_history(user_id, limit=30):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    SELECT role, content FROM convs
    WHERE user_id=?
    ORDER BY id DESC LIMIT ?
    """, (str(user_id), limit))

    rows = cur.fetchall()
    con.close()

    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]


# ----------------------- MEMORY -----------------------
def get_memory(user_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT memory FROM memories WHERE user_id=?", (str(user_id),))
    row = cur.fetchone()
    con.close()
    return row[0] if row else ""


def set_memory(user_id, memory):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO memories (user_id, memory)
    VALUES (?, ?)
    """, (str(user_id), memory))
    con.commit()
    con.close()


# ----------------------- PERSONA MGMT -----------------------
def get_persona(user_id):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("SELECT persona FROM users WHERE user_id=?", (str(user_id),))
    row = cur.fetchone()
    con.close()
    return row[0] if row else "professional"


def set_persona(user_id, persona):
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("UPDATE users SET persona=? WHERE user_id=?", (persona, str(user_id)))
    con.commit()
    con.close()

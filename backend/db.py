import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), 'beespotifywrapped.db')


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS shared_wrapped (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                display_name TEXT,
                data TEXT NOT NULL
            )
        ''')

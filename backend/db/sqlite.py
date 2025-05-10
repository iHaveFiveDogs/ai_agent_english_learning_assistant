import sqlite3
from contextlib import contextmanager

DB_PATH = "word_info.db"

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

def create_word_info_table():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS word_info (
            word TEXT PRIMARY KEY,
            ipa TEXT,
            etymology TEXT
        )
        """)
        conn.commit()

def fetch_word(word):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ipa, etymology FROM word_info WHERE word = ?", (word,))
        row = cursor.fetchone()
        conn.close()
    if row:
        return {"ipa": row[0], "etymology": row[1]}
    return None


def save_words(word, ipa, etymology):
    word_list = [(word, ipa, etymology)]
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executemany("""
            INSERT OR REPLACE INTO word_info (word, ipa, etymology)
            VALUES (?, ?, ?)
        """, word_list)
        conn.commit()

def count_cached_words():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM word_info")
        return cursor.fetchone()[0]

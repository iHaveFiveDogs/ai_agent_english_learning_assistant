import sqlite3
from contextlib import contextmanager

DB_PATH = "word_info.db"
EXPRESS_PATH = "expressions_info.db"
@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()

@contextmanager
def get_expression_connection():
    conn = sqlite3.connect(EXPRESS_PATH)
    try:
        yield conn
    finally:
        conn.close()

# word_info.db
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


#expressions_info.db
def create_expressions_info_table():
    conn = sqlite3.connect("expressions_info.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expressions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression TEXT UNIQUE,
            meaning TEXT,
            etymology TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_expression(expression: str, meaning: str, etymology: str = ""):
    conn = sqlite3.connect("expressions_info.db")
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO expressions (expression, meaning, etymology)
            VALUES (?, ?, ?)
        """, (expression, meaning, etymology))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"⚠️ Expression already exists: {expression}")
    finally:
        conn.close()

def fetch_single_expression(expression: str):
    conn = sqlite3.connect("expressions_info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT expression, meaning, etymology FROM expressions WHERE expression = ?", (expression,))
    result = cursor.fetchone()
    conn.close()
    return result

def fetch_all_expressions():
    conn = sqlite3.connect("expressions_info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT expression, meaning, etymology FROM expressions")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_expression(expression: str):
    conn = sqlite3.connect("expressions_info.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expressions WHERE expression = ?", (expression,))
    conn.commit()
    conn.close()

def count_cached_expressions():
    with get_expression_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM expressions")
        return cursor.fetchone()[0]

if "__main__" == __name__:
    result = count_cached_expressions()
    print(f"Cached expressions: {result}")
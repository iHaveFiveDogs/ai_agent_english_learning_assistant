import sqlite3

def setup_word_db():
    conn = sqlite3.connect("word_info.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS word_info (
            word TEXT PRIMARY KEY,
            ipa TEXT,
            etymology TEXT
        )
    ''')
    conn.commit()
    conn.close()

def fetch_word_from_db(word):
    conn = sqlite3.connect("word_info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM word_info WHERE word = ?", (word,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "ipa": row[0], "etymology": row[1]
        }
    return None

def fetch_all_words_from_db():
    conn = sqlite3.connect("word_info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM word_info")
    rows = cursor.fetchall()
    conn.close()

    return rows

def save_word_to_db(word_pack):
    conn = sqlite3.connect("word_info.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO word_info
        (word, ipa, etymology)
        VALUES (?, ?, ?)
    ''', (
        word_pack["word"],
        word_pack["ipa"],
        word_pack["etymology"]
    ))
    conn.commit()
    conn.close()
# Run this once at app start
if __name__ == "__main__":
    # wordexplainer = fetch_all_words_from_db()
    # print("wordexplainer:")
    # print(wordexplainer)

    # setup_word_db()

    import sqlite3

    conn = sqlite3.connect("word_info.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM word_info")
    print("Cached words:", cursor.fetchone()[0])
    conn.close()

    # import os

    # base_dir = os.path.dirname(__file__)
    # txt_path = os.path.join(base_dir, "..", "resources", "realistic_advanced_words.txt")

    # with open(txt_path, "r", encoding="utf-8") as f:
    #     all_words = [line.strip() for line in f if line.strip()]
    #     unique_words = set(all_words)

    # print("Total words:", len(all_words))
    # print("Unique words:", len(unique_words))

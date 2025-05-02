
import sys
import os
import unicodedata

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.mongodb import articles_chunks, articles_raw
from nltk.tokenize import sent_tokenize

#### handle word_list retrival from alfo agent #####
def extract_word_sentences(chunk, word_list):
    sentences = sent_tokenize(chunk)
    word_sentences = []
    for word in word_list:
        for sentence in sentences:
            if word.lower() in sentence.lower():
                word_sentences.append({"word": word, "sentence": sentence})
                break  # only first match needed
    return word_sentences

#### handle word_list retrival from alfo agent #####

##### handle word explanation from explainer  store into mongodb articles_chunks#####
async def store_word_explanation_to_mongodb(chunk_id, word_list):
    result = await articles_chunks.update_one(
        {"chunk_id": chunk_id},
        {"$push": {
        "word_explanations": {"$each": word_list}
    },
     "$set": {
        "status.word_explained": True
     }}
    )

    
    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            print("✅ word explain Update succeeded!")
        else:
            print("⚠️ Document found, but no changes were made (maybe duplicates or same data).")
    else:
        print("❌ No matching chunk found (chunk_id might be wrong).")

### if there already have word explain ###

async def if_there_are_word_explain(chunk_id):

    
    doc = await articles_chunks.find_one({"chunk_id": chunk_id})
    if doc.get("status", {}).get("word_explained") == True:
        print("✅ Word explainer already done, skipping.")
        return True
    else:
        return False

async def store_combined_word_explanation_to_mongodb(article_id):

    print("Storing combined word explanations...")
    cursor = await articles_chunks.find({"article_id": article_id}).to_list(None)

    all_word_explanations = []

    for chunk in cursor:
        word_packs = chunk.get("word_explanations", [])
        all_word_explanations.extend([p for p in word_packs if p not in all_word_explanations])
        
    result = await articles_raw.update_one(
        {"_id": article_id},
        {"$set": {"word_explanations": all_word_explanations}},
        upsert=True
    )
    

    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            print("✅ word explain Update succeeded!")
        else:
            print("⚠️ word explain service talking : Document found, but no changes were made (maybe duplicates or same data).")
    else:
        print("❌ word explain service talking : No matching article found (article_id might be wrong).")
    
    

    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            print("✅ word explain Update succeeded!")
        else:
            print("⚠️ word explain service talking : Document found, but no changes were made (maybe duplicates or same data).")
    else:
        print("❌ word explain service talking : No matching article found (article_id might be wrong).")

import sqlite3


def save_words_to_cached_db(words):
    if isinstance(words, dict):
        words = [words]  # Convert single word dict to list

    conn = sqlite3.connect("word_info.db")
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT OR REPLACE INTO word_info (word, ipa, etymology)
        VALUES (?, ?, ?)
    ''', [(w["word"], w["ipa"], w["etymology"]) for w in words])
    conn.commit()
    conn.close()

def fetch_word_from_cached_db(word):


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


def load_word_list(path="realistic_advanced_words.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return [w.strip() for w in f if w.strip()]

def filter_uncached_words(word_list):
    return [word for word in word_list if fetch_word_from_cached_db(word) is None]




    if row:
        return {
            "ipa": row[0], "etymology": row[1]
        }
    return None
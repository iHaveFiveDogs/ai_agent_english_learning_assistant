import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.mongodb import articles_chunks, articles_raw
from pymongo import UpdateOne
from nltk.tokenize import sent_tokenize
from db.sqlite import save_words, fetch_word
from services.utiles.print_function_name import log_with_func_name

#### handle word_list retrival from alfo agent #####
def extract_word_sentences(chunk, word_list):
    sentences = sent_tokenize(chunk)
    word_sentences = []
    found = False
    word='' 
    for word in word_list:
        for sentence in sentences:
            if word.lower() in sentence.lower():
                word_sentences.append({"word": word, "sentence": sentence})
                found = True
                break
    if not found:
        word_sentences.append({"word": word, "sentence": "No sentence provided"})  # only first match needed
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
            log_with_func_name("✅ word explain Update succeeded!")
        else:
            log_with_func_name("⚠️ Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ No matching chunk found (chunk_id might be wrong).")

def make_word_explanation_update(chunk_id: str, words: list) -> UpdateOne:
    """
    Returns a MongoDB UpdateOne operation for updating word_explanations in a chunk.
    
    Args:
        chunk_id (str): The chunk identifier.
        words (list): The list of explained word packs.

    Returns:
        UpdateOne: A bulk update operation for MongoDB.
    """
    return UpdateOne(
        {"chunk_id": chunk_id},
        {
            "$set": {
                "word_explanations": words,
                "status.word_explained": True
            }
        }
    )

async def if_there_are_word_explain(chunk_id):

    
    doc = await articles_chunks.find_one({"chunk_id": chunk_id})
    if doc.get("status", {}).get("word_explained") == True:
        log_with_func_name("✅ Word explainer already done, skipping.")
        return True
    else:
        return False

async def store_combined_word_explanation_to_mongodb(article_id):

    log_with_func_name("Storing combined word explanations...")
    cursor = await articles_chunks.find({"article_id": article_id}).to_list(None)

    seen_words = set()
    unique_word_packs = []

    for chunk in cursor:
        word_packs = chunk.get("word_explanations", [])
        for pack in word_packs:
            word = pack.get("word", "").lower().strip()
            if word and word not in seen_words:
                seen_words.add(word)
                unique_word_packs.append(pack)
        
    result = await articles_raw.update_one(
        {"_id": article_id},
        {"$set": {"word_explanations": unique_word_packs}},
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
            log_with_func_name("✅ word explain Update succeeded!")
        else:
            log_with_func_name("⚠️ word explain service talking : Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ word explain service talking : No matching article found (article_id might be wrong).")

def save_words_to_cached_db(word, ipa, etymology):
    save_words(word, ipa, etymology)

def fetch_word_from_cached_db(word):
    return fetch_word(word)

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
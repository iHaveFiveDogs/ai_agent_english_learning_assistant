import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import UpdateOne
from services.utiles.print_function_name import log_with_func_name

##### handle word explanation from explainer  store into mongodb articles_chunks#####
async def store_sentence_explanation_to_mongodb(chunk_id, sentences_list, chunks_collection):
    result = await chunks_collection.update_one(
        {"chunk_id": chunk_id},
        {"$push": {
        "sentence_explanation": {"$each": sentences_list}
    },
     "$set": {
        "status.should_explain_expressions": True
     }}
    )
   
    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            log_with_func_name("✅ sentence explain Update succeeded!")
        else:
            log_with_func_name("⚠️ Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ No matching chunk found (chunk_id might be wrong).")

def make_sentence_explanation_update(chunk_id: str, sentences: list) -> UpdateOne:
    """
    Returns a MongoDB UpdateOne operation for updating sentence_explanations in a chunk.
    
    Args:
        chunk_id (str): The chunk identifier.
        sentences (list): The list of explained sentence packs.
        chunks_collection: The MongoDB collection for chunks.

    Returns:
        UpdateOne: A bulk update operation for MongoDB.
    """
    return UpdateOne(
        {"chunk_id": chunk_id},
        {
            "$set": {
                "sentence_explanation": sentences,
                "status.should_explain_expressions": True
            }
        }
    )

async def if_there_are_sentence_explain(chunk_id, chunks_collection):

    
    doc = await chunks_collection.find_one({"chunk_id": chunk_id})
    if doc.get("status", {}).get("sentence_explained") == True:
        log_with_func_name("✅ Sentence explainer already done, skipping.")
        return True
    else:
        return False

async def store_combined_sentence_explanation_to_mongodb(article_id, chunked_collection, raw_collection):
    
    log_with_func_name("Storing combined sentence explanations...")
    cursor = await chunked_collection.find({"article_id": article_id}).to_list(None)

    seen_sentences = set()
    unique_sentence_packs = []

    for chunk in cursor:
        sentence_packs = chunk.get("sentence_explanation", [])
        for pack in sentence_packs:
            sentence = pack.get("sentence", "").lower().strip()
            if sentence and sentence not in seen_sentences:
                seen_sentences.add(sentence)
                unique_sentence_packs.append(pack)
        
    result = await raw_collection.update_one(
        {"_id": article_id},
        {"$set": {"sentence_explanation": unique_sentence_packs}},
        upsert=True
    )
   
    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            log_with_func_name("✅ sentence explain Update succeeded!")
        else:
            log_with_func_name("⚠️ sentence explain service talking : Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ sentence explain service talking : No matching article found (article_id might be wrong).")




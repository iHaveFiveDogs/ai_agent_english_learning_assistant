import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pymongo import UpdateOne
from nltk.tokenize import sent_tokenize
from db.sqlite import *
from services.utiles.print_function_name import log_with_func_name

#### handle word_list retrival from alfo agent #####
def extract_expression_sentences(chunk, expressions_list):
    sentences = sent_tokenize(chunk)
    expression_sentences = []
    found = False
    expression='' 
    for expression in expressions_list:
        for sentence in sentences:
            if expression.lower() in sentence.lower():
                expression_sentences.append({"expression": expression, "sentence": sentence})
                found = True
                break
    if not found:
        expression_sentences.append({"expression": expression, "sentence": "No sentence provided"})  # only first match needed
    return expression_sentences
#### handle word_list retrival from alfo agent #####
##### handle word explanation from explainer  store into mongodb articles_chunks#####
async def store_expression_explanation_to_mongodb(chunk_id, expressions_list, chunks_collection):
    result = await chunks_collection.update_one(
        {"chunk_id": chunk_id},
        {"$push": {
        "expression_explanation": {"$each": expressions_list}
    },
     "$set": {
        "status.should_explain_expressions": True
     }}
    )

    
    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            log_with_func_name("✅ expression explain Update succeeded!")
        else:
            log_with_func_name("⚠️ Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ No matching chunk found (chunk_id might be wrong).")

def make_expression_explanation_update(chunk_id: str, expressions: list) -> UpdateOne:
    """
    Returns a MongoDB UpdateOne operation for updating expression_explanations in a chunk.
    
    Args:
        chunk_id (str): The chunk identifier.
        words (list): The list of explained word packs.
        chunks_collection: The MongoDB collection for chunks.

    Returns:
        UpdateOne: A bulk update operation for MongoDB.
    """
    return UpdateOne(
        {"chunk_id": chunk_id},
        {
            "$set": {
                "expression_explanation": expressions,
                "status.should_explain_expressions": True
            }
        }
    )

async def if_there_are_expression_explain(chunk_id, chunks_collection):

    
    doc = await chunks_collection.find_one({"chunk_id": chunk_id})
    if doc.get("status", {}).get("expression_explained") == True:
        log_with_func_name("✅ Expression explainer already done, skipping.")
        return True
    else:
        return False

async def store_combined_expression_explanation_to_mongodb(article_id, chunked_collection, raw_collection):
    
    log_with_func_name("Storing combined expression explanations...")
    cursor = await chunked_collection.find({"article_id": article_id}).to_list(None)

    seen_expressions = set()
    unique_expression_packs = []

    for chunk in cursor:
        expression_packs = chunk.get("expression_explanation", [])
        for pack in expression_packs:
            expression = pack.get("expression", "").lower().strip()
            if expression and expression not in seen_expressions:
                seen_expressions.add(expression)
                unique_expression_packs.append(pack)
        
    result = await raw_collection.update_one(
        {"_id": article_id},
        {"$set": {"expression_explanation": unique_expression_packs}},
        upsert=True
    )
    

    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            log_with_func_name("✅ expression explain Update succeeded!")
        else:
            log_with_func_name("⚠️ expression explain service talking : Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ expression explain service talking : No matching article found (article_id might be wrong).")

def save_expressions_to_cached_db(expression, meaning, etymology):
    insert_expression(expression, meaning, etymology)

def fetch_expression_from_cached_db(expression):
    return fetch_single_expression(expression)


def filter_uncached_expressions(expression_list):
    return [expression for expression in expression_list if fetch_expression_from_cached_db(expression) is None]




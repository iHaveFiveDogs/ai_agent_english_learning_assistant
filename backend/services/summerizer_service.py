import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.mongodb import articles_chunks, articles_raw
from pymongo import UpdateOne
from services.utiles.print_function_name import log_with_func_name

async def if_there_are_summary_summarized(chunk_id):
    
    doc = await articles_chunks.find_one({"chunk_id": chunk_id})
    if doc.get("status", {}).get("summarized") == True:
        print("✅ Summarizer already done, skipping.")
        return True
    else:
        return False
    if doc.get("status", {}).get("summarized") == True:
        print("✅ Summarizer already done, skipping.")
        return True
    else:
        return False

async def store_chunked_summaries_to_mongodb(chunk_id, chunk_summary):
    result = await articles_chunks.update_one(
        {"chunk_id": chunk_id},
        {"$set": {
            "summary": chunk_summary,
            "status.summarized": True
        }}
    )
    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            log_with_func_name("✅ chunked Summary Update succeeded!")
        else:
            log_with_func_name("⚠️ Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ No matching chunk found (chunk_id might be wrong).")

async def store_combined_summaries_to_mongodb(article_id, summary):
    log_with_func_name("Storing combined summaries...")
    log_with_func_name(f"Article ID: {article_id}")
    result = await articles_raw.update_one(
        {"_id": article_id},
        {"$set": {"summary": summary}},
        upsert=True
    )
    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            log_with_func_name("✅ combined_summaries Update succeeded!")
        else:
            log_with_func_name("⚠️  summarizer talking :Document found, but no changes were made (maybe duplicates or same data).")
    else:
        log_with_func_name("❌ summarizer talking :No matching article found (article_id might be wrong).")

async def combine_summaries(article_id):
    
    chunks = await articles_chunks.find({"article_id": article_id}).to_list(None)
    
    valid_summaries = []
    missing_chunks = []

    for chunk in chunks:
        summary = chunk.get("summary")
        
        if isinstance(summary, dict) and summary.get("summary").strip():
            valid_summaries.append(summary["summary"].strip())
        else:
            missing_chunks.append(chunk.get("chunk_id", "unknown"))

    if missing_chunks:
        log_with_func_name(f"⚠️  summarizer talking :Missing or invalid summaries for chunks: {missing_chunks}")
    
    if not valid_summaries:
        raise ValueError(f"❌ summarizer talking : No valid summaries found for article {article_id}.")

    combined_summary = "\n".join(valid_summaries)
    
    print("✅ Combined summaries successfully.")
    return combined_summary

async def make_summary_update(chunk_id, summary):
    """
    Returns a MongoDB UpdateOne operation for updating summary in a chunk.
    
    Args:
        chunk_id (str): The chunk identifier.
        summary (str): The summary text.

    Returns:
        UpdateOne: A bulk update operation for MongoDB.
    """
    return UpdateOne(
        {"chunk_id": chunk_id},
        {
            "$set": {
                "summary": summary,
                "status.summarized": True
            }
        }
    )
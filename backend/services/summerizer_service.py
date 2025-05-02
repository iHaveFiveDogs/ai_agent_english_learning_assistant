
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db.mongodb import articles_chunks, articles_raw

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
            print("✅ chunked Summary Update succeeded!")
        else:
            print("⚠️ Document found, but no changes were made (maybe duplicates or same data).")
    else:
        print("❌ No matching chunk found (chunk_id might be wrong).")


async def store_combined_summaries_to_mongodb(article_id, summary):
    print("Storing combined summaries...")
    print(f"Article ID: {article_id}")
    result = await articles_raw.update_one(
        {"_id": article_id},
        {"$set": {"summary": summary}},
        upsert=True
    )
    # Check if the document was found and modified
    if result.matched_count > 0:
        if result.modified_count > 0:
            print("✅ combined_summaries Update succeeded!")
        else:
            print("⚠️  summarizer talking :Document found, but no changes were made (maybe duplicates or same data).")
    else:
        print("❌ summarizer talking :No matching article found (article_id might be wrong).")

async def combine_summaries(article_id):
    print("Combining summaries...")

    chunks = await articles_chunks.find({"article_id": article_id}).to_list(None)
    print("article_id: ",article_id)
    valid_summaries = []
    missing_chunks = []

    for chunk in chunks:
        summary = chunk.get("summary")
        
        if isinstance(summary, dict) and summary.get("summary").strip():
            valid_summaries.append(summary["summary"].strip())
        else:
            missing_chunks.append(chunk.get("chunk_id", "unknown"))

    if missing_chunks:
        print(f"⚠️  summarizer talking :Missing or invalid summaries for chunks: {missing_chunks}")
    
    if not valid_summaries:
        raise ValueError(f"❌ summarizer talking : No valid summaries found for article {article_id}.")

    combined_summary = "\n".join(valid_summaries)
    
    print("✅ Combined summaries successfully.")
    return combined_summary
